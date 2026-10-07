import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Update RouteCard definition
content = content.replace(
    "function RouteCard({ route, selected, onClick, onSave }) {",
    "function RouteCard({ route, selected, onClick, onSave, destination }) {"
)

# Update RouteCard calls
content = content.replace(
    "<RouteCard key={route.id} route={route} selected={route.id === selectedId} onClick={() => setSelectedId(route.id)} />",
    "<RouteCard key={route.id} route={route} selected={route.id === selectedId} onClick={() => setSelectedId(route.id)} destination={destination} />"
)

# Update RouteCard TTS script
old_btn_tts = "const text = `Route ${route.name}. Distance: ${distKm} kilometers. Time: ${route.time_mins} minutes. Accessibility Score: ${route.accessibility_score ?? route.personalized_score ?? 0} out of 100. ${route.pareto_status ? 'Status: ' + route.pareto_status.replaceAll('_', ' ') : ''}.`;"

new_btn_tts = "const text = `Hi! You want to go to ${destination || 'this place'}? Good choice! For this route, the distance is ${distKm} kilometers, and it takes ${route.time_mins} minutes. The accessibility score is ${route.accessibility_score ?? route.personalized_score ?? 0} out of 100.`;"

content = content.replace(old_btn_tts, new_btn_tts)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("RouteCard TTS updated with greeting.")
