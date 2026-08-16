import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import time
from collections import defaultdict
from attacks.scenarios import SCENARIOS
from sanitizer.classifier import check_scope
from tools.tool_registry import TOOL_REGISTRY


def run_llm_only():
    print(f"Running: LLM Only on {len(SCENARIOS)} scenarios...")
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
            neutralized_so_far = stats["neutralized"]
            asr_so_far = round((stats["total"] - neutralized_so_far) / stats["total"] * 100, 1)
            print(f"  Progress: {i+1}/{len(SCENARIOS)} | ASR so far: {asr_so_far}%")

        if tool_name not in TOOL_REGISTRY:
            stats["neutralized"] += 1
            results.append({
                "scenario_id": scenario["id"],
                "category": scenario["category"],
                "action": "BLOCKED",
                "neutralized": True,
                "config": "LLM Only"
            })
            continue

        tool_def = TOOL_REGISTRY[tool_name]
        any_flagged = False

        for param_name, param_value in parameters.items():
            if param_name not in tool_def["allowed_params"]:
                continue

            param_def = tool_def["allowed_params"][param_name]

            try:
                scope_match = check_scope(
                    tool_name=tool_name,
                    param_name=param_name,
                    param_value=param_value,
                    declared_scope=param_def["scope"],
                    user_task=user_task
                )
                if not scope_match:
                    any_flagged = True

            except Exception as e:
                print(f"  Error on {scenario['id']}: {e}")

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
            "config": "LLM Only"
        })

    # Save results immediately
    os.makedirs("results", exist_ok=True)
    with open("results/llm_only.csv", "w", newline="") as f:
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
    print(f"RESULTS: LLM Only")
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
    print(f"Saved to results/llm_only.csv")


if __name__ == "__main__":
    run_llm_only()