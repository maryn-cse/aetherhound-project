# AetherHound - Air-Gapped Signal Anomaly Detection

**Cybersecurity Internship Project | Infotact Solutions**

## About the Project

AetherHound is a defensive cybersecurity project focused on identifying unusual acoustic and Radio Frequency (RF) signal patterns around air-gapped systems.

The project explores Digital Signal Processing (DSP) techniques to analyze signals and identify potentially suspicious activity.

## Project Objectives

- Monitor acoustic and RF signals.
- Analyze signal patterns using Digital Signal Processing (DSP).
- Identify unusual signal activity.
- Develop anomaly detection capabilities.
- Generate alerts for suspicious signal patterns.

## Key Features

### Implemented
- Synthetic audio signal generation.
- Normal and test audio dataset creation.
- Audio signal analysis using Python.
- Signal measurements such as RMS, amplitude and duration.
- Audio waveform visualization.

### Planned
- Live acoustic signal monitoring.
- RF signal analysis.
- Signal anomaly detection.
- Automated alert generation.
- Event logging.
- Advanced signal analysis using machine learning.

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
│   ├── analyze_data.py
│   ├── visualize_data.py
│   └── record_audio.py
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

### 4. Visualize Audio Signals

```powershell
python src/visualize_data.py
```

## Development Status

**Current Status: Development in Progress**

Completed initial audio data generation, basic signal analysis and waveform visualization.

RF monitoring, anomaly detection and automated alert generation are planned for future development.

## Internship

Infotact Solutions - Cybersecurity Internship

## Disclaimer

This project is developed for educational and defensive cybersecurity research using controlled test data and authorized environments.
