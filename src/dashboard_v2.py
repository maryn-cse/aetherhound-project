"""AetherHound - Pro Dashboard

One window for the whole project:
  Overview        detection summary, covert-burst timeline, run-all pipeline
  Live Detection  real-time waterfall + band-level chart (replay or live microphone)
  Spectrogram     normal vs test vs bandpass-filtered spectrograms
  Run Modules     buttons for every script in src/
  Result Images   latest saved PNG graphs

Put this file in src/ and run:  python src/dashboard_pro.py
"""
import glob
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from collections import deque
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

import matplotlib.image as mpimg
import numpy as np
import soundfile as sf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import butter, sosfilt, stft

try:
    import sounddevice as sd
except Exception:  # dashboard still works in replay mode without a microphone
    sd = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
TEST_FILE = PROJECT_ROOT / "data" / "test" / "test_01.wav"
NORMAL_FILE = PROJECT_ROOT / "data" / "normal" / "normal_01.wav"
LOG_FILE = PROJECT_ROOT / "logs" / "detections.log"

NPERSEG = 1024
MAX_FREQ = 5000
BAND_LOW, BAND_HIGH = 2400, 2600   # covert-burst band
TARGET_FPS = 30
WF_ROWS = 70
MIC_FS = 44100

BG, PANEL, GREEN, RED, YELLOW, TEXT = (
    "#101820", "#202C39", "#00FFAA", "#FF5555", "#FFD166", "white")


# =====================================================================
# Signal processing (no GUI code here)
# =====================================================================
def load_mono(path):
    audio, fs = sf.read(path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    return audio, fs


def to_spectrogram(audio, fs):
    freqs, times, Z = stft(audio, fs=fs, nperseg=NPERSEG)
    db = 20 * np.log10(np.abs(Z) + 1e-10)
    keep = freqs <= MAX_FREQ
    return freqs[keep], times, db[keep, :]


def band_mask(freqs):
    return (freqs >= BAND_LOW) & (freqs <= BAND_HIGH)


def bandpass(audio, fs):
    nyq = fs / 2
    sos = butter(4, [BAND_LOW / nyq, BAND_HIGH / nyq], btype="bandpass", output="sos")
    return sosfilt(sos, audio)


def analyse():
    """Detect covert bursts in the test audio. Returns a dict, or None if files are missing."""
    if not TEST_FILE.exists():
        return None
    audio, fs = load_mono(TEST_FILE)
    freqs, times, db = to_spectrogram(audio, fs)
    band = db[band_mask(freqs), :].mean(axis=0)

    normal = None
    if NORMAL_FILE.exists():
        n_audio, n_fs = load_mono(NORMAL_FILE)
        n_freqs, n_times, n_db = to_spectrogram(n_audio, n_fs)
        n_band = n_db[band_mask(n_freqs), :].mean(axis=0)
        threshold = float(n_band.mean() + max(4 * n_band.std(), 6.0))
        normal = (n_freqs, n_times, n_db)
    else:
        threshold = float(np.median(band) + 10.0)

    alert = band > threshold
    events = int(np.sum(alert[1:] & ~alert[:-1]) + (1 if alert[0] else 0))
    peak = float(freqs[np.argmax(db[:, alert].mean(axis=1))]) if alert.any() else None

    filtered = bandpass(audio, fs)
    f_freqs, f_times, f_db = to_spectrogram(filtered, fs)

    return dict(
        audio=audio, fs=fs, freqs=freqs, times=times, db=db, band=band,
        threshold=threshold, alert=alert, events=events, peak=peak,
        normal=normal, filtered=(f_freqs, f_times, f_db),
        duration=len(audio) / fs, alert_pct=100.0 * float(alert.mean()),
    )


def count_events(alert):
    return int(np.sum(alert[1:] & ~alert[:-1]) + (1 if alert[0] else 0))


def classify_audio(path, threshold=None):
    """Automatic verdict for any wav file: ALERT if the covert band goes above the threshold."""
    audio, fs = load_mono(path)
    freqs, times, db = to_spectrogram(audio, fs)
    band = db[band_mask(freqs), :].mean(axis=0)
    if threshold is None:
        threshold = float(np.median(band) + 10.0)
    alert = band > threshold
    peak = float(freqs[np.argmax(db[:, alert].mean(axis=1))]) if alert.any() else None
    return dict(verdict="ALERT" if alert.any() else "NORMAL",
                events=count_events(alert), peak=peak, threshold=threshold,
                max_level=float(band.max()), alert_pct=100.0 * float(alert.mean()),
                duration=len(audio) / fs)


def execute(name, timeout=120):
    """Run src/<name> in a separate process. Returns (output_text, ok)."""
    path = SRC / name
    if not path.exists():
        return f"src/{name} not found", False
    env = dict(os.environ, MPLBACKEND="Agg")  # plt.show() will not block
    try:
        r = subprocess.run([sys.executable, str(path)], cwd=PROJECT_ROOT,
                           capture_output=True, text=True, timeout=timeout,
                           env=env, stdin=subprocess.DEVNULL)
        out = r.stdout
        if r.stderr.strip():
            out += "\n[stderr]\n" + r.stderr
        return out, r.returncode == 0
    except subprocess.TimeoutExpired:
        return f"Timed out after {timeout} s", False
    except Exception as error:
        return str(error), False


def write_log(audio_time, level):
    LOG_FILE.parent.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{stamp} | ALERT | {BAND_LOW}-{BAND_HIGH} Hz | "
                f"audio time {audio_time:.2f}s | level {level:.1f} dB\n")


