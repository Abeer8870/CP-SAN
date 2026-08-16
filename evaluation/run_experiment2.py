import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import time
from attacks.scenarios import SCENARIOS

# Import components separately for ablation
from sanitizer.classifier import check_scope
from sanitizer.rewriter import rewrite_parameter
from tools.tool_registry import TOOL_REGISTRY


def run_with_config(use_patterns=True, use_llm=True, label="CP-SAN"):
    """Run experiment with specific configuration for ablation study."""

    stats = {"total": 0, "sanitized": 0, "forwarded": 0, "blocked": 0}
    results = []

    for scenario in SCENARIOS:
        stats["total"] += 1
        tool_name = scenario["tool"]
        parameters = scenario["injected_params"]
        user_task = scenario["user_task"]

        if tool_name not in TOOL_REGISTRY:
            stats["blocked"] += 1
            results.append({
                "scenario_id": scenario["id"],
                "category": scenario["category"],
                "action": "BLOCKED",
                "neutralized": True,
                "config": label
            })
            continue

        tool_def = TOOL_REGISTRY[tool_name]
        any_sanitized = False

        for param_name, param_value in parameters.items():
            if param_name not in tool_def["allowed_params"]:
                continue

            param_def = tool_def["allowed_params"][param_name]
            flagged = False

            # Layer 1: Pattern matching
            if use_patterns:
                value_lower = str(param_value).lower()
                pattern_hit = any(
                    p.lower() in value_lower
                    for p in param_def["forbidden_patterns"]
                )
                if pattern_hit:
                    flagged = True

            # Layer 2: LLM semantic check
            if use_llm and not flagged:
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
                    time.sleep(1)  # rate limiting
                except Exception as e:
                    print(f"LLM error: {e}")

            if flagged:
                any_sanitized = True

        action = "SANITIZED" if any_sanitized else "FORWARDED"
        neutralized = action == "SANITIZED"

        if neutralized:
            stats["sanitized"] += 1
        else:
            stats["forwarded"] += 1

        results.append({
            "scenario_id": scenario["id"],
            "category": scenario["category"],
            "action": action,
            "neutralized": neutralized,
            "config": label
        })

    return stats, results


def compute_asr(stats):
    total = stats["total"]
    missed = stats["forwarded"]
    return round((missed / total) * 100, 1)


def print_category_breakdown(results, label):
    from collections import defaultdict
    cats = defaultdict(lambda: {"total": 0, "neutralized": 0})
    for r in results:
        cats[r["category"]]["total"] += 1
        if r["neutralized"]:
            cats[r["category"]]["neutralized"] += 1

    print(f"\n--- {label} ---")
    print(f"{'Category':<25} {'Total':>6} {'Caught':>7} {'ASR':>7}")
    for cat, data in sorted(cats.items()):
        asr = round((data["total"] - data["neutralized"]) / data["total"] * 100, 1)
        print(f"{cat:<25} {data['total']:>6} {data['neutralized']:>7} {asr:>6}%")


def main():
    all_results = []

    configs = [
        {"use_patterns": False, "use_llm": False, "label": "No Defense"},
        {"use_patterns": True,  "use_llm": False, "label": "Pattern Only"},
        {"use_patterns": False, "use_llm": True,  "label": "LLM Only"},
        {"use_patterns": True,  "use_llm": True,  "label": "CP-SAN (Full)"},
    ]

    print(f"Running ablation study on {len(SCENARIOS)} scenarios...")
    print(f"{'='*60}")

    summary = []

    for config in configs:
        print(f"\nRunning: {config['label']}...")

        if config["label"] == "No Defense":
            # No defense = everything forwarded
            stats = {
                "total": len(SCENARIOS),
                "sanitized": 0,
                "forwarded": len(SCENARIOS),
                "blocked": 0
            }
            results = [{
                "scenario_id": s["id"],
                "category": s["category"],
                "action": "FORWARDED",
                "neutralized": False,
                "config": "No Defense"
            } for s in SCENARIOS]
        else:
            stats, results = run_with_config(
                use_patterns=config["use_patterns"],
                use_llm=config["use_llm"],
                label=config["label"]
            )

        asr = compute_asr(stats)
        print_category_breakdown(results, config["label"])
        summary.append({"label": config["label"], "asr": asr, "stats": stats})
        all_results.extend(results)

    # Save all results
    os.makedirs("results", exist_ok=True)
    with open("results/ablation_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["scenario_id", "category", "action", "neutralized", "config"])
        writer.writeheader()
        writer.writerows(all_results)

    # Print summary table
    print(f"\n{'='*60}")
    print("ABLATION STUDY SUMMARY")
    print(f"{'='*60}")
    print(f"{'Configuration':<20} {'Neutralized':>12} {'ASR After':>10}")
    print(f"{'='*60}")
    for s in summary:
        neutralized = s["stats"]["sanitized"] + s["stats"]["blocked"]
        print(f"{s['label']:<20} {neutralized:>12} {s['asr']:>9}%")
    print(f"{'='*60}")
    print(f"\nResults saved to results/ablation_results.csv")


if __name__ == "__main__":
    main()