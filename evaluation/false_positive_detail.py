# Save as evaluation/false_positive_detail.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv

print("FALSE POSITIVE ANALYSIS")
print("=" * 70)

false_positives = []
with open("results/task_completion.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["correct"] == "False":
            false_positives.append(row)

print(f"Total false positives: {len(false_positives)}")
print()

for fp in false_positives:
    print(f"ID:     {fp['scenario_id']}")
    print(f"Tool:   {fp['tool']}")
    print(f"Task:   {fp['user_task']}")
    print(f"Params: {fp['parameters']}")
    print(f"Action: {fp['action']}")
    print("-" * 70)