from tools.tool_registry import TOOL_REGISTRY
from attacks.scenarios import SCENARIOS
print(f"Scenarios loaded: {len(SCENARIOS)}")
print(f"Tools loaded: {len(TOOL_REGISTRY)}")
for tool_name, tool_def in TOOL_REGISTRY.items():
    print(f"  - {tool_name}: {tool_def['risk_level']} risk")