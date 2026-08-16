# Save as evaluation/missed_analysis.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from collections import defaultdict

missed = defaultdict(list)

with open("results/ablation_results.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["config"] == "CP-SAN (Full)" and row["neutralized"] == "False":
            missed[row["category"]].append(row["scenario_id"])

print("Scenarios missed by CP-SAN (Full):")
print("=" * 50)
total = 0
for cat, ids in sorted(missed.items()):
    print(f"\n{cat} ({len(ids)} missed):")
    for sid in ids:
        print(f"  - {sid}")
    total += len(ids)

print(f"\nTotal missed: {total} out of 116")
print(f"Overall detection rate: {round((116-total)/116*100, 1)}%")