import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the auto-tts logic in findRoutes
old_tts = """        let text = `I found ${fetchedRoutes.length} routes to your destination. `;
        text += `The recommended accessible route is ${distKm} kilometers and takes approximately ${timeMin} minutes. `;
        text += `It has an accessibility score of ${score} out of 100. `;
        if (fetchedRoutes.length > 1) {
            text += `I have also provided alternative routes for you to compare.`;
        }"""

new_tts = """        let text = `Hi! You want to go to ${destination}? Great choice! `;
        text += `I found ${fetchedRoutes.length} routes to your destination. `;
        text += `The recommended accessible route is ${distKm} kilometers and takes approximately ${timeMin} minutes. `;
        text += `It has an accessibility score of ${score} out of 100. `;
        if (fetchedRoutes.length > 1) {
            text += `I have also provided alternative routes for you to compare.`;
        }"""

content = content.replace(old_tts, new_tts)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Auto-TTS updated with greeting.")
