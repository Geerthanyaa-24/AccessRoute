import re

with open("App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add navGroup item
nav_item = "    ['/travel-planner', '🧳 AI Travel Planner', Sparkles],\n"
if "travel-planner" not in content:
    content = re.sub(
        r"(navGroups = \[\n  { label: 'Explore', items: \[)",
        r"\1\n" + nav_item,
        content
    )

# 2. Add Route
route_str = '                        <Route path="/travel-planner" element={<TravelPlannerPage profile={profile} />} />\n'
if "/travel-planner" not in content.split("Routes")[1]:
    content = re.sub(
        r"(<Route path=\"/\" element=\{<DashboardPage profile=\{profile\} setProfile=\{setProfile\} />\} />)",
        r"\1\n" + route_str,
        content
    )

# 3. Add Component Code
travel_planner_code = """
// ─── AI Accessible Travel Planner Page ──────────────────────────────────────────────
function TravelPlannerPage({ profile }) {
  const [formData, setFormData] = useState({
    origin: '', destination: '', startDate: '', endDate: '', travelers: 1,
    preferences: {
      avoid_stairs: true, prefer_ramps: true, prefer_elevators: true,
      step_free_entry: true, accessible_restroom: true, accessible_parking: false,
      ground_floor: false, accessible_room: true
    }
  });
  
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview, hotels, itinerary, facilities
  
  // Chatbot state
  const [chatMsg, setChatMsg] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', text: 'Hi! I am your AI Travel Assistant. Generate a plan to get started, then ask me anything about it!' }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  
  async function generatePlan(e) {
    e.preventDefault();
    setLoading(true);
    setPlan(null);
    try {
      const res = await fetch(`${API}/api/travel-plan`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: formData.origin || 'Current Location',
          destination: formData.destination || 'New York',
          start_date: formData.startDate || '2026-10-01',
          end_date: formData.endDate || '2026-10-05',
          travelers: formData.travelers,
          accessibility_profile: profile,
          preferences: formData.preferences
        })
      });
      const data = await res.json();
      setPlan(data);
    } catch (err) {
      alert("Error generating plan: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function sendChatMessage(e) {
    e.preventDefault();
    if (!chatMsg.trim() || !plan) return;
    const msg = chatMsg;
    setChatMsg('');
    setChatHistory(old => [...old, { role: 'user', text: msg }]);
    setChatLoading(true);
    
    try {
      const res = await fetch(`${API}/api/travel-chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: msg,
          travel_context: plan
        })
      });
      const data = await res.json();
      setChatHistory(old => [...old, { role: 'assistant', text: data.answer }]);
    } catch (err) {
      setChatHistory(old => [...old, { role: 'assistant', text: 'Sorry, I am having trouble connecting to the backend.' }]);
    } finally {
      setChatLoading(false);
    }
  }

  const togglePref = (k) => setFormData(old => ({...old, preferences: {...old.preferences, [k]: !old.preferences[k]}}));

  return (
    <div className="space-y-6">
      <Panel title="🧳 AI Accessible Travel Planner" icon={<Sparkles size={17} />}>
        <form onSubmit={generatePlan} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Field label="From"><input required className="field" placeholder="Starting location" value={formData.origin} onChange={e => setFormData({...formData, origin: e.target.value})} /></Field>
          <Field label="Destination"><input required className="field" placeholder="Destination" value={formData.destination} onChange={e => setFormData({...formData, destination: e.target.value})} /></Field>
          <Field label="Start Date"><input type="date" required className="field" value={formData.startDate} onChange={e => setFormData({...formData, startDate: e.target.value})} /></Field>
          <Field label="End Date"><input type="date" required className="field" value={formData.endDate} onChange={e => setFormData({...formData, endDate: e.target.value})} /></Field>
          
          <div className="md:col-span-2 lg:col-span-4 border-t pt-4" style={{ borderColor: 'var(--line)' }}>
            <h3 className="text-sm font-bold mb-3">Accessibility Preferences</h3>
            <div className="flex flex-wrap gap-2">
              {Object.keys(formData.preferences).map(pref => (
                <label key={pref} className="flex items-center gap-2 text-xs p-2 border rounded-lg cursor-pointer transition" style={{ borderColor: formData.preferences[pref] ? 'var(--accent)' : 'var(--line)', background: formData.preferences[pref] ? 'var(--accent-light)' : 'var(--surface)' }}>
                  <input type="checkbox" checked={formData.preferences[pref]} onChange={() => togglePref(pref)} className="rounded" />
                  {pref.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                </label>
              ))}
            </div>
          </div>
          
          <div className="md:col-span-2 lg:col-span-4 mt-2">
            <button type="submit" className="primary-button w-full justify-center text-base py-3" disabled={loading}>
              {loading ? <RefreshCw className="animate-spin" size={18} /> : <Sparkles size={18} />}
              {loading ? 'Generating Travel Plan...' : 'Generate Accessible Travel Plan'}
            </button>
          </div>
        </form>
      </Panel>

      {plan && (
        <div className="grid gap-6 xl:grid-cols-3">
          {/* Main Content Area */}
          <div className="xl:col-span-2 space-y-6">
            <Panel title="Trip Overview">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="p-3 bg-opacity-5 rounded-lg" style={{ background: 'var(--accent-light)' }}>
                  <div className="text-xs opacity-70">Destination</div>
                  <div className="font-bold">{plan.trip_overview.destination}</div>
                </div>
                <div className="p-3 bg-opacity-5 rounded-lg" style={{ background: 'var(--accent-light)' }}>
                  <div className="text-xs opacity-70">Dates</div>
                  <div className="font-bold text-xs">{plan.trip_overview.dates}</div>
                </div>
                <div className="p-3 bg-opacity-5 rounded-lg" style={{ background: 'var(--accent-light)' }}>
                  <div className="text-xs opacity-70">Facilities Found</div>
                  <div className="font-bold">{plan.trip_overview.facilities_found}</div>
                </div>
                <div className="p-3 bg-opacity-5 rounded-lg" style={{ background: 'var(--accent-light)' }}>
                  <div className="text-xs opacity-70">Recommended Hotel</div>
                  <div className="font-bold text-xs truncate">{plan.trip_overview.recommended_hotel.name}</div>
                </div>
              </div>
            </Panel>

            <Panel title="Day-by-Day AI Itinerary" icon={<Clock size={17} />}>
              <div className="space-y-6">
                {plan.itinerary.map((day, i) => (
                  <div key={i} className="border-l-2 pl-4 pb-2" style={{ borderColor: 'var(--accent)' }}>
                    <h3 className="font-black text-sm mb-2" style={{ color: 'var(--accent)' }}>{day.day}</h3>
                    <div className="space-y-3">
                      {day.steps.map((step, j) => (
                        <div key={j} className="flex gap-3 text-sm items-start">
                          <CheckCircle2 size={16} className="mt-0.5" style={{ color: 'var(--text-dim)' }} />
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel title="Accessible Hotels" icon={<Building size={17} />}>
              <div className="grid gap-4 sm:grid-cols-2">
                {plan.hotels.map(hotel => (
                  <div key={hotel.id} className="border p-4 rounded-xl shadow-sm" style={{ borderColor: 'var(--line)', background: 'var(--surface)' }}>
                    <h3 className="font-bold">{hotel.name}</h3>
                    <div className="flex justify-between text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                      <span>{hotel.location}</span>
                      <span>{hotel.rating} ⭐ • {hotel.price}</span>
                    </div>
                    
                    <div className="mt-3 flex items-center justify-between">
                      <div>
                        <div className="text-2xl font-black" style={{ color: hotel.accessibility_score > 80 ? '#10b981' : '#f59e0b' }}>
                          {hotel.accessibility_score}
                        </div>
                        <div className="text-[10px] uppercase">Access Score</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-sm">{hotel.confidence}</div>
                        <div className="text-[10px] uppercase">Confidence</div>
                      </div>
                    </div>

                    <div className="mt-3 pt-3 border-t grid grid-cols-2 gap-y-2 text-xs" style={{ borderColor: 'var(--line)' }}>
                      {['ramp', 'elevator', 'ground_floor', 'accessible_room'].map(feat => (
                         <div key={feat} className="flex items-center gap-1">
                           {hotel[feat] === 'AVAILABLE' ? <CheckCircle2 size={12} color="#10b981" /> 
                            : hotel[feat] === 'UNKNOWN' ? <CircleHelp size={12} color="#9ca3af" /> 
                            : <X size={12} color="#ef4444" />}
                           <span className="truncate">{feat.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                         </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </Panel>
          </div>

          {/* Sidebar Area: AI Chat & Map */}
          <div className="space-y-6">
            <Panel title="AI Travel Assistant" icon={<Bot size={17} />}>
              <div className="flex flex-col h-[350px]">
                <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-3 text-sm">
                  {chatHistory.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`p-2.5 rounded-xl max-w-[85%] ${msg.role === 'user' ? 'rounded-tr-none text-white' : 'rounded-tl-none'}`}
                           style={{ background: msg.role === 'user' ? 'var(--accent)' : 'var(--surface-muted)' }}>
                        {msg.text}
                      </div>
                    </div>
                  ))}
                  {chatLoading && <LoadingDots text="Thinking..." />}
                </div>
                <form onSubmit={sendChatMessage} className="flex gap-2">
                  <input className="field flex-1" placeholder="Ask about hotels, routes..." value={chatMsg} onChange={e => setChatMsg(e.target.value)} disabled={chatLoading} />
                  <button type="submit" className="primary-button p-2" disabled={chatLoading || !chatMsg.trim()}><Send size={16} /></button>
                </form>
              </div>
            </Panel>

            <Panel title="Interactive Travel Map" icon={<Map size={17} />}>
              <div className="h-[250px] overflow-hidden rounded-xl bg-gray-100 flex items-center justify-center">
                {/* Simplified placeholder or actual Leaflet map depending on what's available */}
                <MapContainer center={[40.7128, -74.0060]} zoom={12} className="h-full w-full z-0">
                  <AccessRouteMapTiles />
                  {plan.hotels.map(h => h.lat ? (
                    <CircleMarker key={h.id} center={[h.lat, h.lon]} radius={8} pathOptions={{ color: '#fff', fillColor: '#7c3aed', fillOpacity: 0.9 }}>
                    </CircleMarker>
                  ) : null)}
                </MapContainer>
              </div>
            </Panel>
          </div>
        </div>
      )}
    </div>
  );
}
"""

if "function TravelPlannerPage" not in content:
    content = content.replace("export default App;", travel_planner_code + "\nexport default App;")

with open("App.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched App.jsx successfully.")
