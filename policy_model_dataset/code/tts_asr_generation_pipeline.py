"""
=============================================================================
DATASET GENERATION PIPELINE — ASR Post-Refinement Training Data
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

    # Run with default parameters (batch_size=16)
    python code/tts_asr_generation_pipeline.py

    # Custom batch size and output location
    python code/tts_asr_generation_pipeline.py
    --batch_size 32 --output_path ./custom_sft.json

    # Custom Whisper model and noise directory
    python code/tts_asr_generation_pipeline.py
    --asr_model base.en --noise_dir
    ./musan_noise/noise/free-sound/

=============================================================================
"""

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
from kokoro_onnx import Kokoro
from torch_audiomentations import (
    Compose,
    AddColoredNoise,
    AddBackgroundNoise,
    BandPassFilter,
)
from torch_audiomentations.core.transforms_interface import BaseWaveformTransform
from torch_audiomentations.utils.object_dict import ObjectDict

from faster_whisper import WhisperModel
import torch
import jiwer
import numpy as np
import json
import argparse


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


def load_models(tts_model_name="kokoro-v1.0.onnx", asr_model_name="tiny.en"):
    tts_model = Kokoro(tts_model_name, "voices-v1.0.bin")

    compute_type = "float16" if torch.cuda.is_available() else "int8"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    asr_model = WhisperModel(asr_model_name, device=device, compute_type=compute_type)

    return tts_model, asr_model


def load_dataset(path="./datasets/policy_model_dataset/tts_dataset.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [item for item in data["refined_text"]]


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


def generation_pipeline(
    batch_size: int = 16,
    dataset_path: str = "./datasets/policy_model_dataset/tts_input_dataset.json",
    output_path: str = "sft_train.json",
    noise_dir: str = "/kaggle/working/musan_noise/noise/free-sound/",
    asr_model_name: str = "tiny.en",
    tts_model_name: str = "kokoro-v1.0.onnx",
    debug_samples: int = 3,
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gpu_augmenter = get_gpu_augmenter(
        sample_rate=TARGET_SAMPLE_RATE, noise_dir=noise_dir, device=str(device)
    )

    tts_model, asr_model = load_models(
        tts_model_name=tts_model_name, asr_model_name=asr_model_name
    )
    dataset = load_dataset(dataset_path)
    noise_dataset = []

    for i in range(0, len(dataset), batch_size):
        raw_batch = dataset[i : i + batch_size]
        batch_text = [text for text in raw_batch if len(text.split()) >= MIN_WORDS]
        if not batch_text:
            continue

        noise_transcribe = []
        for text in batch_text:
            # Randomize speech rate to compress phonemes and trigger dropped syllables
            rand_speed = float(np.random.uniform(1.25, 1.35))
            voice = np.random.choice(["af_sarah", "af_bella", "am_adam", "bf_emma"])
            samples, sample_rate = tts_model.create(text, voice=voice, speed=rand_speed)
            audio_tensor = torch.from_numpy(np.array(samples)).float().to(device)
            if sample_rate != TARGET_SAMPLE_RATE:
                audio_tensor = F_audio.resample(
                    audio_tensor, orig_freq=sample_rate, new_freq=TARGET_SAMPLE_RATE
                )
            with torch.no_grad():
                noise_voice = noise_addition_gpu(
                    audio_tensor,
                    augmenter=gpu_augmenter,
                    sample_rate=TARGET_SAMPLE_RATE,
                )
            # Disable Whisper's auto-correction context and greedy language modeling
            segments, _ = asr_model.transcribe(
                noise_voice.squeeze().cpu().numpy(),
                beam_size=BEAM_SIZE,
                condition_on_previous_text=CONDITION_ON_PREVIOUS_TEXT,
                temperature=TEMPERATURE,
            )
            noise_raw_text = " ".join([seg.text.strip() for seg in segments])
            noise_transcribe.append(noise_raw_text)

        metrics = calculate_metrics(batch_text, noise_transcribe)

        debug_count = 0
        for raw_asr, refined_text, (wer, cer) in zip(
            noise_transcribe, batch_text, metrics
        ):
            if MIN_CER <= cer <= MAX_CER and MIN_WER <= wer <= MAX_WER:
                if debug_count < debug_samples:
                    print(f"\n\nrefined text : {refined_text}\n")
                    print(f"raw_asr : {raw_asr}\n")
                    print(f"WER: {wer:.2%}   CER: {cer:.2%}\n")
                    debug_count += 1
                noise_dataset.append(
                    {
                        "raw_asr": raw_asr,
                        "refined_text": refined_text,
                    }
                )

    with open(output_path, "w") as f:
        json.dump(noise_dataset, f, indent=2)

    return noise_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TTS-ASR Noise Generation Pipeline")
    parser.add_argument(
        "--batch_size", type=int, default=16, help="Batch size for processing"
    )
    parser.add_argument(
        "--dataset_path",
        type=str,
        default="./datasets/policy_model_dataset/tts_input_dataset.json",
        help="Path to input text dataset JSON",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="sft_train.json",
        help="Output JSON file destination",
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
        "--tts_model", type=str, default="kokoro-v1.0.onnx", help="Kokoro ONNX model"
    )
    parser.add_argument(
        "--debug_samples",
        type=int,
        default=3,
        help="Number of preview outputs to print",
    )
    args = parser.parse_args()

    generation_pipeline(
        batch_size=args.batch_size,
        dataset_path=args.dataset_path,
        output_path=args.output_path,
        noise_dir=args.noise_dir,
        asr_model_name=args.asr_model,
        tts_model_name=args.tts_model,
        debug_samples=args.debug_samples,
    )
