import numpy as np
import soundfile as sf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

NORMAL_DIR = BASE_DIR / "data" / "normal"
TEST_DIR = BASE_DIR / "data" / "test"

NORMAL_DIR.mkdir(parents=True, exist_ok=True)
TEST_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
DURATION = 10


def generate_normal_signal():

    print("Generating normal signal...")

    t = np.linspace(
        0, DURATION,
        SAMPLE_RATE * DURATION,
        endpoint=False
    )

    hum = 0.15 * np.sin(2 * np.pi * 120 * t)

    noise = np.random.normal(0, 0.015, len(t))

    signal = hum + noise

    signal = signal / np.max(np.abs(signal))

    sf.write(
        NORMAL_DIR / "normal_01.wav",
        signal,
        SAMPLE_RATE
    )

    print("Normal signal saved!")


def generate_test_signal():

    print("Generating test signal...")

    t = np.linspace(
        0, DURATION,
        SAMPLE_RATE * DURATION,
        endpoint=False
    )

    hum = 0.15 * np.sin(2 * np.pi * 120 * t)

    noise = np.random.normal(0, 0.015, len(t))

    burst = np.zeros(len(t))

    for start in np.arange(1, DURATION, 1.0):

        start_index = int(start * SAMPLE_RATE)

        end_index = min(
            start_index + int(0.08 * SAMPLE_RATE),
            len(t)
        )

        burst_t = t[start_index:end_index] - start

        burst[start_index:end_index] = (
            0.35 * np.sin(2 * np.pi * 2500 * burst_t)
        )

    signal = hum + noise + burst

    signal = signal / np.max(np.abs(signal))

    sf.write(
        TEST_DIR / "test_01.wav",
        signal,
        SAMPLE_RATE
    )

    print("Test signal saved!")


if __name__ == "__main__":

    generate_normal_signal()

    generate_test_signal()

