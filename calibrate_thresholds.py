import glob
import json
import numpy as np

def parse_and_score(file_pattern):
    scores = []
    files = sorted(glob.glob(file_pattern))
    for file_path in files:
        packets = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "[" in line and "]" in line:
                    try:
                        s = line.find("[")
                        e = line.rfind("]") + 1
                        arr = [abs(v) for v in json.loads(line[s:e])]
                        if len(arr) > 0:
                            packets.append(arr)
                    except Exception:
                        pass
        if len(packets) < 50:
            continue
        
        matrix = np.array(packets)
        
        # 1. L2 Normalization (removes AGC hardware gain jumps)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        norm_matrix = matrix / norms

        # 2. Measure Subcarrier Standard Deviation across time
        subcarrier_stds = np.std(norm_matrix, axis=0)
        score = np.mean(subcarrier_stds) * 1000  # Scale score for readability
        scores.append(score)
    return scores

print("Analyzing recorded trial files...\n")
empty_scores = parse_and_score("empty_*.csv")
stat_scores = parse_and_score("stationary_*.csv")
mot_scores = parse_and_score("motion_*.csv")

avg_empty = np.mean(empty_scores) if empty_scores else 0.0
avg_stat = np.mean(stat_scores) if stat_scores else 0.0
avg_mot = np.mean(mot_scores) if mot_scores else 0.0

# Midpoint boundaries
empty_threshold = (avg_empty + avg_stat) / 2.0
sitting_threshold = (avg_stat + avg_mot) / 2.0

print(f"--- DATASET SCORE RANGES ---")
print(f"Empty Scores      : {[round(s, 2) for s in empty_scores]} | Avg: {avg_empty:.2f}")
print(f"Stationary Scores : {[round(s, 2) for s in stat_scores]} | Avg: {avg_stat:.2f}")
print(f"Motion Scores     : {[round(s, 2) for s in mot_scores]} | Avg: {avg_mot:.2f}")
print(f"----------------------------")
print(f"CALIBRATED EMPTY_THRESHOLD   = {empty_threshold:.2f}")
print(f"CALIBRATED SITTING_THRESHOLD = {sitting_threshold:.2f}\n")

with open("thresholds.json", "w") as f:
    json.dump({
        "EMPTY_THRESHOLD": empty_threshold,
        "SITTING_THRESHOLD": sitting_threshold
    }, f, indent=4)

print("Saved updated settings to 'thresholds.json'!")