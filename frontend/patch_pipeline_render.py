import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make the replacement using regex to handle whitespace
old_str = r"\{\/\* RESULTS AREA \*\/\}\s*\{plan && \("
new_str = "{/* RESULTS AREA */}\n      {loading && <LoadingPipeline formData={formData} />}\n      {plan && !loading && ("

content = re.sub(old_str, new_str, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("LoadingPipeline injected successfully via regex.")
