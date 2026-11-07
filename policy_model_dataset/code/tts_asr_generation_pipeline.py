"""
=============================================================================
MULTI-GPU DATASET GENERATION PIPELINE — ASR Post-Refinement Training Data
=============================================================================

NOISE SETUP (run once before first use)
-----------------------------------------
Source : MUSAN corpus — noise/free-sound subset
License: CC BY 4.0
Page   : https://openslr.org/17/

Download only the noise subset (~30 files) via HuggingFace:

    from huggingface_hub import list_repo_files, hf_hub_download
    import os

    repo_id   = "FluidInference/musan"
    repo_type = "dataset"

    noise_files = [
        f for f in list_repo_files(repo_id, repo_type=repo_type)
        if "noise/free-sound" in f and f.endswith(".wav")
    ]

    os.makedirs("musan_noise", exist_ok=True)
    for f in noise_files[:30]:
        hf_hub_download(
            repo_id=repo_id,
            repo_type=repo_type,
            filename=f,
            local_dir="musan_noise"
        )

Noise path used in pipeline:
    ./musan_noise/noise/free-sound/

=============================================================================
HYPERPARAMETERS
=============================================================================

    MIN_SNR_DB          = 8       # AddBackgroundNoise min SNR
    MAX_SNR_DB          = 13      # AddBackgroundNoise max SNR
    MIN_WER             = 0.08    # filter: minimum word error rate
    MAX_WER             = 0.55    # filter: maximum word error rate
    MIN_CER             = 0.03    # filter: minimum character error rate
    MAX_CER             = 0.25    # filter: maximum character error rate
    MIN_WORDS           = 6       # filter: skip sentences shorter than this
    TTS_SPEED_MIN       = 1.25    # random speed lower bound
    TTS_SPEED_MAX       = 1.35    # random speed upper bound
    WHISPER_BEAM_SIZE   = 1
    WHISPER_TEMPERATURE = 0.0

Execution Examples

    # Run on all available GPUs with default batch size (16)
    python code/tts_asr_generation_pipeline.py

    # Specify 2 GPUs and custom output location
    python code/tts_asr_generation_pipeline.py --num_gpus 2 --output_path ./custom_sft.json

    # Custom Whisper model and noise directory
    python code/tts_asr_generation_pipeline.py --asr_model base.en --noise_dir ./musan_noise/noise/free-sound/

=============================================================================
"""

import os

# ── Prevent CPU thread thrashing across multi-GPU workers ──
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import soundfile as sf
import torchaudio

# torchaudio >= 2.9 removed torchaudio.info and AudioMetaData
# patch them back via soundfile BEFORE torch_audiomentations is imported
if not hasattr(torchaudio, "AudioMetaData"):

    class AudioMetaData:
        def __init__(
            self,
            sample_rate,
            num_frames,
            num_channels,
            bits_per_sample=0,
            encoding="PCM_S",
        ):
            self.sample_rate = sample_rate
            self.num_frames = num_frames
            self.num_channels = num_channels
            self.bits_per_sample = bits_per_sample
            self.encoding = encoding

    torchaudio.AudioMetaData = AudioMetaData

if not hasattr(torchaudio, "info"):

    def _info(path, *args, **kwargs):
        i = sf.info(str(path))
        return torchaudio.AudioMetaData(
            sample_rate=i.samplerate,
            num_frames=i.frames,
            num_channels=i.channels,
        )

    torchaudio.info = _info

import torchaudio.functional as F_audio
from kokoro import KPipeline
from torch_audiomentations import (
    Compose,
    AddBackgroundNoise,
)
from torch_audiomentations.core.transforms_interface import BaseWaveformTransform
from torch_audiomentations.utils.object_dict import ObjectDict

from nltk.translate.chrf_score import sentence_chrf
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import torch
import torch.multiprocessing as mp
import jiwer
import numpy as np
import json
import argparse
from pathlib import Path

try:
    from datasets import load_dataset as hf_load_dataset
except ImportError:
    hf_load_dataset = None


# ── SNR (real background noise mixing) ──
MIN_SNR_DB = 8.0
MAX_SNR_DB = 13.0

# ── Quality Filters ──
MIN_WER = 0.08
MAX_WER = 0.40
MIN_CER = 0.03
MAX_CER = 0.25
MIN_WORDS = 6

# ── Whisper Inference ──
BEAM_SIZE = 1
TEMPERATURE = 0.0
CONDITION_ON_PREVIOUS_TEXT = False

