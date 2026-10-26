import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Target datasets representing each distinct state
TARGET_FILES = {
    "empty_01.csv": "Empty Room",
    "stationary_01.csv": "Stationary Person",
    "motion_04.csv": "Active Motion"
}

# Subcarrier indices matching your plot trace layout
SUBCARRIERS_TO_PLOT = [0, 76, 153, 229, 306, 383]

for filename, label in TARGET_FILES.items():
    packets = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if "[" in line and "]" in line:
                try:
                    s = line.index("[")
                    e = line.rindex("]") + 1
                    arr = [abs(v) for v in json.loads(line[s:e])]
                    if len(arr) > 0:
                        packets.append(arr)
                except:
                    pass

    if not packets:
        print(f"Skipping {filename}: No packet data found.")
        continue

    matrix = np.array(packets)
    num_packets, num_subcarriers = matrix.shape

    # Create dual-panel figure layout
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle(f"ESP32 CSI Analysis — {filename} ({label})", fontsize=16, fontweight='bold')

    # Top Panel: CSI Heatmap
    im = ax1.imshow(matrix.T, aspect="auto", cmap="plasma", origin="lower")
    ax1.set_title("CSI Heatmap (Subcarrier Amplitude Over Time)", fontsize=12)
    ax1.set_ylabel("Subcarrier Index")
    cbar = fig.colorbar(im, ax=ax1)
    cbar.set_label("Amplitude")

    # Bottom Panel: Subcarrier Signal Traces
    ax2.set_title("Individual Subcarrier Signal Traces (Absolute Amplitude)", fontsize=12)
    ax2.set_xlabel("Packet Number (Time Sequence)")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True, linestyle="--", alpha=0.5)

    for sc_idx in SUBCARRIERS_TO_PLOT:
        if sc_idx < num_subcarriers:
            ax2.plot(matrix[:, sc_idx], label=f"Subcarrier {sc_idx}", alpha=0.85)

    ax2.legend(loc="upper right", ncol=3)
    ax2.set_xlim(0, num_packets)

    plt.tight_layout()

    # Save high-resolution PNG asset
    out_name = filename.replace('.csv', '_detailed.png')
    plt.savefig(out_name, dpi=300)
    plt.close()
    print(f"Successfully generated: {out_name}")