# =====================================================================
# GUI
# =====================================================================
root = tk.Tk()
root.title("AetherHound - Pro Dashboard")
root.geometry("1200x850")
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=BG, borderwidth=0)
style.configure("TNotebook.Tab", padding=(16, 7), font=("Arial", 10, "bold"))
style.configure("TFrame", background=BG)
style.configure("Horizontal.TProgressbar", troughcolor=PANEL, background=GREEN)

# ---- scrollable page ------------------------------------------------
main_canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
main_canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)

content = tk.Frame(main_canvas, bg=BG)
window_id = main_canvas.create_window((0, 0), window=content, anchor="nw")


def update_scroll_region(event=None):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    main_canvas.itemconfigure(window_id, width=main_canvas.winfo_width())


content.bind("<Configure>", update_scroll_region)
main_canvas.bind("<Configure>", update_scroll_region)


def mouse_wheel(event):
    if str(event.widget).endswith("!text"):   # let the output box scroll itself
        return
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


root.bind_all("<MouseWheel>", mouse_wheel)

# ---- header ---------------------------------------------------------
tk.Label(content, text="AETHERHOUND", font=("Arial", 26, "bold"),
         fg=GREEN, bg=BG).pack(pady=(12, 0))
tk.Label(content, text="Air-Gapped RF & Acoustic Covert Channel Detector  |  Software Simulation",
         fg=TEXT, bg=BG).pack()
status = tk.Label(content, text="SYSTEM STATUS: READY", font=("Arial", 12, "bold"),
                  fg=GREEN, bg=PANEL, padx=20, pady=6)
status.pack(pady=8)

notebook = ttk.Notebook(content)
notebook.pack(fill="x", padx=10)

tk.Label(content, text="CONSOLE", font=("Arial", 10, "bold"),
         fg=GREEN, bg=BG).pack(anchor="w", padx=14, pady=(10, 0))
output = scrolledtext.ScrolledText(content, height=10, bg=PANEL, fg=GREEN,
                                   font=("Consolas", 10))
output.pack(fill="x", padx=10, pady=(2, 12))


def log(text):
    output.insert(tk.END, text + "\n")
    output.see(tk.END)


def set_status(text, color=GREEN):
    status.config(text="SYSTEM STATUS: " + text, fg=color)


def style_axes(fig, *axes):
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(PANEL)
        ax.tick_params(colors=TEXT)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)


