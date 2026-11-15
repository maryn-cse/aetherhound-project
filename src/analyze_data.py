
import numpy as np
import soundfile as sf
from pathlib import Path

project_path = Path(__file__).resolve().parent.parent

audio_files = [
    project_path / "data" / "normal" / "normal_01.wav",
    project_path / "data" / "test" / "test_01.wav"
]

print("\n===== AETHERHOUND AUDIO ANALYSIS =====")

for file_path in audio_files:
    print(f"\nAnalyzing: {file_path.name}")

    if not file_path.exists():
        print("File not found!")
        continue

    audio, sample_rate = sf.read(file_path)

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    duration = len(audio) / sample_rate
    mean_amplitude = np.mean(audio)
    max_amplitude = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio ** 2))

    print(f"Sample Rate: {sample_rate} Hz")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Samples: {len(audio)}")
    print(f"Mean Amplitude: {mean_amplitude:.4f}")
    print(f"Maximum Amplitude: {max_amplitude:.4f}")
    print(f"RMS: {rms:.4f}")

print("\n===== ANALYSIS COMPLETED =====")
