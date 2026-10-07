import urllib.request
import json
import urllib.error
import traceback

req = urllib.request.Request(
    'http://localhost:8000/api/travel/plan', 
    data=json.dumps({
        'origin': 'Chennai', 
        'destination': 'Mahabalipuram', 
        'start_date': '2026-10-02', 
        'travelers': 1, 
        'accessibility_profile': 'general', 
        'preferences': {}
    }).encode(), 
    headers={'Content-Type': 'application/json'}
)

try:
    res = urllib.request.urlopen(req)
    print(res.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.reason}")
    print(e.read().decode())
except Exception as e:
    traceback.print_exc()
