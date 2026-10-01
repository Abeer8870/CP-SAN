import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import json
import time
from sanitizer.sanitizer import CPSan
from attacks.legitimate_scenarios import LEGITIMATE_SCENARIOS

# Load generated legitimate scenarios
_gen_path = "attacks/generated_legitimate.json"
if os.path.exists(_gen_path):
    with open(_gen_path) as f:
        _generated = json.load(f)

    _converted = []
    for i, s in enumerate(_generated):
        _converted.append({
            "id": s.get("id", f"GEN{i:03d}"),
            "category": "Legitimate",
            "user_task": s.get("user_task", ""),
            "tool": s.get("tool", ""),
            "params": s.get("params", {}),
            "should_forward": True
        })

    ALL_LEGITIMATE = LEGITIMATE_SCENARIOS + _converted
    print(f"Loaded {len(LEGITIMATE_SCENARIOS)} handcrafted + "
          f"{len(_converted)} generated = {len(ALL_LEGITIMATE)} total legitimate scenarios")
else:
    ALL_LEGITIMATE = LEGITIMATE_SCENARIOS
    print(f"No generated scenarios found — using {len(ALL_LEGITIMATE)} handcrafted only")


def run_legitimate_test():
    sanitizer = CPSan(log_path="results/legitimate_log.jsonl")

    correctly_forwarded = 0
    incorrectly_sanitized = 0
    results = []

    print(f"\nTesting {len(ALL_LEGITIMATE)} legitimate scenarios...")
    print("=" * 60)

    for scenario in ALL_LEGITIMATE:
        print(f"Testing {scenario['id']}...", end=" ")

        # Handle both 'params' and 'injected_params' keys
        parameters = scenario.get("params", scenario.get("injected_params", {}))

        if not parameters:
            print("SKIPPED (no parameters)")
            continue

        if not scenario.get("tool"):
            print("SKIPPED (no tool)")
            continue

        try:
            sanitized_params, action = sanitizer.process(
                tool_name=scenario["tool"],
                parameters=parameters,
                user_task=scenario["user_task"]
            )

            # Legitimate scenarios should always be FORWARDED
            correct = action == "FORWARDED"

            if correct:
                correctly_forwarded += 1
                print("✓ FORWARDED (correct)")
            else:
                incorrectly_sanitized += 1
                print(f"✗ {action} (incorrect — false positive)")
                print(f"   Task:   {scenario['user_task']}")
                print(f"   Params: {parameters}")

            results.append({
                "scenario_id": scenario["id"],
                "category": scenario.get("category", "Legitimate"),
                "user_task": scenario["user_task"],
                "tool": scenario["tool"],
                "parameters": str(parameters),
                "action": action,
                "correct": correct
            })

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "scenario_id": scenario["id"],
                "category": scenario.get("category", "Legitimate"),
                "user_task": scenario["user_task"],
                "tool": scenario.get("tool", "unknown"),
                "parameters": str(parameters),
                "action": "ERROR",
                "correct": False
            })

        time.sleep(1)

    # Save results
    os.makedirs("results", exist_ok=True)
    with open("results/task_completion.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "category", "user_task",
            "tool", "parameters", "action", "correct"
        ])
        writer.writeheader()
        writer.writerows(results)

    # Category breakdown
    from collections import defaultdict
    cats = defaultdict(lambda: {"total": 0, "correct": 0})
    for r in results:
        cats[r["tool"]]["total"] += 1
        if r["correct"]:
            cats[r["tool"]]["correct"] += 1

    total = len(results)
    tcr = round(correctly_forwarded / total * 100, 1) if total > 0 else 0
    fpr = round(incorrectly_sanitized / total * 100, 1) if total > 0 else 0

    # Print summary
    print(f"\n{'='*60}")
    print("TASK COMPLETION RATE — BREAKDOWN BY TOOL")
    print(f"{'='*60}")
    print(f"{'Tool':<20} {'Total':>6} {'Correct':>8} {'TCR':>7}")
    print(f"{'-'*60}")
    for tool, data in sorted(cats.items()):
        tool_tcr = round(data["correct"] / data["total"] * 100, 1) if data["total"] > 0 else 0
        print(f"{tool:<20} {data['total']:>6} {data['correct']:>8} {tool_tcr:>6}%")

    print(f"\n{'='*60}")
    print("TASK COMPLETION RATE (TCR) RESULTS")
    print(f"{'='*60}")
    print(f"Total legitimate scenarios: {total}")
    print(f"Correctly forwarded:        {correctly_forwarded}")
    print(f"Incorrectly sanitized:      {incorrectly_sanitized}")
    print(f"Task Completion Rate:       {tcr}%")
    print(f"False Positive Rate:        {fpr}%")
    print(f"{'='*60}")

    if incorrectly_sanitized > 0:
        print(f"\nFALSE POSITIVES — Scenarios incorrectly blocked:")
        print(f"{'-'*60}")
        for r in results:
            if not r["correct"]:
                print(f"  {r['scenario_id']}: {r['user_task'][:50]}")
                print(f"    Tool: {r['tool']} | Action: {r['action']}")

    print(f"\nResults saved to results/task_completion.csv")
    return tcr, fpr


if __name__ == "__main__":
    tcr, fpr = run_legitimate_test()

    print(f"\n{'='*60}")
    print("FINAL METRICS SUMMARY")
    print(f"{'='*60}")
    print(f"Task Completion Rate:          {tcr}%")
    print(f"False Positive Rate:           {fpr}%")
    print(f"{'='*60}")