A = None
try:
    A = analyse()
except Exception as error:
    log(f"[WARN] Analysis failed: {error}")

# =====================================================================
# Tab 1: Overview
# =====================================================================
overview = ttk.Frame(notebook)
notebook.add(overview, text="Overview")

banner = tk.Label(overview, text="", font=("Arial", 16, "bold"), pady=10)
banner.pack(fill="x", padx=20, pady=(14, 6))

cards_row = tk.Frame(overview, bg=BG)
cards_row.pack(pady=6)
card_values = {}
for title in ["Burst Events", "Covert Frequency", "Threshold", "Test Duration", "Sample Rate"]:
    card = tk.Frame(cards_row, bg=PANEL, padx=16, pady=8)
    card.pack(side="left", padx=6)
    tk.Label(card, text=title, fg="#9FB3C8", bg=PANEL, font=("Arial", 9)).pack()
    value = tk.Label(card, text="-", fg=GREEN, bg=PANEL, font=("Arial", 15, "bold"))
    value.pack()
    card_values[title] = value

ov_fig = Figure(figsize=(10, 3.4), dpi=100)
ov_ax = ov_fig.add_subplot(111)
ov_canvas = FigureCanvasTkAgg(ov_fig, master=overview)
ov_canvas.get_tk_widget().pack(pady=8)


def refresh_overview():
    global A
    try:
        A = analyse()
    except Exception as error:
        A = None
        log(f"[WARN] Analysis failed: {error}")
    ov_ax.clear()
    if A is None:
        banner.config(text="NO TEST AUDIO FOUND - run Generate Audio first", bg=YELLOW, fg=BG)
        ov_canvas.draw_idle()
        return
    if A["events"] > 0:
        banner.config(text=f"COVERT SIGNAL DETECTED  |  {A['events']} burst event(s) in "
                           f"{BAND_LOW}-{BAND_HIGH} Hz", bg=RED, fg=TEXT)
    else:
        banner.config(text="SIGNAL WITHIN BASELINE  |  no covert bursts detected", bg="#0B6E4F", fg=TEXT)
    card_values["Burst Events"].config(text=str(A["events"]))
    card_values["Covert Frequency"].config(
        text=f"{A['peak']:.0f} Hz" if A["peak"] else "-")
    card_values["Threshold"].config(text=f"{A['threshold']:.1f} dB")
    card_values["Test Duration"].config(text=f"{A['duration']:.1f} s")
    card_values["Sample Rate"].config(text=f"{A['fs']} Hz")

    t, band, thr = A["times"], A["band"], A["threshold"]
    ov_ax.plot(t, band, color="#00CC99", linewidth=1.2, label=f"{BAND_LOW}-{BAND_HIGH} Hz level")
    ov_ax.axhline(thr, color=YELLOW, linestyle="--", label="Detection threshold")
    ov_ax.fill_between(t, band.min(), band.max(), where=A["alert"],
                       color=RED, alpha=0.35, label="Covert burst")
    ov_ax.set_title("Covert Band Level Over Time")
    ov_ax.set_xlabel("Time (s)")
    ov_ax.set_ylabel("Level (dB)")
    ov_ax.grid(True, alpha=0.2)
    ov_ax.legend(facecolor=PANEL, labelcolor=TEXT, loc="upper right")
    style_axes(ov_fig, ov_ax)
    ov_fig.tight_layout()
    ov_canvas.draw_idle()


PIPELINE = ["mock_fan_malware.py", "analyze_data.py", "spectrogram.py",
            "bandpass_filter.py", "verify_filter.py", "frequency_detector.py",
            "anomaly_detector.py"]
progress = ttk.Progressbar(overview, maximum=len(PIPELINE), length=500)
progress.pack(pady=(6, 2))
pipeline_btn = tk.Button(overview, text="RUN FULL PIPELINE", bg="#00CC99", fg=BG,
                         font=("Arial", 12, "bold"), padx=24, pady=8, cursor="hand2")
