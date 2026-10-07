import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add MapUpdater if missing
if "function MapUpdater({ center })" not in content:
    updater_component = """
function MapUpdater({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, map.getZoom());
    }
  }, [center, map]);
  return null;
}
"""
    # Inject it before DashboardPage
    content = content.replace("function DashboardPage({", updater_component + "\nfunction DashboardPage({")

dashboard_start = content.find("function DashboardPage({")
find_route_start = content.find("function FindRoutePage({")

if dashboard_start != -1 and find_route_start != -1:
    dashboard_block = content[dashboard_start:find_route_start]
    
    # Inject mapCenter state and effect
    state_injection = """
  const [mapCenter, setMapCenter] = useState([13.06, 80.24]);
  
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setMapCenter([pos.coords.latitude, pos.coords.longitude]),
        (err) => console.log('Location access denied or failed', err),
        { enableHighAccuracy: true }
      );
    }
  }, []);
"""
    navigate_idx = dashboard_block.find("const navigate = useNavigate();")
    if navigate_idx != -1:
        insert_idx = navigate_idx + len("const navigate = useNavigate();")
        dashboard_block = dashboard_block[:insert_idx] + state_injection + dashboard_block[insert_idx:]
    
    # Replace center and add MapUpdater
    dashboard_block = dashboard_block.replace("center={[13.06, 80.24]}", "center={mapCenter}")
    # Replace the single instance of AccessRouteMapTiles in DashboardPage with MapUpdater following it
    dashboard_block = dashboard_block.replace("<AccessRouteMapTiles />", "<AccessRouteMapTiles />\n                <MapUpdater center={mapCenter} />", 1)
    
    content = content[:dashboard_start] + dashboard_block + content[find_route_start:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Dashboard securely patched.")
