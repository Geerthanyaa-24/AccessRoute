import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Create the animated pipeline component to inject
pipeline_component = """
// -----------------------------------------------------------------------------
// LOADING PIPELINE VISUALIZATION (Matches Diagram)
// -----------------------------------------------------------------------------
function LoadingPipeline({ formData }) {
  const [step, setStep] = useState(1);

  useEffect(() => {
    const intervals = [
      setTimeout(() => setStep(2), 1500),
      setTimeout(() => setStep(3), 3500),
      setTimeout(() => setStep(4), 5500),
      setTimeout(() => setStep(5), 7500),
    ];
    return () => intervals.forEach(clearTimeout);
  }, []);

  return (
    <div className="mt-10 p-8 rounded-2xl border border-gray-800 shadow-2xl relative overflow-hidden" style={{ background: '#0b132b', color: 'white' }}>
      
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#3b82f6 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>

      <div className="text-center relative z-10 mb-10">
        <h2 className="text-3xl font-black tracking-tight" style={{ color: '#f8fafc' }}>NAVIGATE WITHOUT BARRIERS</h2>
        <p className="text-blue-400 font-medium tracking-wide text-sm mt-1 uppercase">AI-Powered Accessibility Navigation - How It Works</p>
        <div className="mt-4 inline-block bg-blue-900/50 text-blue-200 border border-blue-700/50 px-6 py-1.5 rounded-full text-xs font-bold tracking-wider">
          {step === 1 && "1. COLLECTING USER INPUT..."}
          {step === 2 && "2. FETCHING GEOSPATIAL DATA..."}
          {step === 3 && "3. RUNNING ML PREDICTION ENGINE..."}
          {step === 4 && "4. SCORING & DYNAMIC REROUTING..."}
          {step === 5 && "5. FINALIZING RECOMMENDED ROUTE..."}
          {step > 5 && "COMPLETING..."}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4 relative z-10">
        
        {/* Step 1: User Input */}
        <div className={`p-4 rounded-xl border border-slate-700 bg-slate-800/80 transition-all duration-700 ${step >= 1 ? 'opacity-100 scale-100 shadow-[0_0_20px_rgba(59,130,246,0.3)]' : 'opacity-30 scale-95'}`}>
          <div className="text-center mb-4 text-xs font-bold text-slate-300 uppercase tracking-widest">User Input</div>
          <div className="bg-white rounded-lg p-4 text-slate-900 space-y-3 shadow-inner">
            <div className="flex justify-center mb-2"><Accessibility size={32} className="text-blue-600"/></div>
            <div><div className="text-[10px] font-bold text-slate-500 uppercase">Start</div><div className="text-xs font-medium border-b border-slate-200 pb-1 truncate">{formData.origin || 'Current Location'}</div></div>
            <div><div className="text-[10px] font-bold text-slate-500 uppercase">Destination</div><div className="text-xs font-medium border-b border-slate-200 pb-1 truncate">{formData.destination || 'Hospital'}</div></div>
            <div><div className="text-[10px] font-bold text-slate-500 uppercase">Priority</div><div className="text-xs font-medium border-b border-slate-200 pb-1 text-blue-600">Low-Slope & Ramps</div></div>
          </div>
        </div>

        {/* Step 2: Geospatial Data */}
        <div className={`p-4 rounded-xl border border-slate-700 bg-slate-800/80 transition-all duration-700 ${step >= 2 ? 'opacity-100 scale-100 shadow-[0_0_20px_rgba(59,130,246,0.3)]' : 'opacity-30 scale-95'}`}>
          <div className="text-center mb-4 text-xs font-bold text-slate-300 uppercase tracking-widest">Geospatial Data</div>
          <div className="space-y-3">
            <div className="bg-slate-900 border border-slate-600 rounded-lg p-3 flex items-center gap-3">
              <Map className="text-emerald-400 shrink-0" size={20}/>
              <span className="text-xs font-medium text-slate-300">OpenStreetMap (Ramps)</span>
            </div>
            <div className="bg-slate-900 border border-slate-600 rounded-lg p-3 flex items-center gap-3">
              <ArrowUpToLine className="text-blue-400 shrink-0" size={20}/>
              <span className="text-xs font-medium text-slate-300">Elevators</span>
            </div>
            <div className="bg-slate-900 border border-slate-600 rounded-lg p-3 flex items-center gap-3">
              <AlertTriangle className="text-red-400 shrink-0" size={20}/>
              <span className="text-xs font-medium text-slate-300">Obstacles</span>
            </div>
          </div>
        </div>

        {/* Step 3: AI & ML Engine */}
        <div className={`p-4 rounded-xl border border-slate-700 bg-slate-800/80 transition-all duration-700 ${step >= 3 ? 'opacity-100 scale-100 shadow-[0_0_20px_rgba(139,92,246,0.3)]' : 'opacity-30 scale-95'}`}>
          <div className="text-center mb-4 text-xs font-bold text-slate-300 uppercase tracking-widest">AI & ML Engine</div>
          <div className="bg-slate-100 rounded-lg p-3 mb-3 text-slate-800 text-xs font-medium shadow-inner">
            <ul className="space-y-1">
              <li>• Incline (4.5%)</li>
              <li>• Kerb Height (2cm)</li>
              <li>• Surface (Paved)</li>
              <li>• Tactile Paving</li>
            </ul>
          </div>
          <div className="bg-purple-900/40 border border-purple-500/50 rounded-lg p-3 mb-3 text-center flex flex-col items-center">
            <Brain className="text-purple-400 mb-1" size={24}/>
            <span className="text-[11px] font-bold text-purple-200">Random Forest<br/>Classifier</span>
          </div>
          <div className="text-[11px] space-y-1.5">
            <div className="flex justify-between items-center"><span className="text-slate-400">Segment A</span> <span className="text-emerald-400 font-bold">➔ SAFE</span></div>
            <div className="flex justify-between items-center"><span className="text-slate-400">Segment B</span> <span className="text-red-400 font-bold">➔ UNSAFE</span></div>
          </div>
        </div>

        {/* Step 4: Routing */}
        <div className={`p-4 rounded-xl border border-slate-700 bg-slate-800/80 transition-all duration-700 ${step >= 4 ? 'opacity-100 scale-100 shadow-[0_0_20px_rgba(59,130,246,0.3)]' : 'opacity-30 scale-95'}`}>
          <div className="text-center mb-4 text-xs font-bold text-slate-300 uppercase tracking-widest">Route Scoring</div>
          <div className="space-y-3">
            <div className="bg-slate-100 rounded-lg p-3 text-center shadow-inner">
              <div className="text-xs font-bold text-slate-800">Route A: 82/100</div>
              <div className="mt-1.5 h-1 bg-slate-300 rounded-full overflow-hidden"><div className="h-full bg-blue-500 w-[82%]"></div></div>
            </div>
            <div className="bg-slate-900 border border-red-900/50 rounded-lg p-3 text-center relative overflow-hidden">
              <div className="absolute inset-0 bg-red-500/10 pointer-events-none"></div>
              <div className="text-xs font-bold text-slate-400">Route B</div>
              <div className="text-[9px] text-red-400 mt-0.5 leading-tight">(Blocked Ramp Detected<br/>➔ Recalculating)</div>
            </div>
            <div className="bg-slate-100 rounded-lg p-3 text-center border-2 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
              <div className="text-xs font-bold text-emerald-600">Route C: 94/100</div>
              <div className="text-[9px] text-emerald-600 mb-1">(Most Accessible)</div>
              <div className="mt-1 h-1 bg-slate-300 rounded-full overflow-hidden"><div className="h-full bg-emerald-500 w-[94%]"></div></div>
            </div>
          </div>
        </div>

        {/* Step 5: Final Route */}
        <div className={`p-4 rounded-xl border border-slate-700 bg-slate-800/80 transition-all duration-700 flex flex-col justify-center items-center ${step >= 5 ? 'opacity-100 scale-100 shadow-[0_0_20px_rgba(16,185,129,0.4)] border-emerald-500/50' : 'opacity-30 scale-95'}`}>
          <div className="text-center mb-6 text-xs font-bold text-emerald-400 uppercase tracking-widest">Recommended Route</div>
          <div className="w-24 h-40 bg-slate-900 border-[3px] border-slate-600 rounded-xl relative shadow-2xl flex items-center justify-center overflow-hidden">
             <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'linear-gradient(45deg, transparent 48%, #3b82f6 50%, transparent 52%)', backgroundSize: '15px 15px' }}></div>
             <MapPin className="text-emerald-400 absolute top-4 right-4 animate-bounce" size={20}/>
             <Accessibility className="text-blue-400 absolute bottom-4 left-4" size={16}/>
             <div className="absolute bottom-1/2 left-1/4 w-12 h-1 bg-emerald-500 transform rotate-45"></div>
          </div>
          <div className="mt-4 bg-emerald-900/40 border border-emerald-500/30 p-2 rounded text-center">
            <div className="text-xs font-bold text-emerald-300">Optimal Accessibility: 94/100</div>
            <div className="text-[10px] text-emerald-100/70 mt-0.5">Low-Slope Path</div>
          </div>
        </div>

      </div>
    </div>
  );
}
"""

# Insert the component before TravelPlannerPage
content = content.replace("function TravelPlannerPage", pipeline_component + "\nfunction TravelPlannerPage")

# Add ArrowUpToLine import if missing
if "ArrowUpToLine" not in content:
    content = content.replace("from 'lucide-react';", "ArrowUpToLine, from 'lucide-react';")

# Modify TravelPlannerPage to display it when loading
old_error_block = """      {error && <div className="mt-8 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">{error}</div>}
  
        {/* RESULTS AREA */}
        {plan && ("""

new_error_block = """      {error && <div className="mt-8 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">{error}</div>}
  
        {/* RESULTS AREA */}
        {loading && <LoadingPipeline formData={formData} />}
        {plan && !loading && ("""

content = content.replace(old_error_block, new_error_block)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Loading pipeline visualization injected.")