pipeline_btn.pack(pady=(2, 16))


def run_pipeline():
    pipeline_btn.config(state="disabled")
    progress.config(value=0)

    def worker():
        failures = 0
        for n, name in enumerate(PIPELINE, start=1):
            root.after(0, lambda n=n, name=name: (
                set_status(f"PIPELINE {n}/{len(PIPELINE)}: {name}", YELLOW),
                log(f"\n>>> python src/{name}")))
            out, ok = execute(name)
            failures += 0 if ok else 1
            root.after(0, lambda o=out, k=ok, nm=name, n=n: (
                log((o.strip() or "(no output)") + ("" if k else f"\n[FAILED] {nm}")),
                progress.config(value=n)))
        root.after(0, lambda: pipeline_done(failures))

    threading.Thread(target=worker, daemon=True).start()


def pipeline_done(failures):
    pipeline_btn.config(state="normal")
    if failures:
        set_status(f"PIPELINE FINISHED WITH {failures} ERROR(S)", RED)
    else:
        set_status("PIPELINE COMPLETED")
    refresh_overview()
    show_latest_image()


pipeline_btn.config(command=run_pipeline)

file_verdict = tk.Label(overview, text="CHECK ANY AUDIO FILE", font=("Arial", 24, "bold"),
                        bg=PANEL, fg=YELLOW, pady=12)
file_verdict.pack(fill="x", padx=20, pady=(0, 4))
file_detail = tk.Label(overview, text="", fg=TEXT, bg=BG, font=("Consolas", 10))
file_detail.pack()


def check_file():
    path = filedialog.askopenfilename(initialdir=str(PROJECT_ROOT / "data"),
                                      filetypes=[("WAV audio", "*.wav")])
    if not path:
        return
    try:
        threshold = A["threshold"] if A is not None else None
        r = classify_audio(path, threshold)
    except Exception as error:
        log(f"[ERROR] Cannot analyse {path}: {error}")
        return
    name = Path(path).name
    if r["verdict"] == "ALERT":
        file_verdict.config(text=f"{name}  ->  ALERT", bg=RED, fg=TEXT)
    else:
        file_verdict.config(text=f"{name}  ->  NORMAL", bg="#0B6E4F", fg=TEXT)
    peak = f"{r['peak']:.0f} Hz" if r["peak"] else "-"
    file_detail.config(text=f"Burst events: {r['events']}  |  Covert frequency: {peak}  |  "
                            f"Max band level: {r['max_level']:.1f} dB  |  "
                            f"Threshold: {r['threshold']:.1f} dB")
    log(f"[CHECK] {name}: {r['verdict']}  events={r['events']}  peak={peak}")


tk.Button(overview, text="CHECK AUDIO FILE  (automatic Normal / Alert)", command=check_file,
          bg="#4DA3FF", fg=BG, font=("Arial", 11, "bold"), padx=20, pady=6,
          cursor="hand2").pack(pady=(6, 18))

# =====================================================================
# Tab 2: Live detection (waterfall + band-level strip + microphone)
# =====================================================================
wf_tab = ttk.Frame(notebook)
notebook.add(wf_tab, text="Live Detection")

if A is not None:
    wf_freqs = A["freqs"]
    wf_floor = float(A["db"].min())
    wf_ceil = float(A["db"].max())
else:
    wf_freqs = np.fft.rfftfreq(NPERSEG, 1 / MIC_FS)
    wf_freqs = wf_freqs[wf_freqs <= MAX_FREQ]
    wf_floor, wf_ceil = -120.0, 0.0

CALIBRATE_SECONDS = 3
LEVEL_HISTORY = 200

wf_buffer = np.full((WF_ROWS, len(wf_freqs)), wf_floor)
levels = deque(maxlen=LEVEL_HISTORY)
wf_state = dict(running=False, mode="replay", i=0, prev_alert=False, fps=0.0,
                last=time.perf_counter(), after_id=None, calib=[], calib_until=0.0,
                live_thr=None, events=0, tick=0, t0=0.0, alert_until=0.0)
