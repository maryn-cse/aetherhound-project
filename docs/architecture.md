# AetherHound – System Architecture

## 1. Project Overview

AetherHound is a software-based prototype designed to detect unusual patterns in simulated audio signals that may represent covert communication in air-gapped environments.

Air-gapped systems are designed to operate without direct network or internet connectivity. However, unusual hardware activity may potentially produce acoustic or electromagnetic signals.

AetherHound focuses on analysing audio signals and identifying unusual frequency patterns that could indicate suspicious activity.

The current prototype uses Python-based signal generation, digital signal processing, frequency-based anomaly detection, and a desktop dashboard.

**Project Type:** Software-only prototype  
**Domain:** Hardware Security / Signal Analysis  
**Primary Goal:** Detect unusual frequency patterns in audio signals.

## 2. System Architecture Components

### 2.1 Input Layer

The Input Layer generates or collects audio data for analysis.

Implemented features:

- Generates synthetic normal audio signals using Python.
- Generates synthetic suspicious audio signals containing selected frequency bursts.
- Records audio using a regular microphone.
- Stores generated and recorded audio files for further analysis.
- Simulates fan-speed pulse patterns using a mock fan malware script.
- Saves simulated fan pulse information in `data/test/fan_pulse.csv`.

Input sources:

- Synthetic normal audio.
- Synthetic suspicious audio.
- Recorded microphone audio.
- Simulated fan pulse data.

### 2.2 Signal Processing Layer

The Signal Processing Layer analyses the input audio and extracts useful frequency information.

Technologies used:

- Python
- NumPy
- SciPy
- SoundFile
- Matplotlib

Implemented features:

- Reads WAV audio files.
- Analyses audio samples and signal amplitude.
- Generates audio waveforms.
- Generates spectrograms using Short-Time Fourier Transform (STFT).
- Applies Butterworth bandpass filtering.
- Isolates the selected frequency range of 2400–2600 Hz.
- Calculates frequency-band RMS values for analysis.

The signal processing layer helps identify unusual frequency activity in the selected frequency band.

### 2.3 Detection Layer

The Detection Layer checks whether an audio signal contains unusual frequency activity.

Implemented detection approach:

- Uses normal audio samples as the baseline.
- Calculates the RMS energy in the selected 2400–2600 Hz frequency band.
- Calculates a detection threshold using the normal baseline.
- Compares the frequency-band RMS of test audio against the threshold.
- Classifies audio samples as NORMAL or ALERT.

**Detection Formula:**

Detection Threshold = Normal Baseline RMS × 1.5

**Recorded Test Values:**

- Frequency Band: 2400–2600 Hz
- Normal Baseline RMS: 0.006915
- Detection Threshold: 0.010373

**Detection Test Results:**

- Normal samples passed: 3/3
- Suspicious samples detected: 3/3

An initial overall RMS-based detection approach was also tested. It did not reliably identify the simulated suspicious signals because the overall RMS of the suspicious audio was lower than the normal audio. Frequency-band RMS analysis was then used to identify the unusual frequency activity.

Note: These results are from a small simulated dataset and do not represent real-world detection accuracy.

### 2.4 Output Layer

The Output Layer displays the analysis and detection results.

Implemented features:

- Displays simulated audio waveforms.
- Displays live microphone waveforms.
- Displays spectrogram visualisations.
- Provides a CLI spectrum waterfall visualisation.
- Displays frequency-based anomaly detection results.
- Provides a desktop dashboard with a detection interface.
- Displays NORMAL and ALERT results for tested audio files.

The CLI waterfall processes a stored audio sample and displays its frequency activity in a terminal.

The desktop dashboard provides a graphical interface for viewing the project results.

## 3. System Data Flow

The system follows this processing sequence:

1. Synthetic audio is generated or audio is recorded using a microphone.
2. The audio data is stored as WAV files.
3. The signal processing module reads the audio data.
4. Waveforms and spectrograms are generated for visual analysis.
5. Bandpass filtering isolates the selected frequency range.
6. The detection module calculates frequency-band RMS.
7. The calculated value is compared with the detection threshold.
8. The system classifies the tested audio as NORMAL or ALERT.
9. The results are displayed through the CLI or desktop dashboard.

