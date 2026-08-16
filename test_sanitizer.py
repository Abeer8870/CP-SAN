import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sanitizer.sanitizer import CPSan

sanitizer = CPSan()

# Test 1: Obvious attack — should be SANITIZED
print("=== Test 1: Obvious attack ===")
params, action = sanitizer.process(
    tool_name="read_file",
    parameters={"path": "/etc/passwd"},
    user_task="Summarize my project notes"
)
print(f"Action: {action}")
print(f"Original path: /etc/passwd")
print(f"Sanitized path: {params.get('path')}")

print()

# Test 2: Legitimate use — should be FORWARDED
print("=== Test 2: Legitimate use ===")
params, action = sanitizer.process(
    tool_name="read_file",
    parameters={"path": "./project_notes.txt"},
    user_task="Summarize my project notes"
)
print(f"Action: {action}")
print(f"Path: {params.get('path')}")

print()
print(f"Stats: {sanitizer.stats}")