mic = dict(stream=None, block=np.zeros(NPERSEG))

verdict = tk.Label(wf_tab, text="STOPPED", font=("Arial", 46, "bold"), bg=PANEL, fg=YELLOW, pady=14)
verdict.pack(fill="x", padx=20, pady=(12, 2))

wf_banner = tk.Label(wf_tab, text="LIVE DETECTION STOPPED", font=("Arial", 15, "bold"),
                     bg=PANEL, fg=YELLOW, pady=8)
wf_banner.pack(fill="x", padx=20, pady=(12, 4))

wf_fig = Figure(figsize=(10, 5.6), dpi=100)
grid = wf_fig.add_gridspec(2, 1, height_ratios=[3, 1.2])
wf_ax = wf_fig.add_subplot(grid[0])
wf_im = wf_ax.imshow(wf_buffer, aspect="auto", cmap="viridis", vmin=wf_floor, vmax=wf_ceil,
                     extent=[0, MAX_FREQ, WF_ROWS, 0], interpolation="nearest")
wf_ax.axvspan(BAND_LOW, BAND_HIGH, color=RED, alpha=0.15)
wf_ax.set_xlabel("Frequency (Hz)")
wf_ax.set_ylabel("Time (newest at top)")
wf_ax.set_title("Live Spectrum Waterfall  (red band = covert-burst band)")

lv_ax = wf_fig.add_subplot(grid[1])
(lv_line,) = lv_ax.plot([], [], color="#00CC99", linewidth=1.2)
lv_thr = lv_ax.axhline(0, color=YELLOW, linestyle="--", visible=False)
lv_ax.set_xlim(0, LEVEL_HISTORY)
lv_ax.set_ylabel("Band level (dB)")
lv_ax.set_xlabel("Recent frames")
lv_ax.grid(True, alpha=0.2)
style_axes(wf_fig, wf_ax, lv_ax)
wf_fig.tight_layout()
wf_canvas = FigureCanvasTkAgg(wf_fig, master=wf_tab)
wf_canvas.get_tk_widget().pack(pady=4)

wf_info = tk.Label(wf_tab, text="", fg=TEXT, bg=BG, font=("Consolas", 10))
wf_info.pack()


def mic_callback(indata, frames, time_info, status_info):
    mic["block"] = indata[:, 0].copy()


def wf_column():
    """Return (spectrum column on the display axis, covert-band level, audio time)."""
    if wf_state["mode"] == "replay" and A is not None:
        i = wf_state["i"]
        wf_state["i"] = (i + 1) % A["db"].shape[1]
        return A["db"][:, i], float(A["band"][i]), float(A["times"][i])
    block = np.zeros(NPERSEG)
    data = mic["block"][:NPERSEG]
    block[:len(data)] = data
    window = np.hanning(NPERSEG)
    spectrum = np.abs(np.fft.rfft(block * window)) / window.sum()
    mic_freqs = np.fft.rfftfreq(NPERSEG, 1 / MIC_FS)
    col = np.interp(wf_freqs, mic_freqs, 20 * np.log10(spectrum + 1e-10))
    return col, float(col[band_mask(wf_freqs)].mean()), time.perf_counter() - wf_state["t0"]


def start_calibration():
    """Learn the room's normal level (baseline) for a few seconds."""
    wf_state["calib"] = []
    wf_state["live_thr"] = None
    wf_state["calib_until"] = time.perf_counter() + CALIBRATE_SECONDS
    wf_state["events"] = 0


