# Time-Series & Signal Processing Tutorial (Deep, Detailed, and Practical)

This tutorial covers **core concepts of time-series analysis and signal processing**, especially for **sensor-data, IoT, vibration analysis, manufacturing, medical signals**, and **predictive maintenance**.

We cover:

* Sampling, aliasing
* Filters (low-pass, high-pass, band-pass)
* FFT (Fast Fourier Transform)
* STFT (Short-Time Fourier Transform)
* Wavelet Transform
* Spectral Analysis
* Denoising
* Rolling windows
* Segmentation
* Feature extraction (RMS, kurtosis, crest factor, etc.)

Practical examples are included using **NumPy**, **SciPy**, and **Python concepts**.

---

# 1. What is a Time-Series?

A **time-series** is a sequence of data points collected over time.
Examples:

* Vibration sensor data
* ECG signal
* Temperature recording
* Stock price movement
* Machine current & voltage

Two categories:

* **Continuous-time signals** (ideal, infinite resolution)
* **Discrete-time signals** (sampled signals from hardware)

---

# 2. Sampling and Aliasing

## 2.1 Sampling

Sampling converts a continuous analog signal into digital form.

Sampling frequency: `fs` (samples per second)

Nyquist theorem:

> The sampling frequency must be at least **2x higher than the highest frequency** in the signal.

Example:
If your machine vibration contains frequencies up to 5 kHz → fs must be at least 10 kHz.

## 2.2 Aliasing

Aliasing happens when the signal is **under-sampled**, causing:

* Distortion
* Wrong frequency interpretation

Solution:

* Increase sampling rate
* Use anti-alias low-pass filter

Example:
If fs = 100 Hz and your signal contains 80 Hz → aliasing occurs.

---

# 3. Fourier Transform (FFT)

FFT converts a signal from **time domain → frequency domain**.

Use cases:

* Vibration analysis
* Motor/rotor failure detection
* Frequency-based classification

## 3.1 FFT Concepts

* Magnitude spectrum → amplitude of frequencies
* Power spectral density (PSD)
* Frequency resolution = fs / N

## 3.2 Practical Example (Python)

```python
import numpy as np
import matplotlib.pyplot as plt

fs = 1000  # Sampling frequency
t = np.linspace(0, 1, fs, endpoint=False)

# Create a signal: 5 Hz + 50 Hz components
signal = np.sin(2*np.pi*5*t) + 0.5*np.sin(2*np.pi*50*t)

fft_vals = np.fft.fft(signal)
freqs = np.fft.fftfreq(len(signal), 1/fs)

plt.plot(freqs[:fs//2], np.abs(fft_vals)[:fs//2])
plt.title("FFT Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.show()
```

---

# 4. STFT (Short-Time Fourier Transform)

FFT gives global frequency info, but **cannot detect WHEN frequency changes occur**.

STFT solves this by applying FFT in sliding windows.

Use cases:

* Gearbox vibration monitoring
* Speech processing
* Transient events

## 4.1 How STFT Works

* Choose window size (e.g., 256 samples)
* Slide across the signal (e.g., hop=128)
* Compute FFT for each window

Result: **Time-frequency spectrogram**.

## 4.2 Practical Example

```python
from scipy.signal import stft

f, t, Zxx = stft(signal, fs, nperseg=256)

plt.pcolormesh(t, f, np.abs(Zxx))
plt.title("STFT Spectrogram")
plt.ylabel("Frequency (Hz)")
plt.xlabel("Time (sec)")
plt.show()
```

---

# 5. Wavelet Transform

Wavelets are better than STFT for **non-stationary** signals.
Used in:

* Fault detection
* EEG/ECG analysis
* Sudden machine failures

Wavelet transforms:

* CWT (Continuous Wavelet Transform)
* DWT (Discrete Wavelet Transform)

Wavelets provide **multi-resolution analysis**:

* High frequency → fine time resolution
* Low frequency → coarse time resolution

## 5.1 Python Example (PyWavelets)

```python
import pywt
import numpy as np

coeffs = pywt.wavedec(signal, 'db4', level=5)
```

---

# 6. Filtering (Low-pass, High-pass, Band-pass)

Filters remove unwanted frequencies.

## 6.1 Types of Filters

### Low-pass

Allows low frequency, blocks high frequency (good for noise removal).

### High-pass

Allows high frequency, blocks low (useful for removing drift).

### Band-pass

Allows only a specific band (e.g., 10–50 Hz).

### Band-stop

Blocks a specific band (e.g., 50 Hz power line noise).

## 6.2 Designing Filters in Python

### Example: Low-pass Butterworth Filter

```python
from scipy.signal import butter, filtfilt

fs = 1000
cutoff = 30  # 30 Hz low-pass

b, a = butter(4, cutoff/(fs/2), btype='low')
filtered = filtfilt(b, a, signal)
```

---

# 7. Rolling Windows & Sliding Segmentation

Used in time-series ML models.

## 7.1 Rolling Window Example

```python
import pandas as pd

ts = pd.Series(signal)
rms_rolling = ts.rolling(window=50).apply(lambda x: np.sqrt(np.mean(x**2)))
```

## 7.2 Segmentation for Machine Learning

Segment signal into fixed-size chunks.

```python
seg_size = 256
segments = []
for i in range(0, len(signal)-seg_size, seg_size):
    segments.append(signal[i:i+seg_size])
```

---

# 8. Feature Extraction

Used in ML/AI for classification.

## 8.1 RMS (Root Mean Square)

Energy of the signal.

```python
rms = np.sqrt(np.mean(signal**2))
```

## 8.2 Peak-to-Peak

```python
ptp = np.ptp(signal)
```

## 8.3 Kurtosis

Detects impulsive faults.

```python
from scipy.stats import kurtosis
kurt = kurtosis(signal)
```

## 8.4 Crest Factor

High crest → early bearing failure

```python
crest = np.max(np.abs(signal)) / rms
```

## 8.5 Spectral Features

Using FFT:

* Spectral centroid
* Band energy
* Dominant frequency

Example:

```python
dominant_freq = freqs[np.argmax(np.abs(fft_vals))]
```

---

# 9. Spectral Analysis

Used for vibration, acoustics, power systems.

### Power Spectral Density (PSD)

Shows signal energy vs frequency.

```python
from scipy.signal import welch

f, Pxx = welch(signal, fs)
plt.semilogy(f, Pxx)
```

Welch method reduces noise by segment averaging.

---

# 10. Denoising Techniques

## 10.1 Moving Average Filter

```python
window = 10
smooth = np.convolve(signal, np.ones(window)/window, mode='same')
```

## 10.2 Wavelet Denoising

```python
coeffs = pywt.wavedec(signal, 'db4', level=5)
thresh = 0.2*np.max(coeffs[1])
denoised = pywt.waverec([pywt.threshold(c, thresh) for c in coeffs], 'db4')
```

## 10.3 Savitzky–Golay Filter

Smooths without destroying peaks.

```python
from scipy.signal import savgol_filter
smooth = savgol_filter(signal, 51, 3)
```

---

# 11. Segmentation for Deep Learning

Segmentation into fixed windows for:

* CNN
* LSTM
* Transformer models

Example:

```
Window length: 2 seconds
Sampling rate: 1000 Hz
→ 2000 samples per segment
```

---

# 12. Recommended Libraries

* **NumPy** — FFT, numeric computations
* **SciPy** — STFT, filters, PSD
* **PyWavelets** — wavelet analysis
* **pandas** — rolling windows
* **matplotlib** — visualization

---

# 13. Real-World Use Cases

### Predictive Maintenance

* Bearing failures
* Gearbox wear
* Motor vibration

### Healthcare

* ECG peak detection
* EEG denoising

### Audio Processing

* Noise removal
* Speech spectrograms

### Structural Analysis

* Bridge vibration
* Earthquake detection

---

# 14. Summary

This tutorial covered:

* Sampling & aliasing
* FFT, STFT, Wavelet transform
* Filtering basics
* Feature extraction
* Denoising
* Segmentation & rolling windows
* Spectral analysis

If you want, I can also add:

* More advanced examples
* Real dataset analysis
* Full predictive-maintenance ML pipeline
* Interview questions on signal processing
Here’s a full, end-to-end view of what you asked for, in a practical “you can code this” style:

---

## 1. Full Vibration-Analysis ML Pipeline

(FFT → Features → Classifier)

We’ll imagine a typical **bearing fault detection** scenario:

* You have a vibration sensor on a rotating machine.
* You want to classify:
  **Class 0 = healthy**, **Class 1 = faulty**.

We’ll walk through:

1. Simulating vibration signals (healthy vs faulty)
2. Windowing / segmentation
3. FFT and feature extraction
4. Building a classifier (e.g. RandomForest)
5. Evaluating the model

I’ll show Python-style pseudocode that you could run with `numpy`, `scipy`, `scikit-learn`.

---

### 1.1 Simulate Vibration Data (for learning / testing concepts)

In real life, you’d replace this with **real sensor data** (CSV, binary, etc.).
For now, simulate:

* Healthy: mostly smooth sinusoid + small noise
* Faulty: same sinusoid + high-frequency impulses (fault signatures)