TARGET_SAMPLE_RATE = 16000


def load_models(asr_model_name="tiny.en"):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # KPipeline runs Kokoro-82M natively on PyTorch CUDA — no ONNX Runtime needed
    tts_model = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device=device)
    print(f"[load_models] KPipeline device: {device}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    # Map short names (e.g. tiny.en) to HuggingFace model repo
    if not asr_model_name.startswith("openai/whisper-") and "/" not in asr_model_name:
        hf_model_id = f"openai/whisper-{asr_model_name}"
    else:
        hf_model_id = asr_model_name

    processor = AutoProcessor.from_pretrained(hf_model_id)
    asr_model = AutoModelForSpeechSeq2Seq.from_pretrained(
        hf_model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
    ).to(device)

    return tts_model, asr_model, processor


def resolve_path(path: str) -> str:
    if os.path.exists(path):
        return path
    candidate = Path(__file__).resolve().parent.parent / os.path.basename(path)
    if candidate.exists():
        return str(candidate)
    return path


def load_ground_truth_dataset(
    path: str = "./datasets/policy_model_dataset/combined_dataset.json",
):
    path = resolve_path(path)
    if hf_load_dataset is not None:
        try:
            ds = hf_load_dataset("json", data_files=path, split="train")
            return ds["refined_text"]
        except Exception:
            pass
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line)["refined_text"] for line in f if line.strip()]


def load_tts_dataset(
    path: str = "./datasets/policy_model_dataset/tts_input_dataset.json",
):
    path = resolve_path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data["refined_text"])


class RandomTimeMask(BaseWaveformTransform):
    """
    Native torch-audiomentations transform that lives directly inside Compose([]).
    """

    supported_modes = {"per_batch", "per_example"}

    def __init__(
        self,
        min_ratio: float = 0.05,
        max_ratio: float = 0.15,
        mode: str = "per_example",
        p: float = 0.5,
        sample_rate: int = None,
        output_type: str = "tensor",
    ):
        super().__init__(
            mode=mode,
            p=p,
            sample_rate=sample_rate,
            output_type=output_type,
        )
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

    def randomize_parameters(
        self,
        samples: torch.Tensor,
        sample_rate: int = None,
        targets=None,
        target_rate=None,
        **kwargs,
    ):
        batch_size, _, total_samples = samples.shape
        device = samples.device

        # Generate random lengths and start indices for every selected item in the batch
        ratios = torch.empty(batch_size, device=device).uniform_(
            self.min_ratio, self.max_ratio
        )
        mask_lens = (ratios * total_samples).long()

        start_indices = [
            int(
                torch.randint(
                    0, max(1, total_samples - int(m_len)), (1,), device=device
                ).item()
            )
            for m_len in mask_lens
        ]

        self.transform_parameters["mask_lens"] = mask_lens
        self.transform_parameters["start_indices"] = start_indices

    def apply_transform(
        self,
        samples: torch.Tensor,
        sample_rate: int = None,
        targets=None,
        target_rate=None,
        **kwargs,
    ) -> ObjectDict:
        out = samples.clone()
        mask_lens = self.transform_parameters["mask_lens"]
        start_indices = self.transform_parameters["start_indices"]

        for idx, (start_idx, mask_len) in enumerate(zip(start_indices, mask_lens)):
            if mask_len > 0:
                out[idx, :, start_idx : start_idx + mask_len] = 0.0

        return ObjectDict(
            samples=out,
            sample_rate=sample_rate,
            targets=targets,
            target_rate=target_rate,
        )


# Instantiate the GPU pipeline once on your device
def get_gpu_augmenter(
    sample_rate: int = TARGET_SAMPLE_RATE,
    noise_dir: str = "/kaggle/working/musan_noise/noise/free-sound/",
    device: str = "cuda",
):
    augmenter = Compose(
        transforms=[
            # 1. Packet/VoIP chunk dropouts
            RandomTimeMask(
                min_ratio=0.05,
                max_ratio=0.15,
                p=0.5,
                sample_rate=sample_rate,
                output_type="tensor",
            ),
            AddBackgroundNoise(
                background_paths=noise_dir,
                min_snr_in_db=MIN_SNR_DB,
                max_snr_in_db=MAX_SNR_DB,
                p=1.0,
                output_type="tensor",
            ),
        ],
        output_type="tensor",
    ).to(device)
    return augmenter


