import soundfile as sf
import torchaudio


# ── SNR (real background noise mixing) ──
MIN_SNR_DB = 8
MAX_SNR_DB = 13

# ── WER filter (keep only learnable pairs) ──
MIN_WER = 0.08
MAX_WER = 0.40

# ── Sentence length filter ──
MIN_WORDS = 6

# ── Whisper inference ──
BEAM_SIZE = 1
TEMPERATURE = 0
CONDITION_ON_PREVIOUS_TEXT = False

skip_count = 0
# ── TTS ──
TTS_VOICE = "af_sarah"
TTS_SPEED = 1.30
TARGET_SAMPLE_RATE = 16000

# ── Synthetic layers (add_synthetic_layers) ──
REVERB_RT60 = 0.265
REVERB_RIR_FIRST_SAMPLE = 0.43
LOWPASS_CUTOFF_HZ = 2200.0
HISS_SNR_DB = 70.0
OUTPUT_PEAK = 0.9


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
    rt60 = 0.265
    rir_len = int(rt60 * sr)
    t = torch.linspace(0, rt60, rir_len, device=x.device)
    rir = torch.randn(rir_len, device=x.device) * torch.exp(-6.2 * t / rt60)
    rir[0] = 0.43
    rir = rir / torch.norm(rir)
    n_fft = 2 ** int(np.ceil(np.log2(T + rir_len - 1)))
    x = torch.fft.irfft(
        torch.fft.rfft(x, n=n_fft) * torch.fft.rfft(rir, n=n_fft), n=n_fft
    )[:T]

    # 2. Mic muffle — low-pass at 2200 Hz
    x = F_audio.lowpass_biquad(x, sample_rate=sr, cutoff_freq=2200.0)

    # 3. Gentle preamp hiss (SNR ~70 dB — barely audible)
    hiss = torch.randn_like(x)
    sig_power = x.pow(2).mean().clamp(min=1e-8)
    hiss_power = hiss.pow(2).mean().clamp(min=1e-8)
    scale = torch.sqrt(sig_power / (hiss_power * (10 ** (70.0 / 10.0))))
    x = x + hiss * scale

    return x / x.abs().max().clamp(min=1e-6) * 0.9


# --- TEST & LISTEN ---
test_sentences = [
    # Short (6-10 words)
    "Connection established on port 8443.",
    "System load average is 0.87 across 4 cores.",
    "Authentication token expires in 30 minutes.",
    "Packet loss detected on subnet 192.168.42.0.",
    "CPU temperature exceeded 91 degrees Celsius.",
    "Retry limit of 3 attempts reached.",
    # Medium (11-20 words)
    "Please verify the telemetry data before initiating the shutdown sequence on node 7.",
    "The backup server failed to respond within the 30-second timeout window.",
    "Memory usage reached 94% across all 8 worker threads during peak load.",
    "The firewall blocked 1,247 unauthorized requests from subnet 10.0.0.0 today.",
    "Authentication tokens for 3 admin accounts were rotated after the security audit.",
    "Disk I/O throughput dropped to 42 MB/s on RAID volume 2 during replication.",
    # Medium-Long (20-30 words)
    "The automated diagnostics protocol completed successfully across all 4 nodes, but secondary backup logs from the last 48 hours remain unverified.",
    "Subroutine execution encountered a minor latency spike of 12ms during the initial handshake. Operators should monitor throughput on port 443 closely.",
    "The primary encryption key expired unexpectedly at 00:00. Maintenance teams deployed an emergency patch within 7 minutes to restore secure client authentication.",
    "Network latency between subnet 42 and the primary data center increased by 63% during the 2-hour peak traffic window ending at 14:30.",
    "Version 3.14.1 of the firmware introduced patches for 22 critical vulnerabilities, reducing the total attack surface by approximately 81%.",
    # Long (30-45 words)
    "Although initial memory allocation benchmarks suggested optimal performance under peak loads of 50,000 requests per second, unhandled pointer exceptions eventually triggered a cascading kernel panic across the entire 96-node distributed cluster.",
    "The synchronization protocol encountered an intermittent buffer overflow during packet transmission, causing approximately 14% of the telemetry logs to drop before the secondary failover server on port 5432 could successfully re-establish a secure connection across subnet 42.",
    "Calibration of the spectrometer sensor array requires a stable ambient temperature of 22 degrees Celsius. Any deviation beyond 0.5 degrees introduces systematic calibration drift into the spectral irradiance measurements across all 16 channels.",
    "The system processed 47,312 requests per second, with an average latency of 2.3 milliseconds and a 99th percentile latency of 8.7 milliseconds across all 96 nodes in the cluster.",
    "Diagnostic sweep detected anomalous thermal dissipation rates within core sector 7, prompting an automatic fallback to 3 auxiliary cooling pumps and reducing clock speed by 15%.",
    # Very Long (45+ words)
    "Comprehensive environmental testing confirmed that prolonged exposure to high-frequency electromagnetic interference above 2.4 GHz degrades internal signal integrity by up to 37%. Consequently, engineers reinforced all exterior cabling shielding and upgraded the grounding terminals across 12 server racks to mitigate potential packet corruption risks.",
    "The distributed consensus algorithm requires that at least 2/3 of all 48 active nodes acknowledge receipt of the configuration update before the transaction is considered committed and propagated to the remaining 16 cluster members within a 500ms window.",
    "During the 72-hour stress test, the system maintained 99.97% uptime while processing a sustained load of 120,000 concurrent connections, with memory consumption peaking at 187 GB across the 24-node cluster at hour 61.",
    "The load balancer distributed 8,400,000 requests across 12 backend servers during the 4-hour maintenance window, achieving an average response time of 1.8 milliseconds and a maximum throughput of 580 MB/s on the primary 10-gigabit uplink.",
    # Number-heavy (hardest for Whisper)
    "The 3 primary nodes processed 2,847 transactions in 0.4 seconds, while the 9 secondary nodes handled 14,203 read requests with 99.9% cache hit rate.",
    "Firmware version 2.7.3 resolved 14 of the 19 known vulnerabilities identified in the CVE-2024-3821 advisory, with the remaining 5 patches scheduled for release in Q1 2025.",
    "At 03:47 UTC, the monitoring system detected a 340% spike in inbound traffic on port 80, triggering automatic scaling from 4 to 16 instances within 90 seconds.",
]
import jiwer
from jiwer import transforms as tr