```python
import numpy as np

fs = 10000  # 10 kHz sampling frequency
duration = 1.0  # 1 second per sample
N = int(fs * duration)
t = np.linspace(0, duration, N, endpoint=False)

def simulate_healthy(n_samples=100):
    signals = []
    for _ in range(n_samples):
        base_freq = 50  # 50 Hz vibration
        sig = np.sin(2*np.pi*base_freq*t)
        sig += 0.1 * np.random.randn(N)  # small noise
        signals.append(sig)
    return np.array(signals)

def simulate_faulty(n_samples=100):
    signals = []
    for _ in range(n_samples):
        base_freq = 50
        sig = np.sin(2*np.pi*base_freq*t)
        sig += 0.1 * np.random.randn(N)
        # add impulses to mimic bearing fault
        num_impulses = 10
        idx = np.random.randint(0, N, size=num_impulses)
        sig[idx] += np.random.uniform(3, 5, size=num_impulses)
        signals.append(sig)
    return np.array(signals)

X_healthy = simulate_healthy(200)
X_faulty = simulate_faulty(200)

y_healthy = np.zeros(len(X_healthy))
y_faulty = np.ones(len(X_faulty))

X = np.vstack([X_healthy, X_faulty])   # shape: (400, N)
y = np.concatenate([y_healthy, y_faulty])
```

This gives you a dataset of 400 vibration segments, 1 second each.

---

### 1.2 Windowing / Segmentation (optional but common)

Often you have **long recordings** (minutes/hours). You then:

* Split into smaller windows (e.g. 0.5 s, 1 s, 2 s)
* Treat each window as one “sample”

In our simulated example, each signal is already one window. For real data:

```python
def segment_signal(sig, window_size, step_size):
    segments = []
    for start in range(0, len(sig) - window_size + 1, step_size):
        segments.append(sig[start:start+window_size])
    return np.array(segments)
```

---

### 1.3 Feature Extraction from Each Segment

For each 1-second segment, we’ll extract:

**Time-domain features:**

* RMS
* Standard deviation
* Peak-to-peak
* Kurtosis
* Crest factor

**Frequency-domain features (via FFT):**

* Dominant frequency
* Spectral centroid
* Band energy (e.g. 200–1000 Hz)

Let’s define helpers.

```python
from scipy.stats import kurtosis
from scipy.signal import welch

def compute_time_features(x):
    rms = np.sqrt(np.mean(x**2))
    std = np.std(x)
    ptp = np.ptp(x)  # peak to peak
    kurt = kurtosis(x)
    crest_factor = np.max(np.abs(x)) / (rms + 1e-12)
    return [rms, std, ptp, kurt, crest_factor]

def compute_freq_features(x, fs):
    # use Welch's method for robust spectral estimate
    f, Pxx = welch(x, fs=fs, nperseg=1024)

    # dominant frequency
    dom_freq = f[np.argmax(Pxx)]

    # spectral centroid (weighted average of frequencies)
    spectral_centroid = np.sum(f * Pxx) / (np.sum(Pxx) + 1e-12)

    # band energy between 200 and 1000 Hz
    band_mask = (f >= 200) & (f <= 1000)
    band_energy = np.sum(Pxx[band_mask])

    return [dom_freq, spectral_centroid, band_energy]

def extract_features(signals, fs):
    features = []
    for x in signals:
        f_time = compute_time_features(x)
        f_freq = compute_freq_features(x, fs)
        features.append(f_time + f_freq)
    return np.array(features)

X_feat = extract_features(X, fs)
print(X_feat.shape)  # (400, 5+3) = (400, 8) features
```

Now you’ve turned raw time-series into **feature vectors**.

---

### 1.4 Train a Classifier (RandomForest example)

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

X_train, X_test, y_train, y_test = train_test_split(
    X_feat, y, test_size=0.2, random_state=42, stratify=y
)

clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    random_state=42
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
```

If the features are informative, you’ll see high accuracy even with this simple setup.

---

### 1.5 Possible Pipeline Improvements

Real-world enhancements:

* Normalize/standardize features (`StandardScaler`)
* Use cross-validation (`StratifiedKFold`)
* Try models like XGBoost, SVM, LightGBM
* Add more features:

  * Envelope analysis
  * Harmonic amplitudes (e.g. amplitude at multiples of rotation speed)
  * Wavelet-based features
* Add **multi-class**: healthy, outer race fault, inner race fault, misalignment, looseness etc.

---

## 2. Sensor Noise Modeling

In real vibration systems, sensor data is **never clean**.
Noise can come from:

* Sensor electronics
* Environment
* Mechanical coupling
* Interference (e.g. 50/60 Hz power)

We’ll look at:

1. Types of noise
2. Simple mathematical models
3. Simulation examples
4. How to mitigate noise

---

### 2.1 Common Types of Sensor Noise

1. **Additive White Gaussian Noise (AWGN)**

   * Noise ~ N(0, σ²)
   * “White” = equal power at all frequencies
   * Good generic model for many sensors

2. **Colored noise (1/f, pink noise, etc.)**

   * Power depends on frequency
   * Some sensors show more low-frequency noise (drift)

3. **Quantization noise**

   * Due to ADC (analog-to-digital conversion)
   * Resolution limited by number of bits

4. **Line / mains interference**

   * 50 Hz or 60 Hz + its harmonics

5. **Mechanical / environmental noise**

   * Background vibrations from other machines

---

### 2.2 Modeling Additive Gaussian Noise

You often model:

[
x_{\text{noisy}}(t) = x_{\text{true}}(t) + n(t)
]

with `n(t) ~ N(0, σ²)`

```python
def add_awgn(signal, snr_db):
    # snr_db: desired signal-to-noise ratio in dB
    signal_power = np.mean(signal**2)
    snr_linear = 10**(snr_db / 10)
    noise_power = signal_power / snr_linear
    noise = np.sqrt(noise_power) * np.random.randn(*signal.shape)
    return signal + noise

clean = np.sin(2*np.pi*50*t)
noisy = add_awgn(clean, snr_db=10)  # 10 dB SNR
```

---

### 2.3 Modeling Quantization Noise (ADC)

ADC with `n_bits` → discrete levels.

```python
def quantize(signal, n_bits, v_min=-1.0, v_max=1.0):
    levels = 2**n_bits
    step = (v_max - v_min) / levels
    # clip to range
    s_clipped = np.clip(signal, v_min, v_max)
    # map to integer levels
    q = np.round((s_clipped - v_min) / step)
    # back to continuous
    s_quantized = q * step + v_min
    return s_quantized

sig = np.sin(2*np.pi*50*t)
sig_q = quantize(sig, n_bits=8)
```

This shows how a low-resolution sensor might distort the signal.

---

### 2.4 Modeling 50 Hz / 60 Hz Interference

```python
power_freq = 50  # or 60
interference = 0.2 * np.sin(2*np.pi*power_freq*t)
noisy = clean + interference + 0.05 * np.random.randn(len(clean))
```

You can then apply a **notch filter** to remove it.

```python
from scipy.signal import iirnotch, filtfilt

fs = 1000
f0 = 50  # interference frequency
Q = 30   # quality factor

b, a = iirnotch(f0, Q, fs)
cleaned = filtfilt(b, a, noisy)
```

---

### 2.5 Modeling Drift / Low-Frequency Noise

Low-frequency drift can be modeled with a very low-frequency sinusoid or random walk:

```python
# slow drift (0.1 Hz)
drift = 0.5 * np.sin(2*np.pi*0.1*t)
noisy = clean + drift + 0.05 * np.random.randn(len(clean))
```

Often removed with **high-pass filtering**.

---

### 2.6 Noise Mitigation Techniques in Practice

1. **Hardware level**

   * Shielding, grounding
   * Better cabling
   * Higher quality sensors & ADCs
   * Anti-aliasing filters

2. **Signal processing level**

   * Low-pass filtering
   * Band-pass around known fault frequencies
   * Notch filtering (50/60 Hz)
   * Wavelet denoising
   * Ensemble averaging (if repeated measurements exist)

3. **Feature robustness**

   * Use features that are less sensitive to noise (e.g. energy in band, not individual samples)
   * Use robust statistics (median, trimmed mean)

4. **ML model robustness**

   * Train with noisy data (data augmentation with synthetic noise)
   * Regularization
   * Use ensembles

---

### 2.7 Example: Training with Noise-Augmented Data

You can improve robustness by **adding synthetic noise to training signals**:

```python
def augment_with_noise(signals, snr_db_list=[5, 10, 20]):
    aug_signals = []
    for x in signals:
        for snr in snr_db_list:
            aug_signals.append(add_awgn(x, snr))
    return np.array(aug_signals)

X_healthy_aug = augment_with_noise(X_healthy)
X_faulty_aug = augment_with_noise(X_faulty)

