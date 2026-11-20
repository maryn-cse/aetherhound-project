
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

NORMAL_FILE = "data/normal/normal_01.wav"
TEST_FILE = "data/test/test_01.wav"

LOW_FREQ = 2400
HIGH_FREQ = 2600


def load_audio(file_path):
    audio, sample_rate = sf.read(file_path)

    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    return audio, sample_rate


def calculate_band_rms(audio, sample_rate):
    nyquist = sample_rate / 2

    filter_coefficients = butter(
        4,
        [LOW_FREQ / nyquist, HIGH_FREQ / nyquist],
        btype="bandpass",
        output="sos"
    )

    filtered_audio = sosfilt(filter_coefficients, audio)

    return np.sqrt(np.mean(filtered_audio ** 2))


def main():
    normal_audio, normal_rate = load_audio(NORMAL_FILE)
    test_audio, test_rate = load_audio(TEST_FILE)

    if normal_rate != test_rate:
        print("Error: Sample rates do not match.")
        return

    normal_level = calculate_band_rms(normal_audio, normal_rate)
    test_level = calculate_band_rms(test_audio, test_rate)

    threshold = normal_level * 1.5

    print("AETHERHOUND - FREQUENCY DETECTOR")
    print("--------------------------------")
    print(f"Frequency Band: {LOW_FREQ}-{HIGH_FREQ} Hz")
    print(f"Normal Band RMS: {normal_level:.6f}")
    print(f"Test Band RMS: {test_level:.6f}")
    print(f"Detection Threshold: {threshold:.6f}")

    if test_level > threshold:
        print("[ALERT] Potential frequency anomaly detected!")
    else:
        print("[INFO] No frequency anomaly detected.")


if __name__ == "__main__":
    main()