def wf_tick():
    if not wf_state["running"]:
        return
    t0 = time.perf_counter()
    col, level, audio_time = wf_column()
    wf_buffer[1:] = wf_buffer[:-1]
    wf_buffer[0] = col
    wf_im.set_data(wf_buffer)
    levels.append(level)

    # threshold: replay uses the normal-audio baseline, microphone learns the room
    if wf_state["mode"] == "mic":
        threshold = wf_state["live_thr"]
        if threshold is None:
            wf_state["calib"].append(level)
            left = wf_state["calib_until"] - t0
            if left <= 0 and len(wf_state["calib"]) > 5:
                arr = np.array(wf_state["calib"])
                wf_state["live_thr"] = float(arr.mean() + max(4 * arr.std(), 6.0))
                threshold = wf_state["live_thr"]
                log(f"[LIVE] Baseline learned. Threshold = {threshold:.1f} dB")
            else:
                wf_banner.config(text=f"CALIBRATING baseline... keep the room quiet ({max(left, 0):.0f} s)",
                                 bg=YELLOW, fg=BG)
    else:
        threshold = A["threshold"] if A is not None else None

    alert = threshold is not None and level > threshold
    if threshold is not None:
        if alert:
            wf_banner.config(text=f"ALERT: covert burst at {BAND_LOW}-{BAND_HIGH} Hz  ({level:.1f} dB)",
                             bg=RED, fg=TEXT)
            if not wf_state["prev_alert"]:
                wf_state["events"] += 1
                write_log(audio_time, level)
        else:
            wf_banner.config(text=f"Signal within baseline  ({level:.1f} dB)", bg="#0B6E4F", fg=TEXT)
    # big automatic verdict (ALERT is held for 1 s so it does not flicker)
    if alert:
        wf_state["alert_until"] = t0 + 1.0
    if threshold is None:
        verdict.config(text="LEARNING...", bg=YELLOW, fg=BG)
    elif t0 < wf_state["alert_until"]:
        verdict.config(text="ALERT", bg=RED, fg=TEXT)
    else:
        verdict.config(text="NORMAL", bg="#0B6E4F", fg=TEXT)
    wf_state["prev_alert"] = alert

    wf_state["tick"] += 1
    if wf_state["tick"] % 3 == 0:               # update the strip chart every 3rd frame
        lv_line.set_data(range(len(levels)), list(levels))
        if threshold is not None:
            lv_thr.set_ydata([threshold, threshold])
            lv_thr.set_visible(True)
        lo, hi = min(levels), max(levels)
        if threshold is not None:
            lo, hi = min(lo, threshold), max(hi, threshold)
        lv_ax.set_ylim(lo - 3, hi + 3)
    wf_canvas.draw_idle()

    now = time.perf_counter()
    wf_state["fps"] = 0.9 * wf_state["fps"] + 0.1 * (1 / max(now - wf_state["last"], 1e-6))
    wf_state["last"] = now
    thr_text = f"{threshold:.1f} dB" if threshold is not None else "learning..."
    wf_info.config(text=f"Mode: {wf_state['mode']}  |  FPS: {wf_state['fps']:.0f}  |  "
                        f"Threshold: {thr_text}  |  Alerts: {wf_state['events']}")
    delay = max(1, int(1000 / TARGET_FPS - (time.perf_counter() - t0) * 1000))
    wf_state["after_id"] = root.after(delay, wf_tick)


def stop_mic():
    if mic["stream"] is not None:
        mic["stream"].stop()
        mic["stream"].close()
        mic["stream"] = None


def wf_start(mode):
    wf_stop()
    if mode == "replay" and A is None:
        log("[ERROR] test_01.wav missing - cannot replay")
        return
    if mode == "mic":
        if sd is None:
            log("[ERROR] sounddevice is not installed: pip install sounddevice")
            return
        try:
            mic["stream"] = sd.InputStream(samplerate=MIC_FS, channels=1,
                                           blocksize=NPERSEG, callback=mic_callback)
            mic["stream"].start()
        except Exception as error:
            log(f"[ERROR] Microphone: {error}")
            mic["stream"] = None
            return
    levels.clear()
    wf_state.update(running=True, mode=mode, i=0, prev_alert=False, events=0, tick=0, alert_until=0.0,
                    last=time.perf_counter(), t0=time.perf_counter())
    if mode == "mic":
        start_calibration()
    set_status(f"LIVE DETECTION RUNNING ({mode})")
    wf_tick()


