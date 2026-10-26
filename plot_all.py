import glob
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Find all CSV files in the folder
csv_files = glob.glob("*.csv")

for file in csv_files:
    packets = []
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if "[" in line and "]" in line:
                try:
                    s = line.index("[")
                    e = line.rindex("]") + 1
                    arr = [abs(v) for v in json.loads(line[s:e])]
                    if len(arr) > 0:
                        packets.append(arr)
                except: pass
                
    if not packets:
        continue

    # Math
    matrix = np.array(packets)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_matrix = matrix / norms

    # Plot
    plt.figure(figsize=(10, 4))
    plt.imshow(norm_matrix.T, aspect="auto", cmap="plasma", origin="lower")
    plt.title(f"ESP32 CSI: {file.replace('.csv', '')}", fontsize=14, fontweight='bold')
    plt.xlabel("Packet Index")
    plt.ylabel("Subcarrier Index")
    plt.tight_layout()
    
    # Save
    out_name = file.replace('.csv', '_graph.png')
    plt.savefig(out_name, dpi=300)
    plt.close()
    print(f"Saved {out_name}")