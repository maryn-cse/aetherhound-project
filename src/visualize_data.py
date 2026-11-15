
import soundfile as sf
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

project_path = Path(__file__).resolve().parent.parent

files = {
    "Normal Signal": project_path / "data/normal/normal_01.wav",
    "Test Signal": project_path / "data/test/test_01.wav"
}

for title, file_path in files.items():
    audio, sample_rate = sf.read(file_path)

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    time = np.arange(len(audio)) / sample_rate

    plt.figure(figsize=(12, 4))
    plt.plot(time, audio)
    plt.title(title)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid()
    plt.tight_layout()
    plt.show()
