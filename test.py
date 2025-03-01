import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
from scipy import signal

# Serial Connection Setup
COM_PORT = 'COM4'
BAUD_RATE = 115200
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)

# Parameters
window_size = 500  
update_interval = 50  

# EEG Frequency Bands (Adjusted for More Sensitivity)
delta_band = (0.5, 4)
theta_band = (4, 8)
alpha_band = (8, 13)
beta_band = (13, 30)

# Initialize Data Buffers
eeg_data = np.zeros(window_size)
delta_data = np.zeros(window_size)
theta_data = np.zeros(window_size)
alpha_data = np.zeros(window_size)
beta_data = np.zeros(window_size)

# Create Figure and Subplots
fig, ax = plt.subplots(5, 1, figsize=(12, 10))
labels = ["Raw EEG", "Delta (0.5-4 Hz)", "Theta (4-8 Hz)", "Alpha (8-13 Hz)", "Beta (13-30 Hz)"]
colors = ["black", "blue", "purple", "green", "red"]
lines = []

for i in range(5):
    ax[i].set_xlim(0, window_size)
    ax[i].set_ylim(-1, 1)  # Normalized range
    ax[i].set_title(labels[i])
    ax[i].grid(True)
    line, = ax[i].plot(np.zeros(window_size), lw=2, color=colors[i])
    lines.append(line)

# Bandpass Filter Function (Fixed for Sensitivity)
def bandpass_filter(data, lowcut, highcut, sampling_rate=512, order=2, gain=3.0):
    nyquist = 0.5 * sampling_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(order, [low, high], btype='band')

    if len(data) > order * 2:
        return signal.filtfilt(b, a, data) * gain  # Apply gain to boost signal
    return np.zeros_like(data)

# Fix EEG Normalization Issue
last_valid_value = 0

def read_eeg_data():
    global last_valid_value
    try:
        raw_data = ser.readline().decode('latin-1').strip()
        if raw_data.isdigit():
            value = float(raw_data)

            # Fixed Scaling for EEG Range 0-1023
            normalized_value = (value - 512) / 256  
            if normalized_value < -1.0:
                return last_valid_value
            last_valid_value = normalized_value
            return normalized_value
        else:
            return last_valid_value
    except:
        return last_valid_value

# Update Function
def update(frame):
    global eeg_data, delta_data, theta_data, alpha_data, beta_data

    new_sample = read_eeg_data()
    print(f"New EEG Sample: {new_sample}")  

    eeg_data = np.roll(eeg_data, -1)
    eeg_data[-1] = new_sample

    delta_data = np.roll(delta_data, -1)
    delta_data[-1] = bandpass_filter(eeg_data, delta_band[0], delta_band[1], gain=4.0)[-1]

    theta_data = np.roll(theta_data, -1)
    theta_data[-1] = bandpass_filter(eeg_data, theta_band[0], theta_band[1], gain=3.5)[-1]

    alpha_data = np.roll(alpha_data, -1)
    alpha_data[-1] = bandpass_filter(eeg_data, alpha_band[0], alpha_band[1], gain=3.0)[-1]

    beta_data = np.roll(beta_data, -1)
    beta_data[-1] = bandpass_filter(eeg_data, beta_band[0], beta_band[1], gain=2.0)[-1]

    for i, line in enumerate(lines):
        line.set_ydata([eeg_data, delta_data, theta_data, alpha_data, beta_data][i])

    return lines

ani = animation.FuncAnimation(fig, update, interval=update_interval, blit=False, cache_frame_data=False)

plt.show()
ser.close()
