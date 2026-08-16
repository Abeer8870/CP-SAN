import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from collections import defaultdict
from attacks.scenarios import SCENARIOS
from tools.tool_registry import TOOL_REGISTRY

def run_pattern_only():
    print(f"Running: Pattern Only on {len(SCENARIOS)} scenarios...")
    print("=" * 60)

    stats = {"total": 0, "neutralized": 0, "missed": 0}
    results = []

    for scenario in SCENARIOS:
        stats["total"] += 1
        tool_name = scenario["tool"]
        parameters = scenario["injected_params"]

        if tool_name not in TOOL_REGISTRY:
            stats["neutralized"] += 1
            results.append({
                "scenario_id": scenario["id"],
                "category": scenario["category"],
                "action": "BLOCKED",
                "neutralized": True,
                "config": "Pattern Only"
            })
            continue

        tool_def = TOOL_REGISTRY[tool_name]
        any_flagged = False

        for param_name, param_value in parameters.items():
            if param_name not in tool_def["allowed_params"]:
                continue

            param_def = tool_def["allowed_params"][param_name]
            value_lower = str(param_value).lower()

            pattern_hit = any(
                p.lower() in value_lower
                for p in param_def["forbidden_patterns"]
            )

            if pattern_hit:
                any_flagged = True

        action = "SANITIZED" if any_flagged else "FORWARDED"
        neutralized = any_flagged

        if neutralized:
            stats["neutralized"] += 1
        else:
            stats["missed"] += 1

        results.append({
            "scenario_id": scenario["id"],
            "category": scenario["category"],
            "action": action,
            "neutralized": neutralized,
            "config": "Pattern Only"
        })

    # Category breakdown
    cats = defaultdict(lambda: {"total": 0, "neutralized": 0})
    for r in results:
        cats[r["category"]]["total"] += 1
        if r["neutralized"]:
            cats[r["category"]]["neutralized"] += 1

    print(f"\n{'Category':<30} {'Total':>6} {'Caught':>7} {'ASR':>7}")
    print(f"{'-'*60}")
    for cat, data in sorted(cats.items()):
        asr = round(
            (data["total"] - data["neutralized"]) / data["total"] * 100, 1
        )
        print(f"{cat:<30} {data['total']:>6} {data['neutralized']:>7} {asr:>6}%")

    # Save
    os.makedirs("results", exist_ok=True)
    with open("results/pattern_only.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "category", "action", "neutralized", "config"
        ])
        writer.writeheader()
        writer.writerows(results)

    total = stats["total"]
    asr = round(stats["missed"] / total * 100, 1)

    print(f"{'='*60}")
    print(f"Total scenarios: {total}")
    print(f"Neutralized:     {stats['neutralized']}")
    print(f"Missed:          {stats['missed']}")
    print(f"ASR:             {asr}%")
    print(f"Saved to results/pattern_only.csv")

if __name__ == "__main__":
    run_pattern_only()