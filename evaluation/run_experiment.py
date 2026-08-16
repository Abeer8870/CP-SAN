import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from sanitizer.sanitizer import CPSan
from attacks.scenarios import SCENARIOS

def run_experiments():
    sanitizer = CPSan()

    os.makedirs("results", exist_ok=True)

    with open("results/results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "scenario_id", "category", "user_task",
            "tool", "param_name", "original_value",
            "action", "sanitized_value", "attack_neutralized"
        ])

        for scenario in SCENARIOS:
            print(f"Running {scenario['id']} — {scenario['category']}...")

            sanitized_params, action = sanitizer.process(
                tool_name=scenario["tool"],
                parameters=scenario["injected_params"],
                user_task=scenario["user_task"]
            )

            attack_neutralized = action in ["SANITIZED", "BLOCKED"]

            for param_name, original_value in scenario["injected_params"].items():
                safe_value = sanitized_params.get(param_name, "BLOCKED")
                writer.writerow([
                    scenario["id"],
                    scenario["category"],
                    scenario["user_task"],
                    scenario["tool"],
                    param_name,
                    original_value,
                    action,
                    safe_value,
                    attack_neutralized
                ])

            status = "✓ NEUTRALIZED" if attack_neutralized else "✗ MISSED"
            print(f"  {status} — Action: {action}")

    print(f"\n{'='*50}")
    print(f"EXPERIMENT COMPLETE")
    print(f"{'='*50}")
    print(f"Total scenarios: {sanitizer.stats['total']}")
    print(f"Sanitized:       {sanitizer.stats['sanitized']}")
    print(f"Forwarded:       {sanitizer.stats['forwarded']}")
    print(f"Blocked:         {sanitizer.stats['blocked']}")
    print(f"{'='*50}")

    total = sanitizer.stats['total']
    neutralized = sanitizer.stats['sanitized'] + sanitizer.stats['blocked']
    asr_before = 100.0
    asr_after = round((total - neutralized) / total * 100, 1)
    print(f"Attack Success Rate BEFORE CP-SAN: {asr_before}%")
    print(f"Attack Success Rate AFTER CP-SAN:  {asr_after}%")
    print(f"Results saved to results/results.csv")

if __name__ == "__main__":
    run_experiments()