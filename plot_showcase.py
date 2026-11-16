import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


FILES_TO_PLOT = {
    "Empty Room": "empty_01_detailed.png",      
    "Stationary": "stationary_01_detailed.png", 
    "Active Motion": " motion_04_detailed.png"  
}

def parse_and_normalize(file_path):
    packets = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "[" in line and "]" in line:
                try:
                    s = line.index("[")
                    e = line.rindex("]") + 1
                    arr = [abs(v) for v in json.loads(line[s:e])]
                    if len(arr) > 0:
                        packets.append(arr)
                except: pass
                
    matrix = np.array(packets)
    # L2 Normalization (core innovation)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("ESP32 CSI Sensing: Pure-Math Subcarrier Distortion", fontsize=16, fontweight='bold', y=0.95)

for ax, (title, filename) in zip(axes, FILES_TO_PLOT.items()):
    try:
        norm_matrix = parse_and_normalize(filename)
        im = ax.imshow(norm_matrix.T, aspect="auto", cmap="plasma", origin="lower")
        ax.set_title(title, fontsize=14)
        ax.set_xlabel("Packet Index")
        if ax == axes[0]:
            ax.set_ylabel("Subcarrier Index")
    except Exception as e:
        ax.set_title(f"Error loading {filename}")

plt.tight_layout()
plt.subplots_adjust(top=0.85)
plt.savefig("linkedin_showcase_graph.png", dpi=300)
print("Success! Saved high-res comparison graph as 'linkedin_showcase_graph.png'")
