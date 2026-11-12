import sounddevice as sd
import soundfile as sf
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Save location
SAVE_DIR = BASE_DIR / "data" / "raw"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Recording settings
SAMPLE_RATE = 44100
DURATION = 10

print("AetherHound Audio Recording")
print("---------------------------")

print("Recording started...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1
)

sd.wait()

print("Recording completed!")

# Save audio
file_path = SAVE_DIR / "mic_recording.wav"

sf.write(file_path, audio, SAMPLE_RATE)

print("Audio saved successfully!")
print("File:", file_path)