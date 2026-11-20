
import numpy as np
import soundfile as sf

NORMAL_FILE = "data/normal/normal_01.wav"
TEST_FILE = "data/test/test_01.wav"

def calculate_rms(audio):
    """Calculate the Root Mean Square energy of audio."""
    return np.sqrt(np.mean(audio ** 2))


def load_audio(file_path):
    audio, sample_rate = sf.read(file_path)

    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    return audio, sample_rate


def main():
    normal_audio, normal_rate = load_audio(NORMAL_FILE)
    test_audio, test_rate = load_audio(TEST_FILE)

    if normal_rate != test_rate:
        print("Error: Sample rates do not match.")
        return

    normal_rms = calculate_rms(normal_audio)
    test_rms = calculate_rms(test_audio)

    threshold = normal_rms * 1.5

    print("AETHERHOUND - ANOMALY DETECTOR")
    print("--------------------------------")
    print(f"Normal RMS: {normal_rms:.6f}")
    print(f"Test RMS: {test_rms:.6f}")
    print(f"Detection Threshold: {threshold:.6f}")

    if test_rms > threshold:
        print("[ALERT] Potential audio anomaly detected!")
    else:
        print("[INFO] No anomaly detected by the RMS threshold.")


if __name__ == "__main__":
    main()
