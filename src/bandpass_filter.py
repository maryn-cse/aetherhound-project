
import os
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfilt, stft


INPUT_FILE = "data/test/test_01.wav"
OUTPUT_FILE = "data/test/filtered_test_01.wav"

LOW_FREQ = 2400
HIGH_FREQ = 2600
FILTER_ORDER = 4


def apply_bandpass_filter(audio, sample_rate):
    nyquist = sample_rate / 2

    low = LOW_FREQ / nyquist
    high = HIGH_FREQ / nyquist

    sos = butter(
        FILTER_ORDER,
        [low, high],
        btype="bandpass",
        output="sos"
    )

    filtered_audio = sosfilt(sos, audio)

    return filtered_audio


def main():
    if not os.path.exists(INPUT_FILE):
        print("Input audio file not found:", INPUT_FILE)
        return

    audio, sample_rate = sf.read(INPUT_FILE)

    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    filtered_audio = apply_bandpass_filter(audio, sample_rate)

    sf.write(OUTPUT_FILE, filtered_audio, sample_rate)

    print("Bandpass filtering completed!")
    print("Input file:", INPUT_FILE)
    print("Output file:", OUTPUT_FILE)
    print("Frequency range:", LOW_FREQ, "-", HIGH_FREQ, "Hz")
    print("Sample rate:", sample_rate, "Hz")

    fig, axes = plt.subplots(2, 1, figsize=(10, 7))

    for ax, signal, title in [
        (axes[0], audio, "Original Audio"),
        (axes[1], filtered_audio, "Filtered Audio (2400-2600 Hz)")
    ]:
        frequencies, times, Z = stft(
            signal,
            fs=sample_rate,
            nperseg=1024
        )

        db = 20 * np.log10(np.abs(Z) + 1e-10)

        ax.pcolormesh(times, frequencies, db, shading="auto")
        ax.set_ylim(0, 5000)
        ax.set_ylabel("Frequency (Hz)")
        ax.set_title(title)

    axes[1].set_xlabel("Time (seconds)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
