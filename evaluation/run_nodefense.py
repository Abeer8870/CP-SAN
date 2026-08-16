import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from collections import defaultdict
from attacks.scenarios import SCENARIOS

def run_no_defense():
    print(f"Running: No Defense on {len(SCENARIOS)} scenarios...")
    print("=" * 60)

    results = [{
        "scenario_id": s["id"],
        "category": s["category"],
        "action": "FORWARDED",
        "neutralized": False,
        "config": "No Defense"
    } for s in SCENARIOS]

    # Category breakdown
    cats = defaultdict(lambda: {"total": 0, "neutralized": 0})
    for r in results:
        cats[r["category"]]["total"] += 1

    print(f"\n{'Category':<30} {'Total':>6} {'Caught':>7} {'ASR':>7}")
    print(f"{'-'*60}")
    for cat, data in sorted(cats.items()):
        print(f"{cat:<30} {data['total']:>6} {0:>7} {100.0:>6}%")

    # Save
    os.makedirs("results", exist_ok=True)
    with open("results/no_defense.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "category", "action", "neutralized", "config"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"{'='*60}")
    print(f"Total scenarios: {len(SCENARIOS)}")
    print(f"Neutralized:     0")
    print(f"ASR:             100.0%")
    print(f"Saved to results/no_defense.csv")

if __name__ == "__main__":
    run_no_defense()