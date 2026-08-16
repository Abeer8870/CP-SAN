import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

# Load the approved IDs
with open("results/scenarios_to_keep.json") as f:
    ids_to_keep = set(json.load(f))

# Load generated scenarios
with open("attacks/generated_scenarios.json") as f:
    generated = json.load(f)

# Filter out removed ones
cleaned = [s for s in generated if s["id"] in ids_to_keep]

# How many were removed
removed = len(generated) - len(cleaned)
print(f"Original generated: {len(generated)}")
print(f"Removed:            {removed}")
print(f"Remaining:          {len(cleaned)}")

# Save cleaned file
with open("attacks/generated_scenarios.json", "w") as f:
    json.dump(cleaned, f, indent=2)

print(f"\n✓ generated_scenarios.json updated with {len(cleaned)} clean scenarios")

# Verify total
from attacks.scenarios import SCENARIOS
print(f"Total scenarios now: {len(SCENARIOS)}")
