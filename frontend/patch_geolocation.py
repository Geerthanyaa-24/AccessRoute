import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: DashboardPage mapCenter
old_mapcenter = """  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setMapCenter([pos.coords.latitude, pos.coords.longitude]),
        (err) => console.log('Location access denied or failed', err),
        { enableHighAccuracy: true }
      );
    }
  }, []);"""

new_mapcenter = """  useEffect(() => {
    getDeviceLocation().then(pos => {
      setMapCenter([pos.coords.latitude, pos.coords.longitude]);
    }).catch(err => console.log('Location access denied or failed', err));
  }, []);"""

# Fix 2: useCurrentLocation in FindRoutePage or anywhere else
old_use_curr = """    navigator.geolocation.getCurrentPosition(
      async pos => {
        const { latitude, longitude } = pos.coords;"""

new_use_curr = """    getDeviceLocation().then(async pos => {
        const { latitude, longitude } = pos.coords;"""

content = content.replace(old_mapcenter, new_mapcenter)
content = content.replace(old_use_curr, new_use_curr)
content = content.replace("navigator.geolocation.getCurrentPosition", "getDeviceLocation().then") # catch any remaining

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Geolocation mock patched globally.")
