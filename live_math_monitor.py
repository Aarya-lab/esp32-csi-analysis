import serial
import json
import time
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SERIAL_PORT = "COM8"  # Match your receiver port
BAUD_RATE = 921600
INTERVAL_SECONDS = 30

# Load calibrated mathematical thresholds
if os.path.exists("thresholds.json"):
    with open("thresholds.json", "r") as f:
        cfg = json.load(f)
        EMPTY_THRESHOLD = cfg["EMPTY_THRESHOLD"]
        SITTING_THRESHOLD = cfg["SITTING_THRESHOLD"]
else:
    EMPTY_THRESHOLD = 5.0
    SITTING_THRESHOLD = 15.0

print(f"==================================================")
print(f"   ESP32 Pure-Math 30s Real-Time CSI Monitor     ")
print(f"   Listening on {SERIAL_PORT} @ {BAUD_RATE} Baud")
print(f"   EMPTY_THRESHOLD   : {EMPTY_THRESHOLD:.2f}")
print(f"   SITTING_THRESHOLD : {SITTING_THRESHOLD:.2f}")
print(f"==================================================\n")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    print(f"Error opening serial port {SERIAL_PORT}: {e}")
    exit()

def classify_activity(score):
    if score < EMPTY_THRESHOLD:
        return "🟢 ROOM EMPTY (Static signal)", "ROOM EMPTY"
    elif score < SITTING_THRESHOLD:
        return "🟡 PERSON PRESENT (Sitting / Stationary)", "PERSON PRESENT"
    else:
        return "🚨 MOTION DETECTED (Walking / Movement)", "MOTION DETECTED"

def process_and_plot(csi_packets, attempt_num):
    if not csi_packets:
        print("[WARNING] No valid CSI packets collected during this window.")
        return

    matrix = np.array(csi_packets)
    num_packets, num_subcarriers = matrix.shape

    # 1. L2 Packet Normalization
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_matrix = matrix / norms

    # 2. Compute window subcarrier std score
    subcarrier_stds = np.std(norm_matrix, axis=0)
    score = np.mean(subcarrier_stds) * 1000

    status_str, clean_title = classify_activity(score)
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n==================================================")
    print(f"Attempt {attempt_num} | [{timestamp_str}] 30-SECOND REPORT")
    print(f"Packets Captured : {num_packets}")
    print(f"Activity Metric  : {score:.2f}")
    print(f"STATUS           : {status_str}")
    print(f"==================================================\n")

    # Generate summary plots
    fig, (ax_heatmap, ax_line) = plt.subplots(2, 1, figsize=(10, 6))
    fig.suptitle(f"CSI Monitor Report (Attempt {attempt_num}) | {timestamp_str}\nStatus: {clean_title}", fontsize=11, fontweight="bold")

    im = ax_heatmap.imshow(norm_matrix.T, aspect="auto", cmap="plasma", origin="lower")
    ax_heatmap.set_title("Normalized CSI Subcarrier Spectrum")
    ax_heatmap.set_ylabel("Subcarrier Index")
    fig.colorbar(im, ax=ax_heatmap)

    mean_signal = np.mean(norm_matrix, axis=1)
    ax_line.plot(mean_signal, color='crimson', linewidth=1.2, label="Normalized Subcarrier Power")
    ax_line.set_title("Filtered Signal Level")
    ax_line.set_xlabel("Packet Index")
    ax_line.set_ylabel("Normalized Amplitude")
    ax_line.grid(True, linestyle="--", alpha=0.5)
    ax_line.legend(loc="upper right")

    plt.tight_layout()
    snapshot_filename = f"csi_report_attempt_{attempt_num}.png"
    plt.savefig(snapshot_filename)
    plt.savefig("latest_csi_summary.png")
    plt.close(fig)

    print(f"-> Saved graph snapshot: {snapshot_filename}")

csi_buffer = []
window_start = time.time()
attempt_count = 1
expected_subcarrier_count = None

try:
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        
        if "[" in line and "]" in line:
            try:
                start_idx = line.index("[")
                end_idx = line.rindex("]") + 1
                csi_array = [abs(val) for val in json.loads(line[start_idx:end_idx])]
                if len(csi_array) > 0:
                    if expected_subcarrier_count is None:
                        expected_subcarrier_count = len(csi_array)
                    if len(csi_array) == expected_subcarrier_count:
                        csi_buffer.append(csi_array)
            except (ValueError, json.JSONDecodeError):
                pass

        if time.time() - window_start >= INTERVAL_SECONDS:
            process_and_plot(csi_buffer, attempt_count)
            csi_buffer = []
            attempt_count += 1
            window_start = time.time()

except KeyboardInterrupt:
    print("\nStopping CSI Monitor...")
    ser.close()