def wf_stop():
    wf_state["running"] = False
    if wf_state["after_id"] is not None:
        root.after_cancel(wf_state["after_id"])
        wf_state["after_id"] = None
    stop_mic()
    wf_banner.config(text="LIVE DETECTION STOPPED", bg=PANEL, fg=YELLOW)
    verdict.config(text="STOPPED", bg=PANEL, fg=YELLOW)


def recalibrate():
    if wf_state["running"] and wf_state["mode"] == "mic":
        start_calibration()
        log("[LIVE] Re-calibrating baseline...")
    else:
        log("[INFO] Start LIVE MICROPHONE first")


def play_covert_signal():
    """Play 2500 Hz bursts through the speakers; the microphone hears them live."""
    if sd is None:
        log("[ERROR] sounddevice is not installed: pip install sounddevice")
        return
    fs = MIC_FS
    burst = np.arange(int(0.25 * fs)) / fs
    tone = 0.6 * np.sin(2 * np.pi * 2500 * burst)
    fade = np.minimum(1.0, np.minimum(np.arange(len(tone)), np.arange(len(tone))[::-1]) / 400)
    tone = tone * fade
    gap = np.zeros(int(0.25 * fs))
    signal = np.concatenate([np.concatenate([tone, gap]) for _ in range(6)])
    try:
        sd.play(signal.astype(np.float32), fs)
        log("[LIVE] Playing 2500 Hz covert bursts - keep the microphone near the speaker")
    except Exception as error:
        log(f"[ERROR] Cannot play sound: {error}")


wf_btns = tk.Frame(wf_tab, bg=BG)
wf_btns.pack(pady=(6, 14))
for label, cmd, colour, fg in [
    ("REPLAY TEST AUDIO", lambda: wf_start("replay"), "#00CC99", BG),
    ("LIVE MICROPHONE", lambda: wf_start("mic"), "#4DA3FF", BG),
    ("RE-CALIBRATE", recalibrate, "#FFD166", BG),
    ("PLAY COVERT SIGNAL", play_covert_signal, "#C77DFF", BG),
    ("STOP", wf_stop, "#CC5555", TEXT),
]:
    tk.Button(wf_btns, text=label, command=cmd, bg=colour, fg=fg,
              font=("Arial", 10, "bold"), padx=12, pady=4,
              cursor="hand2").pack(side="left", padx=5)

# =====================================================================
# Tab 3: Spectrograms
# =====================================================================
spec_tab = ttk.Frame(notebook)
notebook.add(spec_tab, text="Spectrogram")
spec_fig = Figure(figsize=(10, 7.5), dpi=100)
spec_canvas = FigureCanvasTkAgg(spec_fig, master=spec_tab)
spec_canvas.get_tk_widget().pack(pady=8)


def draw_spectrograms():
    spec_fig.clear()
    if A is None:
        spec_canvas.draw_idle()
        return
    rows = []
    if A["normal"] is not None:
        rows.append(("Normal audio", A["normal"]))
    rows.append(("Test audio (with covert bursts)", (A["freqs"], A["times"], A["db"])))
    rows.append((f"Test audio after bandpass filter ({BAND_LOW}-{BAND_HIGH} Hz)", A["filtered"]))
    axes = spec_fig.subplots(len(rows), 1)
    axes = np.atleast_1d(axes)
    for ax, (title, (f, t, db)) in zip(axes, rows):
        mesh = ax.pcolormesh(t, f, db, shading="auto", cmap="viridis",
                             vmin=A["db"].min(), vmax=A["db"].max())
        ax.axhline(BAND_LOW, color=RED, linewidth=0.6, alpha=0.7)
        ax.axhline(BAND_HIGH, color=RED, linewidth=0.6, alpha=0.7)
        ax.set_title(title)
        ax.set_ylabel("Frequency (Hz)")
        style_axes(spec_fig, ax)
    axes[-1].set_xlabel("Time (s)")
    spec_fig.tight_layout()
    spec_canvas.draw_idle()


