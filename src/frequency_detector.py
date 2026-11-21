
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
import os

NORMAL_FILE = "data/normal/normal_01.wav"

NORMAL_FILES = [
    "data/normal/normal_01.wav",
    "data/normal/normal_02.wav",
    "data/normal/normal_03.wav"
]

TEST_FILES = [
    "data/test/test_01.wav",
    "data/test/test_02.wav",
    "data/test/test_03.wav"
]

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
    baseline_audio, baseline_rate = load_audio(NORMAL_FILE)
    baseline_level = calculate_band_rms(
        baseline_audio, baseline_rate
    )

    threshold = baseline_level * 1.5

    print("\nAETHERHOUND - BATCH FREQUENCY DETECTOR")
    print("--------------------------------------")
    print(f"Frequency Band: {LOW_FREQ}-{HIGH_FREQ} Hz")
    print(f"Normal Baseline RMS: {baseline_level:.6f}")
    print(f"Detection Threshold: {threshold:.6f}")

    normal_passed = 0
    test_detected = 0

    print("\n--- NORMAL AUDIO TESTS ---")

    for file_path in NORMAL_FILES:
        audio, sample_rate = load_audio(file_path)
        level = calculate_band_rms(audio, sample_rate)

        if level > threshold:
            print(f"[FALSE ALERT] {os.path.basename(file_path)}")
        else:
            print(f"[PASS] {os.path.basename(file_path)} - Normal")
            normal_passed += 1

    print("\n--- SUSPICIOUS AUDIO TESTS ---")

    for file_path in TEST_FILES:
        audio, sample_rate = load_audio(file_path)
        level = calculate_band_rms(audio, sample_rate)

        if level > threshold:
            print(f"[ALERT] {os.path.basename(file_path)} - Anomaly")
            test_detected += 1
        else:
            print(f"[MISSED] {os.path.basename(file_path)}")

    print("\n--- FINAL RESULTS ---")
    print(f"Normal samples passed: {normal_passed}/{len(NORMAL_FILES)}")
    print(f"Suspicious samples detected: {test_detected}/{len(TEST_FILES)}")


if __name__ == "__main__":
    main()
