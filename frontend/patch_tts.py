import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

findRoutes_old = """      try {
      const routeStart = await resolveRouteStart(start);
      const r = await fetch(`${API}/api/routes/compare`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ start: routeStart, destination, profile }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Could not generate routes.');
      const isCoord = /^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$/.test(routeStart);
      setStart(routeStart);

      setRoutes(d.routes || []);
      setSelectedId(d.recommended_route_id || d.routes?.[0]?.id || '');
      setRouteNotice(`${d.routes?.length ?? 0} routes found via ${d.provider || 'routing service'}. Accessibility conditions are unverified.`);
    } catch (err) { setRouteNotice(err.message || 'Could not generate routes.'); }
    finally { setLoading(false); }"""

findRoutes_new = """      try {
      const routeStart = await resolveRouteStart(start);
      const r = await fetch(`${API}/api/routes/compare`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ start: routeStart, destination, profile }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Could not generate routes.');
      const isCoord = /^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$/.test(routeStart);
      setStart(routeStart);

      const fetchedRoutes = d.routes || [];
      setRoutes(fetchedRoutes);
      const recId = d.recommended_route_id || fetchedRoutes[0]?.id || '';
      setSelectedId(recId);
      setRouteNotice(`${fetchedRoutes.length} routes found via ${d.provider || 'routing service'}. Accessibility conditions are unverified.`);

      // AI VOICE SYNTHESIS FOR DEMO
      if (fetchedRoutes.length > 0 && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Stop current speech
        const recRoute = fetchedRoutes.find(r => r.id === recId) || fetchedRoutes[0];
        const distKm = (recRoute.distance_m / 1000).toFixed(1);
        const timeMin = recRoute.time_mins;
        const score = recRoute.accessibility_score || recRoute.personalized_score || 0;
        
        let text = `I found ${fetchedRoutes.length} routes to your destination. `;
        text += `The recommended accessible route is ${distKm} kilometers and takes approximately ${timeMin} minutes. `;
        text += `It has an accessibility score of ${score} out of 100. `;
        if (fetchedRoutes.length > 1) {
            text += `I have also provided alternative routes for you to compare.`;
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95; // Slightly slower for natural feel
        utterance.pitch = 1.0;
        
        // Try to find a good female English voice
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Samantha') || v.name.includes('Female')) || voices[0];
        if (preferredVoice) utterance.voice = preferredVoice;
        
        window.speechSynthesis.speak(utterance);
      }

    } catch (err) { setRouteNotice(err.message || 'Could not generate routes.'); }
    finally { setLoading(false); }"""

# Using robust replace with spaces stripped to handle indentation mismatches
def normalize_space(text): return re.sub(r'\s+', ' ', text)

start_idx = content.find("async function findRoutes(e) {")
if start_idx != -1:
    end_idx = content.find("finally { setLoading(false); }", start_idx)
    if end_idx != -1:
        end_idx += len("finally { setLoading(false); }")
        
        old_block = content[start_idx:end_idx]
        
        # Manually reconstruct the block
        new_block = """async function findRoutes(e) {
    e.preventDefault();
    if (!destination.trim()) { setRouteNotice('Enter a destination to find a route.'); return; }
    setLoading(true); setRouteNotice('');
""" + findRoutes_new
        
        content = content[:start_idx] + new_block + content[end_idx:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("TTS integrated.")
