import json
import numpy as np

def verify_variance(csv_path):
    packets = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "[" in line and "]" in line:
                try:
                    s, e = line.index("["), line.rindex("]") + 1
                    packets.append([abs(v) for v in json.loads(line[s:e])])
                except:
                    pass
    
    raw = np.array(packets)
    
    # 1. Raw Variance (Pre-Normalization)
    raw_var = np.mean(np.var(raw, axis=0))
    
    # 2. L2 Normalized Variance (Post-Normalization)
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    norms[norms == 0] = 1.0  # Prevent division by zero
    l2_matrix = raw / norms
    l2_var = np.mean(np.var(l2_matrix, axis=0))
    
    print(f"File: {csv_path}")
    print(f"  Raw Variance (Pre-L2) : {raw_var:.2f}")
    print(f"  L2 Variance (Post-L2): {l2_var:.6f}\n")

# Run on your three CSV files
for fname in ["motion_04.csv", "empty_01.csv", "stationary_01.csv"]:
    verify_variance(fname)