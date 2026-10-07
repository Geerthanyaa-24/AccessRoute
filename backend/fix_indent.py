import re

filepath = 'backend/main.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("return {'status': 'verified', 'report': report}") or \
       stripped.startswith("return {'status': 'rejected', 'report': report}") or \
       stripped.startswith('return {"status": "resolved", "report": report}'):
        lines[i] = "        " + stripped + "\n"

with open(filepath, 'w') as f:
    f.writelines(lines)
print("Indentation fixed.")
