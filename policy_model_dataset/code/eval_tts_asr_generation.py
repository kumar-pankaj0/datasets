import soundfile as sf
import torchaudio

# torchaudio >= 2.9 removed torchaudio.info and AudioMetaData
# patch them back via soundfile BEFORE torch_audiomentations is imported
if not hasattr(torchaudio, "AudioMetaData"):
    class AudioMetaData:
        def __init__(self, sample_rate, num_frames, num_channels,
                     bits_per_sample=0, encoding="PCM_S"):
            self.sample_rate     = sample_rate
            self.num_frames      = num_frames
            self.num_channels    = num_channels
            self.bits_per_sample = bits_per_sample
            self.encoding        = encoding
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
    tts_model_name="kokoro-v1.0.onnx", asr_model_name="tiny.en"
)


def save_wav(filepath, audio_np, sample_rate=16000):
    audio_int16 = (audio_np * 32767).clip(-32768, 32767).astype(np.int16)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


NOISE_PATH = "/kaggle/working/musan_noise/noise/free-sound/noise-free-sound-0001.wav"
background_noise_add = AddBackgroundNoise(
    background_paths=NOISE_PATH,
    min_snr_in_db=8.0,
    max_snr_in_db=15.0,
    p=1.0,
    output_type="tensor",
)

# --- TEST & LISTEN ---
test_sentence = (
    "The synchronization protocol encountered an intermittent buffer overflow during packet transmission, "
    "causing approximately fourteen percent of the telemetric telemetry logs to drop before the secondary "
    "failover server could successfully re-establish a secure connection across subnet forty-two."
)
print(f"=== GROUND TRUTH ===\n{test_sentence}\n")

samples, original_sample_rate = tts_model.create(
    test_sentence, voice="af_sarah", speed=1.20
)
target_sample_rate = 16000
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

audio_tensor = torch.from_numpy(np.array(samples)).float().to(device)
with torch.no_grad():
    if original_sample_rate != target_sample_rate:
        audio_tensor = F_audio.resample(
            audio_tensor, orig_freq=original_sample_rate, new_freq=target_sample_rate
        )
    # AddBackgroundNoise expects shape (batch, channels, samples)
    audio_3d = audio_tensor.unsqueeze(0).unsqueeze(0)  # (1, 1, T)
    noisy_3d = background_noise_add(
        audio_3d, sample_rate=target_sample_rate
    )  # (1, 1, T)
    realistic_noisy_tensor = noisy_3d.squeeze(0).squeeze(0)  # (T,)

clean_np = audio_tensor.cpu().numpy()
noisy_np = realistic_noisy_tensor.cpu().numpy()

save_wav("realistic_noise_added.wav", noisy_np, target_sample_rate)

segments, _ = asr_model.transcribe(
    noisy_np,
    beam_size=1,
    condition_on_previous_text=False,
    temperature=0.2,
)
whisper_out = " ".join([seg.text.strip() for seg in segments]).strip()
print(f"=== WHISPER TRANSCRIBED ===\n{whisper_out}\n")
print(f"WER: {jiwer.wer(test_sentence, whisper_out):.2%}\n")

print("▶️ Listen to Baseline + Realistic Noise added")
ipd.display(ipd.Audio(noisy_np, rate=target_sample_rate))
