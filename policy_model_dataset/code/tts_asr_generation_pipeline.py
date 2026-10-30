from kokoro_onnx import Kokoro
from torch_audiomentations import (
    Compose,
    AddColoredNoise,
    ApplyBackgroundNoise,
    BandPassFilter,
)
from torch_audiomentations.core.transforms_interface import BaseWaveformTransform
from torch_audiomentations.utils.object_dict import ObjectDict

from faster_whisper import WhisperModel
import torch
import jiwer
import numpy as np
import json


def load_models(tts_model_name="kokoro-v0_19.onnx", asr_model_name="base"):
    tts_model = Kokoro(tts_model_name, "voices.json")

    compute_type = "float16" if torch.cuda.is_available() else "int8"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    asr_model = WhisperModel(asr_model_name, device=device, compute_type=compute_type)

    return tts_model, asr_model


def load_dataset(path="./datasets/policy_model_dataset/tts_dataset.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [item["refined_text"] for item in data]


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
        selected_samples: torch.Tensor,
        sample_rate: int = None,
    ):
        batch_size, _, total_samples = selected_samples.shape
        device = selected_samples.device

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
        selected_samples: torch.Tensor,
        sample_rate: int = None,
    ) -> ObjectDict:
        out = selected_samples.clone()
        mask_lens = self.transform_parameters["mask_lens"]
        start_indices = self.transform_parameters["start_indices"]

        for idx, (start_idx, mask_len) in enumerate(zip(start_indices, mask_lens)):
            if mask_len > 0:
                out[idx, :, start_idx : start_idx + mask_len] = 0.0

        return ObjectDict(samples=out, sample_rate=sample_rate)


# Instantiate the GPU pipeline once on your device
def get_gpu_augmenter(sample_rate: int = 16000, device: str = "cuda"):
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
            # 2. Add real acoustic background noise from folder (optional)
            # ApplyBackgroundNoise(
            #     background_paths="path/to/noise_wavs",
            #     min_snr_in_db=3.0,
            #     max_snr_in_db=15.0,
            #     p=0.7,
            #     sample_rate=sample_rate,
            # ),
            # 3. Add Gaussian white noise (p_decay=0 is standard white noise)
            AddColoredNoise(
                min_snr_in_db=5.0,
                max_snr_in_db=15.0,
                min_f_decay=0.0,
                max_f_decay=0.0,
                p=0.8,
                sample_rate=sample_rate,
                output_type="tensor",
            ),
            # 4. Microphone/telephony band-pass filter
            BandPassFilter(
                min_center_frequency=1000.0,
                max_center_frequency=2500.0,
                p=0.5,
                sample_rate=sample_rate,
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
        Tensor of shape (B, T) clipped to [-1.0, 1.0].
    """
    if audio_batch.ndim == 1:
        audio_batch = audio_batch.unsqueeze(0).unsqueeze(0)
    elif audio_batch.ndim == 2:
        audio_batch = audio_batch.unsqueeze(1)

    noise_audio = augmenter(audio_batch, sample_rate=sample_rate)
    noise_audio = torch.clamp(noise_audio, min=-1.0, max=1.0)

    return noise_audio


def calculate_metrics(targets, predictions):
    return [
        jiwer.wer(target, prediction)
        for target, prediction in zip(targets, predictions)
    ]


def generation_pipeline(batch_size):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gpu_augmenter = get_gpu_augmenter(sample_rate=16000, device=str(device))

    tts_model, asr_model = load_models()
    dataset = load_dataset("./datasets/policy_model_dataset/tts_dataset.json")
    noise_dataset = []

    for i in range(0, len(dataset), batch_size):
        batch_text = dataset[i : i + batch_size]

        noise_transcribe = []
        for text in batch_text:
            samples, sample_rate = tts_model.create(text, voice="af_sarah", speed=1.0)
            audio_tensor = torch.from_numpy(np.array(samples)).float().to(device)
            with torch.no_grad():
                noise_voice = noise_addition_gpu(
                    audio_tensor, augmenter=gpu_augmenter, sample_rate=16000
                )
            segments, _ = asr_model.transcribe(noise_voice.squeeze().cpu().numpy(), beam_size=1)
            noise_raw_text = " ".join([seg.text.strip() for seg in segments])

            noise_transcribe.append(noise_raw_text)

        metrics = calculate_metrics(batch_text, noise_transcribe)

        for raw_asr, refined_text, score in zip(noise_transcribe, batch_text, metrics):
            if 0.3 < score < 0.7:
                noise_dataset.append(
                    {
                        "raw_asr": raw_asr,
                        "refined_text": refined_text,
                    }
                )
    with open("sft_train.json", "w") as f:
        json.dump(noise_dataset, f, indent=2)

    return noise_dataset
