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

    MIN_SNR_DB          = 3.0     # Primary MUSAN noise min SNR (tougher!)
    MAX_SNR_DB          = 9.0     # Primary MUSAN noise max SNR
    WORDS_PER_EDIT      = 18      # Require >= 1 word error per 18 words
    MIN_LEN_RATIO       = 0.85    # Reject truncated ASR outputs (<85% length)
    MAX_LEN_RATIO       = 1.25    # Reject hallucinated ASR outputs (>125% length)
    MAX_WER             = 0.50    # filter: maximum word error rate
    MAX_CER             = 0.25    # filter: maximum character error rate
    MIN_WORDS           = 6       # filter: skip sentences shorter than this
    TTS_SPEED_MIN       = 1.25    # random speed lower bound
    TTS_SPEED_MAX       = 1.35    # random speed upper bound

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
import torch.nn.functional as F_nn
from kokoro import KPipeline
from torch_audiomentations import (
    Compose,
    AddBackgroundNoise,
    AddColoredNoise,
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


# ── CHANGE 1: Tougher Noise SNR, Lead-in Padding, & Smarter Filter Rules ──
MIN_SNR_DB = 3.0
MAX_SNR_DB = 9.0

LEAD_SILENCE_SEC = 0.25  # 250ms lead-in so first syllable isn't cut off
TAIL_SILENCE_SEC = 0.15  # 150ms tail padding

WORDS_PER_EDIT = 18      # Require at least 1 word error per 18 words (min 1)
MIN_LEN_RATIO = 0.85     # Reject truncated sentences missing >15% of words
MAX_LEN_RATIO = 1.25     # Reject runaway hallucinations
MAX_WER = 0.50
MAX_CER = 0.25
MIN_WORDS = 6

# ── Whisper Inference ──
BEAM_SIZE = 1
TEMPERATURE = 0.0
CONDITION_ON_PREVIOUS_TEXT = False

TARGET_SAMPLE_RATE = 16000


def load_models(asr_model_name="tiny.en", device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    is_cuda = (
        isinstance(device, torch.device) and device.type == "cuda"
    ) or str(device).startswith("cuda")
    torch_dtype = torch.float16 if is_cuda else torch.float32

    # KPipeline runs Kokoro-82M natively on PyTorch CUDA — no ONNX Runtime needed
    tts_model = KPipeline(
        lang_code="a", repo_id="hexgrad/Kokoro-82M", device=str(device)
    )
    print(f"[load_models] KPipeline device: {device}")

    # Map short names (e.g. tiny.en) to HuggingFace model repo
    if (
        not asr_model_name.startswith("openai/whisper-")
        and "/" not in asr_model_name
    ):
        hf_model_id = f"openai/whisper-{asr_model_name}"
    else:
        hf_model_id = asr_model_name

    processor = AutoProcessor.from_pretrained(hf_model_id)
    asr_model = AutoModelForSpeechSeq2Seq.from_pretrained(
        hf_model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
    ).to(device)
    asr_model.eval()

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
            return list(ds["refined_text"])
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


# ── CHANGE 2: 3-Layer Complex GPU Audio Degradation Pipeline ──
class RandomMicMuffle(BaseWaveformTransform):
    """
    Simulates a cheap headset, phone call, or distant laptop microphone on GPU using FFT.
    Cuts sub-bass (<150-300Hz) and muffles sharp studio consonant highs (>2800-4200Hz)
    so sounds like 's', 'f', 't', 'k', 'b', 'v' blur naturally under background noise.
    """

    supported_modes = {"per_batch", "per_example"}

    def __init__(
        self,
        min_low_cutoff: float = 150.0,
        max_low_cutoff: float = 300.0,
        min_high_cutoff: float = 2800.0,
        max_high_cutoff: float = 4200.0,
        mode: str = "per_example",
        p: float = 0.75,
        sample_rate: int = None,
        output_type: str = "tensor",
    ):
        super().__init__(
            mode=mode,
            p=p,
            sample_rate=sample_rate,
            output_type=output_type,
        )
        self.min_low_cutoff = min_low_cutoff
        self.max_low_cutoff = max_low_cutoff
        self.min_high_cutoff = min_high_cutoff
        self.max_high_cutoff = max_high_cutoff

    def randomize_parameters(
        self,
        samples: torch.Tensor,
        sample_rate: int = None,
        targets=None,
        target_rate=None,
        **kwargs,
    ):
        batch_size = samples.shape[0]
        device = samples.device
        self.transform_parameters["low_cutoffs"] = torch.empty(
            batch_size, device=device
        ).uniform_(self.min_low_cutoff, self.max_low_cutoff)
        self.transform_parameters["high_cutoffs"] = torch.empty(
            batch_size, device=device
        ).uniform_(self.min_high_cutoff, self.max_high_cutoff)

    def apply_transform(
        self,
        samples: torch.Tensor,
        sample_rate: int = None,
        targets=None,
        target_rate=None,
        **kwargs,
    ) -> ObjectDict:
        sr = sample_rate or TARGET_SAMPLE_RATE
        total_samples = samples.shape[-1]
        device = samples.device

        spec = torch.fft.rfft(samples, dim=-1)
        freqs = torch.fft.rfftfreq(total_samples, d=1.0 / sr, device=device)

        low_cuts = self.transform_parameters["low_cutoffs"].view(-1, 1, 1)
        high_cuts = self.transform_parameters["high_cutoffs"].view(-1, 1, 1)
        freqs_b = freqs.view(1, 1, -1)

        # Smooth frequency roll-off
        high_mask = torch.sigmoid(-(freqs_b - high_cuts) / 250.0)
        low_mask = torch.sigmoid((freqs_b - low_cuts) / 50.0)
        filtered = torch.fft.irfft(
            spec * high_mask * low_mask, n=total_samples, dim=-1
        )

        return ObjectDict(
            samples=filtered,
            sample_rate=sample_rate,
            targets=targets,
            target_rate=target_rate,
        )


def get_gpu_augmenter(
    sample_rate: int = TARGET_SAMPLE_RATE,
    noise_dir: str = "/kaggle/working/musan_noise/noise/free-sound/",
    device: str = "cuda",
):
    augmenter = Compose(
        transforms=[
            # Layer 1: Microphone muffling (blurs studio-sharp TTS consonants)
            RandomMicMuffle(
                min_high_cutoff=2800.0,
                max_high_cutoff=4200.0,
                p=0.75,
                sample_rate=sample_rate,
                output_type="tensor",
            ),
            # Layer 2: Continuous ambient room/fan hum (fills silent gaps in MUSAN clips)
            AddColoredNoise(
                min_snr_in_db=10.0,
                max_snr_in_db=16.0,
                min_f_decay=-3.0,
                max_f_decay=0.0,
                p=0.8,
                sample_rate=sample_rate,
                output_type="tensor",
            ),
            # Layer 3A: Primary real-world MUSAN background noise (3-9 dB)
            AddBackgroundNoise(
                background_paths=noise_dir,
                min_snr_in_db=MIN_SNR_DB,
                max_snr_in_db=MAX_SNR_DB,
                p=1.0,
                output_type="tensor",
            ),
            # Layer 3B: Secondary overlapping MUSAN noise for multi-source complexity
            AddBackgroundNoise(
                background_paths=noise_dir,
                min_snr_in_db=MIN_SNR_DB + 3.0,
                max_snr_in_db=MAX_SNR_DB + 3.0,
                p=0.6,
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
        .replace(",", "")   # "47,312" → "47312"
        .replace(".", "")
        .replace(":", "")
        .replace(";", "")
        .replace("`", "")
        .replace('"', "")
        .replace("%", " percent")  # "14%" → "14 percent"
        .replace("$", "")
    )


# ── CHANGE 4A: Compute word_edits, required_edits, len_ratio, WER, and CER ──
def calculate_metrics(tts_targets, refined_targets, predictions):
    result = []
    for tts_t, ref_t, pred in zip(tts_targets, refined_targets, predictions):
        norm_tts = normalize(tts_t)
        norm_ref = normalize(ref_t)
        norm_pred = normalize(pred)

        # 1. Exact count of word mistakes compared to refined_text
        word_out = jiwer.process_words(norm_ref, norm_pred)
        word_edits = (
            word_out.substitutions + word_out.deletions + word_out.insertions
        )

        # 2. Scale required edits with paragraph length (1 edit per 18 words, min 1)
        ref_words = len(norm_ref.split())
        pred_words = len(norm_pred.split())
        required_edits = max(1, ref_words // WORDS_PER_EDIT)

        # 3. Length ratio check to catch cut-off / truncated transcriptions
        len_ratio = pred_words / max(1, ref_words)

        # 4. Best WER & CER between tts_text and refined_text
        wer = min(jiwer.wer(norm_tts, norm_pred), word_out.wer)
        cer = min(
            jiwer.cer(norm_tts, norm_pred), jiwer.cer(norm_ref, norm_pred)
        )

        result.append((word_edits, required_edits, len_ratio, wer, cer))

    return result


def gpu_worker(gpu_id: int, start_idx: int, end_idx: int, args):
    torch.set_num_threads(2)
    if torch.cuda.is_available():
        torch.cuda.set_device(gpu_id)
        device = torch.device(f"cuda:{gpu_id}")
    else:
        device = torch.device("cpu")

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
        device=device,
    )

    noise_dataset = []
    discarded_dataset = []
    batch_size = args.batch_size

    lead_samples = int(LEAD_SILENCE_SEC * TARGET_SAMPLE_RATE)
    tail_samples = int(TAIL_SILENCE_SEC * TARGET_SAMPLE_RATE)

    for i in range(0, len(tts_texts), batch_size):
        print(
            f"[GPU {gpu_id}] Batch {i}/{len(tts_texts)} ======================="
        )
        batch_indices = [
            idx
            for idx in range(i, min(i + batch_size, len(tts_texts)))
            if tts_texts[idx]
            and ground_truth_texts[idx]
            and len(tts_texts[idx].split()) >= MIN_WORDS
        ]
        if not batch_indices:
            continue

        batch_tts_text = [tts_texts[idx] for idx in batch_indices]
        batch_ground_truth = [ground_truth_texts[idx] for idx in batch_indices]

        # Step A+B: KPipeline handles phonemization + GPU synthesis in one pass
        print(
            f"[GPU {gpu_id}][A+B] TTS synthesis via KPipeline | {len(batch_tts_text)} sentences"
        )
        audio_tensors = []
        audio_lengths = []
        valid_tts_text = []
        valid_ground_truth = []

        for text, gt_text in zip(batch_tts_text, batch_ground_truth):
            rand_speed = float(np.random.uniform(1.25, 1.35))
            voice = np.random.choice(
                ["af_sarah", "af_bella", "am_adam", "bf_emma"]
            )
            chunks = []
            for _, _, audio_chunk in tts_model(
                text, voice=voice, speed=rand_speed
            ):
                if isinstance(audio_chunk, torch.Tensor):
                    chunks.append(audio_chunk.detach().cpu().numpy())
                else:
                    chunks.append(np.asarray(audio_chunk, dtype=np.float32))
            if not chunks:
                continue

            audio_np = np.concatenate(chunks).astype(np.float32)
            audio_tensor = torch.from_numpy(audio_np).to(device)
            audio_tensor = F_audio.resample(
                audio_tensor,
                orig_freq=24000,
                new_freq=TARGET_SAMPLE_RATE,
            )
            flat_audio = audio_tensor.squeeze()

            # ── CHANGE 3: Add 0.25s lead-in padding so first syllable isn't cut off ──
            flat_audio = F_nn.pad(
                flat_audio, (lead_samples, tail_samples), value=0.0
            )

            audio_tensors.append(flat_audio)
            audio_lengths.append(flat_audio.shape[0])
            valid_tts_text.append(text)
            valid_ground_truth.append(gt_text)

        if not audio_tensors:
            continue

        # Step C: True Batched GPU Noise Addition (Repeat audio instead of 0.0s)
        max_len = max(audio_lengths)
        print(
            f"[GPU {gpu_id}][C] Complex 3-Layer Noise | batch shape: ({len(audio_tensors)}, 1, {max_len})"
        )
        batch_audios = torch.zeros(
            size=(len(audio_tensors), 1, max_len),
            dtype=torch.float32,
            device=device,
        )
        for idx, (audio, length) in enumerate(
            zip(audio_tensors, audio_lengths)
        ):
            repeats = (max_len // length) + 1
            batch_audios[idx, 0, :] = audio.repeat(repeats)[:max_len]

        with torch.no_grad():
            noise_voice = noise_addition_gpu(
                batch_audios,
                augmenter=gpu_augmenter,
                sample_rate=TARGET_SAMPLE_RATE,
            )

        # Step D: True Batched Whisper Inference on GPU
        print(
            f"[GPU {gpu_id}][D] Whisper inference | batch: {len(audio_lengths)} clips"
        )
        audio_list = [
            noise_voice[idx, 0, :length].cpu().numpy()
            for idx, length in enumerate(audio_lengths)
        ]
        inputs = processor(
            audio_list,
            sampling_rate=TARGET_SAMPLE_RATE,
            return_tensors="pt",
            truncation=False,
            padding="longest",
            return_attention_mask=True,
        )

        input_features = inputs.input_features
        attention_mask = inputs.attention_mask

        if input_features.shape[-1] < 3000:
            pad_len = 3000 - input_features.shape[-1]
            input_features = F_nn.pad(input_features, (0, pad_len), value=0.0)
            attention_mask = F_nn.pad(attention_mask, (0, pad_len), value=0)

        target_dtype = (
            torch.float16 if torch.cuda.is_available() else torch.float32
        )
        input_features = input_features.to(device, dtype=target_dtype)
        attention_mask = attention_mask.to(device)

        with torch.no_grad():
            predicted_ids = asr_model.generate(
                input_features,
                attention_mask=attention_mask,
                max_new_tokens=440,
                num_beams=BEAM_SIZE,
                do_sample=False,
                no_repeat_ngram_size=4,
            )

        raw_transcriptions = processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )
        noise_transcribe = [t.strip() for t in raw_transcriptions]
        print(
            f"[GPU {gpu_id}][RESULT] transcribed={len(noise_transcribe)} | sample: {noise_transcribe[0][:60] if noise_transcribe else 'N/A'}"
        )

        # ── CHANGE 4B: Filter by scaled required_edits, len_ratio, WER, and CER ──
        metrics = calculate_metrics(
            valid_tts_text, valid_ground_truth, noise_transcribe
        )
        debug_count = 0
        for raw_asr, refined_text, tts_text, (
            word_edits,
            required_edits,
            len_ratio,
            wer,
            cer,
        ) in zip(
            noise_transcribe, valid_ground_truth, valid_tts_text, metrics
        ):
            chrf = sentence_chrf(tts_text, raw_asr)
            if (
                word_edits >= required_edits
                and MIN_LEN_RATIO <= len_ratio <= MAX_LEN_RATIO
                and wer <= MAX_WER
                and cer <= MAX_CER
                and chrf > 0.03
            ):
                print(
                    f"[GPU {gpu_id} | ACCEPTED] edits: {word_edits}/{required_edits}   len: {len_ratio:.2f}   WER: {wer:.2%}   CER: {cer:.2%}"
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
                    f"[GPU {gpu_id} | DISCARD] edits: {word_edits}/{required_edits}   len: {len_ratio:.2f}   WER: {wer:.2%}   CER: {cer:.2%}"
                )
                discarded_dataset.append(
                    {
                        "raw_asr": raw_asr,
                        "refined_text": refined_text,
                        "tts_text": tts_text,
                        "word_edits": word_edits,
                        "required_edits": required_edits,
                        "len_ratio": round(len_ratio, 4),
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

    detected_gpus = (
        torch.cuda.device_count() if torch.cuda.is_available() else 1
    )
    num_gpus = (
        min(args.num_gpus, max(1, detected_gpus))
        if args.num_gpus is not None
        else max(1, detected_gpus)
    )

    print("=================================================================")
    print(f"Total dataset size : {total_samples}")
    print(f"Workers / GPUs     : {num_gpus}")
    print("=================================================================")

    # Pre-cache Whisper & Kokoro weights to disk once before spawning workers.
    from huggingface_hub import snapshot_download

    hf_model_id = (
        f"openai/whisper-{args.asr_model}"
        if not args.asr_model.startswith("openai/whisper-")
        and "/" not in args.asr_model
        else args.asr_model
    )
    snapshot_download(repo_id=hf_model_id)
    snapshot_download(repo_id="hexgrad/Kokoro-82M")
    AutoProcessor.from_pretrained(hf_model_id)
    print(
        "[pre-cache] Whisper & Kokoro weights cached to disk. Zero GPU memory allocated in parent."
    )

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
    print(
        f"Discarded     : {len(final_discarded_dataset)} -> {args.discarded_path}"
    )
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
