
import numpy as np
import soundfile as sf

sample_rate = 44100
duration = 10
time = np.arange(0, duration, 1 / sample_rate)

for i in range(2, 4):
    normal_audio = (
        0.7 * np.sin(2 * np.pi * 120 * time)
        + 0.01 * np.random.randn(len(time))
    )

    filename = f"data/normal/normal_0{i}.wav"
    sf.write(filename, normal_audio, sample_rate)
    print(f"Created: {filename}")

for i in range(2, 4):
    suspicious_audio = (
        0.7 * np.sin(2 * np.pi * 120 * time)
        + 0.01 * np.random.randn(len(time))
    )

    for start in range(1, 10):
        burst_start = int(start * sample_rate)
        burst_end = int((start + 0.2) * sample_rate)

        suspicious_audio[burst_start:burst_end] += (
            0.5 * np.sin(
                2 * np.pi * 2500 * time[burst_start:burst_end]
            )
        )

    filename = f"data/test/test_0{i}.wav"
    sf.write(filename, suspicious_audio, sample_rate)
    print(f"Created: {filename}")

print("All additional audio samples generated!")
