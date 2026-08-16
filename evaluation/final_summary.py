# Save as evaluation/final_summary.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

results = {
    "attack_scenarios": 116,
    "legitimate_scenarios": 100,
    "ablation": {
        "no_defense": 100.0,
        "pattern_only": 37.9,
        "llm_only": 13.8,
        "cpsan_full": 7.8
    },
    "category_breakdown": {
        "Exfiltration": {"total": 25, "asr": 20.0},
        "Lateral Movement": {"total": 25, "asr": 0.0},
        "Persistence": {"total": 20, "asr": 0.0},
        "Privilege Escalation": {"total": 22, "asr": 4.5},
        "Semantic Deception": {"total": 24, "asr": 12.5}
    },
    "task_completion_rate": 99.0,
    "false_positive_rate": 1.0
}

import json
os.makedirs("results", exist_ok=True)
with open("results/final_summary.json", "w") as f:
    json.dump(results, f, indent=2)

print("Final results saved to results/final_summary.json")
print()
print("KEY METRICS:")
print(f"  ASR Before CP-SAN:  100.0%")
print(f"  ASR After CP-SAN:   7.8%")
print(f"  TCR:                99.0%")
print(f"  FPR:                1.0%")