# combine original + augmented, then extract features and train again
```

This helps the classifier learn to ignore moderate noise and still detect faults.

---

## 3. How These Pieces Fit Together in a Real Project

A realistic **vibration-analysis ML system** might look like this:

1. **Data Acquisition Layer**

   * Accelerometers → DAQ → sampled at fs (e.g. 25 kHz)
   * Saved in files or sent via network

2. **Preprocessing**

   * Remove DC offset / drift
   * Anti-alias and band-pass filter around bearing fault frequencies
   * Resample if needed

3. **Segmentation**

   * Fixed time windows (e.g. 1 second)
   * Or rotation-synchronous windowing (per shaft revolution)

4. **Feature Extraction**

   * Time domain: RMS, kurtosis, crest, skewness
   * Frequency domain: band energies, dominant peaks, harmonics
   * Envelope spectra, wavelet features

5. **Noise Modeling / Augmentation**

   * Train models with added synthetic noise
   * Evaluate robustness under different SNR conditions

6. **Classifier / Regressor**

   * For classification: healthy / faulty / fault type
   * For regression: remaining useful life (RUL) or degradation index

7. **Deployment**

   * Run pipeline in real-time or batch
   * Alert thresholds, dashboards, logging

---

If you want, next I can:

* Turn this into a **step-by-step code notebook design**
* Show a **full PyTorch / TensorFlow deep learning version** (CNN on raw vibration)
* Give you **interview-style questions** about vibration analysis & signal processing.
Below is a **complete set of interview-style questions for Vibration Analysis, Time-Series, and Signal Processing**, each with **clear and professional answers**.
These cover **sensor engineering, predictive maintenance, signal processing, classical vibration analysis, and ML for vibration data**.

I split them into:

---

# 🔷 **Section A — Fundamentals of Vibration Analysis (Beginner)**

# 🔶 **Section B — Signal Processing & Frequency-Domain (Intermediate)**

# 🔵 **Section C — Machine Learning for Vibration Data (Advanced)**

# 🟥 **Section D — Real-World Predictive Maintenance Questions**

# 🟣 **Section E — Practical/Hands-On Questions**

---

# 🔷 **SECTION A — BASIC VIBRATION ANALYSIS (Beginner-Level)**

---

### **Q1. What is vibration analysis? Why is it used?**

**Answer:**
Vibration analysis involves measuring oscillations of machines or structures to detect abnormalities such as imbalance, misalignment, wear, looseness, or bearing damage.
It is widely used in predictive maintenance to:

* Identify early faults
* Reduce downtime
* Extend machine life
* Avoid catastrophic failures

---

### **Q2. What sensor is commonly used for vibration analysis and why?**

**Answer:**
The **accelerometer** is the most widely used sensor because:

* It detects vibration in the form of acceleration (g or m/s²)
* High bandwidth (can detect frequencies up to several kHz)
* High sensitivity
* Low noise
* Good for rotating machinery

---

### **Q3. What is the difference between displacement, velocity, and acceleration vibration measurements?**

| Quantity     | Use Case                             | Advantage                      |
| ------------ | ------------------------------------ | ------------------------------ |
| Displacement | Low-frequency faults, shaft movement | Good for misalignment          |
| Velocity     | General machine health               | Directly relates to energy     |
| Acceleration | High-frequency faults (bearings)     | Most sensitive to early faults |

---

### **Q4. What is sampling frequency?**

**Answer:**
Sampling frequency (fs) is the number of samples per second collected from the sensor.

Example:
fs = 10,000 Hz → 10,000 samples per second.

---

### **Q5. What is Nyquist frequency?**

**Answer:**
Nyquist frequency = fs / 2
It represents the highest frequency that can be measured without aliasing.

---

### **Q6. What is aliasing?**

**Answer:**
Aliasing occurs when the sampling frequency is too low, causing high-frequency components to appear as false low-frequency components.
Solution:

* Use fs ≥ 2 × max frequency
* Use anti-aliasing low-pass filters

---

# 🔶 **SECTION B – SIGNAL PROCESSING & FREQUENCY DOMAIN (Intermediate)**

---

### **Q7. What is FFT and why is it used in vibration analysis?**

**Answer:**
FFT (Fast Fourier Transform) converts a signal from time domain → frequency domain.
It is used to identify:

* Dominant frequencies
* Harmonics
* Bearing fault frequencies
* Gear mesh frequencies
* Imbalance, misalignment, looseness

---

### **Q8. What is STFT? When is it useful?**

**Answer:**
STFT (Short-Time Fourier Transform) provides **time-frequency** information by applying FFT over sliding windows.

Useful for:

* Detecting transient events
* Tool breakage
* Bearing impacts
* Sudden structural changes

---

### **Q9. What is a spectrogram?**

**Answer:**
A graphical representation of frequencies over time (output of STFT).
It shows:

* How frequencies evolve
* Energy at each frequency
* Fault progression
* Transients

---

### **Q10. What are high-pass, low-pass, and band-pass filters?**

**Answer:**

* **Low-pass**: removes high-frequency noise
* **High-pass**: removes low-frequency drift
* **Band-pass**: isolates a frequency band (e.g., bearing frequencies)

Example:
Band-pass 500–2000 Hz to isolate bearing impacts.

---

### **Q11. What is envelope analysis? Why is it important?**

**Answer:**
Envelope analysis extracts the **amplitude modulation** of high-frequency signals caused by bearing faults.

Used for:

* Bearing outer race faults
* Ball passing frequencies
* Impacts & impulses

It makes weak bearing fault signatures clearly visible.

---

### **Q12. What is PSD (Power Spectral Density)?**

**Answer:**
PSD shows power distribution of a signal over frequency, often using Welch’s method.

Benefits:

* Reduces noise
* Improves frequency accuracy
* Good for diagnostics

---

### **Q13. What are common spectral features in vibration analysis?**

* Dominant frequency
* Harmonic amplitudes
* Band energy
* Spectral centroid
* Peak frequency
* RMS of specific bands

---

### **Q14. What is kurtosis? Why is it important?**

**Answer:**
Kurtosis measures impulsiveness of a signal.

High kurtosis = many sharp impacts → possible bearing defect or gear fault.

---

### **Q15. What is crest factor?**

**Answer:**
Crest factor = peak amplitude / RMS
High crest factor indicates:

* Strong impacts
* Bearing pitting
* Shaft looseness

---

# 🔵 **SECTION C — MACHINE LEARNING FOR VIBRATION DATA (Advanced)**

---

### **Q16. Which ML algorithms are commonly used for vibration fault classification?**

* Random Forest
* SVM
* Gradient Boosted Trees (XGBoost, LightGBM)
* CNNs for raw vibration
* LSTM/GRU for sequential modeling
* Transformers for time-series

---

### **Q17. Should raw vibration signals be fed directly into ML models?**

**Answer:**
Yes, but only for **deep learning** (CNNs, LSTMs).
Traditional ML requires **feature extraction** first:

* RMS
* Kurtosis
* Frequency peaks
* Envelope spectrum features

---

### **Q18. Why is windowing important in machine learning?**

**Answer:**
Windowing breaks a long signal into smaller segments (e.g., 1-second windows).
Each window becomes one training sample.

Benefits:

* More training samples
* Better temporal resolution
* Fault detection becomes real-time

---

### **Q19. How do you handle noise during training?**

**Answer:**
Techniques:

* Add synthetic Gaussian noise (data augmentation)
* Apply filtering before training
* Use robust features
* Use denoising autoencoders (deep learning)

---

### **Q20. What are typical features for bearing fault diagnosis?**

* RMS
* Kurtosis
* Crest factor
* Clearance impacts
* Envelope spectral peaks
* Ball pass frequencies
* Gear mesh harmonics

---

### **Q21. What is the challenge with highly imbalanced datasets?**

**Answer:**
Most machines are “healthy” most of the time.
Fault data is limited.

Solutions:

* Oversampling
* Data augmentation
* Synthetic faults
* Generative models (GANs)
* Anomaly detection models

---

# 🟥 **SECTION D — REAL-WORLD PREDICTIVE MAINTENANCE QUESTIONS**

---

### **Q22. What are typical fault frequencies for bearings?**

* BPFO = Ball Pass Frequency Outer
* BPFI = Ball Pass Frequency Inner
* BSF = Ball Spin Frequency
* FTF = Fundamental Train Frequency

They depend on bearing geometry.

---

### **Q23. How do you detect shaft imbalance?**

Symptoms:

* Strong peak at **1× rotation frequency**
* Stable amplitude
* Phase typically constant

---

### **Q24. How do you detect misalignment?**

Indicators:

* Harmonics: 1×, 2×, 3× frequencies
* High axial vibration

---

### **Q25. How do you detect looseness?**

Indicators:

* Multiple harmonics
* Nonlinear behavior
* Peaks at high multiples (5×, 6×, 7×)

---

### **Q26. What environmental factors can corrupt sensor measurements?**

* Electromagnetic interference
* Mounting issues
* Temperature drift
* Repeated impacts
* Mechanical coupling from nearby machines

---

### **Q27. What is a synchronous time averaging (STA)?**

**Answer:**
STA removes random noise and enhances periodic components by averaging vibration signals over shaft revolutions.

Used in gear diagnostics.

---

### **Q28. What is a waterfall plot?**

Shows vibration spectra at increasing speeds during a run-up test.

Used for:

* Resonance detection
* Speed-dependent faults

---

### **Q29. Why do we prefer accelerometers for bearing diagnostics?**

Because bearing faults generate **high-frequency impacts**, and accelerometers capture high-frequency content better than velocity sensors.

---

### **Q30. What are the challenges of real-time vibration monitoring?**

* High data rate (kHz sampling)
* Noise
* Memory load
* Real-time feature extraction
* Sensor placement limitations
* Hardware constraints

---

# 🟣 **SECTION E — PRACTICAL / HANDS-ON QUESTIONS**

---

### **Q31. How do you remove 50/60 Hz mains interference?**

Use a notch filter:

```python
from scipy.signal import iirnotch, filtfilt
b, a = iirnotch(50, 30, fs)
clean = filtfilt(b, a, signal)
```

---

### **Q32. How do you compute the dominant frequency?**

```python
freqs = np.fft.fftfreq(N, 1/fs)
dom_freq = freqs[np.argmax(abs_fft)]
```

---

### **Q33. How do you compute the envelope spectrum?**

Steps:

1. Band-pass the signal
2. Compute analytic signal via Hilbert Transform
3. FFT of the envelope

---

### **Q34. How do you implement a low-pass filter?**

```python
from scipy.signal import butter, filtfilt
b, a = butter(4, cutoff/(fs/2), 'low')
filtered = filtfilt(b, a, signal)
```

---

### **Q35. What is the purpose of time-synchronization in vibration signals?**

To align data to machine rotation so that:

* Impacts line up in cycles
* Phase is consistent
* Spectral analysis improves

---

### **Q36. How do you compute kurtosis and crest factor?**

```python
from scipy.stats import kurtosis
k = kurtosis(x)
crest = np.max(np.abs(x)) / (np.sqrt(np.mean(x**2)))
```

---

### **Q37. How do you implement an STFT?**

```python
from scipy.signal import stft
f, t, Zxx = stft(x, fs, nperseg=256)
```

---

### **Q38. What is Welch’s method for PSD and why is it used?**

It averages FFTs from overlapping windows to reduce noise.
More stable than raw FFT.

```python
f, Pxx = welch(x, fs)
```

---

### **Q39. How do you detect impulses in a vibration signal?**

Methods:

* Thresholding
* Wavelet transform
* Short-time kurtosis
* Peak detection

---

### **Q40. How to detect slowly growing faults?**

Techniques:

* Trend of RMS
* Trend of kurtosis
* Spectral peak tracking
* Rolling statistics
* Machine learning anomaly detection

---

# 🎉 Done!

You now have **40 detailed interview questions with answers** covering vibration analysis, signal processing, ML, and predictive maintenance.

If you want, I can also provide:

✅ Practical coding assignments (FFT, STFT, envelope analysis)
✅ A full predictive-maintenance ML project using real bearing datasets (Case Western, NASA IMS)
✅ Signal processing cheat sheet
Just tell me!
Nice, let’s build a *real* predictive-maintenance project outline you could actually implement with the **Case Western Reserve University (CWRU)** and **NASA IMS** bearing datasets. I’ll structure it like a real-world project you’d show in a portfolio or interview.

I’ll focus on:

1. **Project goal & setup**
2. **Data overview: CWRU & NASA IMS**
3. **Preprocessing pipeline**
4. **Feature engineering (time + frequency)**
5. **ML modeling (classification + RUL idea)**
6. **Evaluation & monitoring**
7. **How to structure this as a clean project**

I’ll write code-style snippets in Python (using `numpy`, `pandas`, `scipy`, `scikit-learn`, and optionally `pywt` for wavelets).

---

## 1. Project Goal & Setup

**Goal (high-level):**

> Build a predictive-maintenance ML pipeline that can:
>
> * Detect bearing faults (classification: healthy vs fault types) using CWRU, and
> * Model degradation / Remaining Useful Life (RUL) using NASA IMS (time-to-failure trend).

**Technologies:**

* Python 3.x
* `numpy`, `pandas`
* `scipy` (signal processing)
* `scikit-learn` (classical ML)
* `matplotlib`, `seaborn` (plots)
* Optionally: `pywt` (wavelets), `xgboost`, `pytorch` / `tensorflow` if you go deep learning.

---

## 2. Data Overview

### 2.1 CWRU Bearing Dataset (Classification-focused)

* Collected from a bearing test rig with:

  * Motor, torque transducer, dynamometer.
* Faults introduced via EDM (electrical discharge machining):

  * Inner race fault
  * Outer race fault
  * Ball fault
  * Different fault sizes (e.g., 0.007", 0.014", 0.021")
* Different loads (0/1/2/3 HP).
* Vibration data from accelerometers near the bearings.
* Data files are usually `.mat` (MATLAB) with channels like `X1797_DE_time`, etc.

**Typical labels you create:**

```text
0 = healthy  
1 = inner race fault  
2 = outer race fault  
3 = ball fault
```

### 2.2 NASA IMS Bearing Dataset (Degradation / RUL-focused)

* Test rigs with bearings run until failure.
* Vibration data recorded over days, with failures at the end of each run.
* Three datasets (each test with 4 bearings).
* RUL tasks:

  * Predict time to failure
  * Detect anomaly onset

Here the label is not directly “class”, but more like:

* Time index (cycles),
* or derived RUL: `RUL = t_failure - t_current`.

---

## 3. Data Loading & Preprocessing

### 3.1 Project Structure

A clean project structure:

```text
bearing-pdm/
  data/
    cwru/
    nasa_ims/
  src/
    data_loading.py
    preprocessing.py
    features.py
    models.py
    train_cwru_classifier.py
    train_nasa_rul.py
  notebooks/
    01_explore_cwru.ipynb
    02_explore_nasa.ipynb
  README.md
