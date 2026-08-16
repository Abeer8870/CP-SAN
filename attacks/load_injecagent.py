import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

INJECAGENT_PATH = "InjecAgent/data"

TOOL_MAP = {
    "Gmail": "send_email",
    "Google Calendar": "write_file",
    "Dropbox": "read_file",
    "Slack": "send_email",
    "FileManager": "read_file",
    "Terminal": "execute_command",
    "Browser": "read_file",
    "Google Drive": "read_file",
    "OneDrive": "read_file",
    "Outlook": "send_email",
    "default": "execute_command"
}

def load_injecagent(max_scenarios=100):
    scenarios = []

    files = [
        "test_cases_dh_base.json",
        "test_cases_ds_base.json"
    ]

    for filename in files:
        filepath = os.path.join(INJECAGENT_PATH, filename)
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue

        with open(filepath) as f:
            data = json.load(f)

        print(f"Processing {len(data)} cases from {filename}...")

        for i, record in enumerate(data):
            if len(scenarios) >= max_scenarios:
                break

            # Correct field names from actual data
            user_task = str(record.get("User Instruction", "")).strip()
            attack_instruction = str(record.get("Attacker Instruction", "")).strip()
            user_tool = str(record.get("User Tool", "")).strip()

            if not attack_instruction or not user_task:
                continue

            # Truncate long instructions
            attack_instruction = attack_instruction[:200]

            # Map tool
            tool_name = TOOL_MAP.get(user_tool, TOOL_MAP["default"])

            # Build params based on tool
            if tool_name == "send_email":
                params = {
                    "to": "attacker@external.com",
                    "body": attack_instruction
                }
            elif tool_name == "execute_command":
                params = {"command": attack_instruction}
            else:
                params = {"path": attack_instruction}

            scenario = {
                "id": f"IA{len(scenarios):04d}",
                "category": "InjecAgent-DH" if "dh" in filename else "InjecAgent-DS",
                "user_task": user_task,
                "tool": tool_name,
                "injected_params": params,
                "safe_params": {},
                "source": filename
            }
            scenarios.append(scenario)

    print(f"\nTotal converted: {len(scenarios)} scenarios")
    return scenarios


if __name__ == "__main__":
    scenarios = load_injecagent(100)

    if scenarios:
        print(f"\nSample converted scenario:")
        print(json.dumps(scenarios[0], indent=2))

        # Save
        with open("attacks/injecagent_scenarios.json", "w") as f:
            json.dump(scenarios, f, indent=2)
        print(f"\nSaved {len(scenarios)} scenarios to attacks/injecagent_scenarios.json")
    else:
        print("Still no scenarios — check data manually")