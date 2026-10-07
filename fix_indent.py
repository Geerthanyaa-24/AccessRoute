import re, textwrap

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

def replacer(match):
    dedented_string = textwrap.dedent(match.group(1))
    return 'st.markdown("""' + dedented_string + '"""'

new_content = re.sub(r'st\.markdown\(\s*\"\"\"(.*?)\"\"\"', replacer, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
