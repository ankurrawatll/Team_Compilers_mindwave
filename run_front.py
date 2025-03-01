import tkinter as tk
from tkinter import Label, Button
import subprocess
import threading
import queue
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import numpy as np

# GUI Window Setup
root = tk.Tk()
root.title("EEG & Eye Control GUI")
root.geometry("800x600")

# Status Labels
eye_status = Label(root, text="Eye: Not Running", font=("Arial", 14))
eye_status.pack()

eeg_status = Label(root, text="EEG: Not Running", font=("Arial", 14))
eeg_status.pack()

# EEG Data Queue (for smooth graphing)
eeg_queue = queue.Queue(maxsize=100)

# Matplotlib EEG Visualization
fig, ax = plt.subplots(figsize=(6, 3))
ax.set_title("Real-time EEG Signal")
ax.set_xlabel("Time")
ax.set_ylabel("Amplitude")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Process Variables
eye_process = None
prediction_process = None
ser = None

def start_eye_tracking():
    global eye_process
    if eye_process is None:
        eye_process = subprocess.Popen(["python", "direction.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        eye_status.config(text="Eye: Running ✅")

def start_eeg_prediction():
    global prediction_process, ser
    if prediction_process is None:
        prediction_process = subprocess.Popen(["python", "prediction.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        eeg_status.config(text="EEG: Running ✅")
        ser = serial.Serial('COM4', 115200, timeout=1)
        threading.Thread(target=process_eeg_data, daemon=True).start()

def stop_processes():
    global eye_process, prediction_process, ser
    if eye_process:
        eye_process.terminate()
        eye_process = None
        eye_status.config(text="Eye: Stopped ❌")
    if prediction_process:
        prediction_process.terminate()
        prediction_process = None
        eeg_status.config(text="EEG: Stopped ❌")
    if ser:
        ser.close()
        ser = None

def process_eeg_data():
    while True:
        if ser:
            try:
                raw_data = ser.readline().decode('latin-1').strip()
                if raw_data:
                    eeg_value = float(raw_data)
                    if eeg_queue.full():
                        eeg_queue.get()
                    eeg_queue.put(eeg_value)
                    
                    # Update EEG Graph
                    ax.clear()
                    ax.plot(list(eeg_queue.queue), color='blue')
                    ax.set_title("Real-time EEG Signal")
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Amplitude")
                    canvas.draw()
            except Exception as e:
                eeg_status.config(text="EEG: Error ❌")
        time.sleep(0.1)  # Prevent high CPU load

# Buttons
start_eye_btn = Button(root, text="Start Eye Tracking", command=start_eye_tracking)
start_eye_btn.pack()

start_eeg_btn = Button(root, text="Start EEG Prediction", command=start_eeg_prediction)
start_eeg_btn.pack()

stop_btn = Button(root, text="Stop All", command=stop_processes)
stop_btn.pack()

# Run GUI
root.mainloop()
stop_processes()
