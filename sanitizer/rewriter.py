import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SAFE_DEFAULTS = {
    "read_file": {"path": "./user_document.txt"},
    "send_email": {"to": "user@localhost", "body": "[sanitized content]"},
    "execute_command": {"command": "echo 'command sanitized'"},
    "write_file": {"path": "./output.txt", "content": "[sanitized]"},
    "list_directory": {"path": "./"}
}

def rewrite_parameter(tool_name, param_name, original_value, user_task):
    """
    Rewrites a suspicious parameter to a safe equivalent
    that still serves the user's task where possible.
    """

    prompt = f"""You are a security rewriter for an AI agent system.

A parameter value was flagged as potentially dangerous or out-of-scope.

Tool: {tool_name}
Parameter: {param_name}
Flagged value: "{original_value}"
User's actual task: "{user_task}"

Rewrite this parameter to a safe value that:
1. Still helps complete the user's legitimate task if possible
2. Does not access sensitive paths, external systems, or credentials
3. Is a minimal, conservative version of the original intent

Return ONLY the rewritten value, nothing else.
If no safe rewrite is possible, return exactly: SAFE_DEFAULT"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0
        )
        rewritten = response.choices[0].message.content.strip()

        if rewritten == "SAFE_DEFAULT" or not rewritten:
            return SAFE_DEFAULTS.get(tool_name, {}).get(param_name, "")

        return rewritten

    except Exception as e:
        print(f"Rewriter error: {e}")
        return SAFE_DEFAULTS.get(tool_name, {}).get(param_name, "")