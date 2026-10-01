import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sanitizer.sanitizer import CPSan

cp = CPSan()
result = cp._check_tool_context("execute_command", "Read my project notes")
print("RESULT:", result)