def noise_addition_gpu(
    audio_batch: torch.Tensor, augmenter, sample_rate: int = 16000
) -> torch.Tensor:
    """
    Args:
        audio_batch: Tensor of shape (B, T) or (B, 1, T), float32, on CUDA.
        augmenter: Initialized torch-audiomentations Compose module on CUDA.
    Returns:
        Tensor of shape (B, 1, T) clipped to [-1.0, 1.0].
    """
    if audio_batch.ndim == 1:
        audio_batch = audio_batch.unsqueeze(0).unsqueeze(0)
    elif audio_batch.ndim == 2:
        audio_batch = audio_batch.unsqueeze(1)

    noise_audio = augmenter(audio_batch, sample_rate=sample_rate)
    noise_audio = torch.clamp(noise_audio, min=-1.0, max=1.0)

    return noise_audio


def normalize(text):
    return (
        text.lower()
        .replace("-", " ")  # "re-establish" → "re establish"
        .replace(",", "")  # "47,312" → "47312"
        .replace(".", "")
        .replace("%", " percent")  # optional: "14%" → "14 percent"
    )


def calculate_metrics(targets, predictions):
    result = []
    for target, prediction in zip(targets, predictions):
        target = normalize(target)
        prediction = normalize(prediction)

        result.append((jiwer.wer(target, prediction), jiwer.cer(target, prediction)))

    return result


