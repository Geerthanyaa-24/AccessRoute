import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old function regex (we'll replace everything from `function getDeviceLocation() {` to `}` before `function locationErrorMessage`)
start_marker = "function getDeviceLocation() {"
end_marker = "function locationErrorMessage(error) {"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find getDeviceLocation boundaries")
    exit(1)

new_func = """function getDeviceLocation() {
  return new Promise((resolve) => {
    const fallback = () => {
      console.warn("Native geolocation failed. Falling back to IP location...");
      fetch('https://get.geojs.io/v1/ip/geo.json')
        .then(r => r.json())
        .then(d => {
          if (d.latitude && d.longitude) {
            resolve({ coords: { latitude: parseFloat(d.latitude), longitude: parseFloat(d.longitude) } });
          } else {
            resolve({ coords: { latitude: 13.06, longitude: 80.24 } });
          }
        })
        .catch(() => {
          resolve({ coords: { latitude: 13.06, longitude: 80.24 } });
        });
    };

    if (!navigator.geolocation) return fallback();

    const timeout = window.setTimeout(fallback, 8000);

    navigator.geolocation.getCurrentPosition(
      p => { window.clearTimeout(timeout); resolve(p); },
      e => { window.clearTimeout(timeout); fallback(); },
      { enableHighAccuracy: false, maximumAge: 60000, timeout: 7000 }
    );
  });
}
"""

content = content[:start_idx] + new_func + content[end_idx:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("IP Fallback implemented.")
