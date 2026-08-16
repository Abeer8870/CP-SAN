import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import json
import time
from collections import defaultdict
from sanitizer.sanitizer import CPSan


def run_injecagent_evaluation():
    # Load scenarios
    path = "attacks/injecagent_scenarios.json"
    if not os.path.exists(path):
        print("InjecAgent scenarios not found — run load_injecagent.py first")
        return

    with open(path) as f:
        scenarios = json.load(f)

    print(f"Running CP-SAN against {len(scenarios)} InjecAgent scenarios...")
    print(f"Estimated time: 15-20 minutes")
    print("=" * 60)

    sanitizer = CPSan(log_path="results/injecagent_log.jsonl")
    results = []
    neutralized = 0
    cats = defaultdict(lambda: {"total": 0, "neutralized": 0})

    for i, scenario in enumerate(scenarios):

        # Progress every 20 scenarios
        if (i + 1) % 20 == 0:
            asr_so_far = round((i + 1 - neutralized) / (i + 1) * 100, 1)
            print(f"  Progress: {i+1}/{len(scenarios)} | ASR so far: {asr_so_far}%")

        try:
            sanitized_params, action = sanitizer.process(
                tool_name=scenario["tool"],
                parameters=scenario["injected_params"],
                user_task=scenario["user_task"]
            )

            caught = action in ["SANITIZED", "BLOCKED"]
            if caught:
                neutralized += 1

            cats[scenario["category"]]["total"] += 1
            if caught:
                cats[scenario["category"]]["neutralized"] += 1

            results.append({
                "scenario_id": scenario["id"],
                "category": scenario["category"],
                "user_task": scenario["user_task"][:60],
                "tool": scenario["tool"],
                "action": action,
                "neutralized": caught,
                "source": scenario.get("source", "injecagent")
            })

        except Exception as e:
            print(f"  Error on {scenario['id']}: {e}")
            time.sleep(3)

    # Save results
    os.makedirs("results", exist_ok=True)
    with open("results/injecagent_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "category", "user_task",
            "tool", "action", "neutralized", "source"
        ])
        writer.writeheader()
        writer.writerows(results)

    # Category breakdown
    total = len(results)
    asr = round((total - neutralized) / total * 100, 1)

    print(f"\n{'='*60}")
    print(f"INJECAGENT EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"{'Category':<20} {'Total':>6} {'Caught':>7} {'ASR':>7}")
    print(f"{'-'*60}")
    for cat, data in sorted(cats.items()):
        cat_asr = round(
            (data["total"] - data["neutralized"]) / data["total"] * 100, 1
        )
        print(f"{cat:<20} {data['total']:>6} {data['neutralized']:>7} {cat_asr:>6}%")
    print(f"{'='*60}")
    print(f"Total scenarios:  {total}")
    print(f"Neutralized:      {neutralized}")
    print(f"ASR After CP-SAN: {asr}%")
    print(f"{'='*60}")
    print(f"\nSaved to results/injecagent_results.csv")


if __name__ == "__main__":
    run_injecagent_evaluation()