def gpu_worker(gpu_id: int, start_idx: int, end_idx: int, args):
    # Lock this entire OS process (PyTorch, ONNX, CTranslate2) to physical `gpu_id`
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    torch.set_num_threads(2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Distinct random seeds per worker
    np.random.seed(42 + gpu_id)
    torch.manual_seed(42 + gpu_id)

    # Load slice inside worker to avoid pickling large arrays over IPC
    tts_texts = load_tts_dataset(args.dataset_path)[start_idx:end_idx]
    ground_truth_texts = load_ground_truth_dataset(args.combined_path)[
        start_idx:end_idx
    ]

    print(
        f"[GPU {gpu_id}] Initialized on {device} | Slice [{start_idx}:{end_idx}] ({len(tts_texts)} items)"
    )

    gpu_augmenter = get_gpu_augmenter(
        sample_rate=TARGET_SAMPLE_RATE,
        noise_dir=args.noise_dir,
        device=str(device),
    )
    tts_model, asr_model, processor = load_models(
        asr_model_name=args.asr_model,
    )

    noise_dataset = []
    discarded_dataset = []
    batch_size = args.batch_size

    for i in range(0, len(tts_texts), batch_size):
        print(f"[GPU {gpu_id}] Batch {i}/{len(tts_texts)} =======================")
        batch_indices = [
            idx
            for idx in range(i, min(i + batch_size, len(tts_texts)))
            if len(tts_texts[idx].split()) >= MIN_WORDS
        ]
        if not batch_indices:
            continue

        batch_tts_text = [tts_texts[idx] for idx in batch_indices]
        batch_ground_truth = [ground_truth_texts[idx] for idx in batch_indices]

        # Step A+B: KPipeline handles phonemization + GPU synthesis in one pass
        print(f"[GPU {gpu_id}][A+B] TTS synthesis via KPipeline | {len(batch_tts_text)} sentences")
        audio_tensors = []
        audio_lengths = []
        for text in batch_tts_text:
            rand_speed = float(np.random.uniform(1.25, 1.35))
            voice = np.random.choice(["af_sarah", "af_bella", "am_adam", "bf_emma"])
            # KPipeline yields (graphemes, phonemes, audio) chunks per sentence
            chunks = []
            for _, _, audio_chunk in tts_model(text, voice=voice, speed=rand_speed):
                if isinstance(audio_chunk, torch.Tensor):
                    chunks.append(audio_chunk.detach().cpu().numpy())
                else:
                    chunks.append(np.asarray(audio_chunk, dtype=np.float32))
            if not chunks:
                continue
            # Concatenate sentence chunks → single 1D numpy array at 24kHz
            audio_np = np.concatenate(chunks).astype(np.float32)
            audio_tensor = torch.from_numpy(audio_np).to(device)
            # Resample 24kHz (Kokoro native) → TARGET_SAMPLE_RATE (16kHz for Whisper)
            audio_tensor = F_audio.resample(
                audio_tensor,
                orig_freq=24000,
                new_freq=TARGET_SAMPLE_RATE,
            )
            # Flatten (1, T) to 1D (T,) to store a flat list [audio_1, audio_2] instead of nested [[audio_1], [audio_2]]
            flat_audio = audio_tensor.squeeze()
            audio_tensors.append(flat_audio)
            audio_lengths.append(flat_audio.shape[0])

        # Step C: True Batched GPU Noise Addition (1 single GPU kernel for all B items)
        max_len = max(audio_lengths)
        print(f"[GPU {gpu_id}][C] Noise augmentation | batch shape: ({len(audio_tensors)}, 1, {max_len})")
        batch_audios = torch.zeros(
            size=(len(audio_tensors), 1, max_len), dtype=torch.float32, device=device
        )
        for idx, (audio, length) in enumerate(zip(audio_tensors, audio_lengths)):
            batch_audios[idx, 0, :length] = audio

        with torch.no_grad():
            noise_voice = noise_addition_gpu(
                batch_audios,
                augmenter=gpu_augmenter,
                sample_rate=TARGET_SAMPLE_RATE,
            )

        # Step D: True Batched Whisper Inference on GPU
        print(f"[GPU {gpu_id}][D] Whisper inference | batch: {len(audio_lengths)} clips")
        audio_list = [
            noise_voice[idx, 0, :length].cpu().numpy()
            for idx, length in enumerate(audio_lengths)
        ]
        inputs = processor(
            audio_list,
            sampling_rate=TARGET_SAMPLE_RATE,
            return_tensors="pt",
        ).to(device, dtype=torch.float16 if torch.cuda.is_available() else torch.float32)

        with torch.no_grad():
            predicted_ids = asr_model.generate(
                inputs.input_features,
                max_new_tokens=128,
            )
        raw_transcriptions = processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )
        noise_transcribe = [t.strip() for t in raw_transcriptions]
        print(f"[GPU {gpu_id}][RESULT] transcribed={len(noise_transcribe)} | sample: {noise_transcribe[0][:60] if noise_transcribe else 'N/A'}")

        metrics = calculate_metrics(batch_tts_text, noise_transcribe)
        debug_count = 0
        for raw_asr, refined_text, tts_text, (wer, cer) in zip(
            noise_transcribe, batch_ground_truth, batch_tts_text, metrics
        ):
            chrf = sentence_chrf(tts_text, raw_asr)
            if MIN_CER <= cer <= MAX_CER and MIN_WER <= wer <= MAX_WER and chrf > 0.03:
                print(
                    f"[GPU {gpu_id} | ACCEPTED] WER: {wer:.2%}   CER: {cer:.2%}   chrF: {chrf:.4f}"
                )
                if debug_count < args.debug_samples:
                    print(
                        f"\n[GPU {gpu_id}] tts text : {tts_text}\n"
                        f"[GPU {gpu_id}] refined  : {refined_text}\n"
                        f"[GPU {gpu_id}] raw_asr  : {raw_asr}\n"
                    )
                    debug_count += 1
                noise_dataset.append(
                    {
                        "raw_asr": raw_asr,
                        "refined_text": refined_text,
                    }
                )
            else:
                print(
                    f"[GPU {gpu_id} | DISCARD] WER: {wer:.2%}   CER: {cer:.2%}   chrF: {chrf:.4f}"
                )
                discarded_dataset.append(
                    {
                        "raw_asr": raw_asr,
                        "refined_text": refined_text,
                        "tts_text": tts_text,
                        "wer": round(wer, 4),
                        "cer": round(cer, 4),
                        "chrf": round(chrf, 4),
                    }
                )

    temp_out = f"{args.output_path}.part_{gpu_id}.json"
    temp_disc = f"{args.discarded_path}.part_{gpu_id}.json"

    with open(temp_out, "w", encoding="utf-8") as f:
        json.dump(noise_dataset, f, indent=2)

    with open(temp_disc, "w", encoding="utf-8") as f:
        json.dump(discarded_dataset, f, indent=2)

    print(f"[GPU {gpu_id}] Completed! Accepted: {len(noise_dataset)}")