# =====================================================================
# Tab 4: Run modules
# =====================================================================
def run_script(name):
    set_status(f"RUNNING {name}", YELLOW)
    log(f"\n>>> python src/{name}")

    def worker():
        out, ok = execute(name)
        root.after(0, lambda: script_done(name, out, ok))

    threading.Thread(target=worker, daemon=True).start()


def script_done(name, out, ok):
    log(out.strip() or "(no output)")
    set_status(f"{name} COMPLETED" if ok else f"{name} FAILED", GREEN if ok else RED)
    show_latest_image()


def open_cli_waterfall():
    flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.Popen([sys.executable, str(SRC / "cli_waterfall.py")],
                     cwd=PROJECT_ROOT, creationflags=flags)
    log("\n>>> cli_waterfall.py opened in a new terminal window (Ctrl+C to stop)")


modules_tab = ttk.Frame(notebook)
notebook.add(modules_tab, text="Run Modules")
MODULES = [
    ("Generate Audio", "generate_data.py", "Normal and test audio files"),
    ("Generate Test Samples", "generate_test_samples.py", "Extra normal / test samples"),
    ("Mock Fan Malware", "mock_fan_malware.py", "Creates fan_pulse.csv"),
    ("Record Microphone", "record_audio.py", "Raw recording to data/raw"),
    ("Analyze Data", "analyze_data.py", "RMS, amplitude, duration"),
    ("Spectrogram", "spectrogram.py", "STFT of normal and test audio"),
    ("Bandpass Filter", "bandpass_filter.py", "Isolate 2400-2600 Hz"),
    ("Verify Filter", "verify_filter.py", "Check the filter result"),
    ("Visualize Data", "visualize_data.py", "Waveform graphs"),
    ("Frequency Detector", "frequency_detector.py", "Find covert burst frequency"),
    ("Anomaly Detector", "anomaly_detector.py", "Normal vs suspicious result"),
    ("Performance Test", "performance_test.py", "Speed check"),
    ("CLI Waterfall (new window)", open_cli_waterfall, "Terminal waterfall"),
]
for label, action, description in MODULES:
    row = tk.Frame(modules_tab, bg=BG)
    row.pack(fill="x", padx=24, pady=4)
    command = action if callable(action) else (lambda a=action: run_script(a))
    tk.Button(row, text=label, command=command, width=28, bg="#00CC99", fg=BG,
              font=("Arial", 10, "bold"), cursor="hand2").pack(side="left")
    tk.Label(row, text=description, fg=TEXT, bg=BG).pack(side="left", padx=14)

# =====================================================================
# Tab 5: Result images
# =====================================================================
img_tab = ttk.Frame(notebook)
notebook.add(img_tab, text="Result Images")
img_fig = Figure(figsize=(10, 5), dpi=100)
img_ax = img_fig.add_subplot(111)
img_fig.patch.set_facecolor(BG)
img_canvas = FigureCanvasTkAgg(img_fig, master=img_tab)
img_canvas.get_tk_widget().pack()


def show_latest_image():
    files = glob.glob(str(PROJECT_ROOT / "data" / "**" / "*.png"), recursive=True)
    if not files:
        return
    latest = max(files, key=os.path.getmtime)
    img_ax.clear()
    img_ax.imshow(mpimg.imread(latest))
    img_ax.axis("off")
    img_ax.set_title(Path(latest).name, color=TEXT)
    img_canvas.draw_idle()


tk.Button(img_tab, text="Refresh Latest Image", command=show_latest_image,
          bg="#00CC99", fg=BG, font=("Arial", 10, "bold")).pack(pady=6)


# =====================================================================
# Start
# =====================================================================
def on_tab_changed(event=None):
    if notebook.tab(notebook.select(), "text") == "Spectrogram":
        draw_spectrograms()


notebook.bind("<<NotebookTabChanged>>", on_tab_changed)


def on_close():
    wf_stop()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
refresh_overview()
show_latest_image()
root.mainloop()