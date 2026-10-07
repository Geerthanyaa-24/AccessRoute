import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add ArrowUpToLine correctly
if "ArrowUpToLine" not in content[:2000]:  # Only check imports area
    content = content.replace("} from 'lucide-react';", "  ArrowUpToLine,\n} from 'lucide-react';")
    
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Added ArrowUpToLine to imports.")