def run_multi_gpu_pipeline(args):
    tts_texts = load_tts_dataset(args.dataset_path)
    ground_truth_texts = load_ground_truth_dataset(args.combined_path)

    assert len(tts_texts) == len(ground_truth_texts), (
        f"Length mismatch: {len(tts_texts)} TTS items vs {len(ground_truth_texts)} ground truth records"
    )

    total_samples = len(tts_texts)
    del tts_texts, ground_truth_texts  # Free memory in parent coordinator

    detected_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 1
    num_gpus = (
        min(args.num_gpus, max(1, detected_gpus))
        if args.num_gpus is not None
        else max(1, detected_gpus)
    )

    print("=================================================================")
    print(f"Total dataset size : {total_samples}")
    print(f"Workers / GPUs     : {num_gpus}")
    print("=================================================================")

    # Pre-cache Whisper weights once before spawning workers
    hf_model_id = (
        f"openai/whisper-{args.asr_model}"
        if not args.asr_model.startswith("openai/whisper-") and "/" not in args.asr_model
        else args.asr_model
    )
    AutoProcessor.from_pretrained(hf_model_id)
    AutoModelForSpeechSeq2Seq.from_pretrained(hf_model_id)

    if num_gpus == 1:
        gpu_worker(0, 0, total_samples, args)
        os.replace(f"{args.output_path}.part_0.json", args.output_path)
        os.replace(f"{args.discarded_path}.part_0.json", args.discarded_path)
        return

    chunk_size = (total_samples + num_gpus - 1) // num_gpus
    processes = []

    for gpu_id in range(num_gpus):
        start_idx = gpu_id * chunk_size
        end_idx = min(start_idx + chunk_size, total_samples)
        if start_idx >= end_idx:
            continue

        p = mp.Process(
            target=gpu_worker,
            args=(gpu_id, start_idx, end_idx, args),
        )
        p.start()
        processes.append((gpu_id, p))

    for gpu_id, p in processes:
        p.join()
        if p.exitcode != 0:
            raise RuntimeError(
                f"Worker on GPU {gpu_id} crashed with exit code {p.exitcode}"
            )

    final_noise_dataset = []
    final_discarded_dataset = []

    for gpu_id in range(num_gpus):
        temp_out = f"{args.output_path}.part_{gpu_id}.json"
        temp_disc = f"{args.discarded_path}.part_{gpu_id}.json"

        if os.path.exists(temp_out):
            with open(temp_out, "r", encoding="utf-8") as f:
                final_noise_dataset.extend(json.load(f))
            os.remove(temp_out)

        if os.path.exists(temp_disc):
            with open(temp_disc, "r", encoding="utf-8") as f:
                final_discarded_dataset.extend(json.load(f))
            os.remove(temp_disc)

    with open(args.output_path, "w", encoding="utf-8") as f:
        json.dump(final_noise_dataset, f, indent=2)

    with open(args.discarded_path, "w", encoding="utf-8") as f:
        json.dump(final_discarded_dataset, f, indent=2)

    print("=================================================================")
    print(f"Done! Accepted: {len(final_noise_dataset)} -> {args.output_path}")
    print(f"Discarded     : {len(final_discarded_dataset)} -> {args.discarded_path}")
    print("=================================================================")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)

    parser = argparse.ArgumentParser(
        description="Multi-GPU TTS-ASR Noise Generation Pipeline"
    )
    parser.add_argument(
        "--batch_size", type=int, default=16, help="Batch size for processing"
    )
    parser.add_argument(
        "--num_gpus",
        type=int,
        default=None,
        help="Number of GPUs to use (defaults to all available)",
    )
    parser.add_argument(
        "--dataset_path",
        type=str,
        default="./datasets/policy_model_dataset/tts_input_dataset.json",
        help="Path to input text dataset JSON (cleaned for TTS)",
    )
    parser.add_argument(
        "--combined_path",
        type=str,
        default="./datasets/policy_model_dataset/combined_dataset.json",
        help="Path to combined dataset JSON (ground-truth formatted)",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="sft_train.json",
        help="Output JSON file destination",
    )
    parser.add_argument(
        "--discarded_path",
        type=str,
        default="discarded_samples.json",
        help="Destination file for discarded samples",
    )
    parser.add_argument(
        "--noise_dir",
        type=str,
        default="/kaggle/working/musan_noise/noise/free-sound/",
        help="Directory with background noise audio files",
    )
    parser.add_argument(
        "--asr_model", type=str, default="tiny.en", help="Whisper model name"
    )
    parser.add_argument(
        "--debug_samples",
        type=int,
        default=3,
        help="Number of preview outputs to print",
    )
    args = parser.parse_args()

    run_multi_gpu_pipeline(args)
