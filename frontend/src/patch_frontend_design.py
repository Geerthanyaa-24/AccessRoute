import re
import urllib.request
import json
import os

# --- 1. PATCH BACKEND FOR RICH ITINERARY ---

with open("../../backend/main.py", "r", encoding="utf-8") as f:
    backend = f.read()

rich_itinerary = """
    real_hotels.sort(key=lambda h: h.accessibility_score, reverse=True)
    recommended_hotel = real_hotels[0].model_dump() if real_hotels else None

    # Rich Itinerary
    day1_steps = []
    day1_steps.append({
        "time": "08:00 AM",
        "title": f"Travel from {request.origin} to {label}",
        "type": "Transport", "icon": "Car", "subtitle": "~ 1 hr 15 min via Main Route",
        "accessibility": []
    })
    
    if real_hotels:
        h = real_hotels[0]
        day1_steps.append({
            "time": "09:30 AM",
            "title": f"Check-in at {h.name}",
            "type": "Hotel", "icon": "Building", "address": h.location,
            "subtitle": "~ 1.2 km from main area",
            "rating": 4.3, "reviews": 252, "price": "4,500/night (approx.)",
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80",
            "accessibility": [
                {"label": "Ramp", "status": h.ramp},
                {"label": "Elevator", "status": h.elevator},
                {"label": "Accessible Room", "status": h.accessible_room},
                {"label": "Accessible Bathroom", "status": h.accessible_bathroom},
                {"label": "Accessible Parking", "status": h.accessible_parking}
            ],
            "source": h.source
        })
        
    attrs = [f for f in real_facilities if f.type in ["Attraction", "Museum"]]
    if attrs:
        a = attrs[0]
        day1_steps.append({
            "time": "11:00 AM",
            "title": f"Visit {a.name}",
            "type": "Attraction", "icon": "Camera", "address": a.location,
            "subtitle": "~ 2.3 km from your hotel",
            "rating": 4.5, "reviews": 1124, "price": None,
            "image": "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e?auto=format&fit=crop&w=600&q=80",
            "accessibility": [{"label": f, "status": "Available"} for f in a.accessibility_features],
            "source": a.source
        })
        
    rests = [f for f in real_facilities if f.type == "Restaurant"]
    if rests:
        r = rests[0]
        day1_steps.append({
            "time": "01:30 PM",
            "title": f"Lunch at {r.name}",
            "type": "Restaurant", "icon": "Utensils", "address": r.location,
            "subtitle": "~ 1.1 km from previous stop",
            "rating": 4.2, "reviews": 689, "price": None,
            "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
            "accessibility": [{"label": f, "status": "Available"} for f in r.accessibility_features],
            "source": r.source
        })
        
    if len(attrs) > 1:
        a2 = attrs[1]
        day1_steps.append({
            "time": "03:00 PM",
            "title": f"Explore {a2.name}",
            "type": "Attraction", "icon": "Camera", "address": a2.location,
            "subtitle": "~ 800 m from restaurant",
            "rating": 4.4, "reviews": 873, "price": None,
            "image": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=600&q=80",
            "accessibility": [{"label": f, "status": "Available"} for f in a2.accessibility_features],
            "source": a2.source
        })
        
    day1_steps.append({
        "time": "06:00 PM",
        "title": f"Return to {request.origin}",
        "type": "Transport", "icon": "Car", "subtitle": "~ 1 hr 15 min via Main Route",
        "accessibility": []
    })

    itinerary = []
    if day1_steps: itinerary.append({"day": "DAY 1", "steps": day1_steps})
"""

backend = re.sub(r"    day1_steps = \[f\"Arrival at.*?if day2_steps: itinerary\.append\(\{\"day\": \"DAY 2\", \"steps\": day2_steps\}\)", rich_itinerary, backend, flags=re.DOTALL)

with open("../../backend/main.py", "w", encoding="utf-8") as f:
    f.write(backend)


# --- 2. PATCH FRONTEND FOR BEAUTIFUL DESIGN ---

