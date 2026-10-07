import os
import json
import urllib.request

def generate_ai_summary(trip_data: dict) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    data_mode = os.getenv("DATA_MODE", "demo").strip().lower()
    if not gemini_key or data_mode == "demo":
        origin = trip_data.get("origin", "Origin")
        dest = trip_data.get("destination", "Destination")
        return f"**(DEMO AI SUMMARY)** Your trip from {origin} to {dest} looks fantastic! We have selected highly accessible venues based on your preferences. Make sure to verify specific facilities before arrival." 
        
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
    
    prompt = f"""You are an AI Travel Assistant for accessible travel.
Analyze the following travel plan data. Provide a short, welcoming 2-3 paragraph summary for the user. 
DO NOT INVENT PLACES, RATINGS, OR ACCESSIBILITY DATA. Stick strictly to what is provided below.
If accessibility data is Unknown, mention that the user should verify.

Data:
{json.dumps(trip_data, default=str)[:8000]}
"""
    
    try:
        req = urllib.request.Request(url, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI generation failed: {str(e)}"
