import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find `function NearbyPlacesPage() {` and replace everything until `// --- Reports Page ---` or `function ReportsPage() {`

start_marker = "function NearbyPlacesPage() {"
end_marker = "function AccessibleBuildingsPage() {"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find frontend markers")
    exit(1)

new_component = """function NearbyPlacesPage() {
  const navigate = useNavigate();
  const { toggleSave, isSaved } = useContext(SavedPlacesContext);
  const [center, setCenter] = useState(null);
  const [centerLabel, setCenterLabel] = useState('');
  const [centerSource, setCenterSource] = useState('');
  const [areaQuery, setAreaQuery] = useState('');
  
  const [radius, setRadius] = useState(2000);
  const [category, setCategory] = useState('all');
  const [sortBy, setSortBy] = useState('nearest');
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState('');
  
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [searchTrigger, setSearchTrigger] = useState(0);

  useEffect(() => {
    if (!center) { setPlaces([]); return; }
    const controller = new AbortController();
    async function searchNearby() {
      setLoading(true); setError(''); setSelectedPlace(null);
      try {
        const params = new URLSearchParams({ lat: center.latitude, lon: center.longitude, radius_m: radius, category });
        const r = await fetch(`${API}/api/places/nearby?${params}`, { signal: controller.signal });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail || 'Nearby search failed. OpenStreetMap service may be temporarily slow.');
        setPlaces(d.places || []);
      } catch (err) {
        if (!controller.signal.aborted) { setPlaces([]); setError(err.message || 'Search failed. Please try again.'); }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    searchNearby();
    return () => controller.abort();
  }, [center, searchTrigger, category, radius]); // Trigger on filter changes

  async function useCurrentLocation() {
    setLocating(true); setError('');
    try {
      if (!navigator.geolocation || !window.isSecureContext) throw new Error('Location needs HTTPS or localhost.');
      if (await locationPermissionIsDenied()) throw new Error(deniedLocationMessage());
      const pos = await getDeviceLocation();
      const next = { latitude: pos.coords.latitude, longitude: pos.coords.longitude };
      setCenter(next); setCenterSource('current'); setAreaQuery('');
      setCenterLabel(`Current location (${next.latitude.toFixed(4)}, ${next.longitude.toFixed(4)})`);
      try {
        const r = await fetch(`${API}/api/locations/reverse?lat=${next.latitude}&lon=${next.longitude}`);
        const d = await r.json();
        if (r.ok && d.label) setCenterLabel(d.label);
      } catch { }
    } catch (err) { setError(err.message || locationErrorMessage(err)); }
    finally { setLocating(false); }
  }

  function selectArea(s) { setAreaQuery(s.label); setCenter({ latitude: s.latitude, longitude: s.longitude }); setCenterLabel(s.label); setCenterSource('chosen'); }

  const sortedPlaces = [...places].sort((a, b) => {
    if (sortBy === 'nearest') return a.distance_meters - b.distance_meters;
    if (sortBy === 'accessibility') return b.accessibility.score - a.accessibility.score;
    if (sortBy === 'confidence') return b.accessibility.confidence - a.accessibility.confidence;
    return 0;
  });

  function routeHere(place) {
    if (!center) return;
    const s = centerSource === 'current' ? `${center.latitude}, ${center.longitude}` : centerLabel;
    const dest = [place.name, place.address].filter(Boolean).join(', ');
    navigate('/find-route', { state: { start: s, originLabel: centerLabel, destination: dest } });
  }

  const Badge = ({ icon: Icon, label, status }) => {
    let color = 'var(--text-muted)';
    let check = '?';
    if (status === 'yes' || status === 'main' || status === 'designated') { color = '#10b981'; check = '✓'; }
    if (status === 'no' || status === 'limited') { color = '#ef4444'; check = '✕'; }
    return (
      <div className="flex items-center gap-1.5 text-xs px-2 py-1 rounded-md" style={{ background: 'var(--surface-muted)', color: 'var(--text-main)' }}>
        <span style={{ color, fontWeight: 'bold' }}>{check}</span>
        {label}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Panel title="Nearby Accessible Places" icon={<MapPin size={17} />}>
        <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>Find accessible facilities around you.</p>
        <div className="flex flex-col gap-3">
          <div className="grid gap-2 md:grid-cols-[1fr_auto_auto]">
            <LocationSearchField value={areaQuery} onChange={v => { setAreaQuery(v); const m = v.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/); if (m) { setCenter({ latitude: Number(m[1]), longitude: Number(m[2]) }); setCenterLabel(v); setCenterSource('chosen'); } else if (!v.trim()) { setCenter(null); setCenterLabel(''); } }} onSelect={selectArea} placeholder="Search location..." />
            <button type="button" className="primary-button whitespace-nowrap" onClick={useCurrentLocation} disabled={locating}>
              <LocateFixed size={15} />{locating ? 'Locating...' : 'My Location'}
            </button>
          </div>
          
          <div className="flex flex-wrap gap-2 items-center mt-2">
             <div className="text-xs font-bold uppercase tracking-wider mr-2" style={{ color: 'var(--text-dim)' }}>Category</div>
             {['all', 'hospitals', 'restaurants', 'toilets', 'transport', 'colleges', 'shopping', 'parks', 'pharmacies'].map(c => (
                <button key={c} type="button" className={`px-3 py-1.5 rounded-full text-xs font-semibold capitalize transition-colors ${category === c ? 'bg-[var(--accent)] text-white' : 'bg-[var(--surface-muted)] text-[var(--text-main)] hover:bg-[var(--surface-accent)]'}`} onClick={() => setCategory(c)}>
                  {c}
                </button>
             ))}
          </div>

          <div className="flex flex-wrap gap-4 items-center mt-2 border-t pt-4" style={{ borderColor: 'var(--line)' }}>
            <Field label="Search radius">
              <select className="field text-sm py-1 h-8" value={radius} onChange={e => setRadius(Number(e.target.value))}>
                <option value={500}>500 m</option>
                <option value={1000}>1 km</option>
                <option value={2000}>2 km</option>
                <option value={5000}>5 km</option>
              </select>
            </Field>
            <Field label="Sort by">
              <select className="field text-sm py-1 h-8" value={sortBy} onChange={e => setSortBy(e.target.value)}>
                <option value="nearest">Nearest</option>
                <option value="accessibility">Highest Accessibility</option>
                <option value="confidence">Highest Data Confidence</option>
              </select>
            </Field>
          </div>
        </div>
        {error && <div role="alert" className="mt-4 rounded-xl p-3 text-sm" style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}><AlertTriangle size={14} className="inline mr-1" />{error}</div>}
      </Panel>

      {center && (
        <section className="grid gap-6 xl:grid-cols-2">
          
          <div className="flex flex-col gap-4">
            <Panel title={loading ? 'Searching...' : `Places Found (${sortedPlaces.length})`} icon={loading ? <RefreshCw size={17} className="animate-spin" /> : <MapPin size={17} />}>
              {loading && <LoadingDots text="Finding nearby accessible places..." />}
              {!loading && sortedPlaces.length === 0 && <Empty text={`No accessible ${category === 'all' ? 'places' : category} found within ${radius >= 1000 ? radius/1000 + ' km' : radius + ' m'}.`} icon="M" />}
              
              <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                {sortedPlaces.map(place => (
                  <div key={place.id} 
                       className={`rounded-2xl border p-5 transition-all cursor-pointer ${selectedPlace?.id === place.id ? 'border-[var(--accent)] bg-[var(--surface-accent)] shadow-md' : 'border-[var(--line)] bg-[var(--surface)] hover:border-[var(--accent)] hover:shadow-sm'}`}
                       onClick={() => setSelectedPlace(place)}>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-bold text-base" style={{ color: 'var(--text-main)' }}>{place.name}</h3>
                        <div className="text-xs mt-0.5" style={{ color: 'var(--text-dim)' }}>{place.category} • {(place.distance_meters / 1000).toFixed(1)} km away</div>
                      </div>
                      <div className="text-right shrink-0 ml-4">
                        <div className="text-xl font-black" style={{ color: place.accessibility.score >= 80 ? '#10b981' : place.accessibility.score >= 60 ? '#f59e0b' : '#ef4444' }}>
                          {place.accessibility.score}<span className="text-sm">/100</span>
                        </div>
                        <div className="text-[10px] uppercase font-bold tracking-wider" style={{ color: 'var(--text-dim)' }}>Accessibility</div>
                      </div>
                    </div>

                    <div className="text-xs font-semibold mb-3 px-2 py-1 rounded inline-block" style={{ background: place.accessibility.score >= 80 ? '#d1fae5' : place.accessibility.score >= 60 ? '#fef3c7' : place.accessibility.score >= 40 ? '#fee2e2' : '#f3f4f6', color: place.accessibility.score >= 80 ? '#047857' : place.accessibility.score >= 60 ? '#b45309' : place.accessibility.score >= 40 ? '#b91c1c' : '#4b5563' }}>
                      {place.accessibility.status}
                    </div>

                    <div className="flex flex-wrap gap-2 mb-4">
                      <Badge label="Ramp" status={place.accessibility.ramp} />
                      <Badge label="Entrance" status={place.accessibility.accessible_entrance} />
                      <Badge label="Elevator" status={place.accessibility.elevator} />
                      <Badge label="Toilet" status={place.accessibility.accessible_toilet} />
                    </div>

                    <div className="flex items-center justify-between mt-2 pt-4 border-t border-[var(--line)]">
                      <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        Confidence: <span className="font-bold">{place.accessibility.confidence}%</span>
                      </div>
                      <div className="flex gap-2">
                        {selectedPlace?.id !== place.id && (
                          <button type="button" className="secondary-button text-xs py-1.5" onClick={(e) => { e.stopPropagation(); setSelectedPlace(place); }}>
                            View Details
                          </button>
                        )}
                        <button type="button" className="primary-button text-xs py-1.5 px-4" onClick={(e) => { e.stopPropagation(); routeHere(place); }}>
                          <Navigation2 size={12} /> Route Here
                        </button>
                      </div>
                    </div>

                    {selectedPlace?.id === place.id && (
                      <div className="mt-4 pt-4 border-t border-dashed border-[var(--line)] animate-fade-in">
                        <h4 className="text-xs font-bold uppercase mb-2" style={{ color: 'var(--text-dim)' }}>Accessibility Details</h4>
                        <div className="grid grid-cols-2 gap-y-2 text-sm">
                          <div className="flex justify-between pr-4"><span style={{ color: 'var(--text-muted)' }}>Wheelchair:</span> <span className="font-medium capitalize">{place.accessibility.wheelchair}</span></div>
                          <div className="flex justify-between pr-4"><span style={{ color: 'var(--text-muted)' }}>Ramp:</span> <span className="font-medium capitalize">{place.accessibility.ramp}</span></div>
                          <div className="flex justify-between pr-4"><span style={{ color: 'var(--text-muted)' }}>Elevator:</span> <span className="font-medium capitalize">{place.accessibility.elevator}</span></div>
                          <div className="flex justify-between pr-4"><span style={{ color: 'var(--text-muted)' }}>Accessible Toilet:</span> <span className="font-medium capitalize">{place.accessibility.accessible_toilet}</span></div>
                          <div className="flex justify-between pr-4"><span style={{ color: 'var(--text-muted)' }}>Entrance:</span> <span className="font-medium capitalize">{place.accessibility.accessible_entrance}</span></div>
                          <div className="flex justify-between pr-4"><span style={{ color: 'var(--text-muted)' }}>Tactile Paving:</span> <span className="font-medium capitalize">{place.accessibility.tactile_paving}</span></div>
                        </div>
                        {place.accessibility.known_attributes_count === 0 && (
                          <div className="mt-3 text-xs italic" style={{ color: 'var(--text-muted)' }}>Accessibility information is currently unavailable for this place. Data relies on community OSM contributions.</div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Panel>
          </div>

          <div className="h-[600px] sticky top-6">
            <Panel title="Map" icon={<Map size={17} />} className="h-full flex flex-col">
              <div className="flex-1 overflow-hidden rounded-xl border border-[var(--line)] relative z-0">
                <MapContainer center={[center.latitude, center.longitude]} zoom={14} className="h-full w-full">
                  <AccessRouteMapTiles />
                  <CircleMarker center={[center.latitude, center.longitude]} radius={6} pathOptions={{ color: '#fff', weight: 2, fillColor: '#3b82f6', fillOpacity: 1 }}>
                    <Popup>Your Location</Popup>
                  </CircleMarker>
                  {sortedPlaces.map(p => (
                    <CircleMarker key={p.id} center={[p.location.latitude, p.location.longitude]} radius={selectedPlace?.id === p.id ? 10 : 7} 
                      eventHandlers={{ click: () => setSelectedPlace(p) }}
                      pathOptions={{ 
                        color: selectedPlace?.id === p.id ? '#000' : '#fff', 
                        weight: selectedPlace?.id === p.id ? 3 : 2, 
                        fillColor: p.accessibility.score >= 80 ? '#10b981' : p.accessibility.score >= 60 ? '#f59e0b' : '#ef4444', 
                        fillOpacity: 0.9 
                      }}>
                      <Popup>
                        <strong>{p.name}</strong><br/>
                        {p.category}<br/>
                        Score: {p.accessibility.score}/100<br/>
                        <button className="mt-2 text-xs font-bold text-[var(--accent)]" onClick={() => routeHere(p)}>Route Here</button>
                      </Popup>
                    </CircleMarker>
                  ))}
                </MapContainer>
              </div>
            </Panel>
          </div>
        </section>
      )}
    </div>
  );
}

// --- End of NearbyPlacesPage ---
"""

content = content[:start_idx] + new_component + content[end_idx:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Frontend NearbyPlaces patched successfully.")
