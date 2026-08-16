# Save as evaluation/analyze_exfiltration.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from attacks.scenarios import SCENARIOS

# Load CP-SAN results
missed_ids = set()
with open("results/cpsan_full.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["category"] == "Exfiltration" and row["neutralized"] == "False":
            missed_ids.add(row["scenario_id"])

print(f"Missed Exfiltration scenarios: {len(missed_ids)}")
print("=" * 70)

for s in SCENARIOS:
    if s["id"] in missed_ids:
        print(f"\nID:     {s['id']}")
        print(f"Task:   {s['user_task']}")
        print(f"Tool:   {s['tool']}")
        print(f"Params: {s['injected_params']}")
        if "note" in s:
            print(f"Note:   {s['note']}")
        print("-" * 70)
        