## 4. Technologies and Libraries Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| NumPy | Numerical and signal calculations |
| SciPy | Digital signal processing and filtering |
| SoundDevice | Microphone audio recording |
| SoundFile | Reading and writing audio files |
| Matplotlib | Waveform and spectrogram visualisation |
| Tkinter | Desktop dashboard interface |

## 5. Current Implementation and Testing

The following features have been implemented in the current software prototype:

1. Synthetic normal audio generation.
2. Synthetic suspicious audio generation.
3. Mock fan-speed pulse simulation.
4. Microphone audio recording.
5. Audio signal analysis.
6. Waveform visualisation.
7. Spectrogram generation.
8. Butterworth bandpass filtering.
9. Frequency-band RMS calculation.
10. Frequency-based anomaly detection.
11. Batch testing of normal and suspicious audio samples.
12. CLI spectrum waterfall visualisation.
13. Desktop dashboard development.
14. Live microphone waveform visualisation.
15. Basic performance testing.

### 5.1 Detection Testing

The frequency-based detector was tested using three normal samples and three suspicious samples.

| Test Category | Result |
|---|---:|
| Normal samples passed | 3/3 |
| Suspicious samples detected | 3/3 |

These results demonstrate that the detector identified the generated test signals correctly in the current small test dataset.

They should not be interpreted as validated real-world detection accuracy.

### 5.2 Performance Testing

A basic performance test was conducted by measuring the time taken to launch and execute the detection script.

Recorded result:

- Detection process execution time: approximately 13.71 seconds.

This measurement includes process startup and execution time. It is not an isolated measurement of the detection algorithm.

## 6. Project File Structure and Module Mapping

The project is organised into separate modules based on their responsibilities.

| File / Folder | Responsibility |
|---|---|
| `src/generate_data.py` | Generates synthetic normal and suspicious audio |
| `src/generate_test_samples.py` | Generates additional audio test samples |
| `src/mock_fan_malware.py` | Simulates fan-speed pulse patterns |
| `src/record_audio.py` | Records microphone audio |
| `src/analyze_data.py` | Analyses audio properties |
| `src/visualize_data.py` | Displays audio waveforms |
| `src/spectrogram.py` | Generates spectrograms |
| `src/bandpass_filter.py` | Applies bandpass filtering |
| `src/verify_filter.py` | Checks filtered signal energy |
| `src/anomaly_detector.py` | Implements an initial RMS-based detection approach |
| `src/frequency_detector.py` | Performs frequency-band anomaly detection |
| `src/cli_waterfall.py` | Displays the CLI spectrum waterfall |
| `src/dashboard_v2.py` | Provides the desktop dashboard |
| `src/performance_test.py` | Measures detection process execution time |
| `data/normal/` | Stores normal audio samples |
| `data/test/` | Stores suspicious and processed test samples |
| `data/raw/` | Stores recorded microphone audio |
| `docs/` | Stores project documentation |
| `logs/` | Reserved for project log files |

## 7. Current Limitations

- The current implementation is a software-only prototype.
- Synthetic signals are used to simulate normal and suspicious audio activity.
- Microphone recording uses a regular microphone.
- Actual RF signal monitoring has not been implemented.
- Raspberry Pi and HackRF SDR hardware integration has not been implemented.
- An ultrasonic microphone array has not been integrated.
- Physical server or rack localisation has not been validated.
- Live microphone waveform visualisation is implemented, but automatic live microphone anomaly detection has not yet been validated.
- Machine-learning-based anomaly detection has not yet been implemented.
- Detection results are based on a small simulated dataset.

## 8. Future Enhancements

The following features are planned for future development:

- Implement an autoencoder-based anomaly detection model.
- Train the model using normal signal data.
- Evaluate detection accuracy and false-positive rate using a larger dataset.
- Explore live microphone-based anomaly detection.
- Improve real-time spectrum and spectrogram visualisation.
- Implement timestamped anomaly logging.
- Explore Software Defined Radio (SDR) integration.
- Integrate suitable ultrasonic microphones.
- Investigate physical signal source localisation.
- Improve dashboard performance and usability.

## 9. Conclusion

AetherHound demonstrates a software-based approach to analysing audio signals and identifying unusual frequency patterns.

The current prototype includes synthetic signal generation, microphone recording, digital signal processing, frequency-based anomaly detection, CLI visualisation, and a desktop dashboard.

The project provides a foundation for future development involving machine learning, SDR hardware, and real-world signal monitoring.