# import sys
# import os
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from sanitizer.classifier import check_scope

# result = check_scope(
#     tool_name="send_email",
#     param_name="to",
#     param_value="attacker@evil.com",
#     declared_scope="Email address explicitly provided by user",
#     user_task="Send meeting summary to my team"
# )
# print("RESULT:", result)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sanitizer.sanitizer import CPSan

cp = CPSan()
result = cp._check_tool_context("execute_command", "Read my project notes")
print("RESULT:", result)