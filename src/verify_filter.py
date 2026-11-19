
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ORIGINAL_FILE = "data/test/test_01.wav"
FILTERED_FILE = "data/test/filtered_test_01.wav"

LOW_FREQ = 2400
HIGH_FREQ = 2600


def calculate_band_rms(audio, sample_rate):
    nyquist = sample_rate / 2

    sos = butter(
        4,
        [LOW_FREQ / nyquist, HIGH_FREQ / nyquist],
        btype="bandpass",
        output="sos"
    )

    band_signal = sosfilt(sos, audio)

    return np.sqrt(np.mean(band_signal ** 2))


def main():
    original, fs1 = sf.read(ORIGINAL_FILE)
    filtered, fs2 = sf.read(FILTERED_FILE)

    if original.ndim > 1:
        original = np.mean(original, axis=1)

    if filtered.ndim > 1:
        filtered = np.mean(filtered, axis=1)

    if fs1 != fs2:
        print("Error: Sample rates do not match.")
        return

    original_rms = calculate_band_rms(original, fs1)
    filtered_rms = calculate_band_rms(filtered, fs2)

    print("AETHERHOUND - FILTER VERIFICATION")
    print("--------------------------------")
    print(f"Frequency band: {LOW_FREQ}-{HIGH_FREQ} Hz")
    print(f"Original band RMS: {original_rms:.6f}")
    print(f"Filtered band RMS: {filtered_rms:.6f}")

    if original_rms > 0:
        change = ((filtered_rms - original_rms) / original_rms) * 100
        print(f"Band RMS change: {change:.2f}%")

    if filtered_rms > 0:
        print("Verification completed: Filtered signal contains measurable energy.")
    else:
        print("Warning: No measurable energy in the selected band.")


if __name__ == "__main__":
    main()
