import os
import sys
import time
import numpy as np
import soundfile as sf
from scipy.signal import stft

TEST_FILE = "data/test/test_01.wav"
NORMAL_FILE = "data/normal/normal_01.wav"
WIDTH = 60
HEIGHT = 15
MAX_FREQ = 5000
BAND_LOW, BAND_HIGH = 2400, 2600   # covert burst band
TARGET_FPS = 30
SHADES = "░▒▓█"


def load_spectrogram(path):
    audio, fs = sf.read(path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    freqs, times, Z = stft(audio, fs=fs, nperseg=1024)
    db = 20 * np.log10(np.abs(Z) + 1e-10)
    keep = freqs <= MAX_FREQ
    return freqs[keep], db[keep, :]


def band_level(freqs, db):
    mask = (freqs >= BAND_LOW) & (freqs <= BAND_HIGH)
    return db[mask, :].mean(axis=0)


def get_threshold(test_band):
    """Normal audio level + margin; fallback if normal file is missing."""
    if os.path.exists(NORMAL_FILE):
        nf, ndb = load_spectrogram(NORMAL_FILE)
        nb = band_level(nf, ndb)
        return nb.mean() + max(4 * nb.std(), 6.0)
    return np.median(test_band) + 10.0


def to_row(column, dmin, dmax, freqs):
    idx = np.linspace(0, len(freqs) - 1, WIDTH).astype(int)
    scaled = np.clip((column[idx] - dmin) / (dmax - dmin), 0, 0.999)
    return "".join(SHADES[int(v * len(SHADES))] for v in scaled)


def main():
    os.system("")                              
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    freqs, db = load_spectrogram(TEST_FILE)
    band = band_level(freqs, db)
    threshold = get_threshold(band)
    dmin, dmax = db.min(), db.max()

    history = [" " * WIDTH for _ in range(HEIGHT)]
    n_cols = db.shape[1]
    i = 0
    fps = 0.0
    last = time.perf_counter()

    print("\033[2J", end="")                   
    try:
        while True:
            start = time.perf_counter()

            history.append(to_row(db[:, i], dmin, dmax, freqs))
            history.pop(0)
            alert = band[i] > threshold

            lines = [
                "=" * WIDTH,
                " AETHERHOUND - CLI SPECTRUM WATERFALL",
                f" Mode: SOFTWARE SIMULATION | {fps:5.1f} FPS",
                "=" * WIDTH,
            ]
            lines += list(reversed(history))   # newest row on top
            lines.append("-" * WIDTH)
            lines.append(" 0 Hz" + " " * (WIDTH - 14) + "5000 Hz")
            if alert:
                lines.append(f" [ALERT] Covert burst at {BAND_LOW}-{BAND_HIGH} Hz!   ")
            else:
                lines.append(" [INFO] Signal within baseline.               ")
            lines.append(" Press Ctrl+C to stop.")

            # cursor to top-left, then draw the whole frame in one write (no flicker)
            sys.stdout.write("\033[H" + "\n".join(lines) + "\n")
            sys.stdout.flush()

            i = (i + 1) % n_cols
            time.sleep(max(0, 1 / TARGET_FPS - (time.perf_counter() - start)))
            now = time.perf_counter()
            fps = 1 / (now - last)
            last = now
    except KeyboardInterrupt:
        print("\nAetherHound monitoring stopped.")


if __name__ == "__main__":
    main()