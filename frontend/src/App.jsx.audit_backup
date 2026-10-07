import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Home, MapPin, Building, FileText, Bookmark, User, Settings,
  Map as MapIcon, Route as RouteIcon, Star, Users, Navigation, Search, ArrowRight, Sun, Bell, Moon
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import 'leaflet/dist/leaflet.css';
import { MapContainer, TileLayer, Polyline, Marker } from 'react-leaflet';
import L from 'leaflet';

// Fix leaflet icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const pieData = [
  { name: 'Highly Accessible', value: 45, color: '#10B981' },
  { name: 'Moderate', value: 35, color: '#F59E0B' },
  { name: 'Low Accessibility', value: 20, color: '#EF4444' },
];

export default function App() {
  return (
    <Router>
      <div className="flex h-screen bg-brand-bg text-slate-800 font-sans overflow-hidden">
        {/* SIDEBAR */}
        <Sidebar />

        {/* MAIN CONTENT AREA */}
        <main className="flex-1 flex flex-col h-full overflow-hidden">
          <Header />
          
          <div className="flex-1 p-8 overflow-y-auto">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/find-route" element={<FindRoutePage />} />
              <Route path="/nearby-places" element={<NearbyPlacesPage />} />
              <Route path="/accessible-buildings" element={<AccessibleBuildingsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/saved" element={<SavedPlacesPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

const Sidebar = () => {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <aside className="w-64 bg-brand-blue text-white flex flex-col p-6 rounded-r-3xl my-2 ml-2 shadow-2xl">
      <div className="flex items-center gap-3 mb-2">
        <div className="bg-white text-brand-blue p-1.5 rounded-full">
          <Navigation size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight">AccessRoute</h1>
          <p className="text-[10px] text-blue-200 uppercase tracking-widest">Navigate Without Barriers</p>
        </div>
      </div>
      
      <nav className="flex-1 mt-10 space-y-2">
        <NavItem to="/" icon={<Home size={20} />} label="Dashboard" active={currentPath === '/'} />
        <NavItem to="/find-route" icon={<Search size={20} />} label="Find Route" active={currentPath === '/find-route'} />
        <NavItem to="/nearby-places" icon={<MapPin size={20} />} label="Nearby Places" active={currentPath === '/nearby-places'} />
        <NavItem to="/accessible-buildings" icon={<Building size={20} />} label="Accessible Buildings" active={currentPath === '/accessible-buildings'} />
        <NavItem to="/reports" icon={<FileText size={20} />} label="Reports & Ratings" active={currentPath === '/reports'} />
        <NavItem to="/saved" icon={<Bookmark size={20} />} label="Saved Places" active={currentPath === '/saved'} />
        
        <div className="pt-8 space-y-2">
          <NavItem to="/profile" icon={<User size={20} />} label="Profile" active={currentPath === '/profile'} />
          <NavItem to="/settings" icon={<Settings size={20} />} label="Settings" active={currentPath === '/settings'} />
        </div>
      </nav>
      
      <div className="bg-blue-50/10 rounded-2xl p-4 text-center mt-auto border border-white/10 backdrop-blur-sm">
        <div className="text-4xl mb-2">🧑‍🦽</div>
        <h4 className="font-bold text-sm mb-1">Accessibility for Everyone,</h4>
        <p className="text-xs text-blue-200">Independence for All.</p>
      </div>
    </aside>
  );
};

const Header = () => {
  const location = useLocation();
  const getGreeting = () => {
    switch (location.pathname) {
      case '/': return { title: "Welcome back, User! 👋", subtitle: "Plan your accessible and comfortable journey" };
      case '/find-route': return { title: "Find Accessible Route 🗺️", subtitle: "Enter your destination to get a safe path" };
      case '/nearby-places': return { title: "Nearby Accessible Places 📍", subtitle: "Discover wheelchair-friendly spots around you" };
      default: return { title: "AccessRoute ♿", subtitle: "Navigate without barriers" };
    }
  };
  
  const greeting = getGreeting();

  return (
    <header className="flex justify-between items-center px-8 pt-8 pb-2">
      <div>
        <h2 className="text-3xl font-bold text-brand-blue mb-1">{greeting.title}</h2>
        <p className="text-slate-500">{greeting.subtitle}</p>
      </div>
      <div className="flex items-center gap-6 text-sm text-slate-600 bg-white px-6 py-3 rounded-full shadow-sm">
        <div className="flex items-center gap-2"><Sun size={18} className="text-yellow-500" /> 28°C Chennai</div>
        <div className="h-4 w-px bg-slate-200"></div>
        <Bell size={18} className="text-slate-400 hover:text-slate-800 cursor-pointer" />
        <Moon size={18} className="text-slate-800 bg-slate-100 p-1 rounded-full cursor-pointer" />
      </div>
    </header>
  );
};

// --- PAGES ---

const DashboardPage = () => {
  const [metrics, setMetrics] = useState({
    total_nodes_analyzed: "...",
    safe_nodes: "...",
    average_accessibility_score: "...",
    distribution: { highly_accessible_pct: 45, moderate_pct: 35, low_pct: 20 }
  });

  useEffect(() => {
    fetch('http://localhost:8000/api/metrics/overview')
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error("Error fetching metrics:", err));
  }, []);

  const dynamicPieData = [
    { name: 'Highly Accessible', value: metrics.distribution.highly_accessible_pct, color: '#10B981' },
    { name: 'Moderate', value: metrics.distribution.moderate_pct, color: '#F59E0B' },
    { name: 'Low Accessibility', value: metrics.distribution.low_pct, color: '#EF4444' },
  ];

  return (
  <>
    {/* TOP METRICS */}
    <div className="grid grid-cols-4 gap-6 mb-8">
      <MetricCard icon={<MapPin size={24} />} color="bg-blue-500" title="Analyzed Places" value={metrics.total_nodes_analyzed} change="Live ML Data" />
      <MetricCard icon={<RouteIcon size={24} />} color="bg-emerald-500" title="Safe Nodes" value={metrics.safe_nodes} change="Live ML Data" />
      <MetricCard icon={<Star size={24} />} color="bg-purple-500" title="Avg. Accessibility" value={`${metrics.average_accessibility_score}`} change="Out of 100" />
      <MetricCard icon={<Users size={24} />} color="bg-orange-500" title="Community Ratings" value="2,543" change="+15% this month" />
    </div>

    {/* MIDDLE SECTION */}
    <div className="grid grid-cols-12 gap-6 mb-8">
      {/* Quick Find Route */}
      <div className="col-span-3 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col">
        <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">Find Accessible Route</h3>
        <div className="space-y-4 flex-1">
          <div>
            <label className="text-xs text-slate-500 mb-1 block">From</label>
            <div className="relative">
              <MapPin size={16} className="absolute left-3 top-3 text-slate-400" />
              <input type="text" value="My Location" readOnly className="w-full pl-10 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none" />
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">To</label>
            <div className="relative">
              <MapPin size={16} className="absolute left-3 top-3 text-brand-blue" />
              <input type="text" value="City Library, Anna Salai" readOnly className="w-full pl-10 pr-3 py-2.5 bg-white border border-slate-200 rounded-xl text-sm outline-none" />
            </div>
          </div>
        </div>
        <Link to="/find-route" className="w-full bg-brand-lightblue hover:bg-blue-700 text-white font-bold py-3 rounded-xl mt-6 transition-colors shadow-lg shadow-blue-500/30 flex justify-center items-center gap-2">
          Find Route <ArrowRight size={18} />
        </Link>
      </div>

      {/* Map Snapshot */}
      <div className="col-span-6 bg-white p-3 rounded-2xl shadow-sm border border-slate-100 flex flex-col">
        <h3 className="font-bold text-slate-800 mb-3 px-3">Live Accessibility Map</h3>
        <div className="flex-1 bg-slate-100 rounded-xl overflow-hidden relative">
          <MapContainer center={[13.06, 80.24]} zoom={14} style={{ height: '100%', width: '100%' }} zoomControl={false}>
            <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />
            <Polyline positions={[[13.06, 80.23], [13.065, 80.24], [13.06, 80.25]]} color="#10B981" weight={6} />
            <Marker position={[13.06, 80.23]} />
          </MapContainer>
        </div>
      </div>

      {/* Accessibility Score */}
      <div className="col-span-3 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <h3 className="font-bold text-slate-800 mb-6">Accessibility Score</h3>
        <div className="flex justify-center mb-4">
          <div className="relative w-32 h-32 rounded-full border-8 border-emerald-500 flex flex-col items-center justify-center">
            <div className="text-4xl font-black text-slate-800 -mb-1">4.2</div>
            <div className="text-sm text-slate-400 font-bold">/ 5</div>
          </div>
        </div>
        <div className="text-center mb-6">
          <div className="flex justify-center gap-1 text-yellow-400 mb-1">
            <Star size={16} fill="currentColor" /><Star size={16} fill="currentColor" /><Star size={16} fill="currentColor" /><Star size={16} fill="currentColor" /><Star size={16} className="text-slate-200" />
          </div>
          <div className="text-emerald-600 font-bold mb-1">Good</div>
        </div>
        <div className="space-y-3">
          <FeatureListItem icon="♿" label="Ramps" count="842" />
          <FeatureListItem icon="🛗" label="Elevators" count="623" />
        </div>
      </div>
    </div>

    {/* BOTTOM SECTION */}
    <div className="grid grid-cols-3 gap-6">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <h3 className="font-bold text-slate-800 mb-4">Accessibility Overview</h3>
        <div className="flex items-center gap-4 h-40">
          <div className="w-32 h-32">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={dynamicPieData} cx="50%" cy="50%" innerRadius={35} outerRadius={55} paddingAngle={2} dataKey="value" stroke="none">
                  {dynamicPieData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 space-y-3">
            <LegendItem color="bg-emerald-500" label="Highly Accessible" pct={`${metrics.distribution.highly_accessible_pct}%`} />
            <LegendItem color="bg-amber-500" label="Moderate" pct={`${metrics.distribution.moderate_pct}%`} />
            <LegendItem color="bg-red-500" label="Low Accessibility" pct={`${metrics.distribution.low_pct}%`} />
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <h3 className="font-bold text-slate-800 mb-6">Top Accessible Categories</h3>
        <div className="space-y-4">
          <ProgressBar icon="🏛️" label="Libraries" pct={92} color="bg-emerald-500" />
          <ProgressBar icon="🏥" label="Hospitals" pct={88} color="bg-emerald-500" />
          <ProgressBar icon="🌲" label="Parks" pct={75} color="bg-amber-500" />
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-slate-800">Recent Reports</h3>
          <button className="text-xs text-brand-lightblue font-semibold hover:underline">View All</button>
        </div>
        <div className="flex-1 space-y-4 overflow-y-auto">
          <ReportItem icon="♿" title="Broken ramp near Main Gate" meta="Anna University • 2h ago" status="Low" statusColor="text-red-600 bg-red-100" />
          <ReportItem icon="🛣️" title="Smooth and accessible path" meta="Public Library • 1d ago" status="High" statusColor="text-emerald-600 bg-emerald-100" />
        </div>
      </div>
    </div>
  </>
  );
};

const FindRoutePage = () => {
  const [routes, setRoutes] = useState([]);
  const [selectedRouteId, setSelectedRouteId] = useState('balanced');
  const [loading, setLoading] = useState(false);

  const fetchRoutes = async () => {
    setLoading(true);
    try {
      // Mock API call to our new backend compare_routes endpoint
      const res = await fetch('http://localhost:8000/api/routes/compare?start=Anna%20Salai&destination=Library', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      setRoutes(data.routes);
      setSelectedRouteId('balanced');
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="grid grid-cols-12 gap-6 h-full">
      <div className="col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col h-[calc(100vh-140px)] overflow-y-auto">
        <h3 className="font-bold text-slate-800 mb-6">Route Details</h3>
        <div className="space-y-4 mb-6">
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Starting Point</label>
            <div className="relative">
              <MapPin size={16} className="absolute left-3 top-3 text-slate-400" />
              <input type="text" placeholder="Search starting point..." className="w-full pl-10 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:border-brand-lightblue" />
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Destination</label>
            <div className="relative">
              <MapPin size={16} className="absolute left-3 top-3 text-brand-blue" />
              <input type="text" placeholder="Search destination..." className="w-full pl-10 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:border-brand-lightblue" />
            </div>
          </div>
        </div>
        
        {routes.length === 0 ? (
          <>
            <h4 className="font-bold text-sm text-slate-800 mb-4">Accessibility Preferences</h4>
            <div className="grid grid-cols-2 gap-3 mb-8">
              <FeatureTag icon="♿" label="Wheelchair Friendly" active />
              <FeatureTag icon="🚫" label="Avoid Stairs" active />
              <FeatureTag icon="🛗" label="Elevator Available" active />
              <FeatureTag icon="🦯" label="Tactile Paving" />
            </div>
          </>
        ) : (
          <div className="space-y-4 mb-6">
            <h4 className="font-bold text-sm text-slate-800">Available Routes</h4>
            {routes.map(route => (
              <div 
                key={route.id} 
                onClick={() => setSelectedRouteId(route.id)}
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${selectedRouteId === route.id ? 'border-brand-blue bg-blue-50 shadow-md' : 'border-slate-100 hover:border-slate-300'}`}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-bold text-sm flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{backgroundColor: route.color}}></div>
                    {route.name}
                  </span>
                  <span className="text-xs font-bold text-slate-500">{route.metrics.time_mins} min</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="flex items-center gap-1 text-slate-600"><span>♿ Access:</span> <span className="font-bold">{route.metrics.accessibility_score}/100</span></div>
                  <div className="flex items-center gap-1 text-slate-600"><span>🛡️ Safety:</span> <span className="font-bold">{route.metrics.safety_score}/100</span></div>
                  <div className="flex items-center gap-1 text-slate-600"><span>⛰️ Slope:</span> <span className={`font-bold ${route.metrics.slope_pct > 5 ? 'text-red-500' : 'text-emerald-500'}`}>{route.metrics.slope_pct}%</span></div>
                  <div className="flex items-center gap-1 text-slate-600"><span>🚧 Obs:</span> <span className="font-bold">{route.metrics.obstacles}</span></div>
                </div>
              </div>
            ))}
          </div>
        )}

        <button 
          onClick={fetchRoutes}
          className="w-full bg-brand-lightblue hover:bg-blue-700 text-white font-bold py-3 rounded-xl mt-auto transition-colors flex justify-center items-center gap-2 flex-shrink-0"
        >
          {loading ? 'Calculating...' : 'Generate Accessible Route'} <ArrowRight size={18} />
        </button>
      </div>

      <div className="col-span-8 bg-white p-3 rounded-2xl shadow-sm border border-slate-100 h-[calc(100vh-140px)]">
        <div className="h-full w-full bg-slate-100 rounded-xl overflow-hidden relative">
          <MapContainer center={[13.06, 80.235]} zoom={15} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />
            {routes.map(route => (
              <Polyline 
                key={route.id}
                positions={route.coordinates} 
                color={route.color} 
                weight={selectedRouteId === route.id ? 8 : 4} 
                opacity={selectedRouteId === route.id ? 1 : 0.4}
              />
            ))}
            {routes.length > 0 && (
              <>
                <Marker position={routes[0].coordinates[0]} />
                <Marker position={routes[0].coordinates[routes[0].coordinates.length - 1]} />
              </>
            )}
          </MapContainer>
        </div>
      </div>
    </div>
  );
};

const NearbyPlacesPage = () => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-full">
    <h3 className="font-bold text-slate-800 mb-6">Nearby Accessible Places</h3>
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-1 space-y-4">
        <input type="text" placeholder="Search categories (e.g. Restaurants, Hospitals)" className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm" />
        <div className="p-4 border rounded-xl border-emerald-200 bg-emerald-50 cursor-pointer">
          <h4 className="font-bold text-emerald-800">Public Library (0.8km)</h4>
          <p className="text-xs text-emerald-600 mt-1">Fully Accessible • Ramp & Elevator</p>
        </div>
        <div className="p-4 border rounded-xl border-amber-200 bg-amber-50 cursor-pointer">
          <h4 className="font-bold text-amber-800">City Mall (1.2km)</h4>
          <p className="text-xs text-amber-600 mt-1">Partially Accessible • No Tactile Paving</p>
        </div>
      </div>
      <div className="col-span-2 bg-slate-100 rounded-xl flex items-center justify-center text-slate-400">
        [Map View of Places]
      </div>
    </div>
  </div>
);

const AccessibleBuildingsPage = () => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-full flex items-center justify-center text-slate-400 flex-col">
    <Building size={48} className="mb-4 text-brand-lightblue opacity-50" />
    <h2 className="text-2xl font-bold text-slate-600 mb-2">Accessible Buildings Database</h2>
    <p>Detailed architectural profiles for indoor navigation are syncing...</p>
  </div>
);

const ReportsPage = () => (
  <div className="grid grid-cols-2 gap-6 h-full">
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
      <h3 className="font-bold text-slate-800 mb-6">Report an Obstacle</h3>
      <div className="space-y-4">
        <select className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none">
          <option>Ramp Blocked</option>
          <option>Broken Pavement</option>
          <option>Construction</option>
          <option>Elevator Broken</option>
        </select>
        <textarea placeholder="Describe the issue..." rows="4" className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none"></textarea>
        <button className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-3 rounded-xl transition-colors">Submit Report</button>
      </div>
    </div>
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
      <h3 className="font-bold text-slate-800 mb-6">Live Community Reports</h3>
      <div className="space-y-4">
        <ReportItem icon="🚧" title="Construction on Main St" meta="Reported 5 mins ago" status="Active" statusColor="text-red-600 bg-red-100" />
        <ReportItem icon="🚗" title="Car blocking wheelchair ramp" meta="Reported 1 hr ago" status="Reviewing" statusColor="text-amber-600 bg-amber-100" />
      </div>
    </div>
  </div>
);

const SavedPlacesPage = () => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-full">
    <h3 className="font-bold text-slate-800 mb-6">Saved Places</h3>
    <p className="text-slate-500 text-sm">You have no saved places yet. Bookmark a location to see it here.</p>
  </div>
);

const ProfilePage = () => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-full flex flex-col items-center pt-20">
    <div className="w-24 h-24 bg-brand-blue rounded-full flex items-center justify-center text-white text-3xl font-bold mb-4">U</div>
    <h2 className="text-2xl font-bold text-slate-800 mb-1">Accessibility User</h2>
    <p className="text-slate-500 mb-8">Joined Sept 2026</p>
    <div className="grid grid-cols-3 gap-6 w-full max-w-2xl text-center">
      <div className="p-4 border rounded-xl border-slate-100"><div className="text-2xl font-bold text-brand-blue">12</div><div className="text-xs text-slate-500">Routes Taken</div></div>
      <div className="p-4 border rounded-xl border-slate-100"><div className="text-2xl font-bold text-brand-blue">4</div><div className="text-xs text-slate-500">Reports Submitted</div></div>
      <div className="p-4 border rounded-xl border-slate-100"><div className="text-2xl font-bold text-brand-blue">15</div><div className="text-xs text-slate-500">Places Reviewed</div></div>
    </div>
  </div>
);

const SettingsPage = () => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-full max-w-2xl mx-auto">
    <h3 className="font-bold text-slate-800 mb-6">Routing Preferences</h3>
    <div className="space-y-6">
      <div>
        <div className="flex justify-between text-sm font-bold text-slate-600 mb-2"><span>Prioritize Accessibility</span> <span>High</span></div>
        <input type="range" min="0" max="100" defaultValue="80" className="w-full accent-brand-blue" />
      </div>
      <div>
        <div className="flex justify-between text-sm font-bold text-slate-600 mb-2"><span>Safety Weight</span> <span>Medium</span></div>
        <input type="range" min="0" max="100" defaultValue="50" className="w-full accent-brand-blue" />
      </div>
      <div>
        <div className="flex justify-between text-sm font-bold text-slate-600 mb-2"><span>Avoid Slopes</span> <span>Strict</span></div>
        <input type="range" min="0" max="100" defaultValue="90" className="w-full accent-brand-blue" />
      </div>
      <button className="w-full bg-slate-800 text-white font-bold py-3 rounded-xl mt-8">Save Preferences</button>
    </div>
  </div>
);

// --- COMPONENTS ---

const NavItem = ({ to, icon, label, active }) => (
  <Link to={to} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${active ? 'bg-white text-brand-blue font-bold shadow-sm' : 'text-blue-100 hover:bg-white/10'}`}>
    {icon} <span className="text-sm">{label}</span>
  </Link>
);

const MetricCard = ({ icon, color, title, value, change }) => (
  <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
    <div className={`w-12 h-12 rounded-full ${color} text-white flex items-center justify-center shadow-lg shadow-black/5`}>
      {icon}
    </div>
    <div>
      <h4 className="text-xs text-slate-500 font-semibold uppercase tracking-wider">{title}</h4>
      <div className="text-2xl font-black text-slate-800 my-0.5">{value}</div>
      <div className="text-xs text-emerald-500 font-medium">{change}</div>
    </div>
  </div>
);

const FeatureTag = ({ icon, label, active }) => (
  <div className={`flex flex-col items-center justify-center p-3 rounded-xl text-center border cursor-pointer transition-all ${active ? 'border-brand-lightblue bg-blue-50' : 'border-slate-100 bg-slate-50 hover:border-slate-300'}`}>
    <span className="text-2xl mb-1">{icon}</span>
    <span className="text-[10px] leading-tight text-slate-600 font-bold">{label}</span>
  </div>
);

const FeatureListItem = ({ icon, label, count }) => (
  <div className="flex justify-between items-center text-sm">
    <div className="flex items-center gap-2 text-slate-600"><span>{icon}</span> {label}</div>
    <span className="font-bold text-slate-800">{count}</span>
  </div>
);

const LegendItem = ({ color, label, pct }) => (
  <div className="flex justify-between items-center text-sm">
    <div className="flex items-center gap-2">
      <div className={`w-2.5 h-2.5 rounded-full ${color}`}></div>
      <span className="text-slate-600">{label}</span>
    </div>
    <span className="font-bold">{pct}</span>
  </div>
);

const ProgressBar = ({ icon, label, pct, color }) => (
  <div className="flex items-center gap-3 text-sm">
    <div className="w-24 flex items-center gap-2 text-slate-600"><span>{icon}</span><span className="truncate">{label}</span></div>
    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
      <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }}></div>
    </div>
    <div className="w-8 text-right font-bold text-slate-800">{pct}%</div>
  </div>
);

const ReportItem = ({ icon, title, meta, status, statusColor }) => (
  <div className="flex items-center gap-4">
    <div className="w-10 h-10 rounded-full bg-blue-50 border border-blue-100 flex items-center justify-center text-lg">{icon}</div>
    <div className="flex-1 min-w-0">
      <h4 className="text-sm font-bold text-slate-800 truncate">{title}</h4>
      <p className="text-[11px] text-slate-400 truncate">{meta}</p>
    </div>
    <div className={`px-2 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider ${statusColor}`}>{status}</div>
  </div>
);
