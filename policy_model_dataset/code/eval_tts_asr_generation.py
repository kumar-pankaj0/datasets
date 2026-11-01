import wave
import IPython.display as ipd
import numpy as np
import torch
import torch.nn.functional as F
import torchaudio.functional as F_audio
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
    tts_model_name="kokoro-v1.0.onnx", asr_model_name="tiny.en"
)


def save_wav(filepath, audio_np, sample_rate=16000):
    audio_int16 = (audio_np * 32767).clip(-32768, 32767).astype(np.int16)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def realistic_bad_mic_gpu(audio_1d: torch.Tensor, sr: int = 16000) -> torch.Tensor:
    """
    Locks in Clip 5 as the exact baseline floor, then injects 2 to 4 sharp
    "zoo-zoo" disturbance spikes directly onto spoken words to force 25%-40% WER.
    """
    device = audio_1d.device
    x = audio_1d.clone()
    T = x.shape[-1]

    # =========================================================================
    # PART A: THE PERFECT BASELINE (Locked from Clip 5)
    # =========================================================================
    # 1. Baseline consonant clipping
    peak = x.abs().max().clamp(min=1e-6)
    x = x / peak
    clip_thresh = float(torch.empty(1).uniform_(0.38, 0.52).item())
    x_clipped = torch.clamp(x, min=-clip_thresh, max=clip_thresh) / clip_thresh

    # 2. Baseline room reverb (rir[0] = 0.33)
    rt60_sec = float(torch.empty(1).uniform_(0.14, 0.22).item())
    rir_len = int(rt60_sec * sr)
    t_rir = torch.linspace(0, rt60_sec, rir_len, device=device)

    decay_env = torch.exp(-6.2 * t_rir / rt60_sec)
    rir = torch.randn(rir_len, device=device) * decay_env
    rir[0] = 0.33
    rir = rir / torch.norm(rir)

    n_fft = 2 ** int(np.ceil(np.log2(T + rir_len - 1)))
    X_fft = torch.fft.rfft(x_clipped, n=n_fft)
    R_fft = torch.fft.rfft(rir, n=n_fft)
    x_reverb = torch.fft.irfft(X_fft * R_fft, n=n_fft)[:T]

    # 3. Baseline muffle filter (2050Hz - 2500Hz)
    lowpass_hz = float(torch.empty(1).uniform_(2050.0, 2500.0).item())
    highpass_hz = float(torch.empty(1).uniform_(250.0, 330.0).item())
    x_muffled = F_audio.lowpass_biquad(x_reverb, sample_rate=sr, cutoff_freq=lowpass_hz)
    x_muffled = F_audio.highpass_biquad(
        x_muffled, sample_rate=sr, cutoff_freq=highpass_hz
    )

    # 4. Baseline gentle syllable wobble
    num_knots = max(6, int(T / sr * 4.0))
    gain_knots = torch.empty(1, 1, num_knots, device=device).uniform_(0.55, 1.05)
    gain_curve = F.interpolate(
        gain_knots, size=T, mode="linear", align_corners=False
    ).squeeze()
    x_pumped = x_muffled * gain_curve

    # 5. Baseline structured noise floor (8.0 dB to 11.0 dB)
    raw_noise_1 = torch.randn(T, device=device)
    raw_noise_2 = torch.randn(T, device=device)

    rumble_noise = F_audio.lowpass_biquad(
        raw_noise_1, sample_rate=sr, cutoff_freq=320.0
    )
    rumble_noise = F_audio.highpass_biquad(
        rumble_noise, sample_rate=sr, cutoff_freq=85.0
    )
    formant_noise = F_audio.bandpass_biquad(
        raw_noise_2, sample_rate=sr, central_freq=750.0, Q=0.5
    )

    noise_knots = torch.empty(1, 1, max(5, int(T / sr * 3.0)), device=device).uniform_(
        0.5, 1.15
    )
    noise_env = F.interpolate(
        noise_knots, size=T, mode="linear", align_corners=False
    ).squeeze()

    voice_env = F_audio.lowpass_biquad(x_pumped.abs(), sample_rate=sr, cutoff_freq=25.0)
    voice_env_norm = voice_env / voice_env.max().clamp(min=1e-6)
    baseline_breakup = formant_noise * voice_env_norm * 0.06

    structured_noise = (
        (rumble_noise * 0.70) + (formant_noise * noise_env * 0.25) + baseline_breakup
    )

    snr_rumble_db = float(torch.empty(1).uniform_(8.0, 11.0).item())
    sig_power = x_pumped.pow(2).mean().clamp(min=1e-8)
    rumble_power = structured_noise.pow(2).mean().clamp(min=1e-8)
    rumble_scale = torch.sqrt(
        sig_power / (rumble_power * (10 ** (snr_rumble_db / 10.0)))
    )

    # =========================================================================
    # PART B: TARGETED "ZOO-ZOO" DISTURBANCE SPIKES ON ACTIVE WORDS
    # =========================================================================
    # Create a resonant "zoo-zoo" buzz texture (850Hz narrow band + fast 25Hz flutter)
    raw_buzz = torch.randn(T, device=device)
    zoo_buzz = F_audio.bandpass_biquad(
        raw_buzz, sample_rate=sr, central_freq=880.0, Q=1.4
    )
    t_sec = torch.linspace(0, T / sr, T, device=device)
    flutter = 0.9 * (
        1.0 + torch.sin(4 * np.pi * 34.0 * t_sec)
    )  # 28Hz "zoo-zoo" vibration
    zoo_buzz = zoo_buzz * flutter

    # Pick 3 to 5 spike locations specifically where the speaker is talking (voice_env_norm > 0.25)
    active_indices = torch.nonzero(voice_env_norm > 0.25).squeeze(-1)
    spike_mask = torch.zeros(T, device=device)
    voice_duck_mask = torch.ones(T, device=device)

    num_spikes = np.random.randint(7, 11)
    for _ in range(num_spikes):
        spike_len = np.random.randint(
            int(0.14 * sr), int(0.28 * sr)
        )  # 140ms to 280ms burst
        if len(active_indices) > spike_len:
            center_idx = int(
                active_indices[np.random.randint(0, len(active_indices))].item()
            )
            start_pos = max(0, min(T - spike_len, center_idx - spike_len // 2))
        else:
            start_pos = np.random.randint(0, max(1, T - spike_len))

        # Smooth bell-shaped spike window (hann window) so it surges like real mic breakup
        window = torch.hann_window(spike_len, device=device)
        spike_strength = float(torch.empty(1).uniform_(2.4, 3.4).item())
        spike_mask[start_pos : start_pos + spike_len] += window * spike_strength

        # Simultaneously duck/muffle the clean voice by 65% right under the spike
        voice_duck_mask[start_pos : start_pos + spike_len] *= 1.0 - 0.65 * window

    # Apply the ducking to the voice during spikes and scale the zoo-zoo burst
    x_spiked_voice = x_pumped * voice_duck_mask
    zoo_spike_signal = zoo_buzz * spike_mask * torch.sqrt(sig_power) * 1.8

    # Subtle background preamp hiss
    white_hiss = torch.randn(T, device=device)
    snr_hiss_db = float(torch.empty(1).uniform_(60.0, 84.0).item())
    hiss_power = white_hiss.pow(6).mean().clamp(min=1e-8)
    hiss_scale = torch.sqrt(sig_power / (hiss_power * (10 ** (snr_hiss_db / 10.0))))

    # Final Mix: Baseline + Zoo-Zoo Spikes + Hiss
    x_noisy = (
        x_spiked_voice
        + (structured_noise * rumble_scale)
        + zoo_spike_signal
        + (white_hiss * hiss_scale)
    )

    # Normalize to realistic peak
    x_noisy = x_noisy / x_noisy.abs().max().clamp(min=1e-6) * 0.9
    return x_noisy


# --- TEST & LISTEN ---
test_sentence = (
    "The synchronization protocol encountered an intermittent buffer overflow during packet transmission, "
    "causing approximately fourteen percent of the telemetric telemetry logs to drop before the secondary "
    "failover server could successfully re-establish a secure connection across subnet forty-two."
)
print(f"=== GROUND TRUTH ===\n{test_sentence}\n")

samples, orig_sr = tts_model.create(test_sentence, voice="af_sarah", speed=1.20)
target_sr = 16000
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

audio_tensor = torch.from_numpy(np.array(samples)).float().to(device)
with torch.no_grad():
    if orig_sr != target_sr:
        audio_tensor = F_audio.resample(
            audio_tensor, orig_freq=orig_sr, new_freq=target_sr
        )
    realistic_noisy_tensor = realistic_bad_mic_gpu(audio_tensor, sr=target_sr)

clean_np = audio_tensor.cpu().numpy()
noisy_np = realistic_noisy_tensor.cpu().numpy()

save_wav("realistic_distant_mic.wav", noisy_np, target_sr)

segments, _ = asr_model.transcribe(
    noisy_np,
    beam_size=1,
    condition_on_previous_text=False,
    temperature=0.2,
)
whisper_out = " ".join([seg.text.strip() for seg in segments]).strip()
print(f"=== WHISPER TRANSCRIBED ===\n{whisper_out}\n")
print(f"WER: {jiwer.wer(test_sentence, whisper_out):.2%}\n")

print("▶️ Listen to Baseline + Zoo-Zoo Spikes Audio:")
ipd.display(ipd.Audio(noisy_np, rate=target_sr))