def normalize(text):
    return (
        text.lower()
        .replace("-", " ")  # "re-establish" → "re establish"
        .replace(",", "")  # "47,312" → "47312"
        .replace(".", "")
        .replace("%", " percent")  # optional: "14%" → "14 percent"
    )


def evaluate(ground_truth, whisper_out):
    gt_n = normalize(ground_truth)
    hyp_n = normalize(whisper_out)

    wer = jiwer.wer(gt_n, hyp_n)
    cer = jiwer.cer(gt_n, hyp_n)

    return wer, cer


for i, test_sentence in enumerate(test_sentences):
    if len(str(i)) == 1:
        idx = f"000{i}"
    elif len(str(i)) == 2:
        idx = f"00{i}"
    elif len(str(i)) == 3:
        idx = f"0{i}"
    else:
        idx = i

    background_noise_add = AddBackgroundNoise(
        background_paths=f"/kaggle/working/musan_noise/noise/free-sound/noise-free-sound-{idx}.wav",
        min_snr_in_db=10,
        max_snr_in_db=10,
        p=1.0,
        output_type="tensor",
    )

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

    # Usage
    wer, cer = evaluate(test_sentence, whisper_out)

    # Secondary: WER just catches total hallucinations (loose upper bound)
    if 0.03 <= cer <= 0.25 and 0.08 <= wer <= 0.55:
        print(f"=== GROUND TRUTH ===\n{test_sentence}\n")
        print(f"=== WHISPER TRANSCRIBED ===\n{whisper_out}\n")
        print(f"WER: {wer:.2%}   CER: {cer:.2%}")

        print("▶️ Listen to Real Noise + Synthetic Layers")
        ipd.display(ipd.Audio(noisy_np, rate=target_sample_rate))
    else:
        skip_count += 1

print("skip count  :", skip_count)


"""
================= FINAL HYPER-PARAMETERS =============
# ── SNR (real background noise mixing) ──
MIN_SNR_DB = 8
MAX_SNR_DB = 13

# ── WER filter (keep only learnable pairs) ──
MIN_WER = 0.08
MAX_WER = 0.40

# ── Sentence length filter ──
MIN_WORDS = 6

# ── Whisper inference ──
BEAM_SIZE = 1
TEMPERATURE = 0
CONDITION_ON_PREVIOUS_TEXT = False

# ── TTS ──
TTS_VOICE = "af_sarah"
TTS_SPEED = 1.30
TARGET_SAMPLE_RATE = 16000

# ── Synthetic layers (add_synthetic_layers) ──
REVERB_RT60 = 0.265
REVERB_RIR_FIRST_SAMPLE = 0.43
LOWPASS_CUTOFF_HZ = 2200.0
HISS_SNR_DB = 70.0
OUTPUT_PEAK = 0.9

"""
