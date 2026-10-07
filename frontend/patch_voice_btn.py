import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Volume2 to lucide-react imports if it's missing
if "Volume2" not in content:
    content = content.replace("import { MapPin", "import { MapPin, Volume2")

# Inject a speak function and button into RouteCard
routecard_old = """          <div className="flex items-center gap-1 shrink-0">
            {selected && <CheckCircle2 size={17} style={{ color: 'var(--route-optimized)' }} />}"""

routecard_new = """          <div className="flex items-center gap-1 shrink-0">
            <button
              type="button"
              onClick={e => {
                e.stopPropagation();
                if ('speechSynthesis' in window) {
                  window.speechSynthesis.cancel();
                  const distKm = (route.distance_m / 1000).toFixed(1);
                  const text = `Route ${route.name}. Distance: ${distKm} kilometers. Time: ${route.time_mins} minutes. Accessibility Score: ${route.accessibility_score ?? route.personalized_score ?? 0} out of 100. ${route.pareto_status ? 'Status: ' + route.pareto_status.replaceAll('_', ' ') : ''}.`;
                  const u = new SpeechSynthesisUtterance(text);
                  u.rate = 0.95;
                  window.speechSynthesis.speak(u);
                }
              }}
              className="rounded-lg p-1.5 transition-colors hover:bg-black/5 dark:hover:bg-white/5"
              style={{ color: 'var(--route-optimized)' }}
              title="Play AI Voice Summary"
            >
              <Volume2 size={15} />
            </button>
            {selected && <CheckCircle2 size={17} style={{ color: 'var(--route-optimized)' }} />}"""

content = content.replace(routecard_old, routecard_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("RouteCard updated with Voice Button.")