```

### 3.2 Loading CWRU (.mat) Files

You’ll use `scipy.io.loadmat`:

```python
from scipy.io import loadmat
import numpy as np
import glob

def load_cwru_file(path, label):
    mat = loadmat(path)
    # key names differ; you inspect one file first in a notebook
    key = [k for k in mat.keys() if 'DE_time' in k][0]
    signal = mat[key].ravel()
    return signal, label

def load_cwru_dataset(base_dir):
    X_signals = []
    y_labels = []

    # Example: healthy files
    for file in glob.glob(base_dir + "/normal/*.mat"):
        sig, lab = load_cwru_file(file, label=0)
        X_signals.append(sig)
        y_labels.append(lab)

    # inner race faults:
    for file in glob.glob(base_dir + "/inner/*.mat"):
        sig, lab = load_cwru_file(file, label=1)
        X_signals.append(sig)
        y_labels.append(lab)

    # outer race:
    for file in glob.glob(base_dir + "/outer/*.mat"):
        sig, lab = load_cwru_file(file, label=2)
        X_signals.append(sig)
        y_labels.append(lab)

    # ball fault:
    for file in glob.glob(base_dir + "/ball/*.mat"):
        sig, lab = load_cwru_file(file, label=3)
        X_signals.append(sig)
        y_labels.append(lab)

    return X_signals, np.array(y_labels)
```

### 3.3 Segmenting into Windows

Recordings are long, so you break them into windows (e.g. 1-second windows).

```python
def segment_signal(sig, window_size, step_size):
    segments = []
    for start in range(0, len(sig) - window_size + 1, step_size):
        segments.append(sig[start:start+window_size])
    return np.array(segments)

def segment_all(signals, labels, fs, window_sec=0.2, overlap=0.5):
    window_size = int(fs * window_sec)
    step_size = int(window_size * (1 - overlap))
    X_seg = []
    y_seg = []
    for sig, lab in zip(signals, labels):
        segs = segment_signal(sig, window_size, step_size)
        X_seg.append(segs)
        y_seg.append(np.full(len(segs), lab))
    return np.vstack(X_seg), np.concatenate(y_seg)
```

You’ll need `fs` (sampling frequency) from dataset docs (e.g., 12 kHz or 48 kHz depending on file).

---

## 4. Feature Engineering

We want robust, well-known features for vibration PDM.

### 4.1 Time-Domain Features (per window)

* mean
* std
* RMS
* skewness
* kurtosis
* peak-to-peak
* crest factor
* shape factor, impulse factor (optional)

```python
import numpy as np
from scipy.stats import skew, kurtosis

def time_features(x):
    rms = np.sqrt(np.mean(x**2))
    return [
        np.mean(x),
        np.std(x),
        rms,
        skew(x),
        kurtosis(x),
        np.ptp(x),  # peak-to-peak
        np.max(np.abs(x)) / (rms + 1e-12),  # crest factor
    ]
```

### 4.2 Frequency-Domain Features (FFT / PSD)

Using Welch:

```python
from scipy.signal import welch

def freq_features(x, fs):
    f, Pxx = welch(x, fs=fs, nperseg=1024)
    # Dominant frequency
    dom_freq = f[np.argmax(Pxx)]
    # Spectral centroid
    spectral_centroid = np.sum(f * Pxx) / (np.sum(Pxx) + 1e-12)
    # Band energies (e.g. 1–3 kHz, 3–6 kHz, etc.)
    def band_energy(fmin, fmax):
        idx = (f >= fmin) & (f <= fmax)
        return np.sum(Pxx[idx])
    band1 = band_energy(0, fs/8)
    band2 = band_energy(fs/8, fs/4)
    band3 = band_energy(fs/4, fs/2)
    return [dom_freq, spectral_centroid, band1, band2, band3]
