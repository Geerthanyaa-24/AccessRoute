import sys

with open("main.py", "a", encoding="utf-8") as f:
    f.write("""

# ====================================================================
# 🧳 AI ACCESSIBLE TRAVEL PLANNER MODULE
# ====================================================================
from typing import List, Optional

class Hotel(BaseModel):
    id: str
    name: str
    location: str
    rating: float
    price: str
    ground_floor: str
    ramp: str
    elevator: str
    step_free_entry: str
    accessible_room: str
    accessible_bathroom: str
    accessible_parking: str
    accessible_restaurant: str
    accessible_restroom: str
    confidence: str
    source: str
    last_verified: str
    accessibility_score: int

class Facility(BaseModel):
    id: str
    name: str
    type: str
    location: str
    accessibility_features: List[str]
    confidence: str
    source: str
    verification_status: str
    last_verified: str
    accessibility_score: int

class TripPlanRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    travelers: int
    accessibility_profile: AccessibilityProfile
    preferences: dict[str, bool]

# DEMO SYNTHETIC DATA FOR TRAVEL PLANNER
DEMO_HOTELS = [
    Hotel(
        id="h1", name="Grand Accessible Resort", location="Downtown", rating=4.8, price="$$$",
        ground_floor="AVAILABLE", ramp="AVAILABLE", elevator="AVAILABLE", step_free_entry="AVAILABLE",
        accessible_room="AVAILABLE", accessible_bathroom="AVAILABLE", accessible_parking="UNKNOWN",
        accessible_restaurant="AVAILABLE", accessible_restroom="AVAILABLE",
        confidence="HIGH", source="Verified Community", last_verified="2026-09-01", accessibility_score=94
    ),
    Hotel(
        id="h2", name="City Center Inn", location="City Center", rating=4.2, price="$$",
        ground_floor="AVAILABLE", ramp="NOT AVAILABLE", elevator="AVAILABLE", step_free_entry="UNKNOWN",
        accessible_room="AVAILABLE", accessible_bathroom="AVAILABLE", accessible_parking="NOT AVAILABLE",
        accessible_restaurant="AVAILABLE", accessible_restroom="UNKNOWN",
        confidence="MEDIUM", source="Automated Crawl", last_verified="2026-08-15", accessibility_score=72
    )
]

DEMO_FACILITIES = [
    Facility(
        id="f1", name="Central Park", type="Attractions", location="Downtown",
        accessibility_features=["Flat paths", "Accessible restrooms", "Ramped entrances"],
        confidence="HIGH", source="Official Data", verification_status="VERIFIED", last_verified="2026-09-10",
        accessibility_score=88
    ),
    Facility(
        id="f2", name="Metro Station A", type="Transport", location="City Center",
        accessibility_features=["Elevator to platform", "Tactile paving"],
        confidence="HIGH", source="Transport Authority", verification_status="VERIFIED", last_verified="2026-09-20",
        accessibility_score=95
    )
]

@app.post("/api/travel-plan")
def generate_travel_plan(request: TripPlanRequest):
    # Base recommendation logic based on profile
    recommended_hotel = DEMO_HOTELS[0] if request.accessibility_profile.mobility else DEMO_HOTELS[1]
    
    # Generate structured Day-by-Day itinerary
    itinerary = [
        {
            "day": "DAY 1",
            "steps": [
                f"Arrival at {request.destination}",
                f"Check-in at {recommended_hotel.name}",
                "Dinner at Accessible Restaurant",
                "Evening relaxation"
            ]
        },
        {
            "day": "DAY 2",
            "steps": [
                "Breakfast at hotel",
                "Visit Central Park (Accessible Attraction)",
                "Lunch nearby",
                "Afternoon museum tour (Elevator access verified)"
            ]
        }
    ]

    return {
        "status": "success",
        "trip_overview": {
            "origin": request.origin,
            "destination": request.destination,
            "dates": f"{request.start_date} to {request.end_date}",
            "travelers": request.travelers,
            "facilities_found": len(DEMO_FACILITIES),
            "recommended_hotel": recommended_hotel.model_dump()
        },
        "itinerary": itinerary,
        "hotels": [h.model_dump() for h in DEMO_HOTELS],
        "facilities": [f.model_dump() for f in DEMO_FACILITIES]
    }

@app.get("/api/hotels")
def get_hotels():
    return {"hotels": [h.model_dump() for h in DEMO_HOTELS]}

@app.get("/api/facilities")
def get_facilities():
    return {"facilities": [f.model_dump() for f in DEMO_FACILITIES]}

class TravelChatRequest(BaseModel):
    message: str
    travel_context: dict[str, Any]

@app.post("/api/travel-chat")
def travel_chat(request: TravelChatRequest):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    msg = request.message.lower()
    fallback_response = "I am the AI Travel Assistant. I see you are traveling to " + request.travel_context.get("destination", "your destination") + ". "
    
    if "hotel" in msg and "ramp" in msg:
        fallback_response += "The Grand Accessible Resort has a verified ramp available. City Center Inn does not."
    elif "hotel" in msg:
        fallback_response += "Based on your accessibility profile, I recommend the Grand Accessible Resort."
    elif "attraction" in msg:
        fallback_response += "Central Park is highly accessible with flat paths and ramped entrances."
    elif "elevator" in msg:
        fallback_response += "Both recommended hotels have elevators, but verify if they are operational on arrival."
    else:
        fallback_response += "I can help you find accessible hotels, routes, and attractions for your trip. How can I assist you?"

    if not api_key:
        return {"answer": fallback_response, "provider": "deterministic_fallback"}
    
    # If API key exists, use OpenAI
    system = "You are an AI Travel Assistant for accessible travel. Use only the provided travel context. Never invent accessibility features like ramps or elevators if they are marked UNKNOWN."
    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Context: {json.dumps(request.travel_context)}\n\nQuestion: {request.message}"}
        ],
        "temperature": 0.2
    }
    
    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data["choices"][0]["message"]["content"]
        return {"answer": answer, "provider": "openai"}
    except Exception as exc:
        return {"answer": fallback_response + "\\n\\n(AI provider unavailable)", "provider": "fallback"}
""")
print("Successfully appended Travel Planner module to main.py")
