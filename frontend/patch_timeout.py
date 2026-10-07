import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Increase custom setTimeout to 30000
content = re.sub(
    r'const timeout = window\.setTimeout\(\(\) => reject\(\{ code: 3 \}\), 10000\);',
    'const timeout = window.setTimeout(() => reject({ code: 3 }), 30000);',
    content
)

# Increase native geolocation timeout to 30000 and enable High Accuracy which sometimes forces Windows Location Service to wake up
content = re.sub(
    r'\{ enableHighAccuracy: false, maximumAge: 60000, timeout: 10000 \}',
    '{ enableHighAccuracy: true, maximumAge: 60000, timeout: 30000 }',
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Timeout extended.")