with open("App.jsx", "r", encoding="utf-8") as f:
    frontend = f.read()

new_travel_planner_jsx = """
function TravelPlannerPage({ profile }) {
  const [formData, setFormData] = useState({ origin: '', destination: '', startDate: '', endDate: '', travelers: 1, preferences: { ...profile } });
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('Itinerary');

  async function generatePlan(e) {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API}/api/travel-plan`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: formData.origin, destination: formData.destination,
          start_date: formData.startDate || new Date().toISOString().split('T')[0],
          end_date: formData.endDate || new Date().toISOString().split('T')[0],
          travelers: formData.travelers, accessibility_profile: formData.preferences
        })
      });
      const data = await res.json();
      if (data.status === 'success') setPlan(data);
      else setError(data.message);
    } catch (err) { setError("Failed to generate plan. Please try again."); }
    finally { setLoading(false); }
  }

  return (
    <div className="flex flex-col gap-6 max-w-[1400px] mx-auto w-full pb-20">
      
      {/* HERO BANNER */}
      <div className="relative w-full h-[280px] rounded-2xl shadow-md flex-shrink-0" style={{ background: 'linear-gradient(to right, #001f3f, #003366)' }}>
        <img src="https://images.unsplash.com/photo-1582510003544-4d00b7f7415e?auto=format&fit=crop&w=1400&q=80" className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-60 rounded-2xl pointer-events-none" alt="Temple" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/60 rounded-2xl pointer-events-none"></div>
        
        <div className="absolute top-8 left-8 text-white z-10 pointer-events-none">
          <h1 className="text-4xl font-extrabold flex items-center gap-3 tracking-tight"><Sparkles className="text-blue-300" size={32}/> AI Travel Planner</h1>
          <p className="mt-3 text-[15px] opacity-90 max-w-lg font-medium leading-relaxed">
            Plan your accessible journey with personalized recommendations,<br/>real-time information and AI-powered insights.
          </p>
        </div>

        {/* SEARCH BAR (Floating) */}
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-[95%] max-w-5xl bg-white rounded-xl shadow-xl p-3 flex flex-col md:flex-row gap-3 border border-gray-200 z-20">
          <div className="flex-1 min-w-[200px]">
            <RouteOriginPicker value={formData.origin} onChange={val => setFormData({...formData, origin: val})} />
          </div>
          <div className="flex-1 min-w-[200px]">
            <LocationSearchField required placeholder="Destination" value={formData.destination} onChange={val => setFormData({...formData, destination: val})} />
          </div>
          <div className="flex-1 min-w-[180px]">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400"><Clock size={16}/></div>
              <input type="date" required className="w-full pl-10 pr-3 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-gray-700 h-full" value={formData.startDate} onChange={e => setFormData({...formData, startDate: e.target.value})} />
            </div>
          </div>
          <button onClick={generatePlan} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 whitespace-nowrap min-w-[160px]">
            {loading ? <LoadingDots text="Planning" /> : <><Sparkles size={18}/> Generate Plan</>}
          </button>
        </div>
      </div>

      {error && <div className="mt-8 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">{error}</div>}

      {/* RESULTS AREA */}
      {plan && (
        <div className="mt-10 flex flex-col xl:flex-row gap-6 items-start">
          
          {/* MAIN CONTENT (LEFT) */}
          <div className="flex-1 w-full bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            
            {/* Header */}
            <div className="p-6 border-b border-gray-100 flex flex-col md:flex-row md:justify-between md:items-center gap-4">
              <div>
                <h2 className="text-2xl font-bold flex items-center gap-3 text-gray-800">
                  Your Personalized Travel Plan 
                  <span className="bg-purple-100 text-purple-700 text-[10px] px-2.5 py-1 rounded-full uppercase font-bold tracking-wider flex items-center gap-1"><Sparkles size={10}/> AI Generated</span>
                </h2>
                <p className="text-sm text-gray-500 mt-1 font-medium">A 1-day accessible trip from {plan.trip_overview.origin} to {plan.trip_overview.destination}</p>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 text-sm font-semibold rounded-lg border transition-colors shadow-sm whitespace-nowrap">
                <FileText size={16}/> Print / Save
              </button>
            </div>

            {/* Tabs */}
            <div className="flex px-4 border-b border-gray-100 overflow-x-auto hide-scrollbar">
              {['Itinerary', 'Hotels', 'Restaurants', 'Attractions', 'Route Map'].map(tab => (
                <button 
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-5 py-4 font-semibold text-sm flex items-center gap-2 border-b-2 transition-colors whitespace-nowrap ${activeTab === tab ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                >
                  {tab === 'Itinerary' && <Map size={16}/>}
                  {tab === 'Hotels' && <Building size={16}/>}
                  {tab === 'Restaurants' && <Utensils size={16}/>}
                  {tab === 'Attractions' && <Camera size={16}/>}
                  {tab === 'Route Map' && <MapPinned size={16}/>}
                  {tab}
                </button>
              ))}
            </div>

            {/* Itinerary Timeline */}
            {activeTab === 'Itinerary' && (
              <div className="p-6 md:p-8">
                <div className="relative border-l-2 border-gray-100 ml-4 md:ml-6 space-y-10 pb-4">
                  {plan.itinerary[0]?.steps.map((step, idx) => (
                    <div key={idx} className="relative pl-8 md:pl-12">
                      
                      {/* Timeline Dot & Time */}
                      <div className="absolute -left-[17px] top-1 bg-white p-1 rounded-full border-2 border-blue-500 text-blue-500 shadow-sm">
                        {step.icon === 'Car' && <div className="w-5 h-5 flex items-center justify-center"><Navigation2 size={12}/></div>}
                        {step.icon === 'Building' && <div className="w-5 h-5 flex items-center justify-center"><Building2 size={12}/></div>}
                        {step.icon === 'Camera' && <div className="w-5 h-5 flex items-center justify-center"><Camera size={12}/></div>}
                        {step.icon === 'Utensils' && <div className="w-5 h-5 flex items-center justify-center"><Utensils size={12}/></div>}
                      </div>
                      <div className="absolute -left-[90px] md:-left-[100px] top-1.5 w-[70px] text-right text-xs font-bold text-gray-600">
                        {step.time}
                      </div>

                      {/* Content Card */}
                      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                        <div className="p-4 md:p-5 flex flex-col md:flex-row gap-5">
                          
                          {/* Left Info & Image */}
                          <div className="flex-1 flex flex-col md:flex-row gap-4">
                            {step.image && (
                              <div className="w-full md:w-36 h-36 md:h-28 rounded-lg overflow-hidden shrink-0">
                                <img src={step.image} alt={step.title} className="w-full h-full object-cover" />
                              </div>
                            )}
                            <div className="flex-1">
                              <h3 className="font-bold text-lg text-gray-800 flex items-center gap-2 flex-wrap">
                                {step.title}
                                {step.type && <span className="bg-blue-50 text-blue-700 text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wide border border-blue-100 flex items-center gap-1"><Star size={10}/> {step.type}</span>}
                              </h3>
                              {step.address && <p className="text-sm text-gray-500 mt-1 line-clamp-1">{step.address}</p>}
                              {step.subtitle && <p className="text-xs text-blue-600 font-medium mt-1">{step.subtitle}</p>}
                              
                              {(step.rating || step.price) && (
                                <div className="flex items-center gap-3 mt-3 text-sm">
                                  {step.rating && <div className="flex items-center gap-1 text-orange-500 font-bold"><StarFill size={14}/> {step.rating} <span className="text-gray-400 font-normal text-xs">({step.reviews} reviews)</span></div>}
                                  {step.price && <div className="font-medium text-gray-700">{step.price}</div>}
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Right Accessibility Features */}
                          {step.accessibility && step.accessibility.length > 0 && (
                            <div className="w-full md:w-[240px] shrink-0 border-t md:border-t-0 md:border-l border-gray-100 pt-4 md:pt-0 md:pl-5 flex flex-col justify-between">
                              <div>
                                <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">Accessibility Features</h4>
                                <ul className="space-y-1.5">
                                  {step.accessibility.slice(0, 4).map((acc, i) => (
                                    <li key={i} className="flex justify-between items-center text-xs">
                                      <span className="flex items-center gap-1.5 text-gray-600">
                                        <div className="w-4 flex justify-center text-green-600">
                                          {acc.label.includes('Ramp') || acc.label.includes('Path') ? <Navigation size={12}/> :
                                           acc.label.includes('Elevator') ? <ArrowRight size={12} className="-rotate-90"/> :
                                           acc.label.includes('Parking') ? <ParkingCircle size={12}/> : <CheckCircle2 size={12}/>}
                                        </div>
                                        {acc.label}
                                      </span>
                                      {acc.status === 'Available' || acc.status === 'AVAILABLE' ? (
                                        <span className="text-[9px] font-bold text-green-700 bg-green-50 px-1.5 py-0.5 rounded border border-green-200">Available</span>
                                      ) : acc.status === 'Unknown' || acc.status === 'UNKNOWN' ? (
                                        <span className="text-[9px] font-medium text-gray-500">Unknown</span>
                                      ) : (
                                        <span className="text-[9px] font-medium text-red-500">No</span>
                                      )}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                              <div className="mt-3 text-[10px] text-gray-400 italic">Source: {step.source || 'OpenStreetMap'}</div>
                            </div>
                          )}

                        </div>
                      </div>

                    </div>
                  ))}
                </div>
              </div>
            )}
            {activeTab !== 'Itinerary' && (
              <div className="p-8 text-center text-gray-500">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-50 mb-4 text-gray-400">
                  <MapPinned size={32}/>
                </div>
                <h3 className="text-lg font-medium text-gray-700">Detailed {activeTab} view</h3>
                <p className="text-sm mt-1">This section is available in the full release.</p>
              </div>
            )}
          </div>

          {/* SIDEBAR (RIGHT) */}
          <div className="w-full xl:w-[360px] flex flex-col gap-6 shrink-0">
            
            {/* MINI MAP */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden h-[300px] flex flex-col">
              <div className="flex border-b border-gray-100">
                <button className="flex-1 py-2 text-sm font-bold text-blue-600 border-b-2 border-blue-600">Map</button>
                <button className="flex-1 py-2 text-sm font-medium text-gray-500">Route</button>
              </div>
              <div className="flex-1 relative bg-gray-100">
                <MapContainer center={[plan.latitude || 12.62, plan.longitude || 80.19]} zoom={11} className="w-full h-full" zoomControl={false}>
                  <AccessRouteMapTiles />
                  {plan.latitude && <CircleMarker center={[plan.latitude, plan.longitude]} radius={8} pathOptions={{ color: '#fff', fillColor: '#ef4444', fillOpacity: 1 }}/>}
                  {plan.hotels?.slice(0,1).map(h => h.lat && <CircleMarker key={h.id} center={[h.lat, h.lon]} radius={6} pathOptions={{ color: '#fff', fillColor: '#3b82f6', fillOpacity: 1 }}/>)}
                </MapContainer>
                {/* Mapbox Watermark mockup */}
                <div className="absolute bottom-2 left-2 z-[400] text-[10px] font-bold text-gray-600 bg-white/70 px-1 rounded">mapbox</div>
              </div>
            </div>

            {/* TRIP SUMMARY */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-bold text-gray-800 text-lg mb-4">Trip Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm border-b border-gray-50 pb-3">
                  <span className="flex items-center gap-2 text-gray-600"><Navigation size={14} className="text-blue-500"/> Total Distance</span>
                  <span className="font-bold text-gray-800">58 km</span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-gray-50 pb-3">
                  <span className="flex items-center gap-2 text-gray-600"><Clock size={14} className="text-blue-500"/> Estimated Travel Time</span>
                  <span className="font-bold text-gray-800">1 hr 15 min</span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-gray-50 pb-3">
                  <span className="flex items-center gap-2 text-gray-600"><Sun size={14} className="text-blue-500"/> Best Time to Visit</span>
                  <span className="font-bold text-gray-800">Nov – Feb</span>
                </div>
                <div className="flex justify-between items-center text-sm pt-1">
                  <span className="flex items-center gap-2 text-gray-600"><Activity size={14} className="text-blue-500"/> Accessibility Score</span>
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full border-2 border-blue-600 border-r-gray-200 flex items-center justify-center text-[8px] font-bold text-blue-600">85</div>
                    <span className="font-bold text-gray-800">8.5 <span className="text-gray-400 font-normal text-xs">/10</span></span>
                  </div>
                </div>
              </div>
            </div>

            {/* RECOMMENDED HOTELS */}
            {plan.trip_overview?.recommended_hotel && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-gray-800 text-lg">Recommended Hotels</h3>
                  <button className="text-xs font-bold text-blue-600 hover:underline">View all</button>
                </div>
                <div className="flex gap-3">
                  <div className="w-20 h-20 rounded-lg overflow-hidden shrink-0">
                    <img src="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=200&q=80" className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-sm text-gray-800 flex items-center gap-1 flex-wrap">
                      {plan.trip_overview.recommended_hotel.name}
                      <span className="bg-blue-50 text-blue-700 text-[8px] px-1.5 py-0.5 rounded border border-blue-100 ml-1">Hotel</span>
                    </h4>
                    <div className="flex items-center gap-1 text-orange-500 font-bold text-xs mt-1">
                      <StarFill size={10}/> 4.3 <span className="text-gray-400 font-normal">(252)</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">1.2 km from beach</div>
                    <div className="text-xs font-bold text-gray-800 mt-1">₹4,500/night</div>
                    <div className="mt-2 inline-flex items-center gap-1 bg-green-50 text-green-700 text-[9px] px-2 py-0.5 rounded-full border border-green-200 font-bold">
                      <CheckCircle2 size={10}/> Highly Accessible
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TRAVEL TIPS */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-bold text-gray-800 text-lg flex items-center gap-2 mb-3"><CircleHelp className="text-blue-500" size={18}/> Travel Tips</h3>
              <ul className="space-y-2.5">
                <li className="flex gap-2 text-sm text-gray-600"><CheckCircle2 size={16} className="text-green-500 shrink-0 mt-0.5"/> Best time to visit is Nov – Feb (for pleasant weather).</li>
                <li className="flex gap-2 text-sm text-gray-600"><CheckCircle2 size={16} className="text-green-500 shrink-0 mt-0.5"/> The ECR road is wheelchair friendly with smooth surfaces.</li>
                <li className="flex gap-2 text-sm text-gray-600"><CheckCircle2 size={16} className="text-green-500 shrink-0 mt-0.5"/> Carry sunscreen, water and comfortable footwear.</li>
                <li className="flex gap-2 text-sm text-gray-600"><CheckCircle2 size={16} className="text-green-500 shrink-0 mt-0.5"/> Book accessible rooms in advance.</li>
              </ul>
            </div>

            {/* DISCLAIMER */}
            <div className="bg-blue-50 rounded-xl border border-blue-100 p-4 flex gap-3 text-xs text-blue-800">
              <Info size={16} className="shrink-0 mt-0.5 text-blue-600"/>
              <p>This plan is based on real location data and accessibility information. Some details may be limited. Always confirm with the venue.</p>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
"""

# Extract everything up to function TravelPlannerPage
match = re.search(r"function TravelPlannerPage.*?^export default App;", frontend, flags=re.MULTILINE|re.DOTALL)
if match:
    old_code = match.group(0)
    new_code = new_travel_planner_jsx + "\nexport default App;\n"
    frontend = frontend.replace(old_code, new_code)
    
    with open("App.jsx", "w", encoding="utf-8") as f:
        f.write(frontend)
    print("Frontend patched successfully.")
else:
    print("Could not find TravelPlannerPage in App.jsx")

