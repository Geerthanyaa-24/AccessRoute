import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# We'll completely replace getDeviceLocation to just mock a Chennai location for demo purposes.
start_marker = "function getDeviceLocation() {"
end_marker = "function locationErrorMessage(error) {"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

new_func = """function getDeviceLocation() {
  return new Promise((resolve) => {
    // For this specific AccessRoute Demo (which uses Chennai OSM dataset),
    // we bypass actual IP geolocation if you are out of state, to prevent 
    // 2,000+ km pedestrian routing errors from Valhalla.
    console.log("Mocking device location to Chennai for demo routing compatibility.");
    resolve({ coords: { latitude: 13.06, longitude: 80.24 } });
  });
}
"""

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_func + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Mock location applied.")
