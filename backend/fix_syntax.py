import sys

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix f-string 1
bad_str1 = '''            {"role": "user", "content": f"Context: {json.dumps(request.travel_context)}

Question: {request.message}"}'''
good_str1 = '            {"role": "user", "content": f"Context: {json.dumps(request.travel_context)}\\n\\nQuestion: {request.message}"}'

# Fix string 2
bad_str2 = '''    response += "

*[Note: Add your OPENAI_API_KEY to the .env file to unlock the full Generative AI Chatbot instead of this offline contextual mode!]*"'''
good_str2 = '    response += "\\n\\n*[Note: Add your OPENAI_API_KEY to the .env file to unlock the full Generative AI Chatbot instead of this offline contextual mode!]*"'

content = content.replace(bad_str1, good_str1)
content = content.replace(bad_str2, good_str2)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
