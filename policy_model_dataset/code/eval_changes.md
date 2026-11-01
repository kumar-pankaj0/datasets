# Changes to `eval_tts_asr_generation.py`

Use `torch_audiomentations.AddBackgroundNoise` — it accepts a file/folder path directly and handles loading, resampling, and SNR mixing internally.

## What is `AddBackgroundNoise`?

- Lives in `torch_audiomentations` (install: `pip install torch-audiomentations`)
- Parameter `sounds_path` = path to a single .wav file OR a folder of noise files
- Parameters `min_snr_db` / `max_snr_db` control noise level (higher = cleaner signal)
- Input tensor shape must be `(batch, channels, samples)` — returns same shape

---

## Diff

### 1. Import block (top of file)

```diff
-import torchaudio.functional as F_audio
+import torchaudio.functional as F_audio
+from torch_audiomentations import AddBackgroundNoise
```

### 2. Replace the entire `realistic_bad_mic_gpu` function

```diff
-def realistic_bad_mic_gpu(audio_1d: torch.Tensor, sr: int = 16000) -> torch.Tensor:
-    """
-    Locks in Clip 5 as the exact baseline floor, then injects 2 to 4 sharp
-    "zoo-zoo" disturbance spikes directly onto spoken words to force 25%-40% WER.
-    """
-    device = audio_1d.device
-    x = audio_1d.clone()
-    T = x.shape[-1]
-    # ... (all 140+ lines of synthetic noise code)
-    return x_noisy
+NOISE_PATH = "/kaggle/working/musan_noise/noise/free-sound/noise-free-sound-0001.wav"
+
+add_bg_noise = AddBackgroundNoise(
+    sounds_path=NOISE_PATH,   # single file — or pass folder to pick randomly
+    min_snr_db=8.0,
+    max_snr_db=15.0,
+    p=1.0,
+)
```

### 3. Replace the function call in the test block

```diff
-with torch.no_grad():
-    if orig_sr != target_sr:
-        audio_tensor = F_audio.resample(
-            audio_tensor, orig_freq=orig_sr, new_freq=target_sr
-        )
-    realistic_noisy_tensor = realistic_bad_mic_gpu(audio_tensor, sr=target_sr)
+with torch.no_grad():
+    if orig_sr != target_sr:
+        audio_tensor = F_audio.resample(
+            audio_tensor, orig_freq=orig_sr, new_freq=target_sr
+        )
+    # AddBackgroundNoise needs shape (batch, channels, samples)
+    audio_3d = audio_tensor.unsqueeze(0).unsqueeze(0)          # (1, 1, T)
+    noisy_3d = add_bg_noise(audio_3d, sample_rate=target_sr)   # (1, 1, T)
+    realistic_noisy_tensor = noisy_3d.squeeze(0).squeeze(0)    # back to (T,)
```

### 4. Save filename + print label

```diff
-save_wav("realistic_distant_mic.wav", noisy_np, target_sr)
+save_wav("musan_real_noise_mix.wav", noisy_np, target_sr)
```

```diff
-print("▶️ Listen to Baseline + Zoo-Zoo Spikes Audio:")
+print("▶️ Listen to Real MUSAN Noise Mix:")
```

---

## SNR Guide

| min_snr_db / max_snr_db | Effect               |
|-------------------------|----------------------|
| 3 / 8                   | Heavy noise ~35-45% WER |
| 8 / 15                  | Moderate noise ~20-30% WER |
| 15 / 25                 | Light noise ~5-15% WER |

## Tip — use all 29 noise files randomly

```python
sounds_path="/kaggle/working/musan_noise/noise/free-sound/"
```
Pass the folder instead of one file — `AddBackgroundNoise` picks randomly each call.