```

### 4.3 Combine Features

```python
def extract_features_from_segments(X_seg, fs):
    feat_list = []
    for x in X_seg:
        feats_t = time_features(x)
        feats_f = freq_features(x, fs)
        feat_list.append(feats_t + feats_f)
    return np.array(feat_list)
```

Now you have feature matrix:
`X_feat.shape = (num_segments, num_features)` and labels `y_seg`.

---

## 5. ML Modeling for CWRU (Classification)

### 5.1 Train/Test Split

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X_feat, y_seg, test_size=0.2, random_state=42, stratify=y_seg
)
```

### 5.2 Standardization

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)
```

### 5.3 Train a Classifier (Random Forest / XGBoost)

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

clf = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    class_weight='balanced',
    random_state=42
)
clf.fit(X_train_sc, y_train)

y_pred = clf.predict(X_test_sc)

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
```

You can then log:

* Accuracy
* Macro F1
* Per-class recall (important for minority fault classes)

### 5.4 Optional: Deep Learning on Raw Vibration (Short version)

You can also feed raw windows into a 1D CNN:

* Input shape: `(window_size, 1)`
* Conv1D → ReLU → MaxPool → Dense → Softmax

That’s a great “bonus” section if you’re interviewing for ML / DL roles.

---

## 6. NASA IMS: RUL / Degradation Modeling

NASA IMS is more involved, but a good high-level approach:

### 6.1 Idea

* Data is recorded at regular intervals (e.g. once per minute).
* Bearing runs from healthy → failure.
* Define RUL per time index:

  ```text
  RUL(t) = t_failure - t
  ```

You treat each vibration snapshot as one sample with an RUL label.

### 6.2 Preprocessing Flow

Per bearing:

1. Load each vibration file / snapshot into an array.
2. For each snapshot, extract same features as above (time + frequency-domain).
3. Create a dataframe with:

   * `cycle` (time index)
   * extracted features
   * `RUL` or `degradation_index`

Example:

```python
import pandas as pd

def build_nasa_bearing_df(file_paths, fs, failure_cycle):
    rows = []
    for cycle, path in enumerate(sorted(file_paths)):
        signal = np.loadtxt(path)  # or appropriate loader
        feats = time_features(signal) + freq_features(signal, fs)
        rul = failure_cycle - cycle
        rows.append({"cycle": cycle, "RUL": rul, **{f"feat_{i}": v for i, v in enumerate(feats)}})
    return pd.DataFrame(rows)
```

### 6.3 Modeling RUL

Now this becomes a **regression** problem:

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

