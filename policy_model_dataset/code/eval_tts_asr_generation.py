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

import wave
import IPython.display as ipd
import numpy as np
import torch
import torchaudio.functional as F_audio
from torch_audiomentations import AddBackgroundNoise
from faster_whisper import WhisperModel
import jiwer
from kokoro_onnx import Kokoro

# Assuming load_models is already defined in your notebook session


def load_models(tts_model_name="kokoro-v1.0.onnx", asr_model_name="tiny.en"):
    tts_model = Kokoro(tts_model_name, "voices-v1.0.bin")

    compute_type = "float16" if torch.cuda.is_available() else "int8"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    asr_model = WhisperModel(asr_model_name, device=device, compute_type=compute_type)

    return tts_model, asr_model


tts_model, asr_model = load_models(
    tts_model_name="kokoro-v1.0.onnx", asr_model_name="base"
)


def save_wav(filepath, audio_np, sample_rate=16000):
    audio_int16 = (audio_np * 32767).clip(-32768, 32767).astype(np.int16)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def add_synthetic_layers(x: torch.Tensor, sr: int = 16000) -> torch.Tensor:
    """Stack light synthetic degradation ON TOP of real noise.
    Adds: small room reverb + mic muffle (low-pass) + gentle preamp hiss.
    """
    T = x.shape[-1]

    # 1. Small room reverb
    rt60 = 0.18
    rir_len = int(rt60 * sr)
    t = torch.linspace(0, rt60, rir_len, device=x.device)
    rir = torch.randn(rir_len, device=x.device) * torch.exp(-6.2 * t / rt60)
    rir[0] = 0.33
    rir = rir / torch.norm(rir)
    n_fft = 2 ** int(np.ceil(np.log2(T + rir_len - 1)))
    x = torch.fft.irfft(
        torch.fft.rfft(x, n=n_fft) * torch.fft.rfft(rir, n=n_fft), n=n_fft
    )[:T]

    # 2. Mic muffle — low-pass at 2200 Hz
    x = F_audio.lowpass_biquad(x, sample_rate=sr, cutoff_freq=2200.0)

    # 3. Gentle preamp hiss (SNR ~70 dB — barely audible)
    hiss = torch.randn_like(x)
    sig_power   = x.pow(2).mean().clamp(min=1e-8)
    hiss_power  = hiss.pow(2).mean().clamp(min=1e-8)
    scale = torch.sqrt(sig_power / (hiss_power * (10 ** (70.0 / 10.0))))
    x = x + hiss * scale

    return x / x.abs().max().clamp(min=1e-6) * 0.9


# --- TEST & LISTEN ---
test_sentances = [
    # Short (1 sentence)
    "System nominal.",
    # Short (1 sentence)
    "Please verify the telemetry data before initiating the shutdown sequence.",
    # Medium (1 sentence)
    "The automated diagnostics protocol completed successfully across all four nodes, but secondary backup logs remain unverified.",
    # Medium (2 sentences)
    "Subroutine execution encountered a minor latency spike during the initial handshake. Operators should monitor throughput closely.",
    # Medium-Long (1 sentence)
    "Diagnostic sweep detected anomalous thermal dissipation rates within core sector seven, prompting an automatic fallback to auxiliary cooling pumps.",
    # Medium-Long (2 sentences)
    "The primary encryption key expired unexpectedly at midnight. Maintenance teams deployed an emergency patch to restore secure client authentication channels.",
    # Long (1 sentence)
    "Although initial memory allocation benchmarks suggested optimal performance under peak loads, unhandled pointer exceptions eventually triggered a cascading kernel panic across the entire distributed cluster.",
    # Long (2 sentences)
    "Calibration of the spectrometer sensor array requires a stable ambient temperature of twenty-two degrees Celsius. Any deviation beyond this threshold introduces systematic calibration drift into the spectral irradiance measurements.",
    # Very Long (1 sentence)
    "The synchronization protocol encountered an intermittent buffer overflow during packet transmission, causing approximately fourteen percent of the telemetric telemetry logs to drop before the secondary failover server could successfully re-establish a secure connection across subnet forty-two.",
    # Very Long (2 sentences)
    "Comprehensive environmental testing confirmed that prolonged exposure to high-frequency electromagnetic interference degrades internal signal integrity. Consequently, engineers reinforced all exterior cabling shielding and upgraded the grounding terminals to mitigate potential packet corruption risks during severe electrical storms.",
]
for idx, test_sentence in enumerate(test_sentances):
    background_noise_add = AddBackgroundNoise(
        background_paths=f"/kaggle/working/musan_noise/noise/free-sound/noise-free-sound-000{idx}.wav",
        min_snr_in_db=0.7,
        max_snr_in_db=1,
        p=1.0,
        output_type="tensor",
    )
    print(f"=== GROUND TRUTH ===\n{test_sentence}\n")

    samples, original_sample_rate = tts_model.create(
        test_sentence, voice="af_sarah", speed=1.30
    )
    target_sample_rate = 16000
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    audio_tensor = torch.from_numpy(np.array(samples)).float().to(device)
    with torch.no_grad():
        if original_sample_rate != target_sample_rate:
            audio_tensor = F_audio.resample(
                audio_tensor,
                orig_freq=original_sample_rate,
                new_freq=target_sample_rate,
            )
        # AddBackgroundNoise expects shape (batch, channels, samples)
        audio_3d = audio_tensor.unsqueeze(0).unsqueeze(0)  # (1, 1, T)
        noisy_3d = background_noise_add(
            audio_3d, sample_rate=target_sample_rate
        )  # (1, 1, T)
        realistic_noisy_tensor = noisy_3d.squeeze(0).squeeze(0)  # (T,)

        # Stack synthetic layers on top of real noise
        realistic_noisy_tensor = add_synthetic_layers(
            realistic_noisy_tensor, sr=target_sample_rate
        )

    clean_np = audio_tensor.cpu().numpy()
    noisy_np = realistic_noisy_tensor.cpu().numpy()

    save_wav("realistic_noise_added.wav", noisy_np, target_sample_rate)

    segments, _ = asr_model.transcribe(
        noisy_np,
        beam_size=1,
        condition_on_previous_text=False,
        temperature=0,
    )
    whisper_out = " ".join([seg.text.strip() for seg in segments]).strip()
    print(f"=== WHISPER TRANSCRIBED ===\n{whisper_out}\n")
    print(f"WER: {jiwer.wer(test_sentence, whisper_out):.2%}\n")

    print("▶️ Listen to Real Noise + Synthetic Layers")
    ipd.display(ipd.Audio(noisy_np, rate=target_sample_rate))
