# AetherHound – Air-Gapped Signal Anomaly Detection

## Project Overview

AetherHound is a software-based prototype designed to analyse audio signals and detect unusual frequency patterns that may indicate suspicious activity in air-gapped environments.

The project uses Python-based signal processing techniques to generate, analyse, filter, and visualise audio signals. It also includes a frequency-based anomaly detection module and a desktop dashboard.

**Project Domain:** Hardware Security / Signal Analysis  
**Project Type:** Software-only Prototype  
**Programming Language:** Python

## Objectives

- Generate normal and suspicious audio signals.
- Record audio using a microphone.
- Analyse audio waveforms and frequency patterns.
- Generate spectrograms for signal visualisation.
- Apply bandpass filtering to isolate selected frequency ranges.
- Detect unusual frequency activity.
- Display analysis results through a CLI and desktop dashboard.

## Implemented Features

### 1. Audio Signal Generation
- Generates synthetic normal audio samples.
- Generates suspicious audio samples containing selected frequency bursts.
- Creates simulated fan-speed pulse patterns.

### 2. Audio Recording and Analysis
- Records audio using a regular microphone.
- Reads and analyses WAV files.
- Calculates signal properties such as duration, amplitude, and RMS.

### 3. Signal Processing
- Generates waveform visualisations.
- Generates spectrograms using Short-Time Fourier Transform (STFT).
- Applies Butterworth bandpass filtering.
- Analyses the selected 2400–2600 Hz frequency band.

### 4. Frequency-Based Anomaly Detection
- Calculates normal baseline frequency-band RMS.
- Applies a threshold based on the normal baseline.
- Classifies tested audio samples as NORMAL or ALERT.

**Detection formula:**

`Detection Threshold = Normal Baseline RMS × 1.5`

### 5. Visualisation
- CLI spectrum waterfall using stored audio samples.
- Desktop dashboard for displaying project results.
- Simulated audio waveform visualisation.
- Live microphone waveform visualisation.

## Test Results

The frequency-based detector was tested using a small simulated dataset.

| Test | Result |
|---|---:|
| Normal samples passed | 3/3 |
| Suspicious samples detected | 3/3 |
| Frequency band | 2400–2600 Hz |
| Normal baseline RMS | 0.006915 |
| Detection threshold | 0.010373 |

These results apply only to the current simulated test samples. They do not represent validated real-world detection accuracy.

## Technologies Used

- Python
- NumPy
- SciPy
- SoundDevice
- SoundFile
- Matplotlib
- Tkinter

## Project Structure

```text
AetherHound/
├── data/
│   ├── normal/
│   ├── raw/
│   └── test/
├── docs/
│   └── architecture.md
├── src/
│   ├── generate_data.py
│   ├── generate_test_samples.py
│   ├── mock_fan_malware.py
│   ├── record_audio.py
│   ├── analyze_data.py
│   ├── visualize_data.py
│   ├── spectrogram.py
│   ├── bandpass_filter.py
│   ├── verify_filter.py
│   ├── anomaly_detector.py
│   ├── frequency_detector.py
│   ├── cli_waterfall.py
│   ├── dashboard_v2.py
│   └── performance_test.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/maryn-cse/aetherhound-project.git
cd aetherhound-project
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

Run the individual Python modules from the project root directory.

Example:

```bash
python src/generate_data.py
```

Run frequency-based detection:

```bash
python src/frequency_detector.py
```

Run the CLI waterfall:

```bash
python src/cli_waterfall.py
```

Run the desktop dashboard:

```bash
python src/dashboard_v2.py
```

## Current Limitations

- This is currently a software-only prototype.
- Synthetic audio signals are used for testing.
- Microphone recording uses a regular microphone.
- Actual RF signal monitoring is not implemented.
- Raspberry Pi and HackRF SDR integration is not implemented.
- Physical server or rack localisation has not been validated.
- Machine-learning-based anomaly detection is planned but not yet implemented.
- Live microphone waveform visualisation is available, but live microphone anomaly detection has not yet been validated.

## Future Enhancements

- Implement machine-learning-based anomaly detection using an autoencoder.
- Improve detection using a larger audio dataset.
- Evaluate detection accuracy and false-positive rates.
- Explore live microphone-based anomaly detection.
- Implement timestamped anomaly logging.
- Explore SDR hardware integration.
- Investigate physical signal source localisation.

## Project Status

**Current Progress:** Week 2 development

The current prototype includes audio generation, microphone recording, signal processing, frequency-based anomaly detection, CLI visualisation, and a desktop dashboard.

Further development will focus on improving detection, testing, and exploring machine-learning and hardware integration.

## Author

MaryN

GitHub: https://github.com/maryn-cse/aetherhound-project
