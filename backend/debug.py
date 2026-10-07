import sys
sys.path.append(".")
from api.travel import create_travel_plan
from api_models.travel import TravelPlanRequest, AccessibilityProfile, AccessibilityPreferences

req = TravelPlanRequest(
    origin='Chennai', 
    destination='Mahabalipuram', 
    start_date='2026-10-02', 
    travelers=1, 
    accessibility_profile=AccessibilityProfile.general, 
    preferences=AccessibilityPreferences()
)

try:
    res = create_travel_plan(req)
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
