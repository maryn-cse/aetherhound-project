
import tkinter as tk
from tkinter import scrolledtext
import soundfile as sf
import numpy as np
import subprocess
import sys
from pathlib import Path
import sounddevice as sd
from matplotlib.animation import FuncAnimation

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PROJECT_ROOT = Path(__file__).resolve().parent.parent

root = tk.Tk()
root.title("AetherHound - Signal Monitoring Dashboard")
root.geometry("1100x750")
root.configure(bg="#101820")

main_canvas = tk.Canvas(root, bg="#101820", highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
main_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)

content = tk.Frame(main_canvas, bg="#101820")
window_id = main_canvas.create_window(
    (0, 0), window=content, anchor="nw"
)

def update_scroll_region(event=None):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    main_canvas.itemconfigure(window_id, width=main_canvas.winfo_width())

content.bind("<Configure>", update_scroll_region)
main_canvas.bind("<Configure>", update_scroll_region)

def mouse_wheel(event):
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

root.bind_all("<MouseWheel>", mouse_wheel)


tk.Label(
    content, text="AETHERHOUND",
    font=("Arial", 24, "bold"),
    fg="#00FFAA", bg="#101820"
).pack(pady=15)

tk.Label(
    content,
    text="Air-Gapped Signal Anomaly Detection | Software Simulation",
    fg="white", bg="#101820"
).pack()

status = tk.Label(
    content, text="SYSTEM STATUS: READY",
    font=("Arial", 14, "bold"),
    fg="#00FFAA", bg="#202C39",
    padx=20, pady=10
)
status.pack(pady=15)


audio_path = PROJECT_ROOT / "data" / "test" / "test_01.wav"
audio, sample_rate = sf.read(audio_path)

if audio.ndim > 1:
    audio = np.mean(audio, axis=1)

time_axis = np.arange(len(audio)) / sample_rate

figure = Figure(figsize=(9, 4), dpi=100)
axis = figure.add_subplot(111)
axis.plot(time_axis, audio, color="#00CC99", linewidth=0.6)

axis.set_title("Simulated Audio Waveform", color="white")
axis.set_xlabel("Time (seconds)", color="white")
axis.set_ylabel("Amplitude", color="white")
axis.set_facecolor("#202C39")
figure.patch.set_facecolor("#101820")
axis.tick_params(colors="white")
axis.grid(True, alpha=0.2)

canvas = FigureCanvasTkAgg(figure, master=content)
canvas.draw()
canvas.get_tk_widget().pack(pady=15)


LIVE_SAMPLE_RATE = 44100
BUFFER_SIZE = 2048

live_audio = np.zeros(BUFFER_SIZE)

live_figure = Figure(figsize=(9, 3), dpi=100)
live_axis = live_figure.add_subplot(111)

live_line, = live_axis.plot(
    np.arange(BUFFER_SIZE),
    live_audio,
    color="#00FFAA"
)

live_axis.set_title("Live Microphone Waveform", color="white")
live_axis.set_xlabel("Samples", color="white")
live_axis.set_ylabel("Amplitude", color="white")
live_axis.set_facecolor("#202C39")
live_figure.patch.set_facecolor("#101820")
live_axis.tick_params(colors="white")
live_axis.grid(True, alpha=0.2)

live_canvas = FigureCanvasTkAgg(live_figure, master=content)
live_canvas.draw()
live_canvas.get_tk_widget().pack(pady=15)

mic_status = tk.Label(
    content,
    text="MICROPHONE: STOPPED",
    fg="yellow",
    bg="#101820",
    font=("Arial", 11, "bold")
)
mic_status.pack(pady=5)

mic_stream = None

def audio_callback(indata, frames, time_info, status_info):
    global live_audio
    live_audio = indata[:, 0].copy()

def update_live_graph():
    live_line.set_ydata(live_audio)
    live_axis.set_ylim(-1, 1)
    live_canvas.draw_idle()

    if root.winfo_exists():
        root.after(50, update_live_graph)

def start_microphone():
    global mic_stream

    if mic_stream is not None:
        return

    try:
        mic_stream = sd.InputStream(
            samplerate=LIVE_SAMPLE_RATE,
            channels=1,
            blocksize=BUFFER_SIZE,
            callback=audio_callback
        )
        mic_stream.start()
        mic_status.config(
            text="MICROPHONE: LIVE",
            fg="#00FFAA"
        )
    except Exception as error:
        mic_status.config(
            text="MICROPHONE ERROR: " + str(error),
            fg="red"
        )
        mic_stream = None

def stop_microphone():
    global mic_stream

    if mic_stream is not None:
        mic_stream.stop()
        mic_stream.close()
        mic_stream = None

    mic_status.config(
        text="MICROPHONE: STOPPED",
        fg="yellow"
    )

tk.Button(
    content,
    text="START MICROPHONE",
    command=start_microphone,
    bg="#00CC99",
    fg="#101820",
    font=("Arial", 11, "bold")
).pack(pady=5)

tk.Button(
    content,
    text="STOP MICROPHONE",
    command=stop_microphone,
    bg="#CC5555",
    fg="white",
    font=("Arial", 11, "bold")
).pack(pady=5)

update_live_graph()


tk.Label(
    content, text="DETECTION RESULTS",
    font=("Arial", 13, "bold"),
    fg="#00FFAA", bg="#101820"
).pack(pady=5)

results_box = scrolledtext.ScrolledText(
    content, width=100, height=12,
    bg="#202C39", fg="#00FFAA",
    font=("Consolas", 10)
)
results_box.pack(padx=20, pady=5)

def run_detection():
    status.config(text="SYSTEM STATUS: ANALYSING...", fg="yellow")
    results_box.delete("1.0", tk.END)
    results_box.insert(tk.END, "Running frequency detector...\n")
    root.update_idletasks()

    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "src" / "frequency_detector.py")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )

        results_box.delete("1.0", tk.END)

        if result.returncode == 0:
            results_box.insert(tk.END, result.stdout)
            status.config(
                text="SYSTEM STATUS: DETECTION COMPLETED",
                fg="#00FFAA"
            )
        else:
            results_box.insert(tk.END, result.stderr)
            status.config(text="SYSTEM STATUS: DETECTION ERROR", fg="red")

    except Exception as error:
        results_box.insert(tk.END, str(error))
        status.config(text="SYSTEM STATUS: ERROR", fg="red")

tk.Button(
    content, text="RUN DETECTION",
    command=run_detection,
    font=("Arial", 12, "bold"),
    bg="#00CC99", fg="#101820",
    padx=25, pady=10,
    cursor="hand2"
).pack(pady=15)

tk.Label(
    content,
    text="AetherHound | Software-Only Prototype",
    fg="gray", bg="#101820"
).pack(pady=15)

root.mainloop()