feature_cols = [c for c in df.columns if c.startswith("feat_")]
X = df[feature_cols].values
y = df["RUL"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

reg = GradientBoostingRegressor(random_state=42)
reg.fit(X_train, y_train)

y_pred = reg.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print("RMSE:", rmse)
```

You can also:

* Convert RUL to discrete classes (e.g. “healthy / warning / critical”).
* Use time-series models (LSTM, temporal CNN).

---

## 7. Sensor Noise & Robustness (Optional but Impressive)

You can improve realism by:

* Adding synthetic noise during training (data augmentation)
* Testing performance at different SNR levels
* Comparing models with and without filtering

E.g.:

```python
def add_awgn(x, snr_db):
    power = np.mean(x**2)
    snr_lin = 10**(snr_db/10)
    noise_power = power / snr_lin
    noise = np.sqrt(noise_power) * np.random.randn(*x.shape)
    return x + noise
```

You can augment each segment with different noise levels and retrain.

---

## 8. Evaluation & Visualization

Things to plot and show in your project:

* Raw signal vs filtered signal
* FFT spectrum for healthy vs faulty
* Histogram of features (e.g. kurtosis distributions per class)
* Confusion matrix for CWRU classifier
* RUL prediction vs true RUL for NASA IMS (line plot)
* Feature importance from RandomForest / XGBoost

Example: feature importance:

```python
import matplotlib.pyplot as plt
import numpy as np

importances = clf.feature_importances_
idx = np.argsort(importances)[::-1]
plt.bar(range(len(importances)), importances[idx])
plt.xticks(range(len(importances)), np.array(feature_cols)[idx], rotation=90)
plt.tight_layout()
plt.show()
```

---

## 9. How to Present This as a Portfolio Project

In your **README.md**, you should highlight:

* **Problem statement:** Predict bearing faults and bearing life using real datasets.
* **Datasets:** CWRU (classification) + NASA IMS (RUL regression).
* **Pipeline:**

  * Sampling & segmentation
  * Signal processing (FFT, Welch, maybe envelope / wavelet)
  * Feature extraction
  * ML modeling (RandomForest, GradientBoosting, etc.)
  * Evaluation and key metrics
* **Results:**

  * Classification accuracy / F1-scores on CWRU
  * RMSE / MAE for RUL on NASA IMS
* **Extensions:**

  * CNN on raw signals
  * Deployment idea (real-time edge monitoring)
  * Noise robustness experiments

This looks extremely strong in interviews, especially for:

* Data scientist / ML engineer roles in industrial / IoT / automotive
* Reliability / condition-monitoring / predictive maintenance roles
* Any role involving **time-series + sensors**.

---

If you want, I can next:

* Help you write the **actual code structure** (with function signatures)
* Draft a **professional README** for this project
* Add **interview-style explanations** for each step so you can explain it confidently.
Your full KONUX domain tutorial is ready!
If you want, I can also create:

✅ KONUX-style interview questions (with ideal answers)
✅ A signal-processing + ML pipeline specifically for railway switches
✅ A cheat sheet for KONUX-style predictive maintenance
✅ Practical coding exercises for each section
Just let me know!
Nice, this is exactly the kind of preparation that makes you dangerous in a KONUX-style interview 😄
I’ll give you three things:

1. **Code examples for each major section** (synthetic switch data, preprocessing, features, noise/missing data handling)
2. **ML models for switch anomaly detection** (Isolation Forest + Autoencoder)
3. **A KONUX-focused interview Q&A set** with good, concise answers you can adapt

Everything will be Python-style and oriented around **railway switch vibration / acceleration data**.

---

## 1. Code Examples for Each Section

### 1.1 Simulating Switch Acceleration Data (Normal vs Degraded)

In reality you’d read from sensors, but for practice & portfolio you can simulate:

* Normal switch actuation = smooth motion + characteristic impact at closure
* Degraded switch = higher friction (longer duration, more noise, extra impacts)

```python
import numpy as np

fs = 2000  # 2 kHz sampling rate
T = 2.0    # 2 seconds per switching event
N = int(fs * T)
t = np.linspace(0, T, N, endpoint=False)

def simulate_switch_event(health="normal"):
    # Base low-frequency motion (e.g. motor movement)
    base = 0.5 * np.sin(2 * np.pi * 2 * t)  # 2 Hz component

    # Impact when rail locks into place (short, sharp pulse)
    impact_center = int(1.2 * fs)  # around 1.2s
    impact = np.zeros_like(t)
    width = int(0.02 * fs)  # 20 ms pulse

    impact[impact_center:impact_center+width] = np.hanning(width) * 5.0

    # Noise
    noise_level = 0.1 if health == "normal" else 0.25
    noise = noise_level * np.random.randn(N)

    # Extra effects for degraded case
    if health == "degraded":
        # Slightly longer and more “ringing” after impact
        ringing = 0.8 * np.sin(2 * np.pi * 80 * t) * np.exp(-5 * (t - 1.2).clip(min=0))
    else:
        ringing = 0.4 * np.sin(2 * np.pi * 80 * t) * np.exp(-7 * (t - 1.2).clip(min=0))

    sig = base + impact + ringing + noise
    return sig

normal_signal = simulate_switch_event("normal")
degraded_signal = simulate_switch_event("degraded")
```

You can plot them with matplotlib to visually see the difference.

---

### 1.2 Preprocessing: Filtering, Detrending, Segmentation

#### Low-pass / Band-pass Filtering

```python
from scipy.signal import butter, filtfilt

def butter_bandpass(low, high, fs, order=4):
    nyq = fs / 2
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return b, a

def apply_bandpass(x, low=5, high=500, fs=2000):
    b, a = butter_bandpass(low, high, fs)
    return filtfilt(b, a, x)

filtered_normal = apply_bandpass(normal_signal, 5, 400, fs)
```

#### Segmentation into Windows (e.g. for ML)

For switches, often one *event* (one throw) is one window. For more granular analysis, you can split into sub-windows:

```python
def sliding_windows(x, window_size, step):
    segments = []
    for start in range(0, len(x) - window_size + 1, step):
        segments.append(x[start:start+window_size])
    return np.array(segments)

win_size = int(0.25 * fs)  # 250 ms
step = int(0.1 * fs)       # 100 ms
segments = sliding_windows(filtered_normal, win_size, step)
```

---

### 1.3 Feature Extraction (Time, Frequency, Time-Frequency)

#### Time-Domain Features

```python
from scipy.stats import skew, kurtosis

def time_features(x):
    rms = np.sqrt(np.mean(x**2))
    return {
        "mean": np.mean(x),
        "std": np.std(x),
        "rms": rms,
        "skew": skew(x),
        "kurtosis": kurtosis(x),
        "ptp": np.ptp(x),
        "crest_factor": np.max(np.abs(x)) / (rms + 1e-12),
    }
```

#### Frequency-Domain Features (Welch PSD)

```python
from scipy.signal import welch

def freq_features(x, fs):
    f, Pxx = welch(x, fs=fs, nperseg=256)
    dom_freq = f[np.argmax(Pxx)]
    spectral_centroid = np.sum(f * Pxx) / (np.sum(Pxx) + 1e-12)

    def band_energy(lo, hi):
        idx = (f >= lo) & (f <= hi)
        return np.sum(Pxx[idx])

    return {
        "dom_freq": dom_freq,
        "spec_centroid": spectral_centroid,
        "band_0_50": band_energy(0, 50),
        "band_50_150": band_energy(50, 150),
        "band_150_400": band_energy(150, 400),
    }
```

#### Simple Time-Frequency Feature: Local Energy Around Impact

You might want to characterize just the impact region:

```python
def impact_window_features(x, fs, center_sec=1.2, window_sec=0.1):
    center = int(center_sec * fs)
    half = int(window_sec * fs / 2)
    seg = x[max(0, center-half):center+half]
    feats = time_features(seg)
    feats = {f"impact_{k}": v for k, v in feats.items()}
    return feats
```

#### Combine Features

```python
def extract_features_for_event(x, fs):
    feats = {}
    feats.update(time_features(x))
    feats.update(freq_features(x, fs))
    feats.update(impact_window_features(x, fs))
    return feats
```

Now you can call:

```python
feat_normal = extract_features_for_event(filtered_normal, fs)
feat_degraded = extract_features_for_event(filtered_degraded, fs)
```

and convert them into a `pandas.DataFrame` for ML.

---

### 1.4 Handling Noise, Missing Values, Drift

#### Noise – Smoothing / Denoising

Simple moving-average smoothing:

```python
def moving_average(x, k=5):
    kernel = np.ones(k) / k
    return np.convolve(x, kernel, mode='same')
```

Wavelet denoising (if using `pywt`):

```python
import pywt

def wavelet_denoise(x, wavelet="db4", level=3):
    coeffs = pywt.wavedec(x, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    uthresh = sigma * np.sqrt(2 * np.log(len(x)))
    coeffs_thresh = [pywt.threshold(c, uthresh, mode='soft') for c in coeffs]
    return pywt.waverec(coeffs_thresh, wavelet)

denoised = wavelet_denoise(normal_signal)
```

#### Missing Data – Interpolation

If you have a time index and gaps:

```python
import pandas as pd

# Example: time series with missing points
ts = pd.Series(normal_signal, index=pd.date_range("2024-01-01", periods=len(normal_signal), freq="5ms"))
ts_missing = ts.copy()
ts_missing.iloc[100:200] = np.nan

# Interpolate linearly
ts_filled = ts_missing.interpolate(method='time')
```

#### Drift – High-Pass Filter / Detrending

```python
from scipy.signal import detrend

detrended = detrend(normal_signal)  # removes linear trend
```

---

## 2. ML Models for Switch Anomaly Detection

Let’s build:

1. **Isolation Forest** on features (unsupervised anomaly detection)
2. **Autoencoder** (reconstruction-based anomaly score)

Assume we’ve collected many **normal** switch events and a smaller number of **abnormal** ones.

### 2.1 Build a Feature Dataset

```python
import pandas as pd

def build_feature_table(signals, labels, fs):
    rows = []
    for x, lab in zip(signals, labels):
        x_filt = apply_bandpass(x, 5, 400, fs)
        feats = extract_features_for_event(x_filt, fs)
        feats["label"] = lab  # 0 = normal, 1 = degraded/anomaly
        rows.append(feats)
    return pd.DataFrame(rows)

# Example: generate synthetic dataset
X_signals = []
y_labels = []
for _ in range(300):
    X_signals.append(simulate_switch_event("normal"))
    y_labels.append(0)
for _ in range(100):
    X_signals.append(simulate_switch_event("degraded"))
    y_labels.append(1)

df = build_feature_table(X_signals, y_labels, fs)
feature_cols = [c for c in df.columns if c != "label"]
```

---

### 2.2 Isolation Forest (Unsupervised Anomaly Detection)

Train only on **normal** data (label = 0), then evaluate anomaly scores.

```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np

df_normal = df[df["label"] == 0]
df_all = df.copy()

scaler = StandardScaler()
X_normal = scaler.fit_transform(df_normal[feature_cols])
X_all = scaler.transform(df_all[feature_cols])

iso = IsolationForest(
    n_estimators=200,
    contamination=0.2,  # expected proportion of anomalies in test
    random_state=42
)
iso.fit(X_normal)

scores = -iso.score_samples(X_all)  # higher = more anomalous
df_all["anomaly_score"] = scores

# Simple thresholding
threshold = np.percentile(scores[df_all["label"]==0], 95)  # 95th percentile of normal
df_all["pred_anomaly"] = (df_all["anomaly_score"] > threshold).astype(int)

from sklearn.metrics import classification_report
print(classification_report(df_all["label"], df_all["pred_anomaly"]))
```

This gives you a KONUX-style story:

> “We trained an unsupervised anomaly detection model on normal switch actuation patterns. We extracted vibration features, fit an Isolation Forest, and used anomaly scores to flag abnormal events.”

---

### 2.3 Autoencoder (Reconstruction-Based Anomaly Detection)

Using a simple Keras-based dense autoencoder on features.

```python
import tensorflow as tf
from tensorflow.keras import layers, models

X = scaler.fit_transform(df_normal[feature_cols])  # use only normal
input_dim = X.shape[1]

inp = layers.Input(shape=(input_dim,))
encoded = layers.Dense(16, activation="relu")(inp)
encoded = layers.Dense(8, activation="relu")(encoded)
decoded = layers.Dense(16, activation="relu")(encoded)
out = layers.Dense(input_dim, activation=None)(decoded)

autoencoder = models.Model(inp, out)
autoencoder.compile(optimizer="adam", loss="mse")

autoencoder.fit(
    X, X,
    epochs=50,
    batch_size=32,
    validation_split=0.1,
    verbose=0
)

# Reconstruction error as anomaly score
X_all = scaler.transform(df_all[feature_cols])
recon = autoencoder.predict(X_all)
recon_err = np.mean((X_all - recon)**2, axis=1)

df_all["recon_error"] = recon_err
thr = np.percentile(recon_err[df_all["label"]==0], 95)
df_all["pred_anomaly_ae"] = (df_all["recon_error"] > thr).astype(int)

print(classification_report(df_all["label"], df_all["pred_anomaly_ae"]))
```

Story for interview:

> “We learned a compact representation of normal switch behavior using an autoencoder, and used reconstruction error as an online anomaly score. This works well for complex, nonlinear sensor patterns.”

---

## 3. KONUX-Specific Interview Q&A (With Strong Answers)

Here are question–answer pairs tailored to KONUX’s domain: **railway switches, IIoT, vibration, predictive maintenance**.

### 3.1 Domain & Product

**Q1: What do you understand about KONUX’s product and domain?**
**A:** KONUX combines IIoT sensors (e.g., accelerometers on railway switches) with AI-based analytics to monitor the health of railway infrastructure, especially switches. The system continuously analyzes vibration and operating patterns to detect degradation early, estimate remaining useful life, and recommend optimal maintenance interventions. The goal is to increase availability, reduce delays, and optimize maintenance resources for infrastructure managers.

---

**Q2: How would you explain “switch monitoring” to a non-technical person?**
**A:** A railway switch is like a track junction that guides trains to different tracks. If it fails, trains can be delayed or even derailed. KONUX puts smart sensors on these switches to listen to how they move and vibrate. By analyzing those “sounds” digitally, we can see when a switch is starting to wear down and tell operators: “Fix this one soon, before it causes trouble.”

---

### 3.2 Sensor Data & Signal Processing

**Q3: How would you analyze mechanical sensor data from a railway switch?**
**A:** I would:

1. Preprocess the raw acceleration signal:

   * Remove obvious noise/drift (high-pass, band-pass filters)
   * Segment around known events (e.g., during the actual switch actuation)
2. Extract features:

   * Time domain (RMS, kurtosis, crest factor, peak-to-peak)
   * Frequency domain (dominant frequencies, band energy, spectral centroid using FFT or Welch PSD)
   * Event-specific features: impact magnitude and shape near the locking moment
3. Compare features over time or across switches:

   * Look for trends (increasing RMS/kurtosis)
   * Model normal patterns and identify deviations using anomaly detection or supervised models.

---

**Q4: What techniques would you use to extract features from vibration or acceleration signals?**
**A:**

* **Time-domain:** RMS, peak, peak-to-peak, skewness, kurtosis, crest factor.
* **Frequency-domain:** FFT-based features, dominant frequency, harmonic amplitudes, band energies, spectral centroid.
* **Time-frequency domain:** STFT or wavelet transforms to capture transient events, especially the short impacts during switch movement.
* **Event-focused features:** energy and shape of the closing impact, duration of motion, asymmetry between opening/closing phases.

---

### 3.3 Anomaly Detection & Predictive Maintenance

**Q5: How would you approach anomaly detection for switches with mostly “normal” data and few failures?**
**A:** I would use **semi-supervised or unsupervised** anomaly detection:

* Model “normal behavior” using:

  * Isolation Forest
  * One-Class SVM
  * Autoencoders (on time-series or features)
* Train only on healthy switch events.
* For each new event, compute anomaly scores (e.g., reconstruction error, isolation score).
* Calibrate thresholds based on historical data and acceptable false-positive rate.
* Combine sensor anomaly scores with contextual features (temperature, load, traffic) before raising alarms.

---

**Q6: How would you design a predictive maintenance model for switches?**
**A:** A layered approach:

1. **Detection** – Is this event abnormal now?
2. **Diagnosis** – What type of degradation is likely (e.g., friction, looseness)?
3. **Prognosis** – Estimate how the degradation evolves over time using:

   * Trend models on features (e.g., RMS/kurtosis slope)
   * Regression models (RandomForest, Gradient Boosting) predicting degradation index or RUL
   * Time-series models (LSTM, temporal CNN) that process the sequence of events over weeks/months.

Then map these outputs into simple maintenance actions: “Monitor”, “Plan intervention”, “Immediate attention”.

---

### 3.4 Handling Real-World Sensor Problems

**Q7: What challenges do you expect with noisy sensor data in the rail environment? How would you handle them?**
**A:** Challenges:

* High ambient noise from passing trains and nearby equipment
* Electrical interference (50/60 Hz)
* Mechanical coupling between nearby structures
* Weather influence, temperature drift
* Loose or aging sensor mounts

Mitigation:

* Carefully designed band-pass and notch filters
* Wavelet-based denoising to preserve impacts
* Using features that are robust to noise (e.g., band energy rather than single sample values)
* Modeling noise characteristics by comparing “quiet” vs “operational” periods.

---

**Q8: How would you treat missing data in sensor streams?**
**A:** Depends on severity:

* **Short gaps:** forward/backward fill, interpolation (linear, time-based)
* **Long gaps:** treat as downtime segments and exclude from continuous models
* Add metadata flags (e.g., “gap”, “sensor offline”) so downstream models don’t misinterpret it.
* If necessary, infer missing behavior using model-based approaches (Kalman filters, forecasting models).

I’d also try to detect systematic data loss (network or device issues) and create monitoring dashboards.

---

**Q9: How do you deal with sensor drift and calibration issues?**
**A:**

* Use **high-pass** filters to remove slow drift.
* Use reference states: e.g., known “idle” conditions where the system should be quiet, and recalibrate offsets.
* Build temperature-compensation models if drift correlates with temperature.
* Detect anomalies such as constant-offset or saturation that indicate sensor failure rather than asset degradation.

---

### 3.5 ML & System Design

**Q10: How would you design an end-to-end pipeline for switch monitoring?**
**A:**

1. **Ingestion:** IIoT sensors send raw acceleration + metadata to the cloud (e.g., via MQTT/Kafka).
2. **Preprocessing service:**

   * Synchronization, resampling, filtering
   * Segmentation around switching events (using point machine signals)
3. **Feature extraction service:**

   * Compute time, frequency, time-frequency features
4. **Model service:**

   * Anomaly detection (Isolation Forest / Autoencoder)
   * Degradation modeling (trends, RUL)
5. **Decision layer:**

   * Convert scores to discrete health states + maintenance recommendations
6. **Reporting & UX:**

   * Dashboards for operators
   * Alerts integrated into maintenance planning systems

Everything is monitored, versioned (models + data), and retrained periodically.

---

**Q11: How would you validate that your model is actually useful for operators, not just accurate on a test set?**
**A:**

* Evaluate not only model metrics (AUC, F1, precision/recall), but **business metrics**:

  * Reduction in unplanned failures
  * Earlier detection horizon
  * Fewer unnecessary site visits
* Collaborate with domain experts / maintenance engineers to:

  * Check if flagged anomalies correspond to meaningful issues
  * Validate that explanations (features, trends) are interpretable
* Run **shadow deployments** where predictions are logged but not yet acted on, compare against future failures.
* Collect feedback from operators and refine alert thresholds and UX.

---

**Q12: How would you explain an anomaly detection decision to a field engineer?**
**A:**

> “In the last 50 switching cycles, the closing impact has become sharper and higher in amplitude, and the energy in the 100–300 Hz band has increased by 40%. Historically, these patterns correlate with increased friction or loosening of some components. That’s why the system is suggesting a check on this switch.”

I would always point to **trend changes in intuitive features** (RMS, impact magnitude, certain frequency bands), not just “the model said so.”

---

If you want, I can next:

* Help you turn all this into a **polished project README**
* Draft a **1–2 minute spoken explanation** you can use when they ask “Tell us about a relevant project”
* Build a **mock KONUX interview script** where I ask and you answer, and then I give you feedback.
Here is a **clear, simple, and detailed explanation** of the requirement:

# ✅ **“Experience applying digital signal processing (DSP) techniques to extract features and insights from sensor or time-series data”**

This phrase appears in job descriptions for positions in:

* Data science
* Machine learning
* Robotics
* Embedded systems
* IoT (Internet of Things)
* Audio/speech processing
* Biomedical engineering
* Automotive systems

It describes a set of **skills and knowledge** related to analyzing signals and time-based data.

---

# 🔵 **1. What is Digital Signal Processing (DSP)?**

**DSP (Digital Signal Processing)** is the science of analyzing, transforming, and extracting information from **digital signals**, which are sequences of data measured over time.

Examples of signals:

* ECG heart signals
* Accelerometer/gyroscope data
* Audio recordings
* Vibration sensors
* Temperature/time logs
* EEG brain signals
* Radar or LiDAR signals

A signal is basically:

> “A series of numbers changing over time.”

DSP is used to clean, transform, and understand these numbers.

---

# 🔵 **2. What does this requirement really mean?**

It means the candidate has experience in:

### ✔ Analyzing time-series or sensor data

### ✔ Applying DSP algorithms

### ✔ Extracting meaningful features

### ✔ Preparing data for machine learning or system monitoring

### ✔ Understanding frequency, noise, patterns, and trends

---

# 🔵 **3. What types of DSP techniques are expected? (Very Important)**

Below are the most common DSP skills companies look for:

---

## ⭐ **A. Filtering (Removing noise)**

Used to clean raw sensor data.

### Techniques:

* **Low-pass filter** → keep slow changes, remove high-frequency noise
* **High-pass filter** → keep fast changes, remove slow drift
* **Band-pass filter** → keep only specific frequency range
* **Notch filter** → remove a very specific noise frequency (e.g., 50/60Hz interference)

### Example:

Removing noise from accelerometer signals before analyzing human motion.

---

## ⭐ **B. Fourier Transform (Frequency Analysis)**

### What it does:

Converts a signal from **time domain → frequency domain**.

Useful for:

* Detecting periodic patterns
* Finding dominant frequencies
* Identifying machine vibrations
* Speech/sound analysis

Techniques:

* **FFT (Fast Fourier Transform)**
* **STFT (Short-Time Fourier Transform)**
* **Power Spectral Density (PSD)**

---

## ⭐ **C. Feature Extraction from Signals**

DSP extracts features useful for:

* Machine learning
* Anomaly detection
* Classification
* Predictive maintenance

### Common features:

#### **Time-domain features**

* Mean, median, variance
* Peak value
* RMS (Root Mean Square)
* Zero-crossing rate
* Signal energy

#### **Frequency-domain features**

* Dominant frequency
* Spectral centroid
* Spectral entropy
* Band energy

#### **Wavelet features**

* Multi-scale decomposition
* Transient event detection

---

## ⭐ **D. Smoothing and Denoising**

To reduce noise while keeping the main signal.

Methods:

* **Moving average filter**
* **Savitzky–Golay smoothing**
* **Median filtering**
* **Wavelet denoising**

---

## ⭐ **E. Time–Frequency Analysis**

Used for non-stationary signals (signals whose pattern changes over time).

Techniques:

* STFT
* Wavelet Transform
* Spectrograms

This is common in:

* Speech
* Seismic signals
* Biological signals

---

## ⭐ **F. Sensor Fusion**

Combining data from multiple sensors to estimate the true state.

Examples:

* Accelerometer + gyroscope → orientation estimation
* GPS + IMU → navigation
* Multiple microphones → sound localization

Techniques include:

* **Kalman Filters**
* **Extended Kalman Filters**
* **Complementary filters**

---

# 🔵 **4. Why do companies ask for DSP experience?**

Because raw sensor/time-series data is usually:

* Noisy
* High-frequency
* Complex
* Hard to interpret directly

DSP helps clean and transform the data so that:

* ML models perform better
* Sensors produce reliable readings
* Systems can make decisions
* Performance is stable

---

# 🔵 **5. Real-world examples (Easy to understand)**

### ✓ **1. Wearable devices**

Extracting steps, heart rate, posture, sleep stages using accelerometer + DSP.

### ✓ **2. Predictive maintenance**

Using vibration and sound signals to detect:

* bearing wear
* machine failure
* motor imbalance

### ✓ **3. Automotive**

Processing sensors like:

* LiDAR
* Radar
* Wheel-speed sensors
* IMU sensors

DSP extracts motion information for self-driving cars.

### ✓ **4. Medical**

Processing:

* ECG
* EEG
* EMG
* Blood pressure waveforms

DSP extracts health indicators.

### ✓ **5. Speech/audio**

Noise removal, voice detection, feature extraction (MFCCs).

---

# 🔵 **6. What skills are implied in this requirement?**

Companies expect the candidate to know:

### ✔ Signal filtering

### ✔ Fourier/Wavelet transforms

### ✔ Feature engineering for time-series

### ✔ Noise reduction techniques

### ✔ Sensor calibration and preprocessing

### ✔ Time-series segmentation

### ✔ Spectral analysis

### ✔ Event detection

Tools & libraries commonly used:

* **Python**: NumPy, SciPy, librosa, pywt
* **MATLAB**
* **R** for time-series
* **C/C++** for embedded DSP

---

# 🔵 **7. How to mention your DSP skills in a resume? (Example)**

**“Applied digital signal processing (DSP) techniques — filtering, FFT, wavelets, smoothing, and spectral analysis — to extract meaningful features from sensor and time-series data for machine learning and predictive analytics.”**

Or:

**“Designed and implemented DSP pipelines for IMU, audio, and biomedical signals, including noise reduction, frequency-domain analysis, and feature extraction.”**

---

# 🟢 **If you want, I can also provide**:

✔ Visual diagrams for DSP processes
✔ Interview questions for DSP + time-series
✔ Python examples (with code)
✔ A list of DSP features for ML
✔ A resume summary describing DSP experience

Just tell me!
Absolutely — here are **clear visual diagrams for DSP processes** AND **real interview questions with answers** for DSP + time-series analysis.

Everything is written in simple English and beginner-friendly.

---

# 🎨 **VISUAL DIAGRAMS FOR DSP PROCESSES**

Below are clean, easy-to-understand ASCII diagrams showing the full DSP workflow.

---

# 🔵 **1. Full DSP Pipeline (Overview Diagram)**

```
        Raw Sensor Signal
                │
                ▼
       ┌─────────────────┐
       │  Preprocessing  │
       │ (cleaning data) │
       └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │  Filtering       │
       │ (remove noise)   │
       └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │Transformation    │
       │(FFT, Wavelets)   │
       └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │ Feature Extract │
       │ (time/frequency)│
       └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │ ML Model or     │
       │ Decision System │
       └─────────────────┘
```

---

# 🔵 **2. Time-Domain → Frequency-Domain (FFT) Diagram**

```
Time Domain Signal (Waveform)
     ┌───────────────────────────────────────┐
     │   /\      /\         /\               │
     │  /  \    /  \   /\  /  \   /\         │
     └───────────────────────────────────────┘
                    │
                    ▼  Fourier Transform (FFT)
Frequency Domain (Spectrum)
     ┌───────────────────────────────────────┐
     │   |        |          |               │
     │   |        |          |               │
     │  f1       f2        f3  --> Frequency │
     └───────────────────────────────────────┘
```

Purpose:

* Time domain hides frequency patterns
* FFT reveals dominant frequencies (vibration, sound, cycles)

---

# 🔵 **3. Filtering Pipeline (Low-Pass, High-Pass, Band-Pass)**

### **Low-pass (keep slow changes)**

```
Signal → [Low-Pass Filter] → Smooth signal
```

### **High-pass (keep fast changes)**

```
Signal → [High-Pass Filter] → Sharp edges / sudden changes
```

### **Band-pass (keep only a frequency range)**

```
Signal → [Band-Pass Filter] → Only frequencies between f1 and f2
```

---

# 🔵 **4. Rolling Window / Sliding Window for Time-Series**

```
Signal:  [ 1  2  4  5  7  8  4  3  2 ]
Windows:
        [1 2 4]
           [2 4 5]
              [4 5 7]
                 [5 7 8]
                    ...

Each window → compute features:
- Mean
- Variance
- RMS
- Max/min
```

Used for:

* Feature extraction
* Event detection
* Input to ML models

---

# 🔵 **5. Wavelet Transform Diagram (Time–Frequency Analysis)**

```
Time Domain Signal
       ┌───────────────, , ,───────────────┐
       │    Low freq         High freq     │
       └────────────────────────────────────┘
                 │
                 ▼
Wavelet Transform (Multi-scale)
       ┌────────────────────────────────────┐
Scale 1:   |------------ Low frequencies -----|
Scale 2:            |---- Mid frequencies ----|
Scale 3:                     |-- High freq --|
       └────────────────────────────────────┘
```

Purpose:

* Detect transient events
* Analyze signals whose frequency changes over time (ECG, EEG, seismic signals)

---

# 🔵 **6. Sensor Fusion (Kalman Filter) Diagram**

```
Accelerometer →──┐
                  │
Gyroscope    →──┐ │
                 ▼ ▼
           ┌──────────────┐
           │ Kalman Filter │
           │ (Sensor Fusion)│
           └──────────────┘
                 │
                 ▼
          Estimated State
       (position, velocity, angle)
```

Purpose:

* Combine noisy sensors
* Estimate the real system state

---

# 🎯 **DSP + TIME-SERIES INTERVIEW QUESTIONS**

Below are the **most common real interview questions**, with **clear, short answers**.

---

# 🔵 **1. What is digital signal processing (DSP)?**

DSP is the technique of **analyzing, transforming, and extracting information from signals** that change over time (e.g., audio, acceleration, voltage, vibration).

---

# 🔵 **2. What are time-domain vs. frequency-domain features?**

### Time-domain:

* Mean
* Variance
* RMS
* Zero-crossing rate
* Peak-to-peak amplitude

### Frequency-domain:

* FFT peaks
* Dominant frequency
* Spectral centroid
* Spectral entropy

---

# 🔵 **3. What is the Fourier Transform and why is it used?**

The Fourier Transform converts a signal from the **time domain to frequency domain**.
It reveals periodic patterns hidden in the signal.

Used for:

* Vibration analysis
* Speech processing
* Machine fault detection

---

# 🔵 **4. What is the difference between FFT and STFT?**

| FFT                           | STFT                                   |
| ----------------------------- | -------------------------------------- |
| One global frequency analysis | Time-localized frequency analysis      |
| No time information           | Shows how frequencies change over time |
| Good for stationary signals   | Good for non-stationary signals        |

---

# 🔵 **5. What is the purpose of filtering?**

To remove unwanted noise or isolate specific frequency components.

Types:

* Low-pass
* High-pass
* Band-pass
* Notch filters

---

# 🔵 **6. What is aliasing? How do you avoid it?**

Aliasing = high-frequency signals appear as low frequency when sampling too slowly.

Prevent using:

* **Nyquist rate** (sample at ≥ 2× max frequency)
* **Anti-aliasing filters**

---

# 🔵 **7. Explain windowing in DSP.**

Signals are often processed in **small segments (windows)**.

Windows avoid edge artifacts.

Common windows:

* Hamming
* Hann
* Blackman

---

# 🔵 **8. What is RMS and why is it important?**

RMS (root mean square) measures the **energy** of a signal.
Useful for:

* Vibration
* Electrical signals
* Audio loudness

---

# 🔵 **9. What is sensor fusion?**

Combining multiple sensors (IMU, GPS, Radar, Camera) to estimate a system’s true state.

Techniques:

* Kalman Filter
* Complementary Filter
* Particle Filter

---

# 🔵 **10. How do you handle noise in sensor data?**

Methods:

* Low-pass filters
* Wavelet denoising
* Median filtering
* Moving average smoothing

---

# 🔵 **11. What features would you extract from a vibration signal?**

Time-domain:

* RMS, peak, crest factor
* Kurtosis, variance

Frequency-domain:

* FFT peaks
* PSD
* Dominant frequency

---

# 🔵 **12. What is the Nyquist Theorem?**

You must sample at **at least twice the highest frequency** in the signal to avoid aliasing.

---

# 🔵 **13. What is a spectrogram?**

A time-frequency image produced by STFT:

```
Time on X-axis  
Frequency on Y-axis  
Color = amplitude
```

Used in speech and audio analysis.

---

# 🔵 **14. What is wavelet transform used for?**

To analyze signals where frequency changes over time.
Useful for:

* ECG/EEG
* Seismic data
* Transient anomaly detection

---

# 🔵 **15. How do you prepare time-series data for machine learning?**

Steps:

1. Filtering (noise removal)
2. Normalization
3. Sliding windows
4. Feature extraction
5. Train/test split that respects time order
6. Model training (LSTM, CNN, Random Forest, etc.)

---

# 🟢 **If you'd like, I can also provide:**

✔ Python code examples for DSP (FFT, filters, wavelets)
✔ A PDF or PowerPoint version of all diagrams
✔ Extra interview questions (50+)
✔ Industry-specific examples (automotive, medical, IoT, finance)

Just tell me!
