import subprocess
import time

# Define scripts
eye_script = "direction.py"
prediction_script = "prediction.py"

# Open log files to prevent terminal flooding
eye_log = open("eye_log.txt", "w")
prediction_log = open("prediction_log.txt", "w")

# Start both scripts with logs redirected
eye_process = subprocess.Popen(["python", eye_script], stdout=eye_log, stderr=eye_log)
prediction_process = subprocess.Popen(["python", prediction_script], stdout=prediction_log, stderr=prediction_log)

print("✅ Both scripts started successfully! Running in background.")

try:
    while True:
        time.sleep(1)  # Keep main script alive
except KeyboardInterrupt:
    print("\n🔴 Stopping both scripts...")

    # Terminate both processes safely
    eye_process.terminate()
    prediction_process.terminate()

    # Wait for processes to exit  
    eye_process.wait()
    prediction_process.wait()

    print("✅ Both scripts stopped successfully!")

    # Close log files
    eye_log.close()
    prediction_log.close()
