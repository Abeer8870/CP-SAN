import json

with open("results/legitimate_log.jsonl") as f:
    for line in f:
        entry = json.loads(line)
        if entry["action"] != "FORWARDED":
            print(json.dumps(entry, indent=2))