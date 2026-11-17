
import os
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import stft

normal_file = "data/normal/normal_01.wav"
test_file = "data/test/test_01.wav"
output_file = "data/test/spectrogram.png"

print("=" * 55)
print("       AETHERHOUND - SPECTROGRAM ANALYSIS")
print("=" * 55)

if not os.path.exists(normal_file):
    raise FileNotFoundError(f"Missing file: {normal_file}")

if not os.path.exists(test_file):
    raise FileNotFoundError(f"Missing file: {test_file}")

normal_audio, normal_rate = sf.read(normal_file)
test_audio, test_rate = sf.read(test_file)

if normal_audio.ndim > 1:
    normal_audio = np.mean(normal_audio, axis=1)

if test_audio.ndim > 1:
    test_audio = np.mean(test_audio, axis=1)

print("\n[1] Audio files loaded successfully")
print(f"Normal sample rate: {normal_rate} Hz")
print(f"Test sample rate: {test_rate} Hz")

if normal_rate != test_rate:
    raise ValueError("Audio sample rates do not match!")


frequencies_normal, times_normal, Z_normal = stft(
    normal_audio, fs=normal_rate, nperseg=1024
)

frequencies_test, times_test, Z_test = stft(
    test_audio, fs=test_rate, nperseg=1024
)


normal_db = 20 * np.log10(np.abs(Z_normal) + 1e-10)
test_db = 20 * np.log10(np.abs(Z_test) + 1e-10)

print("\n[2] STFT processing completed")
print(f"Normal spectrogram shape: {normal_db.shape}")
print(f"Test spectrogram shape: {test_db.shape}")


os.makedirs(os.path.dirname(output_file), exist_ok=True)

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

plot1 = axes[0].pcolormesh(
    times_normal,
    frequencies_normal,
    normal_db,
    shading="auto",
    cmap="viridis"
)
axes[0].set_title("Normal Audio Spectrogram")
axes[0].set_ylabel("Frequency (Hz)")
fig.colorbar(plot1, ax=axes[0], label="Magnitude (dB)")

plot2 = axes[1].pcolormesh(
    times_test,
    frequencies_test,
    test_db,
    shading="auto",
    cmap="viridis"
)
axes[1].set_title("Test Audio Spectrogram")
axes[1].set_xlabel("Time (seconds)")
axes[1].set_ylabel("Frequency (Hz)")
fig.colorbar(plot2, ax=axes[1], label="Magnitude (dB)")

plt.tight_layout()

plt.savefig(output_file, dpi=150)

print("\n[3] Spectrogram image saved successfully")
print(f"Output: {output_file}")

print("\n[4] Opening spectrogram graph...")
plt.show()

print("\nAetherHound spectrogram analysis completed!")
print("=" * 55)
