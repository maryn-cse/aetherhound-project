# AetherHound - Air-Gapped Signal Anomaly Detection

**Cybersecurity Internship Project | Infotact Solutions**

## About the Project

AetherHound is a defensive cybersecurity project focused on identifying unusual acoustic and Radio Frequency (RF) signal patterns around air-gapped systems.

The current implementation is a **software-only prototype** that uses synthetic audio data to explore Digital Signal Processing (DSP) techniques and identify potentially suspicious signal patterns.

## Project Objectives

- Monitor acoustic and RF signals.
- Analyze signal patterns using Digital Signal Processing (DSP).
- Identify unusual signal activity.
- Develop anomaly detection capabilities.
- Generate alerts for suspicious signal patterns.

## Key Features

### Implemented

- Synthetic normal and test audio signal generation.
- Normal and test audio dataset creation.
- Audio recording using a microphone.
- Audio signal analysis using Python.
- Signal measurements such as RMS, amplitude and duration.
- Audio waveform visualization.
- Simulated fan-speed pulse generation.
- Short-Time Fourier Transform (STFT) processing.
- Normal and test audio spectrogram visualization.

### Planned

- Live acoustic signal monitoring.
- RF signal analysis.
- Signal anomaly detection using machine learning.
- Automated alert generation.
- Event logging.
- Advanced signal analysis using an autoencoder.

## Technologies Used

- Python
- NumPy
- SciPy
- SoundDevice
- SoundFile
- Matplotlib
- GNU Radio (planned)
- TensorFlow / PyTorch (planned)

## Project Structure

```text
AetherHound/
├── data/
│   ├── normal/
│   ├── test/
│   └── raw/
├── src/
│   ├── generate_data.py
│   ├── record_audio.py
│   ├── analyze_data.py
│   ├── visualize_data.py
│   ├── mock_fan_malware.py
│   └── spectrogram.py
├── requirements.txt
├── README.md
└── .gitignore
```

## How to Run

### 1. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Generate Test Audio

```powershell
python src/generate_data.py
```

### 3. Analyze Audio

```powershell
python src/analyze_data.py
```

### 4. Visualize Audio Waveforms

```powershell
python src/visualize_data.py
```

### 5. Run Mock Fan Simulation

```powershell
python src/mock_fan_malware.py
```

### 6. Generate Spectrograms

```powershell
python src/spectrogram.py
```

The spectrogram output is saved as `data/test/spectrogram.png`.

## Development Status

**Current Status: Development in Progress**

The initial software prototype includes synthetic audio generation, basic signal analysis, waveform visualization, simulated fan-speed pulses and spectrogram analysis.

Actual RF monitoring, hardware-based signal capture, machine-learning anomaly detection and automated alert generation are planned for future development.

## Internship

Infotact Solutions - Cybersecurity Internship

## Disclaimer

This project is developed for educational and defensive cybersecurity research using controlled test data and authorized environments. The current version is a software-only prototype and does not perform real RF monitoring or physical server detection.