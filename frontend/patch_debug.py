import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Inject console.log
old_load = """        const d = await r.json();
        if (active) setMetrics(d);"""

new_load = """        const d = await r.json();
        console.log('Metrics loaded:', d);
        if (active) setMetrics(d);"""

if "console.log('Metrics loaded:'" not in content:
    content = content.replace(old_load, new_load)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected console.log")
else:
    print("Already injected")
