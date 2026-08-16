import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import time
from collections import defaultdict
from attacks.scenarios import SCENARIOS
from sanitizer.classifier import check_scope
from tools.tool_registry import TOOL_REGISTRY


def run_cpsan_full():
    print(f"Running: CP-SAN Full on {len(SCENARIOS)} scenarios...")
    print(f"Estimated time: 25-35 minutes")
    print("=" * 60)

    stats = {"total": 0, "neutralized": 0, "missed": 0}
    results = []

    for i, scenario in enumerate(SCENARIOS):
        stats["total"] += 1
        tool_name = scenario["tool"]
        parameters = scenario["injected_params"]
        user_task = scenario["user_task"]

        # Progress every 20 scenarios
        if (i + 1) % 20 == 0:
            asr_so_far = round(
                (stats["total"] - stats["neutralized"]) / stats["total"] * 100, 1
            )
            print(f"  Progress: {i+1}/{len(SCENARIOS)} | ASR so far: {asr_so_far}%")

        if tool_name not in TOOL_REGISTRY:
            stats["neutralized"] += 1
            results.append({
                "scenario_id": scenario["id"],
                "category": scenario["category"],
                "action": "BLOCKED",
                "neutralized": True,
                "config": "CP-SAN Full"
            })
            continue

        tool_def = TOOL_REGISTRY[tool_name]
        any_flagged = False

        for param_name, param_value in parameters.items():
            if param_name not in tool_def["allowed_params"]:
                continue

            param_def = tool_def["allowed_params"][param_name]
            flagged = False

            # Layer 1: Pattern matching (fast, no API call)
            value_lower = str(param_value).lower()
            pattern_hit = any(
                p.lower() in value_lower
                for p in param_def["forbidden_patterns"]
            )

            if pattern_hit:
                flagged = True

            # Layer 2: LLM semantic check
            # Only call if pattern didn't already catch it
            if not flagged:
                try:
                    scope_match = check_scope(
                        tool_name=tool_name,
                        param_name=param_name,
                        param_value=param_value,
                        declared_scope=param_def["scope"],
                        user_task=user_task
                    )
                    if not scope_match:
                        flagged = True

                except Exception as e:
                    print(f"  Error on {scenario['id']}: {e}")

            if flagged:
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
            "config": "CP-SAN Full"
        })

    # Save results
    os.makedirs("results", exist_ok=True)
    with open("results/cpsan_full.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "category", "action", "neutralized", "config"
        ])
        writer.writeheader()
        writer.writerows(results)

    # Category breakdown
    cats = defaultdict(lambda: {"total": 0, "neutralized": 0})
    for r in results:
        cats[r["category"]]["total"] += 1
        if r["neutralized"]:
            cats[r["category"]]["neutralized"] += 1

    total = stats["total"]
    asr = round(stats["missed"] / total * 100, 1)

    print(f"\n{'='*60}")
    print(f"RESULTS: CP-SAN Full")
    print(f"{'='*60}")
    print(f"{'Category':<30} {'Total':>6} {'Caught':>7} {'ASR':>7}")
    print(f"{'-'*60}")
    for cat, data in sorted(cats.items()):
        cat_asr = round(
            (data["total"] - data["neutralized"]) / data["total"] * 100, 1
        )
        print(f"{cat:<30} {data['total']:>6} {data['neutralized']:>7} {cat_asr:>6}%")
    print(f"{'='*60}")
    print(f"Total scenarios: {total}")
    print(f"Neutralized:     {stats['neutralized']}")
    print(f"Missed:          {stats['missed']}")
    print(f"ASR:             {asr}%")
    print(f"Saved to results/cpsan_full.csv")


if __name__ == "__main__":
    run_cpsan_full()