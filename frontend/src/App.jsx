import React, {
  createContext, useCallback, useContext, useEffect, useMemo, useRef, useState,
} from 'react';
import { createPortal } from 'react-dom';
import {
  BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate,
} from 'react-router-dom';
import {
  Home, MapPin, Building2, FileText, Bookmark, UserRound, Settings, Search,
  ArrowRight, Sun, Moon, Navigation, Route as RouteIcon, Star, Users, Menu, X,
  SlidersHorizontal, Accessibility, Eye, Ear, Brain, ShieldCheck, Clock3, Ruler,
  AlertTriangle, CheckCircle2, Info, Bot, Send, Plus, Trash2, Save, ChevronRight,
  BarChart3, Database, Layers, MapPinned, RefreshCw, LocateFixed, Heart, Sparkles,
  LogOut, CircleHelp, Gauge, Zap, Flag, Building, Hospital, Trees, School, Store,
  ExternalLink, Footprints, Phone, Globe, Clock, Navigation2, ChevronDown, ChevronUp,
  Coffee, ShoppingBag, Utensils, ParkingCircle, Bike, Bus, Share2, Bell, Lock,
  Palette, HelpCircle, Award, TrendingUp, Activity, Map, Filter, Star as StarFill,
  Edit3, Camera, Upload,
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Legend,
} from 'recharts';
import {
  MapContainer, TileLayer, Polyline as LeafletPolyline, Marker, Popup,
  CircleMarker, useMap,
} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// ─── Constants ────────────────────────────────────────────────────────────────
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

// ─── Contexts ─────────────────────────────────────────────────────────────────
const ProfileUpdateContext = createContext(null);
const ThemeContext = createContext('light');
const SavedPlacesContext = createContext({ saved: [], toggleSave: () => {}, isSaved: () => false });

// ─── Leaflet icon fix ─────────────────────────────────────────────────────────
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// ─── Defaults ─────────────────────────────────────────────────────────────────
const defaultProfile = {
  mobility: true, avoid_stairs: true, low_slope: true,
  visual: false, hearing: false, cognitive: false,
  prioritize_confidence: true,
  distance_weight: 0.25, obstacle_weight: 0.30,
  confidence_weight: 0.20, simplicity_weight: 0.15, safety_weight: 0.10,
};

function loadSavedProfile() {
  try {
    const saved = JSON.parse(localStorage.getItem('accessroute_profile') || 'null');
    if (saved && typeof saved === 'object' && !Array.isArray(saved)) return { ...defaultProfile, ...saved };
  } catch { /* ignore */ }
  return { ...defaultProfile };
}

function loadSavedPlaces() {
  try {
    const data = JSON.parse(localStorage.getItem('accessroute_saved_places') || '[]');
    if (Array.isArray(data)) return data;
  } catch { /* ignore */ }
  return [];
}

// ─── Navigation groups ────────────────────────────────────────────────────────
const navGroups = [
  { label: 'Explore', items: [
    ['/travel-planner', '🧳 AI Travel Planner', Sparkles],

    ['/', 'Dashboard', Home],
    ['/find-route', 'Find Accessible Route', Search],
    ['/nearby-places', 'Nearby Places', MapPin],
    ['/accessible-buildings', 'Accessible Buildings', Building2],
  ]},
  { label: 'Community', items: [
    ['/reports', 'Reports & Ratings', FileText],
    ['/saved', 'Saved Places', Bookmark],
  ]},
  { label: 'Account', items: [
    ['/profile', 'Profile', UserRound],
    ['/settings', 'Settings', Settings],
  ]},
];

// ─── Location helpers ─────────────────────────────────────────────────────────
async function locationPermissionIsDenied() {
  if (!navigator.permissions?.query) return false;
  try { return (await navigator.permissions.query({ name: 'geolocation' })).state === 'denied'; }
  catch { return false; }
}
function deniedLocationMessage() {
  return 'Location permission is blocked. In browser site settings (icon beside the address bar), allow Location and turn on device location, then try again.';
}
function getDeviceLocation() {
  return new Promise((resolve, reject) => {
    const timeout = window.setTimeout(() => reject({ code: 3 }), 10000);
    navigator.geolocation.getCurrentPosition(
      p => { window.clearTimeout(timeout); resolve(p); },
      e => { window.clearTimeout(timeout); reject(e); },
      { enableHighAccuracy: false, maximumAge: 60000, timeout: 10000 },
    );
  });
}
function locationErrorMessage(error) {
  if (error?.code === 1) return 'Location permission is blocked. Allow Location for this site in browser settings.';
  if (error?.code === 2) return 'Your device could not determine its location. Turn on device location or choose a place instead.';
  if (error?.code === 3) return 'Location lookup timed out. Try again or choose a place instead.';
  return 'Could not access your location. Allow browser location access or choose a place.';
}
async function resolveRouteStart(value) {
  if (!/^(my location|current location)$/i.test(value.trim())) return value;
  if (!navigator.geolocation || !window.isSecureContext) throw new Error('Current location requires browser location access on HTTPS or localhost.');
  if (await locationPermissionIsDenied()) throw new Error(deniedLocationMessage());
  const position = await getDeviceLocation();
  return `${position.coords.latitude},${position.coords.longitude}`;
}

// ─── Map Tiles ───────────────────────────────────────────────────────────────
function AccessRouteMapTiles() {
  const theme = useContext(ThemeContext);
  if (MAPBOX_TOKEN) {
    const style = theme === 'dark' ? 'mapbox/dark-v11' : 'mapbox/streets-v12';
    return (
      <TileLayer
        url={`https://api.mapbox.com/styles/v1/${style}/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`}
        tileSize={512} zoomOffset={-1}
        attribution='&copy; <a href="https://www.mapbox.com/">Mapbox</a> &copy; OpenStreetMap'
      />
    );
  }
  return <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />;
}

// ─── Location search field ────────────────────────────────────────────────────

function SuggestionsPortal({ inputRef, suggestions, onSelect, open }) {
  const [rect, setRect] = useState(null);

  useEffect(() => {
    if (!open || !inputRef.current) { setRect(null); return; }
    function update() {
      const r = inputRef.current?.getBoundingClientRect();
      if (r) setRect({ top: r.bottom, left: r.left, width: r.width });
    }
    update();
    window.addEventListener('scroll', update, true);
    window.addEventListener('resize', update);
    return () => {
      window.removeEventListener('scroll', update, true);
      window.removeEventListener('resize', update);
    };
  }, [open, inputRef]);

  if (!open || !rect || suggestions.length === 0) return null;

  return createPortal(
    <div
      style={{
        position: 'fixed',
        top: rect.top + 4,
        left: rect.left,
        width: rect.width,
        zIndex: 99999,
        maxHeight: 288,
        overflowY: 'auto',
        borderRadius: 14,
        border: '1px solid var(--line, #e0d8f5)',
        background: 'var(--surface, #fff)',
        boxShadow: '0 16px 48px rgba(0,0,0,.18)',
      }}
    >
      {suggestions.map((s, i) => (
        <button
          key={`${s.latitude},${s.longitude}`}
          type="button"
          onMouseDown={e => { e.preventDefault(); onSelect(s); }}
          style={{
            display: 'flex', width: '100%', alignItems: 'center', gap: 8,
            padding: '10px 14px', textAlign: 'left', fontSize: 13,
            color: 'var(--text-main, #1a1428)',
            background: 'none', border: 'none',
            borderBottom: i < suggestions.length - 1 ? '1px solid var(--line, #e0d8f5)' : 'none',
            cursor: 'pointer',
          }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--surface-muted, #f5f2fd)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'none'; }}
        >
          <MapPin size={13} style={{ color: 'var(--accent, #7c3aed)', flexShrink: 0 }} />
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>{s.label}</span>
        </button>
      ))}
    </div>,
    document.body
  );
}

function LocationSearchField({ value, onChange, onSelect, placeholder, required = false }) {
  const [suggestions, setSuggestions] = useState([]);
  const [searching, setSearching] = useState(false);
  const [inputText, setInputText] = useState(value || '');
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef(null);
  const inputRef = useRef(null);
  const timerRef = useRef(null);
  const skipNextSearch = useRef(false);

  // Sync inputText when parent value changes externally
  useEffect(() => {
    const isCoord = /^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$/.test(value || '');
    if (isCoord) {
      const [lat, lon] = value.split(',').map(s => s.trim());
      fetch(`${API}/api/locations/reverse?lat=${lat}&lon=${lon}`)
        .then(r => r.json()).then(d => { if (d.label) setInputText(d.label); })
        .catch(() => setInputText(value));
    } else if (value === '' || value === 'My Location') {
      setInputText('');
    }
  }, [value]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = e => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  function handleInput(e) {
    const text = e.target.value;
    setInputText(text);
    onChange(text);
    setSuggestions([]);
    setOpen(false);
    if (skipNextSearch.current) { skipNextSearch.current = false; return; }
    clearTimeout(timerRef.current);
    if (text.trim().length < 2) { setSearching(false); return; }
    timerRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const r = await fetch(`${API}/api/locations/search?q=${encodeURIComponent(text.trim())}`);
        const d = await r.json();
        const results = d.suggestions || [];
        setSuggestions(results);
        setOpen(results.length > 0);
      } catch { setSuggestions([]); setOpen(false); }
      finally { setSearching(false); }
    }, 400);
  }

  function selectSuggestion(s) {
    const coords = `${s.latitude}, ${s.longitude}`;
    skipNextSearch.current = true;
    setInputText(s.label);
    setSuggestions([]);
    setOpen(false);
    onChange(coords);
    onSelect?.(s);
  }

  return (
    <div className="relative" ref={wrapperRef}>
      <input
        ref={inputRef}
        className="field"
        value={inputText}
        placeholder={placeholder}
        required={required}
        autoComplete="off"
        onChange={handleInput}
        onFocus={() => { if (suggestions.length > 0) setOpen(true); }}
      />
      {searching && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex gap-0.5 pointer-events-none">
          <span className="loading-dot h-1.5 w-1.5 rounded-full" style={{ background: 'var(--accent)' }} />
          <span className="loading-dot h-1.5 w-1.5 rounded-full" style={{ background: 'var(--accent)' }} />
          <span className="loading-dot h-1.5 w-1.5 rounded-full" style={{ background: 'var(--accent)' }} />
        </div>
      )}
      <SuggestionsPortal inputRef={inputRef} suggestions={suggestions} onSelect={selectSuggestion} open={open} />
    </div>
  );
}

// ─── Route origin picker ──────────────────────────────────────────────────────
function RouteOriginPicker({ value, onChange }) {
  const [mode, setMode] = useState('my');
  const [locationLabel, setLocationLabel] = useState('');
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState('');

  function switchMode(next) {
    setMode(next);
    setLocationError('');
    setLocationLabel('');
    if (next === 'my') onChange('My Location');
    else onChange('');
  }

  async function useCurrentLocation() {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser.');
      return;
    }
    setLocating(true);
    setLocationError('');
    try {
      const pos = await getDeviceLocation();
      const { latitude, longitude } = pos.coords;
      const coords = `${latitude}, ${longitude}`;
      onChange(coords);
      setLocationLabel(`${latitude.toFixed(5)}, ${longitude.toFixed(5)}`);
      try {
        const r = await fetch(`${API}/api/locations/reverse?lat=${latitude}&lon=${longitude}`);
        const d = await r.json();
        if (r.ok && d.label) setLocationLabel(d.label);
      } catch { /* keep coords */ }
    } catch (err) {
      setLocationError(locationErrorMessage(err));
    } finally {
      setLocating(false);
    }
  }

  return (
    <div>
      <div className="origin-choice" role="group" aria-label="Starting location type">
        <button type="button" className={mode === 'my' ? 'origin-choice-active' : ''} onClick={() => switchMode('my')}>
          <LocateFixed size={14} /> My Location
        </button>
        <button type="button" className={mode === 'choose' ? 'origin-choice-active' : ''} onClick={() => switchMode('choose')}>
          <Search size={14} /> Choose Location
        </button>
      </div>
      {mode === 'my' ? (
        <div className="mt-2 flex items-center justify-between gap-2 rounded-xl border border-dashed px-3 py-2.5" style={{ borderColor: 'var(--line)' }}>
          <span className="min-w-0 truncate text-xs" style={{ color: locationLabel ? 'var(--text-main)' : 'var(--text-muted)' }}>
            {locationLabel || 'Click to use your current GPS location'}
          </span>
          <button
            type="button"
            onClick={useCurrentLocation}
            disabled={locating}
            className="shrink-0 rounded-lg px-2 py-1 text-xs font-bold transition"
            style={{ color: 'var(--accent)', background: 'var(--accent-light)' }}
          >
            {locating ? 'Locating…' : locationLabel ? 'Refresh' : 'Use location'}
          </button>
        </div>
      ) : (
        <div className="mt-2">
          <LocationSearchField
            value={value === 'My Location' ? '' : value}
            onChange={onChange}
            placeholder="Search starting location…"
            required
          />
        </div>
      )}
      {locationError && <p className="mt-1 text-xs text-red-500">{locationError}</p>}
    </div>
  );
}


// ─── Route polyline with auto-fit ─────────────────────────────────────────────
function RoutePolyline({ positions, color, weight, opacity = 1, fit = false, onClick }) {
  const map = useMap();
  useEffect(() => {
    if (fit && positions?.length > 1) map.fitBounds(positions, { padding: [32, 32], maxZoom: 16 });
  }, [positions, fit, map]);
  return (
    <LeafletPolyline
      positions={positions}
      pathOptions={{ color, weight, opacity }}
      eventHandlers={onClick ? { click: onClick } : {}}
    />
  );
}

// ─── Map viewport setter ──────────────────────────────────────────────────────
function MapViewport({ center, zoom }) {
  const map = useMap();
  useEffect(() => { if (center) map.setView(center, zoom ?? 14); }, [center, zoom, map]);
  return null;
}

// ─── Map click handler (for reports pin placement) ───────────────────────────
function MapClickHandler({ onClick }) {
  const map = useMap();
  useEffect(() => {
    if (!map || !onClick) return;
    map.on('click', onClick);
    return () => map.off('click', onClick);
  }, [map, onClick]);
  return null;
}

// ─── Route path legend (theme aware) ─────────────────────────────────────────
function RoutePathLegend() {
  return (
    <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs route-legend-text">
      <span className="flex items-center gap-2"><span className="route-legend-line route-legend-optimized" />Optimized path</span>
      <span className="flex items-center gap-2"><span className="route-legend-line route-legend-alternative" />Alternative paths</span>
      <span className="flex items-center gap-2"><span className="route-legend-dot route-legend-origin" />Starting point</span>
      <span className="flex items-center gap-2"><span className="route-legend-dot route-legend-destination" />Destination</span>
    </div>
  );
}

// ─── Wheelchair badge ─────────────────────────────────────────────────────────
function WheelchairBadge({ value }) {
  if (value === 'yes' || value === 'designated') return <span className="badge-accessible">♿ Accessible</span>;
  if (value === 'limited') return <span className="badge-limited">⚠ Limited</span>;
  if (value === 'no') return <span className="badge-no">✗ Not accessible</span>;
  return <span className="badge-unknown">Unknown</span>;
}

// ─── Shared UI components ─────────────────────────────────────────────────────
function Panel({ title, icon, children, className = '', action }) {
  return (
    <section className={`app-panel border p-5 ${className}`} style={{ background: 'var(--surface)', borderColor: 'var(--line)' }}>
      <div className="mb-5 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-base font-bold" style={{ color: 'var(--text-main)' }}>{icon}{title}</div>
        {action}
      </div>
      {children}
    </section>
  );
}

function MetricCard({ icon, color, title, value, change }) {
  return (
    <div className="app-metric-card flex items-center gap-4 rounded-2xl border p-5">
      <div className={`rounded-2xl ${color} p-3 text-white`}>{React.cloneElement(icon, { size: 22 })}</div>
      <div>
        <div className="text-[11px] font-bold uppercase tracking-wide" style={{ color: 'var(--text-dim)' }}>{title}</div>
        <div className="my-0.5 text-2xl font-black" style={{ color: 'var(--text-main)' }}>{value}</div>
        <div className="text-xs font-medium text-emerald-600">{change}</div>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  const isInputWithSpecialLabel = React.isValidElement(children) && children.type === 'input'
    && (label === 'Starting point' || label === 'Destination');
  if (isInputWithSpecialLabel) {
    const { value, onChange } = children.props;
    const update = v => onChange({ target: { value: v } });
    return (
      <label className="block">
        <div className="mb-2 text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{label}</div>
        {label === 'Starting point'
          ? <RouteOriginPicker value={value} onChange={update} />
          : <LocationSearchField value={value} onChange={update} placeholder="Search destination" required />}
      </label>
    );
  }
  return (
    <label className="block">
      <div className="mb-2 text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{label}</div>
      {children}
    </label>
  );
}

function Detail({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg px-3 py-2" style={{ background: 'var(--surface-muted)' }}>
      <span className="text-sm" style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span className="text-sm font-semibold" style={{ color: 'var(--text-main)' }}>{value}</span>
    </div>
  );
}

function Empty({ text, icon }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl py-10 text-center" style={{ background: 'var(--surface-muted)' }}>
      {icon && <div className="text-4xl opacity-40">{icon}</div>}
      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{text}</p>
    </div>
  );
}

function LoadingDots({ text = 'Loading…' }) {
  return (
    <div className="flex items-center gap-2 py-4 justify-center" style={{ color: 'var(--text-muted)' }}>
      <div className="loading-dot h-2 w-2 rounded-full bg-blue-500" />
      <div className="loading-dot h-2 w-2 rounded-full bg-blue-500" />
      <div className="loading-dot h-2 w-2 rounded-full bg-blue-500" />
      <span className="text-sm ml-1">{text}</span>
    </div>
  );
}

function SettingRow({ title, description, children }) {
  return (
    <div className="setting-row flex items-center justify-between gap-4 rounded-2xl border p-4">
      <div>
        <div className="font-bold" style={{ color: 'var(--text-main)' }}>{title}</div>
        {description && <div className="mt-1 text-xs leading-5" style={{ color: 'var(--text-muted)' }}>{description}</div>}
      </div>
      {children}
    </div>
  );
}

function ScoreCircle({ score, size = 120, strokeWidth = 10, color = 'var(--route-optimized)' }) {
  const r = (size - strokeWidth * 2) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--line)" strokeWidth={strokeWidth} />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={strokeWidth}
        strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
    </svg>
  );
}

// ─── Route card ───────────────────────────────────────────────────────────────
function RouteCard({ route, selected, onClick, onSave }) {
  const theme = useContext(ThemeContext);
  const { isSaved, toggleSave } = useContext(SavedPlacesContext);
  const savedPlace = { name: route.name, detail: `${route.distance_m} m · ${route.time_mins} min`, score: route.accessibility_score ?? 0, type: 'route', lat: route.coordinates?.[0]?.[0], lon: route.coordinates?.[0]?.[1] };
  const saved = isSaved(route.name);

  return (
    <div
      className={`rounded-2xl border p-4 cursor-pointer transition-all ${selected ? 'route-card-selected' : 'route-card-unselected'}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick()}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="font-bold truncate" style={{ color: selected ? 'var(--route-optimized)' : 'var(--text-main)' }}>{route.name}</div>
          <div className="mt-0.5 text-xs" style={{ color: 'var(--text-dim)' }}>{route.pareto_status?.replaceAll('_', ' ')}</div>
          {route.provider && <div className="mt-0.5 text-[10px]" style={{ color: 'var(--text-dim)' }}>{route.provider}</div>}
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {selected && <CheckCircle2 size={17} style={{ color: 'var(--route-optimized)' }} />}
          <button
            type="button"
            onClick={e => { e.stopPropagation(); toggleSave(savedPlace); }}
            className="rounded-lg p-1.5 transition-colors"
            style={{ color: saved ? '#e11d48' : 'var(--text-dim)' }}
            title={saved ? 'Remove from saved' : 'Save place'}
          >
            <Heart size={15} fill={saved ? 'currentColor' : 'none'} />
          </button>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div className="rounded-xl p-2" style={{ background: 'var(--surface-muted)' }}>
          <div style={{ color: 'var(--text-dim)' }}>Distance</div>
          <div className="mt-0.5 font-bold" style={{ color: 'var(--text-main)' }}>{route.distance_m} m</div>
        </div>
        <div className="rounded-xl p-2" style={{ background: 'var(--surface-muted)' }}>
          <div style={{ color: 'var(--text-dim)' }}>Time</div>
          <div className="mt-0.5 font-bold" style={{ color: 'var(--text-main)' }}>{route.time_mins} min</div>
        </div>
        <div className="rounded-xl p-2" style={{ background: 'var(--surface-muted)' }}>
          <div style={{ color: 'var(--text-dim)' }}>Score</div>
          <div className="mt-0.5 font-bold" style={{ color: 'var(--route-optimized)' }}>{route.personalized_score ?? '—'}/100</div>
        </div>
        <div className="rounded-xl p-2" style={{ background: 'var(--surface-muted)' }}>
          <div style={{ color: 'var(--text-dim)' }}>Access</div>
          <div className="mt-0.5 font-bold" style={{ color: 'var(--text-main)' }}>{route.accessibility_score ?? '—'}/100</div>
        </div>
        <div className="rounded-xl p-2" style={{ background: 'var(--surface-muted)' }}>
          <div style={{ color: 'var(--text-dim)' }}>Confidence</div>
          <div className="mt-0.5 font-bold" style={{ color: 'var(--text-main)' }}>{route.confidence_score ?? '—'}%</div>
        </div>
        <div className="rounded-xl p-2" style={{ background: 'var(--surface-muted)' }}>
          <div style={{ color: 'var(--text-dim)' }}>Obstacles</div>
          <div className="mt-0.5 font-bold" style={{ color: (route.obstacles || 0) > 0 ? '#f59e0b' : 'var(--route-optimized)' }}>{route.obstacles ?? 0}</div>
        </div>
      </div>
      {route.route_status && (
        <div className={`mt-3 rounded-lg px-3 py-1.5 text-xs font-semibold ${route.route_status === 'clear_of_reported_obstacles' ? 'badge-accessible' : 'badge-limited'}`}>
          {route.route_status === 'clear_of_reported_obstacles' ? '✓ Clear of reported obstacles' : `⚠ ${route.affected_reports?.length} active report(s) nearby`}
        </div>
      )}
    </div>
  );
}

// ─── Weight slider ────────────────────────────────────────────────────────────
function Weight({ label, value }) {
  const setProfile = useContext(ProfileUpdateContext);
  const key = { Distance: 'distance_weight', Obstacles: 'obstacle_weight', Confidence: 'confidence_weight', Simplicity: 'simplicity_weight', Safety: 'safety_weight' }[label];
  return (
    <label className="block">
      <div className="mb-1 flex justify-between text-xs" style={{ color: 'var(--text-muted)' }}>
        <span>{label}</span><span className="font-bold">{Math.round(value * 100)}%</span>
      </div>
      <input type="range" min="0" max="1" step="0.05" value={value} aria-label={`${label} route weight`}
        onChange={e => { if (setProfile && key) setProfile(p => ({ ...p, [key]: Number(e.target.value) })); }}
        className="w-full" />
    </label>
  );
}

// ─── Login Page ───────────────────────────────────────────────────────────────
function LoginPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [role, setRole] = useState('user');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('user@accessroute.local');
  const [password, setPassword] = useState('ChangeMe123!');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setEmail(role === 'maintainer' ? 'maintainer@accessroute.local' : 'user@accessroute.local');
  }, [role]);

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setError('');
    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body = mode === 'login' ? { email, password, role } : { name, email, password, role };
      const r = await fetch(`${API}${endpoint}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || d.message || 'Request failed');
      if (mode === 'register') { setMode('login'); setPassword(''); setError('Account created! Sign in with your new account.'); }
      else { localStorage.setItem('accessroute_token', d.token); localStorage.setItem('accessroute_user', JSON.stringify(d.user)); onAuthenticated(d.user); }
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #f3f0fa 0%, #ede9fb 50%, #e8f5f0 100%)' }}>
      <div className="grid w-full max-w-5xl overflow-hidden rounded-[2rem] bg-white shadow-2xl lg:grid-cols-2">
        {/* Left panel */}
        <div className="hidden p-10 text-white lg:flex lg:flex-col lg:justify-between" style={{ background: 'linear-gradient(160deg, #5b21b6 0%, #7c3aed 60%, #6d28d9 100%)' }}>
          <div>
            <div className="mb-8 flex items-center gap-3">
              <div className="rounded-full bg-white/20 p-3"><Navigation size={26} /></div>
              <span className="text-2xl font-black">AccessRoute</span>
            </div>
            <h1 className="text-4xl font-black leading-tight">Accessible navigation for everyone.</h1>
            <p className="mt-5 leading-7" style={{ color: 'rgba(255,255,255,0.8)' }}>Personalized routes, accessibility insights, community reports, and safer mobility decisions — all in one place.</p>
            <div className="mt-8 space-y-3">
              {['♿ Optimized accessible routes', '🗺️ Real-time mapping & alternatives', '🏢 Building accessibility database', '🤖 AI route assistant'].map(f => (
                <div key={f} className="flex items-center gap-3 text-sm" style={{ color: 'rgba(255,255,255,0.85)' }}><CheckCircle2 size={16} className="text-emerald-300 shrink-0" />{f}</div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border p-4 text-sm" style={{ borderColor: 'rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.8)' }}>Secure role-based entry for users and maintainers.</div>
        </div>
        {/* Right panel */}
        <form onSubmit={submit} className="p-6 sm:p-10 flex flex-col justify-center">
          <div className="mb-6 lg:hidden flex items-center gap-2 text-xl font-black" style={{ color: '#5b21b6' }}><Navigation />AccessRoute</div>
          <h2 className="text-3xl font-black text-slate-800">{mode === 'login' ? 'Welcome back!' : 'Create account'}</h2>
          <p className="mt-2 mb-6 text-sm text-slate-500">Choose your account type to continue.</p>
          <div className="mb-5 grid grid-cols-2 gap-2 rounded-2xl bg-slate-100 p-1">
            {['user', 'maintainer'].map(r => (
              <button key={r} type="button" onClick={() => setRole(r)} className={`rounded-xl px-3 py-3 text-sm font-bold capitalize transition ${role === r ? 'bg-white shadow' : 'text-slate-500'}`} style={role === r ? { color: '#5b21b6' } : {}}>{r}</button>
            ))}
          </div>
          {mode === 'register' && (
            <label className="mb-4 block text-sm font-bold text-slate-600">Full name<input className="field mt-2" value={name} onChange={e => setName(e.target.value)} required minLength={2} placeholder="Your full name" /></label>
          )}
          <label className="mb-4 block text-sm font-bold text-slate-600">Email<input className="field mt-2" type="email" value={email} onChange={e => setEmail(e.target.value)} required /></label>
          <label className="mb-5 block text-sm font-bold text-slate-600">Password<input className="field mt-2" type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} /></label>
          {error && <div className={`mb-4 rounded-xl p-3 text-sm ${error.includes('created') ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>{error}</div>}
          <button disabled={busy} className="primary-button w-full mb-3">{busy ? 'Please wait…' : mode === 'login' ? 'Sign in to AccessRoute' : 'Create my account'}</button>
          <button type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }} className="w-full text-sm font-bold" style={{ color: '#7c3aed' }}>
            {mode === 'login' ? "Don't have an account? Register" : 'Already have an account? Sign in'}
          </button>
          {mode === 'login' && <p className="mt-5 text-center text-xs text-slate-400">Demo: use prefilled credentials or create a new account.</p>}
        </form>
      </div>
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────
function Sidebar({ mobileNav, setMobileNav }) {
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('accessroute_user') || 'null');
  const groups = [
    ...navGroups,
    ...(user?.role === 'maintainer' ? [{ label: 'Administration', items: [['/maintainer', 'Maintainer Console', ShieldCheck]] }] : []),
  ];
  return (
    <aside
      id="primary-sidebar"
      className={`app-sidebar ${mobileNav ? 'fixed inset-y-0 left-0 z-50 flex' : 'hidden'} lg:flex w-72 shrink-0 flex-col p-5`}
    >
      {/* Brand */}
      <div className="flex items-center justify-between mb-6">
        <Link to="/" className="flex items-center gap-3" onClick={() => setMobileNav(false)}>
          <div className="rounded-full bg-white/15 p-2.5"><Navigation size={22} /></div>
          <div>
            <div className="text-lg font-extrabold tracking-tight">AccessRoute</div>
            <div className="text-[10px] uppercase tracking-[0.15em] opacity-60">Navigate without barriers</div>
          </div>
        </Link>
        <button className="lg:hidden rounded-lg p-1.5 hover:bg-white/10" onClick={() => setMobileNav(false)} aria-label="Close navigation">
          <X size={18} />
        </button>
      </div>

      {/* User chip */}
      {user && (
        <div className="mb-6 rounded-2xl p-3 flex items-center gap-3" style={{ background: 'rgba(255,255,255,0.08)' }}>
          <div className="h-9 w-9 rounded-full bg-white/20 flex items-center justify-center text-sm font-bold shrink-0">
            {user.name?.[0]?.toUpperCase() || '?'}
          </div>
          <div className="min-w-0">
            <div className="text-sm font-bold truncate">{user.name}</div>
            <div className="text-[11px] opacity-60 capitalize">{user.role}</div>
          </div>
        </div>
      )}

      {/* Nav links — scrollable so sidebar never overflows */}
      <nav className="app-sidebar-scroll flex-1 space-y-6">
        {groups.map(group => (
          <div key={group.label}>
            <div className="mb-2 px-2 text-[10px] font-bold uppercase tracking-[0.18em] opacity-50">{group.label}</div>
            <div className="space-y-1">
              {group.items.map(([to, label, Icon]) => {
                const active = location.pathname === to || (to !== '/' && location.pathname.startsWith(to));
                return (
                  <Link
                    key={to} to={to}
                    onClick={() => setMobileNav(false)}
                    className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${active ? 'nav-link-active' : 'nav-link-inactive'}`}
                  >
                    <Icon size={17} />
                    <span>{label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Bottom card */}
      <div className="mt-4 rounded-2xl p-4 text-center" style={{ background: 'rgba(255,255,255,0.08)' }}>
        <div className="mb-2 text-3xl">🧑‍🦽</div>
        <div className="text-sm font-bold">Accessibility for Everyone</div>
        <div className="mt-1 text-xs opacity-60">Independence for all.</div>
      </div>
    </aside>
  );
}

// ─── Header ───────────────────────────────────────────────────────────────────
function Header({ theme, toggleTheme, mobileNav, setMobileNav, onSignOut, role }) {
  const location = useLocation();
  const headings = {
    '/': ['Dashboard', '📊'],
    '/find-route': ['Find Accessible Route', '🗺️'],
    '/nearby-places': ['Nearby Accessible Places', '📍'],
    '/accessible-buildings': ['Accessible Buildings', '🏢'],
    '/reports': ['Reports & Ratings', '📝'],
    '/saved': ['Saved Places', '🔖'],
    '/profile': ['Your Accessibility Profile', '♿'],
    '/settings': ['Settings', '⚙️'],
    '/maintainer': ['Maintainer Console', '🛡️'],
  };
  const [title, emoji] = headings[location.pathname] || headings['/'];
  return (
    <header className="app-header flex items-center justify-between gap-4 border-b px-4 py-3.5 sm:px-6 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <button className="header-icon-button lg:hidden" onClick={() => setMobileNav(!mobileNav)} aria-label="Toggle navigation" aria-expanded={mobileNav} aria-controls="primary-sidebar">
          {mobileNav ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div className="min-w-0">
          <h1 className="app-heading text-lg font-extrabold sm:text-xl">{emoji} {title}</h1>
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <button onClick={toggleTheme} className="header-icon-button" aria-label={theme === 'light' ? 'Enable dark mode' : 'Enable light mode'} title="Toggle theme">
          {theme === 'light' ? <Moon size={17} /> : <Sun size={17} />}
        </button>
        <button onClick={onSignOut} className="header-icon-button signout-icon-button" aria-label="Sign out" title="Sign out">
          <LogOut size={17} />
        </button>
      </div>
    </header>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('accessroute_theme') === 'dark' ? 'dark' : 'light');
  const [profile, setProfile] = useState(loadSavedProfile);
  const [mobileNav, setMobileNav] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [authUser, setAuthUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('accessroute_user') || 'null'); } catch { return null; }
  });
  const [savedPlaces, setSavedPlaces] = useState(loadSavedPlaces);

  useEffect(() => {
    try { localStorage.setItem('accessroute_profile', JSON.stringify(profile)); } catch { /* ignore */ }
  }, [profile]);

  useEffect(() => {
    try { localStorage.setItem('accessroute_saved_places', JSON.stringify(savedPlaces)); } catch { /* ignore */ }
  }, [savedPlaces]);

  function signOut() {
    const token = localStorage.getItem('accessroute_token');
    fetch(`${API}/api/auth/logout?token=${encodeURIComponent(token || '')}`, { method: 'POST' }).catch(() => {});
    localStorage.removeItem('accessroute_token');
    localStorage.removeItem('accessroute_user');
    setAuthUser(null);
  }

  function toggleTheme() {
    setTheme(cur => {
      const next = cur === 'light' ? 'dark' : 'light';
      localStorage.setItem('accessroute_theme', next);
      return next;
    });
  }

  function toggleSave(place) {
    setSavedPlaces(old => {
      const exists = old.find(p => p.name === place.name);
      return exists ? old.filter(p => p.name !== place.name) : [...old, { ...place, savedAt: new Date().toISOString() }];
    });
  }

  const savedCtx = useMemo(() => ({
    saved: savedPlaces,
    toggleSave,
    isSaved: name => savedPlaces.some(p => p.name === name),
  }), [savedPlaces]);

  return (
    <ThemeContext.Provider value={theme}>
      <SavedPlacesContext.Provider value={savedCtx}>
        <Router>
          {!authUser
            ? <Routes><Route path="*" element={<LoginPage onAuthenticated={setAuthUser} />} /></Routes>
            : (
              <div className={`app-shell ${theme === 'dark' ? 'theme-dark' : 'theme-light'}`}>
                <div className="flex" style={{ minHeight: '100vh' }}>
                  {mobileNav && <button type="button" className="fixed inset-0 z-40 bg-black/40 lg:hidden" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}
                  <Sidebar mobileNav={mobileNav} setMobileNav={setMobileNav} />
                  <div className="main-content min-w-0 flex-1">
                    <Header theme={theme} toggleTheme={toggleTheme} mobileNav={mobileNav} setMobileNav={setMobileNav} onSignOut={signOut} role={authUser.role} />
                    <div className="p-4 sm:p-6 lg:p-8">
                      <Routes>
                        <Route path="/" element={<DashboardPage profile={profile} setProfile={setProfile} />} />
                        <Route path="/travel-planner" element={<TravelPlannerPage profile={profile} />} />
                        <Route path="/find-route" element={
                          <ProfileUpdateContext.Provider value={setProfile}>
                            <FindRoutePage profile={profile} setProfile={setProfile} setChatOpen={setChatOpen} />
                          </ProfileUpdateContext.Provider>
                        } />
                        <Route path="/nearby-places" element={<NearbyPlacesPage />} />
                        <Route path="/accessible-buildings" element={<AccessibleBuildingsPage />} />
                        <Route path="/reports" element={<ReportsPage />} />
                        <Route path="/saved" element={<SavedPlacesPage />} />
                        <Route path="/profile" element={<ProfilePage profile={profile} setProfile={setProfile} />} />
                        <Route path="/settings" element={<SettingsPage profile={profile} setProfile={setProfile} toggleTheme={toggleTheme} theme={theme} />} />
                        <Route path="/maintainer" element={<MaintainerPage />} />
                      </Routes>
                    </div>
                  </div>
                </div>
                <ChatAssistant open={chatOpen} setOpen={setChatOpen} profile={profile} />
              </div>
            )
          }
        </Router>
      </SavedPlacesContext.Provider>
    </ThemeContext.Provider>
  );
}

// ─── Dashboard Page ───────────────────────────────────────────────────────────
const preferenceOptions = [
  { key: 'mobility', label: 'Mobility / Wheelchair access', icon: '♿' },
  { key: 'avoid_stairs', label: 'Avoid stairs & steps', icon: '🚫' },
  { key: 'low_slope', label: 'Prefer low slopes', icon: '⛰️' },
  { key: 'visual', label: 'Visual guidance cues', icon: '👁️' },
  { key: 'hearing', label: 'Visual alerts (no audio)', icon: '👂' },
  { key: 'cognitive', label: 'Simpler route instructions', icon: '🧠' },
  { key: 'prioritize_confidence', label: 'High-confidence data only', icon: '✓' },
];

function DashboardPage({ profile, setProfile }) {
  const [metrics, setMetrics] = useState(null);
  const [routes, setRoutes] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [start, setStart] = useState('My Location');
  const [destination, setDestination] = useState('');
  const [loading, setLoading] = useState(false);
  const [datasetPreview, setDatasetPreview] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const r = await fetch(`${API}/api/metrics/overview`);
        if (!r.ok) return;
        const d = await r.json();
        if (active) setMetrics(d);
      } catch { if (active) setMetrics(null); }
    }
    load();
    const interval = window.setInterval(load, 30000);
    return () => { active = false; window.clearInterval(interval); };
  }, []);

  useEffect(() => {
    fetch(`${API}/api/dataset/preview?limit=12`)
      .then(r => r.json())
      .then(d => setDatasetPreview(d))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!routes.length) return;
    const sel = routes.find(r => r.id === selectedId) || routes[0];
    localStorage.setItem('accessroute_route_context', JSON.stringify({ start, destination, selected_route: sel || null, routes, profile }));
  }, [routes, selectedId, start, destination, profile]);

  async function findRoute(e) {
    e.preventDefault();
    if (!destination.trim()) { window.alert('Enter a destination to find a route.'); return; }
    setLoading(true);
    try {
      const routeStart = await resolveRouteStart(start);
      const r = await fetch(`${API}/api/routes/compare`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ start: routeStart, destination, profile }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Could not generate a route.');
      const nextRoutes = d.routes || [];
      const nextSel = d.recommended_route_id || nextRoutes[0]?.id || '';
      setStart(routeStart);

      setRoutes(nextRoutes);
      setSelectedId(nextSel);
    } catch (err) { window.alert(err.message || 'Could not generate a route.'); }
    finally { setLoading(false); }
  }

  const selected = routes.find(r => r.id === selectedId) || routes[0];

  const pieData = metrics?.distribution ? [
    { name: 'Highly Accessible', value: metrics.distribution.highly_accessible_pct, color: '#10b981' },
    { name: 'Moderate', value: metrics.distribution.moderate_pct, color: '#f59e0b' },
    { name: 'Low Accessibility', value: metrics.distribution.low_pct, color: '#ef4444' },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Metric cards */}
      <section className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
        <MetricCard icon={<MapPin />} color="bg-blue-500" title="Analyzed Places" value={metrics?.data_summary?.records ?? '—'} change="Dataset records" />
        <MetricCard icon={<RouteIcon />} color="bg-emerald-500" title="Safe Nodes" value={metrics?.safe_nodes ?? '—'} change="Accessibility signals" />
        <MetricCard icon={<Star />} color="bg-purple-500" title="Avg. Accessibility" value={metrics?.average_accessibility_score ?? '—'} change="Out of 100" />
        <MetricCard icon={<Users />} color="bg-orange-500" title="Community Reports" value={metrics?.report_count ?? '—'} change="Submitted reports" />
      </section>

      {/* Route finder + map */}
      <section className="grid gap-6 xl:grid-cols-12">
        <Panel className="xl:col-span-4" title="Find Accessible Route" icon={<Search size={17} />}>
          <form onSubmit={findRoute} className="space-y-4">
            <Field label="From">
              <RouteOriginPicker value={start} onChange={setStart} />
            </Field>
            <Field label="To">
              <LocationSearchField value={destination} onChange={setDestination} placeholder="Search destination (e.g. City Library)" required />
            </Field>
            <div>
              <div className="mb-2 text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Quick preferences</div>
              <div className="grid grid-cols-2 gap-2">
                {[['mobility', '♿ Mobility'], ['avoid_stairs', '🚫 No stairs'], ['low_slope', '⛰️ Low slope'], ['prioritize_confidence', '✓ Confidence']].map(([key, label]) => (
                  <label key={key} className="flex items-center gap-2 rounded-xl border p-2.5 text-xs cursor-pointer" style={{ borderColor: profile[key] ? 'var(--accent)' : 'var(--line)', background: profile[key] ? 'var(--accent-light)' : 'var(--surface-muted)' }}>
                    <input type="checkbox" checked={profile[key]} onChange={e => setProfile({ ...profile, [key]: e.target.checked })} />
                    <span style={{ color: 'var(--text-main)' }}>{label}</span>
                  </label>
                ))}
              </div>
            </div>
            <button className="primary-button w-full" disabled={loading}>{loading ? 'Calculating routes…' : 'Find Accessible Route'}<ArrowRight size={16} /></button>
          </form>
          {routes.length > 0 && (
            <div className="mt-4 space-y-2">
              <div className="text-xs font-bold uppercase tracking-wide mb-2" style={{ color: 'var(--text-muted)' }}>Route results</div>
              {routes.map(r => (
                <button key={r.id} onClick={() => setSelectedId(r.id)}
                  className={`w-full rounded-xl border px-3 py-2.5 text-left text-xs transition ${r.id === selectedId ? 'route-card-selected' : 'route-card-unselected'}`}>
                  <span className="block font-bold truncate" style={{ color: 'var(--text-main)' }}>{r.name}</span>
                  <span className="mt-0.5 block" style={{ color: 'var(--text-muted)' }}>{r.distance_m} m · {r.time_mins} min · Score: {r.personalized_score}/100</span>
                </button>
              ))}
              <button className="secondary-button w-full mt-2" onClick={() => navigate('/find-route', { state: { routes, start, destination, selectedId } })}>
                Full route details <ChevronRight size={15} />
              </button>
            </div>
          )}
        </Panel>

        <Panel className="xl:col-span-8" title="Live Accessibility Map" icon={<Map size={17} />}>
          <div className="h-[360px] overflow-hidden rounded-xl">
            <MapContainer center={[13.06, 80.24]} zoom={13} className="h-full w-full" zoomControl={true}>
              <AccessRouteMapTiles />
              {routes.filter(r => r.id !== selectedId).map(r => (
                <RoutePolyline key={r.id} positions={r.coordinates || []} color="var(--route-alternative)" weight={4} opacity={0.7} onClick={() => setSelectedId(r.id)} />
              ))}
              {selected?.coordinates && (
                <>
                  <RoutePolyline positions={selected.coordinates} color="var(--route-optimized)" weight={6} fit />
                  <CircleMarker center={selected.coordinates[0]} radius={9} pathOptions={{ color: '#fff', weight: 3, fillColor: '#2563eb', fillOpacity: 1 }}>
                    <Popup>Starting point</Popup>
                  </CircleMarker>
                  <CircleMarker center={selected.coordinates[selected.coordinates.length - 1]} radius={9} pathOptions={{ color: '#fff', weight: 3, fillColor: '#e11d48', fillOpacity: 1 }}>
                    <Popup>Destination: {destination}</Popup>
                  </CircleMarker>
                </>
              )}
              {!selected?.coordinates && (
                <CircleMarker center={[13.06, 80.24]} radius={10} pathOptions={{ color: '#fff', weight: 3, fillColor: '#2563eb', fillOpacity: 1 }}>
                  <Popup>Search for a route to see it on the map.</Popup>
                </CircleMarker>
              )}
            </MapContainer>
          </div>
          <RoutePathLegend />
          {selected && (
            <div className="mt-3 grid grid-cols-4 gap-2 text-xs">
              {[
                ['Distance', `${selected.distance_m} m`],
                ['Time', `${selected.time_mins} min`],
                ['Access Score', `${selected.accessibility_score ?? '—'}/100`],
                ['Obstacles', selected.obstacles ?? 0],
              ].map(([l, v]) => (
                <div key={l} className="rounded-xl p-2.5 text-center" style={{ background: 'var(--surface-muted)' }}>
                  <div style={{ color: 'var(--text-dim)' }}>{l}</div>
                  <div className="mt-0.5 font-bold" style={{ color: 'var(--text-main)' }}>{v}</div>
                </div>
              ))}
            </div>
          )}
        </Panel>
      </section>

      {/* Charts and stats */}
      <section className="grid gap-6 xl:grid-cols-4 md:grid-cols-2">
        {/* Accessibility Score */}
        <Panel title="Accessibility Score" icon={<Award size={17} />}>
          <div className="flex flex-col items-center gap-3 py-2">
            <div className="relative">
              <ScoreCircle score={metrics?.average_accessibility_score ?? 0} size={130} strokeWidth={12} />
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-3xl font-black" style={{ color: 'var(--text-main)' }}>
                  {metrics ? (metrics.average_accessibility_score / 20).toFixed(1) : '—'}
                </div>
                <div className="text-xs font-bold" style={{ color: 'var(--text-dim)' }}>/ 5.0</div>
              </div>
            </div>
            <div className="flex gap-0.5 text-amber-400">
              {[1,2,3,4,5].map(n => <Star key={n} size={16} fill={n <= Math.round((metrics?.average_accessibility_score || 0) / 20) ? 'currentColor' : 'none'} />)}
            </div>
            <div className="w-full space-y-3 pt-2">
              {[['♿', 'Ramps', metrics?.feature_counts?.ramps], ['⛰️', 'Low slopes', metrics?.feature_counts?.low_slope], ['🦯', 'Tactile paths', metrics?.feature_counts?.tactile_paving]].map(([icon, label, count]) => (
                <div key={label} className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}><span>{icon}</span>{label}</span>
                  <span className="font-bold" style={{ color: 'var(--text-main)' }}>{count ?? '—'}</span>
                </div>
              ))}
            </div>
          </div>
        </Panel>

        {/* Accessibility overview pie */}
        <Panel title="Accessibility Overview" icon={<Activity size={17} />}>
          {pieData.length ? (
            <div className="flex flex-col items-center gap-4">
              <div className="accessibility-overview-chart h-40 w-full max-w-[180px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} dataKey="value" innerRadius={42} outerRadius={66} paddingAngle={3} stroke="none">
                      {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                    </Pie>
                    <Tooltip formatter={v => `${v}%`} contentStyle={{ background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: 8 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-full space-y-2.5">
                {pieData.map(item => (
                  <div key={item.name} className="flex items-center gap-3 text-sm">
                    <span className="h-3 w-3 shrink-0 rounded-full" style={{ background: item.color }} />
                    <span className="flex-1 text-xs" style={{ color: 'var(--text-muted)' }}>{item.name}</span>
                    <span className="font-bold tabular-nums" style={{ color: 'var(--text-main)' }}>{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          ) : <Empty text="Accessibility distribution unavailable." />}
        </Panel>

        {/* Surface types */}
        <Panel title="Surface Types" icon={<Layers size={17} />}>
          {metrics?.surface_distribution?.length ? (
            <div className="space-y-4">
              {metrics.surface_distribution.slice(0, 5).map((item, i) => (
                <div key={item.name} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span style={{ color: 'var(--text-muted)' }}>{item.name}</span>
                    <span className="font-bold" style={{ color: 'var(--text-main)' }}>{item.pct}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full" style={{ background: 'var(--line)' }}>
                    <div className="h-full rounded-full" style={{ width: `${item.pct}%`, background: item.pct >= 35 ? '#10b981' : item.pct >= 15 ? '#f59e0b' : '#3b82f6' }} />
                  </div>
                </div>
              ))}
            </div>
          ) : <Empty text="No surface data available." />}
          <button className="secondary-button mt-5 w-full" onClick={() => navigate('/accessible-buildings')}>
            Explore buildings <ChevronRight size={15} />
          </button>
        </Panel>

        {/* Recent reports */}
        <Panel title="Recent Reports" icon={<Flag size={17} />}>
          {metrics?.recent_reports?.length ? (
            <div className="space-y-3">
              {metrics.recent_reports.map(r => (
                <div key={r.id} className="flex items-center gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full" style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}>
                    <AlertTriangle size={15} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-bold" style={{ color: 'var(--text-main)' }}>{r.obstacle_type}</div>
                    <div className="text-[11px]" style={{ color: 'var(--text-dim)' }}>{r.severity} severity</div>
                  </div>
                  <span className={`rounded-lg px-2 py-1 text-[10px] font-bold uppercase tracking-wide ${r.status === 'resolved' ? 'badge-accessible' : 'badge-limited'}`}>
                    {(r.status || 'pending').replaceAll('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          ) : <Empty text="No community reports submitted yet." />}
          <button className="secondary-button mt-5 w-full" onClick={() => navigate('/reports')}>
            View all reports <ChevronRight size={15} />
          </button>
        </Panel>
      </section>

      {/* Data science bar chart — surface & feature breakdown */}
      {metrics && (
        <section className="grid gap-6 xl:grid-cols-2">
          <Panel title="Surface Type Breakdown" icon={<BarChart3 size={17} />}>
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.surface_distribution || []} layout="vertical" margin={{ left: 10, right: 20, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" horizontal={false} />
                  <XAxis type="number" tick={{ fill: 'var(--text-dim)', fontSize: 11 }} tickFormatter={v => `${v}%`} domain={[0, 'dataMax']} />
                  <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} width={90} />
                  <Tooltip
                    formatter={(v, n) => [`${v}%`, 'Coverage']}
                    contentStyle={{ background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: 10, fontSize: 12 }}
                    labelStyle={{ color: 'var(--text-main)', fontWeight: 700 }}
                  />
                  <Bar dataKey="pct" radius={[0, 6, 6, 0]}>
                    {(metrics.surface_distribution || []).map((entry, i) => (
                      <Cell key={i} fill={entry.pct >= 35 ? '#10b981' : entry.pct >= 15 ? '#3b82f6' : entry.pct >= 8 ? '#f59e0b' : '#94a3b8'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              {[['#10b981', '≥35% major'], ['#3b82f6', '15–34%'], ['#f59e0b', '8–14%'], ['#94a3b8', '<8% minor']].map(([color, label]) => (
                <span key={label} className="flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
                  <span className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: color }} />{label}
                </span>
              ))}
            </div>
          </Panel>

          <Panel title="Accessibility Feature Coverage" icon={<Activity size={17} />}>
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    { name: 'Ramps & kerbs', value: metrics.feature_counts?.ramps ?? 0, pct: Math.round(((metrics.feature_counts?.ramps ?? 0) / (metrics.data_summary?.records || 1)) * 100) },
                    { name: 'Tactile paving', value: metrics.feature_counts?.tactile_paving ?? 0, pct: Math.round(((metrics.feature_counts?.tactile_paving ?? 0) / (metrics.data_summary?.records || 1)) * 100) },
                    { name: 'Low slope', value: metrics.feature_counts?.low_slope ?? 0, pct: Math.round(((metrics.feature_counts?.low_slope ?? 0) / (metrics.data_summary?.records || 1)) * 100) },
                    { name: 'Safe nodes', value: metrics.safe_nodes ?? 0, pct: Math.round(((metrics.safe_nodes ?? 0) / (metrics.data_summary?.records || 1)) * 100) },
                  ]}
                  margin={{ left: 10, right: 20, top: 4, bottom: 4 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                  <YAxis tick={{ fill: 'var(--text-dim)', fontSize: 11 }} tickFormatter={v => `${v}%`} domain={[0, 100]} />
                  <Tooltip
                    formatter={(v, n, props) => [`${props.payload.pct}% (${props.payload.value} nodes)`, 'Coverage']}
                    contentStyle={{ background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: 10, fontSize: 12 }}
                    labelStyle={{ color: 'var(--text-main)', fontWeight: 700 }}
                  />
                  <Bar dataKey="pct" radius={[6, 6, 0, 0]} fill="var(--route-optimized)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="mt-3 text-xs" style={{ color: 'var(--text-dim)' }}>
              Percentage of {metrics.data_summary?.records} dataset nodes with each accessibility feature.
            </p>
          </Panel>
        </section>
      )}

      {/* Profile + data transparency */}
      <section className="grid gap-6 lg:grid-cols-2">
        <Panel title="Your Accessibility Profile" icon={<Accessibility size={17} />} action={
          <button className="secondary-button text-xs" onClick={() => navigate('/profile')}>Edit <ChevronRight size={13} /></button>
        }>
          <div className="grid gap-2 sm:grid-cols-2">
            {preferenceOptions.map(item => (
              <div key={item.key} className="flex items-center gap-3 rounded-xl px-3 py-2.5" style={{ background: profile[item.key] ? 'var(--accent-light)' : 'var(--surface-muted)', border: `1px solid ${profile[item.key] ? 'var(--accent)' : 'var(--line)'}` }}>
                <span className="text-base">{item.icon}</span>
                <div className="min-w-0">
                  <div className="text-xs font-bold truncate" style={{ color: 'var(--text-main)' }}>{item.label}</div>
                  <div className="text-[11px]" style={{ color: 'var(--text-dim)' }}>{profile[item.key] ? 'Enabled' : 'Disabled'}</div>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Data Transparency" icon={<Database size={17} />}>
          <div className="space-y-2">
            <Detail label="Dataset records" value={metrics?.data_summary?.records ?? datasetPreview?.total ?? '—'} />
            <Detail label="Data fields" value={metrics?.data_summary?.columns?.length ?? datasetPreview?.columns?.length ?? '—'} />
            <Detail label="Completeness" value={metrics?.data_summary ? `${metrics.data_summary.confidence}%` : '—'} />
            <Detail label="Active reports" value={metrics?.active_report_count ?? '—'} />
            <Detail label="Routing mode" value={MAPBOX_TOKEN ? 'Mapbox Directions' : 'OSM + Valhalla'} />
          </div>
          <div className="mt-4 rounded-xl p-3 text-xs leading-5" style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}>
            <Info size={13} className="inline mr-1 mb-0.5" />Data availability is not proof of accessibility. Confirm conditions locally.
          </div>
        </Panel>
      </section>

      {/* Dataset Preview Table */}
      {datasetPreview && datasetPreview.records?.length > 0 && (
        <section>
          <Panel title={`Dataset Preview — ${datasetPreview.total.toLocaleString()} records`} icon={<Database size={17} />}>
            <p className="mb-3 text-xs" style={{ color: 'var(--text-muted)' }}>
              Showing first {datasetPreview.records.length} rows of the accessibility routing dataset used for route scoring and analysis.
            </p>
            <div className="overflow-x-auto rounded-xl" style={{ border: '1px solid var(--line)' }}>
              <table className="w-full min-w-[640px] text-xs border-collapse">
                <thead>
                  <tr style={{ background: 'var(--surface-muted)' }}>
                    {datasetPreview.columns.map(col => (
                      <th key={col} className="px-3 py-2.5 text-left font-bold uppercase tracking-wide whitespace-nowrap" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--line)' }}>
                        {col.replace(/_/g, ' ')}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {datasetPreview.records.map((row, i) => (
                    <tr key={i} style={{ background: i % 2 === 0 ? 'var(--surface)' : 'var(--surface-muted)' }}>
                      {datasetPreview.columns.map(col => {
                        const val = row[col];
                        const isScore = col === 'accessibility_score';
                        const isBool = col === 'has_ramp' || col === 'tactile_paving';
                        return (
                          <td key={col} className="px-3 py-2 whitespace-nowrap font-mono" style={{ borderBottom: '1px solid var(--line)', color: isScore ? (val >= 80 ? '#10b981' : val >= 50 ? '#f59e0b' : '#ef4444') : 'var(--text-main)', fontWeight: isScore ? 700 : 400 }}>
                            {isBool ? (val ? '✓' : '✗') : val !== null && val !== undefined ? String(val) : '—'}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-3 flex flex-wrap gap-4 text-xs" style={{ color: 'var(--text-dim)' }}>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-emerald-500 inline-block" />Score ≥ 80 — High accessibility</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-amber-500 inline-block" />Score 50–79 — Moderate</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-red-500 inline-block" />Score &lt; 50 — Low accessibility</span>
            </div>
          </Panel>
        </section>
      )}
    </div>
  );
}


// ─── Find Route Page ──────────────────────────────────────────────────────────
function FindRoutePage({ profile, setProfile, setChatOpen }) {
  const location = useLocation();
  const initial = location.state || {};
  const [start, setStart] = useState(initial.start || 'My Location');

  const [destination, setDestination] = useState(initial.destination || '');
  const [routes, setRoutes] = useState(initial.routes || []);
  const [selectedId, setSelectedId] = useState(initial.selectedId || initial.routes?.[0]?.id || '');
  const [loading, setLoading] = useState(false);
  const [compareMode, setCompareMode] = useState('all');
  const [rerouting, setRerouting] = useState(false);
  const [routeNotice, setRouteNotice] = useState('');

  const { toggleSave, isSaved } = useContext(SavedPlacesContext);
  const selected = routes.find(r => r.id === selectedId) || routes[0];

  useEffect(() => {
    if (!routes.length) return;
    const sel = routes.find(r => r.id === selectedId) || routes[0];
    localStorage.setItem('accessroute_route_context', JSON.stringify({ start, destination, selected_route: sel || null, routes, profile }));
  }, [routes, selectedId, start, destination, profile]);

  async function findRoutes(e) {
    e.preventDefault();
    if (!destination.trim()) { setRouteNotice('Enter a destination to find a route.'); return; }
    setLoading(true); setRouteNotice('');
    try {
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
    finally { setLoading(false); }
  }

  async function reroute() {
    setRerouting(true); setRouteNotice('Recalculating around current reports…');
    try {
      const routeStart = await resolveRouteStart(start);
      const r = await fetch(`${API}/api/routes/reroute`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ start: routeStart, destination, profile }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Rerouting failed.');
      setRoutes(d.routes || []);
      setSelectedId(d.recommended_route_id || d.routes?.[0]?.id || '');
      setRouteNotice(`Routes refreshed. ${d.active_reports_considered?.length ?? 0} active reports considered.`);
    } catch (err) { setRouteNotice(err.message || 'Rerouting failed.'); }
    finally { setRerouting(false); }
  }

  function filteredRoutes() {
    const opt = routes.find(r => r.is_recommended) || routes[0];
    if (compareMode === 'pareto') return routes.filter(r => r.pareto_status === 'non_dominated');
    if (compareMode === 'accessible') return [...routes].sort((a, b) => (b.accessibility_score || 0) - (a.accessibility_score || 0));
    return routes;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-12">
      {/* Left panel */}
      <section className="space-y-5 xl:col-span-4">
        <Panel title="Route Details" icon={<Navigation2 size={17} />}>
          <form onSubmit={findRoutes} className="space-y-4">
            <Field label="Starting point">
              <RouteOriginPicker value={start} onChange={setStart} />
            </Field>
            <Field label="Destination">
              <LocationSearchField value={destination} onChange={setDestination} placeholder="Search destination…" required />
            </Field>
            <div>
              <div className="mb-3 text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Accessibility preferences</div>
              <div className="grid grid-cols-2 gap-2">
                {preferenceOptions.map(item => (
                  <label key={item.key} className="flex cursor-pointer items-center gap-2 rounded-xl border p-2.5 text-xs transition"
                    style={{ borderColor: profile[item.key] ? 'var(--accent)' : 'var(--line)', background: profile[item.key] ? 'var(--accent-light)' : 'var(--surface-muted)' }}>
                    <input type="checkbox" checked={!!profile[item.key]} onChange={e => setProfile({ ...profile, [item.key]: e.target.checked })} />
                    <span style={{ color: 'var(--text-main)' }}>{item.icon} {item.label}</span>
                  </label>
                ))}
              </div>
            </div>
            <button className="primary-button w-full" disabled={loading}>
              {loading ? 'Generating routes…' : 'Generate Accessible Routes'}<ArrowRight size={16} />
            </button>
          </form>
          {routeNotice && (
            <div className="mt-3 rounded-xl p-3 text-xs leading-5" style={{ background: 'var(--surface-muted)', color: 'var(--text-muted)' }}>
              <Info size={12} className="inline mr-1 mb-0.5" />{routeNotice}
            </div>
          )}
        </Panel>

        {/* Comparison settings */}
        <Panel title="Route Comparison" icon={<SlidersHorizontal size={17} />}>
          <Field label="View mode">
            <select className="field" value={compareMode} onChange={e => setCompareMode(e.target.value)}>
              <option value="all">All route alternatives</option>
              <option value="pareto">Pareto non-dominated only</option>
              <option value="accessible">Accessibility focused</option>
            </select>
          </Field>
          <div className="mt-4 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Priority weights</div>
            {[['Distance', profile.distance_weight], ['Obstacles', profile.obstacle_weight], ['Confidence', profile.confidence_weight], ['Simplicity', profile.simplicity_weight], ['Safety', profile.safety_weight]].map(([label, value]) => (
              <Weight key={label} label={label} value={value} />
            ))}
          </div>
        </Panel>

        {/* Dynamic rerouting */}
        <Panel title="Dynamic Rerouting" icon={<RefreshCw size={17} />}>
          <p className="text-sm leading-6" style={{ color: 'var(--text-muted)' }}>Refresh routes after new obstacles are reported. AccessRoute will re-rank alternatives using active community reports.</p>
          <button className="secondary-button mt-4 w-full" onClick={reroute} disabled={rerouting}>
            <RefreshCw size={15} className={rerouting ? 'animate-spin' : ''} />
            {rerouting ? 'Recalculating…' : 'Reroute around obstacles'}
          </button>
        </Panel>

        {/* Selected route details */}
        {selected && (
          <Panel title="Selected Route" icon={<CheckCircle2 size={17} />}>
            <div className="relative flex items-center justify-center py-4">
              <ScoreCircle score={selected.personalized_score ?? 0} size={120} strokeWidth={11} />
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-3xl font-black" style={{ color: 'var(--text-main)' }}>{selected.personalized_score ?? '—'}</div>
                <div className="text-xs" style={{ color: 'var(--text-dim)' }}>/100</div>
              </div>
            </div>
            <div className="space-y-2">
              <Detail label="Distance" value={`${selected.distance_m} m`} />
              <Detail label="Travel time" value={`${selected.time_mins} min`} />
              <Detail label="Accessibility" value={`${selected.accessibility_score ?? '—'}/100`} />
              <Detail label="Safety score" value={`${selected.safety_score ?? '—'}/100`} />
              <Detail label="Obstacles" value={selected.obstacles ?? 0} />
              <Detail label="Confidence" value={`${selected.confidence_score ?? '—'}%`} />
              <Detail label="Pareto status" value={String(selected.pareto_status || '—').replaceAll('_', ' ')} />
              <Detail label="Route status" value={String(selected.route_status || 'Not assessed').replaceAll('_', ' ')} />
            </div>
            {selected.affected_reports?.length > 0 && (
              <div className="mt-3 rounded-xl p-3 text-xs leading-5 badge-limited">
                <AlertTriangle size={13} className="inline mr-1 mb-0.5" />
                {selected.affected_reports.length} active community report(s) near this route.
              </div>
            )}
            <button className="secondary-button mt-4 w-full" onClick={() => setChatOpen(true)}>
              <Bot size={15} /> Explain this route with AI
            </button>
          </Panel>
        )}
      </section>

      {/* Right panel */}
      <section className="space-y-5 xl:col-span-8">
        <Panel title="Route Map" icon={<Map size={17} />}>
          <div className="h-[480px] overflow-hidden rounded-2xl">
            <MapContainer center={[13.06, 80.24]} zoom={14} className="h-full w-full">
              <AccessRouteMapTiles />
              {routes.filter(r => r.id !== selectedId).map(r => (
                <RoutePolyline key={r.id} positions={r.coordinates || []} color="var(--route-alternative)" weight={4} opacity={0.6} onClick={() => setSelectedId(r.id)} />
              ))}
              {selected?.coordinates && (
                <>
                  <RoutePolyline positions={selected.coordinates} color="var(--route-optimized)" weight={7} fit />
                  <CircleMarker center={selected.coordinates[0]} radius={9} pathOptions={{ color: '#fff', weight: 3, fillColor: '#2563eb', fillOpacity: 1 }}>
                    <Popup>Start: {start}</Popup>
                  </CircleMarker>
                  <CircleMarker center={selected.coordinates[selected.coordinates.length - 1]} radius={9} pathOptions={{ color: '#fff', weight: 3, fillColor: '#e11d48', fillOpacity: 1 }}>
                    <Popup>Destination: {destination}</Popup>
                  </CircleMarker>
                </>
              )}
            </MapContainer>
          </div>
          <RoutePathLegend />
        </Panel>

        {/* Route alternatives */}
        <Panel title="Route Alternatives" icon={<RouteIcon size={17} />} action={
          <span className="tag">{compareMode}</span>
        }>
          <div className="mb-3" style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            {routes.length ? `${filteredRoutes().length} of ${routes.length} routes shown` : 'Generate routes to see alternatives'}
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {filteredRoutes().map(route => (
              <RouteCard key={route.id} route={route} selected={route.id === selectedId} onClick={() => setSelectedId(route.id)} />
            ))}
          </div>
          {!routes.length && <Empty text="No routes generated yet. Enter start and destination above." icon="🗺️" />}
        </Panel>

        {/* Score breakdown */}
        {selected && Object.keys(selected.score_breakdown || {}).length > 0 && (
          <Panel title="Accessibility Score Breakdown" icon={<CircleHelp size={17} />}>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(selected.score_breakdown).map(([key, value]) => (
                <div key={key} className="rounded-xl p-4" style={{ background: 'var(--surface-muted)' }}>
                  <div className="text-xs capitalize" style={{ color: 'var(--text-muted)' }}>{key.replaceAll('_', ' ')}</div>
                  <div className="mt-1 text-xl font-black" style={{ color: 'var(--text-main)' }}>{value}</div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full" style={{ background: 'var(--line)' }}>
                    <div className="h-full rounded-full bg-emerald-500" style={{ width: `${Math.min(100, Number(value) || 0)}%` }} />
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-sm leading-6" style={{ color: 'var(--text-muted)' }}>
              Score reflects trade-offs among distance, obstacles, slope, safety, and data confidence. Not a guarantee of real-world accessibility.
            </p>
          </Panel>
        )}
      </section>
    </div>
  );
}

// ─── Nearby Places Page ───────────────────────────────────────────────────────
function NearbyPlacesPage() {
  const navigate = useNavigate();
  const { toggleSave, isSaved } = useContext(SavedPlacesContext);
  const [areaQuery, setAreaQuery] = useState('');
  const [center, setCenter] = useState(null);
  const [centerLabel, setCenterLabel] = useState('');
  const [centerSource, setCenterSource] = useState('chosen');
  const [category, setCategory] = useState('all');
  const [radius, setRadius] = useState(2000);
  const [wheelchairFilter, setWheelchairFilter] = useState('all');
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState('');
  const [expandedPlace, setExpandedPlace] = useState('');
  const [searchTrigger, setSearchTrigger] = useState(0);

  useEffect(() => {
    if (!center) { setPlaces([]); return; }
    const controller = new AbortController();
    async function searchNearby() {
      setLoading(true); setError('');
      try {
        const params = new URLSearchParams({ lat: center.latitude, lon: center.longitude, radius_m: radius, category });
        const r = await fetch(`${API}/api/places/nearby?${params}`, { signal: controller.signal });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail || 'Nearby search failed. The OpenStreetMap data service may be temporarily slow — try again in a moment.');
        setPlaces(d.places || []);
      } catch (err) {
        if (!controller.signal.aborted) { setPlaces([]); setError(err.message || 'Search failed. Please try again.'); }
      }
      finally { if (!controller.signal.aborted) setLoading(false); }
    }
    searchNearby();
    return () => controller.abort();
  }, [center, searchTrigger]);

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
      } catch { /* keep coords */ }
    } catch (err) { setError(err.message || locationErrorMessage(err)); }
    finally { setLocating(false); }
  }

  function selectArea(s) { setAreaQuery(s.label); setCenter({ latitude: s.latitude, longitude: s.longitude }); setCenterLabel(s.label); setCenterSource('chosen'); }

  function triggerSearch() {
    if (center) setSearchTrigger(t => t + 1);
    else setError('Please choose an area or use your current location first.');
  }


  const categoryMatches = {
    health: ['hospital', 'clinic', 'doctors', 'pharmacy'],
    education: ['school', 'college', 'university', 'library'],
    community: ['community centre', 'social facility'],
  };

  const visiblePlaces = places.filter(p =>
    p.distance_m <= radius
    && (category === 'all' || categoryMatches[category]?.includes(p.category.toLowerCase()))
    && (wheelchairFilter === 'all' || p.wheelchair === wheelchairFilter)
  );

  function planRoute(place) {
    if (!center) return;
    const s = centerSource === 'current' ? `${center.latitude}, ${center.longitude}` : centerLabel;
    const dest = [place.name, place.address].filter(Boolean).join(', ');
    navigate('/find-route', { state: { start: s, originLabel: centerLabel, destination: dest } });
  }

  function savePlace(place) {
    toggleSave({
      name: place.name,
      detail: `${place.category} · ${place.distance_m < 1000 ? `${place.distance_m} m` : `${(place.distance_m / 1000).toFixed(1)} km`}`,
      score: place.wheelchair === 'yes' ? 90 : 60,
      type: 'place',
      lat: place.latitude, lon: place.longitude,
      wheelchair: place.wheelchair,
      address: place.address,
    });
  }

  return (
    <div className="space-y-6">
      <Panel title="Find Nearby Accessible Places" icon={<MapPin size={17} />}>
        <div className="flex flex-col gap-2">
          <div className="grid gap-2 md:grid-cols-[1fr_auto_auto_auto]">
            <LocationSearchField value={areaQuery} onChange={v => { setAreaQuery(v); const m = v.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/); if (m) { setCenter({ latitude: Number(m[1]), longitude: Number(m[2]) }); setCenterLabel(v); setCenterSource('chosen'); } else if (!v.trim()) { setCenter(null); setCenterLabel(''); } }} onSelect={selectArea} placeholder="Type an area or address (e.g. T Nagar, Chennai)…" />
            <button type="button" className="secondary-button whitespace-nowrap" onClick={() => setFiltersOpen(o => !o)} aria-expanded={filtersOpen}>
              <Filter size={15} /> Filters {filtersOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            <button type="button" className="secondary-button whitespace-nowrap" onClick={triggerSearch} disabled={loading || !center} title="Re-run search with current area and filters">
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />{loading ? 'Searching…' : 'Refresh'}
            </button>
            <button type="button" className="primary-button whitespace-nowrap" onClick={useCurrentLocation} disabled={locating}>
              <LocateFixed size={15} />{locating ? 'Locating…' : 'My Location'}
            </button>
          </div>
          {!centerLabel && (
            <p className="text-xs px-1" style={{ color: 'var(--text-muted)' }}>
              💡 Type an area name above and pick a suggestion <strong>or</strong> click <strong>My Location</strong> for GPS-based search.
            </p>
          )}
          {centerLabel && <p className="text-xs" style={{ color: 'var(--text-muted)' }}>📍 Searching near: <strong>{centerLabel}</strong></p>}
        </div>
        {filtersOpen && (
          <div className="mt-4 grid gap-3 border-t pt-4 sm:grid-cols-3" style={{ borderColor: 'var(--line)' }}>
            <Field label="Place type">
              <select className="field" value={category} onChange={e => setCategory(e.target.value)}>
                <option value="all">All nearby places</option>
                <option value="health">Health services</option>
                <option value="education">Education & Libraries</option>
                <option value="community">Community services</option>
              </select>
            </Field>
            <Field label="Search radius">
              <select className="field" value={radius} onChange={e => setRadius(Number(e.target.value))}>
                <option value={500}>500 m</option>
                <option value={1000}>1 km</option>
                <option value={2000}>2 km</option>
                <option value={5000}>5 km</option>
              </select>
            </Field>
            <Field label="Wheelchair access">
              <select className="field" value={wheelchairFilter} onChange={e => setWheelchairFilter(e.target.value)}>
                <option value="all">All places</option>
                <option value="yes">Accessible (tagged yes)</option>
                <option value="limited">Limited access</option>
                <option value="no">Not accessible</option>
                <option value="unknown">Status unknown</option>
              </select>
            </Field>
          </div>
        )}
        {error && <div role="alert" className="mt-3 rounded-xl p-3 text-sm" style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}><AlertTriangle size={14} className="inline mr-1" />{error}</div>}
      </Panel>

      <section className="grid gap-6 xl:grid-cols-2">
        <Panel title={loading ? 'Searching…' : `Nearby places (${visiblePlaces.length})`} icon={loading ? <RefreshCw size={17} className="animate-spin" /> : <MapPin size={17} />}>
          {!center && <Empty text="Choose a search area or use your current location to find nearby places." icon="📍" />}
          {center && !loading && visiblePlaces.length === 0 && !error && <Empty text="No places matched these filters. Try a larger radius or different type." icon="🔍" />}
          {loading && <LoadingDots text="Searching nearby places…" />}
          <div className="space-y-3 mt-2">
            {visiblePlaces.map(place => (
              <article key={place.id} className="rounded-2xl border p-4 transition" style={{ borderColor: 'var(--line)', background: 'var(--surface)' }}>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="font-bold truncate" style={{ color: 'var(--text-main)' }}>{place.name}</h3>
                    <p className="mt-0.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                      {place.category} · {place.distance_m < 1000 ? `${place.distance_m} m` : `${(place.distance_m / 1000).toFixed(1)} km away`}
                    </p>
                    {place.address && <p className="mt-0.5 text-xs truncate" style={{ color: 'var(--text-dim)' }}>{place.address}</p>}
                  </div>
                  <div className="shrink-0 flex items-center gap-1.5">
                    <WheelchairBadge value={place.wheelchair} />
                    <button
                      type="button"
                      onClick={() => savePlace(place)}
                      className="rounded-lg p-1.5 transition-colors"
                      style={{ color: isSaved(place.name) ? '#e11d48' : 'var(--text-dim)' }}
                      title={isSaved(place.name) ? 'Remove from saved' : 'Save place'}
                    >
                      <Heart size={15} fill={isSaved(place.name) ? 'currentColor' : 'none'} />
                    </button>
                  </div>
                </div>

                {expandedPlace === place.id && (
                  <div className="mt-3 space-y-2 border-t pt-3 text-xs" style={{ borderColor: 'var(--line)', color: 'var(--text-muted)' }}>
                    <p><strong>Wheelchair:</strong> {place.wheelchair === 'yes' || place.wheelchair === 'designated' ? 'Tagged accessible (unverified independently)' : place.wheelchair === 'limited' ? 'Limited access tagged' : place.wheelchair === 'no' ? 'Tagged not wheelchair accessible' : 'Wheelchair access not recorded in OSM'}</p>
                    {place.opening_hours && <p><strong>Hours:</strong> {place.opening_hours}</p>}
                    {place.website && <a className="font-semibold underline" href={place.website} target="_blank" rel="noreferrer" style={{ color: 'var(--accent)' }}><Globe size={11} className="inline mr-1" />Visit website</a>}
                    <p style={{ color: 'var(--text-dim)' }}>Source: {place.source}</p>
                  </div>
                )}

                <div className="mt-3 flex gap-2">
                  <button type="button" className="secondary-button flex-1 text-xs" onClick={() => setExpandedPlace(expandedPlace === place.id ? '' : place.id)} aria-expanded={expandedPlace === place.id}>
                    {expandedPlace === place.id ? <ChevronUp size={13} /> : <ChevronDown size={13} />}{expandedPlace === place.id ? 'Less info' : 'More info'}
                  </button>
                  <button type="button" className="primary-button flex-1 text-xs" onClick={() => planRoute(place)}>
                    <Navigation2 size={13} />Plan route
                  </button>
                </div>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Map" icon={<Map size={17} />}>
          <div className="h-[540px] overflow-hidden rounded-xl">
            <MapContainer center={center ? [center.latitude, center.longitude] : [13.06, 80.24]} zoom={14} className="h-full w-full">
              <AccessRouteMapTiles />
              {center && <MapViewport center={[center.latitude, center.longitude]} />}
              {center && (
                <CircleMarker center={[center.latitude, center.longitude]} radius={10} pathOptions={{ color: '#fff', weight: 3, fillColor: '#2563eb', fillOpacity: 1 }}>
                  <Popup>Search center</Popup>
                </CircleMarker>
              )}
              {visiblePlaces.map(place => (
                <CircleMarker key={place.id} center={[place.latitude, place.longitude]} radius={8}
                  pathOptions={{ color: '#fff', weight: 2, fillColor: place.wheelchair === 'yes' || place.wheelchair === 'designated' ? '#10b981' : place.wheelchair === 'limited' ? '#f59e0b' : place.wheelchair === 'no' ? '#ef4444' : '#6366f1', fillOpacity: 0.95 }}>
                  <Popup>
                    <strong>{place.name}</strong><br />
                    {place.category} · {place.distance_m} m<br />
                    ♿ {place.wheelchair || 'unknown'}
                  </Popup>
                </CircleMarker>
              ))}
            </MapContainer>
          </div>
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <span className="badge-accessible">♿ Accessible</span>
            <span className="badge-limited">⚠ Limited</span>
            <span className="badge-no">✗ Not accessible</span>
            <span className="badge-unknown">? Unknown</span>
            <span className="flex items-center gap-1" style={{ color: 'var(--text-dim)' }}><span className="h-2.5 w-2.5 rounded-full bg-indigo-500 inline-block" />Untagged</span>
          </div>
        </Panel>
      </section>
    </div>
  );
}

// ─── Accessible Buildings Page ────────────────────────────────────────────────
function AccessibleBuildingsPage() {
  const { toggleSave, isSaved } = useContext(SavedPlacesContext);
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [mapCenter] = useState([13.06, 80.24]);
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/buildings`)
      .then(res => res.json())
      .then(data => {
        setBuildings(data.buildings || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load buildings', err);
        setLoading(false);
      });
  }, []);

  const checklist = ['Step-free entry', 'Accessible toilets', 'Elevator / lift', 'Tactile guidance paths', 'Clear wayfinding signage', 'Rest areas', 'Wide doorways ≥90cm', 'Emergency egress access', 'Accessible parking', 'Hearing loop system'];

  const filtered = buildings.filter(b =>
    !searchQuery || b.name.toLowerCase().includes(searchQuery.toLowerCase()) || b.type.toLowerCase().includes(searchQuery.toLowerCase())
  );


  return (
    <div className="space-y-6">
      <Panel title="Accessible Buildings Directory" icon={<Building2 size={17} />}>
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-dim)' }} />
            <input className="field pl-9" placeholder="Search buildings by name or type…" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
          </div>
        </div>
      </Panel>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map(b => {
          const saved = isSaved(b.name);
          return (
            <div key={b.id} className="rounded-2xl border p-5 transition-all cursor-pointer" style={{ borderColor: selectedBuilding?.id === b.id ? 'var(--route-optimized)' : 'var(--line)', background: selectedBuilding?.id === b.id ? 'var(--surface-accent)' : 'var(--surface)' }}
              onClick={() => setSelectedBuilding(selectedBuilding?.id === b.id ? null : b)}>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <Building2 size={16} style={{ color: 'var(--accent)' }} />
                    <span className="text-[11px] font-bold uppercase tracking-wide" style={{ color: 'var(--text-dim)' }}>{b.type}</span>
                  </div>
                  <h3 className="mt-1 font-bold text-sm" style={{ color: 'var(--text-main)' }}>{b.name}</h3>
                  <p className="mt-0.5 text-xs" style={{ color: 'var(--text-muted)' }}>{b.address}</p>
                </div>
                <div className="shrink-0 text-right">
                  <div className="text-xl font-black" style={{ color: b.score >= 85 ? '#10b981' : b.score >= 70 ? '#f59e0b' : '#ef4444' }}>{b.score}%</div>
                  <div className="text-[11px]" style={{ color: 'var(--text-dim)' }}>access score</div>
                </div>
              </div>

              <div className="mt-3 flex items-center gap-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                <StarFill size={12} className="text-amber-400 fill-amber-400" />
                <span>{b.rating}</span>
                <span>({b.reviews} reviews)</span>
              </div>

              {selectedBuilding?.id === b.id && (
                <div className="mt-4 space-y-2 border-t pt-4" style={{ borderColor: 'var(--line)' }}>
                  <div className="text-xs font-bold uppercase tracking-wide mb-2" style={{ color: 'var(--text-muted)' }}>Accessibility features</div>
                  {b.features.map(f => (
                    <div key={f} className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-main)' }}>
                      <CheckCircle2 size={13} className="text-emerald-500 shrink-0" />{f}
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-4 grid grid-cols-3 gap-2">
                <button type="button" className="secondary-button text-xs" onClick={e => { e.stopPropagation(); setSelectedBuilding(selectedBuilding?.id === b.id ? null : b); }}>
                  {selectedBuilding?.id === b.id ? 'Less' : 'Details'}
                </button>
                <button type="button" className="secondary-button text-xs" onClick={e => { e.stopPropagation(); navigate('/find-route', { state: { destination: `${b.name}, ${b.address}` } }); }}>
                  <Navigation2 size={12} />Route
                </button>
                <button type="button" className="secondary-button text-xs" onClick={e => { e.stopPropagation(); toggleSave({ name: b.name, detail: `${b.type} · ${b.score}% score`, score: b.score, type: 'building', lat: b.lat, lon: b.lon }); }}
                  style={{ color: saved ? '#e11d48' : 'var(--text-main)' }}>
                  <Heart size={12} fill={saved ? 'currentColor' : 'none'} />{saved ? 'Saved' : 'Save'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Map */}
      <Panel title="Buildings Map" icon={<Map size={17} />}>
        <div className="h-[360px] overflow-hidden rounded-xl">
          <MapContainer center={[13.06, 80.24]} zoom={13} className="h-full w-full">
            <AccessRouteMapTiles />
            {filtered.map(b => (
              <CircleMarker key={b.id} center={[b.lat, b.lon]} radius={9}
                pathOptions={{ color: '#fff', weight: 2, fillColor: b.score >= 85 ? '#10b981' : b.score >= 70 ? '#f59e0b' : '#ef4444', fillOpacity: 0.95 }}>
                <Popup><strong>{b.name}</strong><br />{b.type}<br />Accessibility: {b.score}%</Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
      </Panel>

      {/* Checklist */}
      <Panel title="Accessibility Checklist" icon={<CheckCircle2 size={17} />}>
        <p className="mb-4 text-sm" style={{ color: 'var(--text-muted)' }}>Standard features to look for when assessing a building's accessibility:</p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {checklist.map(item => (
            <div key={item} className="rounded-xl p-3 text-sm" style={{ background: 'var(--surface-muted)' }}>
              <CheckCircle2 size={15} className="mb-2 text-emerald-500" />
              <div style={{ color: 'var(--text-main)' }}>{item}</div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

// ─── Reports Page ─────────────────────────────────────────────────────────────
function ReportsPage() {
  const [report, setReport] = useState({ latitude: 13.06, longitude: 80.24, obstacle_type: 'Uneven surface', description: '', severity: 'medium' });
  const [submitted, setSubmitted] = useState([]);
  const [allReports, setAllReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [center, setCenter] = useState(null);
  const [locating, setLocating] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/obstacles`).then(r => r.json()).then(d => setAllReports(d.reports || [])).catch(() => {});
  }, [submitted]);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/obstacles/report`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(report) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Failed to submit report.');
      setSubmitted(old => [d.report || d, ...old]);
      setReport({ ...report, description: '' });
    } catch (err) { window.alert(err.message); }
    finally { setLoading(false); }
  }

  async function useLocation() {
    setLocating(true);
    try {
      const pos = await getDeviceLocation();
      setReport(r => ({ ...r, latitude: pos.coords.latitude, longitude: pos.coords.longitude }));
      setCenter({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
    } catch { /* ignore */ }
    finally { setLocating(false); }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Panel title="Report Accessibility Issue" icon={<Flag size={17} />}>
        <form onSubmit={submit} className="space-y-4">
          <Field label="Obstacle type">
            <select className="field" value={report.obstacle_type} onChange={e => setReport({ ...report, obstacle_type: e.target.value })}>
              {['Uneven surface', 'Blocked ramp', 'Missing ramp', 'Stairs only', 'Construction blocking path', 'Closed pathway', 'Broken elevator', 'No tactile paving', 'Flooded path', 'Poor lighting', 'Other'].map(o => <option key={o}>{o}</option>)}
            </select>
          </Field>
          <Field label="Severity">
            <select className="field" value={report.severity} onChange={e => setReport({ ...report, severity: e.target.value })}>
              <option value="low">Low — Minor inconvenience</option>
              <option value="medium">Medium — Significant barrier</option>
              <option value="high">High — Route completely blocked</option>
            </select>
          </Field>
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Latitude">
              <input className="field" type="number" step="any" value={report.latitude} onChange={e => setReport({ ...report, latitude: Number(e.target.value) })} />
            </Field>
            <Field label="Longitude">
              <input className="field" type="number" step="any" value={report.longitude} onChange={e => setReport({ ...report, longitude: Number(e.target.value) })} />
            </Field>
          </div>
          <button type="button" className="secondary-button w-full" onClick={useLocation} disabled={locating}>
            <LocateFixed size={14} />{locating ? 'Getting location…' : 'Use my current location'}
          </button>
          <Field label="Description">
            <textarea className="field" rows={4} placeholder="Describe the obstacle so others know what to expect…" value={report.description} onChange={e => setReport({ ...report, description: e.target.value })} />
          </Field>
          <button className="primary-button w-full" disabled={loading}>
            <Flag size={15} />{loading ? 'Submitting…' : 'Submit Report'}
          </button>
        </form>

        {/* Map for pin placement — tap to set location */}
        <div className="mt-4 overflow-hidden rounded-xl" style={{ border: '1px solid var(--line)' }}>
          <div className="px-3 py-2 text-xs font-semibold flex items-center gap-2" style={{ background: 'var(--surface-muted)', color: 'var(--text-muted)' }}>
            <MapPin size={12} />
            Tap the map to set precise report location
          </div>
          <div className="h-[220px]">
            <MapContainer center={[report.latitude, report.longitude]} zoom={15} className="h-full w-full" style={{ cursor: 'crosshair' }}>
              <AccessRouteMapTiles />
              <MapViewport center={[report.latitude, report.longitude]} />
              <MapClickHandler onClick={e => setReport(r => ({ ...r, latitude: +e.latlng.lat.toFixed(6), longitude: +e.latlng.lng.toFixed(6) }))} />
              <CircleMarker center={[report.latitude, report.longitude]} radius={11} pathOptions={{ color: '#fff', weight: 3, fillColor: '#ef4444', fillOpacity: 0.9 }}>
                <Popup>📍 Report location<br />{report.latitude.toFixed(5)}, {report.longitude.toFixed(5)}</Popup>
              </CircleMarker>
            </MapContainer>
          </div>
        </div>
      </Panel>


      <div className="space-y-5">
        <Panel title="Your Submitted Reports" icon={<CheckCircle2 size={17} />}>
          {submitted.length === 0 ? <Empty text="Reports you submit will appear here." icon="📝" /> : (
            <div className="space-y-3">
              {submitted.map((item, i) => (
                <div key={i} className="rounded-xl border p-4" style={{ borderColor: 'var(--line)' }}>
                  <div className="flex justify-between gap-2">
                    <div className="font-bold" style={{ color: 'var(--text-main)' }}>{item.obstacle_type || 'Obstacle report'}</div>
                    <span className={`tag ${item.severity === 'high' ? 'bg-red-100 text-red-700' : item.severity === 'medium' ? 'badge-limited' : 'badge-accessible'}`}>{item.severity}</span>
                  </div>
                  <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>{item.description || 'No description provided.'}</p>
                  <div className="mt-2 text-xs" style={{ color: 'var(--text-dim)' }}>{item.latitude}, {item.longitude}</div>
                </div>
              ))}
            </div>
          )}
        </Panel>

        <Panel title="Community Reports" icon={<Users size={17} />}>
          {allReports.length === 0 ? <Empty text="No community reports yet." icon="👥" /> : (
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {allReports.slice(0, 20).map(r => (
                <div key={r.id} className="rounded-xl border p-3 text-sm" style={{ borderColor: 'var(--line)' }}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold" style={{ color: 'var(--text-main)' }}>{r.obstacle_type}</span>
                    <span className={`tag text-[10px] ${r.status === 'resolved' ? 'badge-accessible' : r.status === 'verified' ? 'bg-blue-100 text-blue-700' : 'badge-limited'}`}>{r.status?.replaceAll('_', ' ')}</span>
                  </div>
                  <p className="mt-1 text-xs" style={{ color: 'var(--text-muted)' }}>{r.description || 'No description.'}</p>
                  <div className="mt-1 text-[11px]" style={{ color: 'var(--text-dim)' }}>{r.latitude?.toFixed(4)}, {r.longitude?.toFixed(4)} · {r.severity}</div>
                </div>
              ))}
            </div>
          )}
          <div className="mt-4 rounded-xl p-3 text-xs leading-5" style={{ background: 'var(--surface-muted)', color: 'var(--text-muted)' }}>
            <Info size={12} className="inline mr-1" />Reports are community observations. They should be reviewed and verified before being treated as confirmed barriers.
          </div>
        </Panel>
      </div>
    </div>
  );
}

// ─── Saved Places Page ────────────────────────────────────────────────────────
function SavedPlacesPage() {
  const { saved, toggleSave } = useContext(SavedPlacesContext);
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all');
  const typeIcons = { route: RouteIcon, place: MapPin, building: Building2 };

  const filtered = saved.filter(p => filter === 'all' || p.type === filter);

  return (
    <div className="space-y-6">
      <Panel title="Saved Places" icon={<Bookmark size={17} />} action={
        <span className="tag">{saved.length} saved</span>
      }>
        <div className="mb-4 flex gap-2 flex-wrap">
          {['all', 'route', 'place', 'building'].map(t => (
            <button key={t} type="button"
              className={`rounded-full px-4 py-1.5 text-xs font-bold capitalize transition ${filter === t ? 'primary-button' : 'secondary-button'}`}
              onClick={() => setFilter(t)}>
              {t === 'all' ? 'All' : t + 's'}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <Empty text={saved.length === 0 ? "No saved places yet. Save routes, nearby places, and buildings from their respective pages." : `No saved ${filter}s.`} icon="🔖" />
        ) : (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {filtered.map(place => {
              const Icon = typeIcons[place.type] || MapPin;
              return (
                <div key={place.name} className="saved-card flex items-start justify-between gap-3 rounded-2xl border p-4 transition-all" style={{ borderColor: 'var(--line)' }}>
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="rounded-xl p-2.5 shrink-0" style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}>
                      <Icon size={17} />
                    </div>
                    <div className="min-w-0">
                      <div className="font-bold text-sm truncate" style={{ color: 'var(--text-main)' }}>{place.name}</div>
                      <div className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{place.detail}</div>
                      {place.savedAt && <div className="text-[11px] mt-1" style={{ color: 'var(--text-dim)' }}>Saved {new Date(place.savedAt).toLocaleDateString()}</div>}
                      {place.score > 0 && (
                        <div className="mt-1 text-xs font-bold" style={{ color: '#10b981' }}>{place.score}% accessibility</div>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 shrink-0">
                    {place.type === 'route' || place.type === 'place' || place.type === 'building' ? (
                      <button type="button" className="secondary-button text-xs py-1 px-2"
                        onClick={() => navigate('/find-route', { state: { destination: place.name } })}>
                        <Navigation2 size={11} />Route
                      </button>
                    ) : null}
                    <button type="button" className="rounded-lg p-1.5 transition-colors text-red-400 hover:bg-red-50 hover:text-red-600"
                      onClick={() => toggleSave(place)} title="Remove from saved">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Panel>

      <Panel title="How to Save Places" icon={<Info size={17} />}>
        <div className="grid gap-3 sm:grid-cols-3">
          {[['Routes', '🗺️', 'In Find Route, click the ♥ heart icon on any route card.'], ['Nearby places', '📍', 'In Nearby Places, click the ♥ heart icon on any place card.'], ['Buildings', '🏢', 'In Accessible Buildings, click Save on any building card.']].map(([title, icon, desc]) => (
            <div key={title} className="rounded-xl p-4" style={{ background: 'var(--surface-muted)' }}>
              <div className="text-2xl mb-2">{icon}</div>
              <div className="font-bold text-sm mb-1" style={{ color: 'var(--text-main)' }}>{title}</div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{desc}</div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

// ─── Profile Page ─────────────────────────────────────────────────────────────
function ProfilePage({ profile, setProfile }) {
  const [saved, setSaved] = useState(false);
  const user = JSON.parse(localStorage.getItem('accessroute_user') || 'null');
  const [editName, setEditName] = useState(user?.name || '');
  const [editEmail, setEditEmail] = useState(user?.email || '');

  function saveProfile() {
    try {
      localStorage.setItem('accessroute_profile', JSON.stringify(profile));
      setSaved(true);
      window.setTimeout(() => setSaved(false), 2500);
    } catch { setSaved(false); }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* User info */}
      <Panel title="Account Information" icon={<UserRound size={17} />}>
        <div className="mb-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full text-2xl font-black text-white" style={{ background: 'var(--accent)' }}>
            {editName?.[0]?.toUpperCase() || '?'}
          </div>
          <div>
            <div className="text-lg font-black" style={{ color: 'var(--text-main)' }}>{editName}</div>
            <div className="text-sm capitalize" style={{ color: 'var(--text-muted)' }}>{user?.role} account</div>
          </div>
        </div>
        <div className="space-y-4">
          <label className="block text-sm font-bold" style={{ color: 'var(--text-main)' }}>
            Full name
            <input className="field mt-2" value={editName} onChange={e => setEditName(e.target.value)} placeholder="Your full name" />
          </label>
          <label className="block text-sm font-bold" style={{ color: 'var(--text-main)' }}>
            Email address
            <input className="field mt-2" type="email" value={editEmail} onChange={e => setEditEmail(e.target.value)} />
          </label>
          <div className="rounded-xl p-3 text-xs" style={{ background: 'var(--surface-muted)', color: 'var(--text-muted)' }}>
            <Info size={12} className="inline mr-1" />Account changes are stored locally in this demo.
          </div>
        </div>
      </Panel>

      {/* Accessibility preferences */}
      <Panel title="Accessibility Preferences" icon={<Accessibility size={17} />}>
        <p className="mb-4 text-sm" style={{ color: 'var(--text-muted)' }}>Choose preferences that describe how routes should be evaluated for you.</p>
        <div className="grid gap-3 sm:grid-cols-2">
          {preferenceOptions.map(item => (
            <label key={item.key} className="flex items-center gap-3 rounded-2xl border p-4 cursor-pointer transition-all"
              style={{ borderColor: profile[item.key] ? 'var(--accent)' : 'var(--line)', background: profile[item.key] ? 'var(--accent-light)' : 'var(--surface-muted)' }}>
              <input type="checkbox" checked={!!profile[item.key]} onChange={e => setProfile({ ...profile, [item.key]: e.target.checked })} />
              <span className="text-xl">{item.icon}</span>
              <span className="text-sm font-semibold" style={{ color: 'var(--text-main)' }}>{item.label}</span>
            </label>
          ))}
        </div>
      </Panel>

      {/* Route weights */}
      <Panel title="Route Priority Weights" icon={<Gauge size={17} />}>
        <p className="mb-4 text-sm" style={{ color: 'var(--text-muted)' }}>Adjust how much each factor influences your personalized route score.</p>
        <div className="space-y-5">
          {[['distance_weight', 'Distance weight'], ['obstacle_weight', 'Obstacle avoidance'], ['confidence_weight', 'Data confidence'], ['simplicity_weight', 'Route simplicity'], ['safety_weight', 'Safety priority']].map(([key, label]) => (
            <div key={key}>
              <div className="mb-2 flex justify-between text-sm font-bold">
                <span style={{ color: 'var(--text-main)' }}>{label}</span>
                <span style={{ color: 'var(--accent)' }}>{Math.round(profile[key] * 100)}%</span>
              </div>
              <input type="range" min="0" max="1" step="0.05" value={profile[key]}
                onChange={e => setProfile({ ...profile, [key]: Number(e.target.value) })}
                className="w-full" />
            </div>
          ))}
        </div>
        <div className="mt-6 flex items-center gap-3">
          <button type="button" onClick={saveProfile} className="primary-button">
            <Save size={16} />Save profile
          </button>
          {saved && <span role="status" className="text-sm font-semibold text-emerald-600">✓ Profile saved!</span>}
        </div>
      </Panel>

      {/* Profile summary */}
      <Panel title="Profile Summary" icon={<Activity size={17} />}>
        <div className="space-y-2">
          {preferenceOptions.map(item => (
            <div key={item.key} className="flex items-center justify-between rounded-lg px-3 py-2" style={{ background: 'var(--surface-muted)' }}>
              <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                <span>{item.icon}</span>{item.label}
              </div>
              <span className={`text-xs font-bold ${profile[item.key] ? 'text-emerald-600' : ''}`} style={{ color: profile[item.key] ? undefined : 'var(--text-dim)' }}>
                {profile[item.key] ? '✓ Enabled' : '— Disabled'}
              </span>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

// ─── Settings Page ────────────────────────────────────────────────────────────
function SettingsPage({ profile, setProfile, toggleTheme, theme }) {
  const [notifications, setNotifications] = useState(() => JSON.parse(localStorage.getItem('accessroute_notifications') || 'true'));
  const [units, setUnits] = useState(() => localStorage.getItem('accessroute_units') || 'metric');
  const [language, setLanguage] = useState(() => localStorage.getItem('accessroute_lang') || 'en');
  const [saved, setSaved] = useState(false);

  function saveSettings() {
    localStorage.setItem('accessroute_notifications', JSON.stringify(notifications));
    localStorage.setItem('accessroute_units', units);
    localStorage.setItem('accessroute_lang', language);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2500);
  }

  return (
    <div className="max-w-3xl space-y-6">
      <Panel title="Display & Theme" icon={<Palette size={17} />}>
        <SettingRow title="Dark mode" description="Switch between light and dark interface themes.">
          <button type="button" onClick={toggleTheme} className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors ${theme === 'dark' ? 'bg-blue-600' : 'bg-slate-200'}`}>
            <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${theme === 'dark' ? 'translate-x-6' : 'translate-x-1'}`} />
          </button>
        </SettingRow>
        <SettingRow title="Distance units" description="Choose between metric and imperial measurements.">
          <select className="field max-w-[160px]" value={units} onChange={e => setUnits(e.target.value)}>
            <option value="metric">Kilometres / metres</option>
            <option value="imperial">Miles / feet</option>
          </select>
        </SettingRow>
        <SettingRow title="Language" description="Interface language (demo only).">
          <select className="field max-w-[160px]" value={language} onChange={e => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="ta">Tamil</option>
            <option value="hi">Hindi</option>
          </select>
        </SettingRow>
      </Panel>

      <Panel title="Routing & Navigation" icon={<Navigation size={17} />}>
        <SettingRow title="Prioritize accessible infrastructure" description="Give more weight to ramps, step-free paths, and low slopes.">
          <input type="checkbox" checked={profile.mobility} onChange={e => setProfile({ ...profile, mobility: e.target.checked })} />
        </SettingRow>
        <SettingRow title="Avoid stairs and steps" description="Route calculations will penalize routes containing stairs.">
          <input type="checkbox" checked={profile.avoid_stairs} onChange={e => setProfile({ ...profile, avoid_stairs: e.target.checked })} />
        </SettingRow>
        <SettingRow title="Prefer high-confidence data" description="Prefer route segments with stronger verified data coverage.">
          <input type="checkbox" checked={profile.prioritize_confidence} onChange={e => setProfile({ ...profile, prioritize_confidence: e.target.checked })} />
        </SettingRow>
      </Panel>

      <Panel title="Notifications" icon={<Bell size={17} />}>
        <SettingRow title="Community report alerts" description="Show updates about new obstacle reports near your saved places.">
          <input type="checkbox" checked={notifications} onChange={e => setNotifications(e.target.checked)} />
        </SettingRow>
      </Panel>

      <Panel title="Privacy & Data" icon={<Lock size={17} />}>
        <div className="rounded-xl p-4 text-sm leading-6" style={{ background: 'var(--surface-muted)', color: 'var(--text-muted)' }}>
          <p>AccessRoute separates measured data, user reports, model estimates, and unverified information. Your location is only used for route calculations and is not stored on servers.</p>
          <p className="mt-3">Community reports are pseudonymous. Avoid including personally identifying information in report descriptions.</p>
        </div>
      </Panel>

      <Panel title="About AccessRoute" icon={<Info size={17} />}>
        <div className="space-y-2">
          <Detail label="Version" value="2.0.0" />
          <Detail label="Routing provider" value={MAPBOX_TOKEN ? 'Mapbox Directions' : 'OpenStreetMap + Valhalla'} />
          <Detail label="Geocoding" value={MAPBOX_TOKEN ? 'Mapbox Geocoding v6' : 'Nominatim + Photon'} />
          <Detail label="Map tiles" value={MAPBOX_TOKEN ? 'Mapbox Streets / Dark' : 'OpenStreetMap'} />
        </div>
      </Panel>

      <div className="flex items-center gap-3">
        <button type="button" onClick={saveSettings} className="primary-button"><Save size={15} />Save settings</button>
        {saved && <span className="text-sm font-semibold text-emerald-600">✓ Settings saved!</span>}
      </div>
    </div>
  );
}

// ─── Maintainer Page ──────────────────────────────────────────────────────────
function MaintainerPage() {
  const [summary, setSummary] = useState(null);
  const [reports, setReports] = useState([]);
  const token = localStorage.getItem('accessroute_token') || '';

  async function load() {
    const [a, b] = await Promise.all([
      fetch(`${API}/api/maintainer/summary?token=${encodeURIComponent(token)}`),
      fetch(`${API}/api/obstacles`),
    ]);
    const sd = await a.json(); const rd = await b.json();
    if (a.ok) setSummary(sd);
    if (b.ok) setReports(rd.reports || []);
  }

  useEffect(() => { load().catch(() => {}); }, []);

  async function action(id, type) {
    await fetch(`${API}/api/maintainer/reports/${id}/${type}?token=${encodeURIComponent(token)}`, { method: 'POST' });
    load();
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard icon={<Clock3 />} color="bg-amber-500" title="Pending" value={summary?.pending_reports ?? '—'} change="Awaiting review" />
        <MetricCard icon={<AlertTriangle />} color="bg-red-500" title="Active" value={summary?.active_reports ?? '—'} change="Affecting navigation" />
        <MetricCard icon={<CheckCircle2 />} color="bg-emerald-500" title="Resolved" value={summary?.resolved_reports ?? '—'} change="Closed reports" />
        <MetricCard icon={<Database />} color="bg-blue-500" title="Dataset" value={summary?.data_summary?.records ?? '—'} change="Accessibility records" />
      </div>

      <Panel title="Community Report Verification" icon={<ShieldCheck size={17} />}>
        <div className="space-y-3">
          {reports.length === 0 ? <Empty text="No community reports yet." icon="📝" /> : reports.map(r => (
            <div key={r.id} className="flex flex-col gap-3 rounded-2xl border p-4 md:flex-row md:items-center md:justify-between" style={{ borderColor: 'var(--line)' }}>
              <div className="min-w-0">
                <div className="font-bold" style={{ color: 'var(--text-main)' }}>{r.obstacle_type} <span className={`tag ml-2 ${r.status === 'resolved' ? 'badge-accessible' : r.status === 'verified' ? 'bg-blue-100 text-blue-700' : 'badge-limited'}`}>{r.status}</span></div>
                <div className="mt-1 text-xs" style={{ color: 'var(--text-dim)' }}>{r.latitude}, {r.longitude} · {r.severity}</div>
                <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>{r.description || 'No description provided.'}</p>
              </div>
              {r.status === 'pending_verification' && (
                <div className="flex gap-2 shrink-0">
                  <button className="primary-button text-sm" onClick={() => action(r.id, 'verify')}><CheckCircle2 size={14} />Verify</button>
                  <button className="danger-button text-sm" onClick={() => action(r.id, 'reject')}><X size={14} />Reject</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </Panel>

      <Panel title="Maintainer Guidelines" icon={<Info size={17} />}>
        <div className="grid gap-4 md:grid-cols-3">
          {[['Verify before trust', 'bg-blue-50', 'A community report is evidence, not proof. Verification changes status without claiming permanent accessibility.'], ['Monitor confidence', 'bg-amber-50', 'Low-confidence or conflicting information should remain visible to route users.'], ['Reroute after changes', 'bg-emerald-50', 'After verification, users can refresh route alternatives to incorporate current reports.']].map(([title, bg, desc]) => (
            <div key={title} className="rounded-2xl p-4" style={{ background: 'var(--surface-muted)' }}>
              <div className="font-bold mb-2" style={{ color: 'var(--text-main)' }}>{title}</div>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{desc}</p>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

// ─── Chat Assistant ───────────────────────────────────────────────────────────
function ChatAssistant({ open, setOpen, profile }) {
  const [messages, setMessages] = useState(() => {
    try { return JSON.parse(localStorage.getItem('accessroute_chat_history') || '[]'); } catch { return []; }
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [routeContext, setRouteContext] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => { localStorage.setItem('accessroute_chat_history', JSON.stringify(messages.slice(-40))); }, [messages]);

  useEffect(() => {
    if (!open) return;
    fetch(`${API}/api/chat/status`).then(r => r.json()).then(setStatus).catch(() => setStatus({ configured: false }));
    try { setRouteContext(JSON.parse(localStorage.getItem('accessroute_route_context') || '{}')); } catch { setRouteContext({}); }
  }, [open]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  const suggestions = [
    '🗺️ Which route is best for my profile?',
    '⚖️ Compare the available routes',
    '❓ Why was this route selected?',
    '⚠️ What obstacles are reported?',
    '📊 How confident is the accessibility data?',
    '♿ What features does the optimized route have?',
    '🔄 Should I reroute around obstacles?',
    '🏢 Any accessible buildings nearby?',
  ];

  async function send(text = message) {
    const question = text.replace(/^[🗺️⚖️❓⚠️📊♿🔄🏢]\s*/, '').trim();
    if (!question || loading) return;
    setMessage('');
    setMessages(old => [...old, { role: 'user', text: question }]);
    setLoading(true);
    try {
      const ctx = (() => { try { return JSON.parse(localStorage.getItem('accessroute_route_context') || '{}'); } catch { return routeContext; } })();
      const r = await fetch(`${API}/api/chat/message`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: question, profile, route_context: ctx }),
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Assistant request failed');
      setMessages(old => [...old, { role: 'assistant', text: d.answer || 'I could not generate an answer.', provider: d.provider }]);
    } catch (err) {
      setMessages(old => [...old, { role: 'assistant', text: `The assistant encountered an issue: ${err.message || 'Please check the backend is running.'}` }]);
    }
    finally { setLoading(false); }
  }

  const routeName = routeContext?.selected_route?.name;

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="fixed bottom-6 right-6 z-40 flex items-center gap-2 rounded-full px-5 py-3 font-bold text-white shadow-xl transition" style={{ background: 'var(--accent)' }}>
        <Bot size={18} />AccessRoute AI
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex max-h-[calc(100dvh-2rem)] w-[min(480px,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl border shadow-2xl" style={{ background: 'var(--surface)', borderColor: 'var(--line)' }}>
      {/* Header */}
      <div className="flex shrink-0 items-center justify-between px-4 py-4 text-white" style={{ background: 'var(--accent)' }}>
        <div className="flex items-center gap-3">
          <div className="rounded-xl p-2" style={{ background: 'rgba(255,255,255,0.15)' }}><Bot size={19} /></div>
          <div>
            <div className="font-black">AccessRoute Assistant</div>
            <div className="text-[11px] opacity-70">{status?.configured ? `AI · ${status.model || 'OpenAI'}` : 'Smart local assistant'}</div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button title="Clear chat" onClick={() => { setMessages([]); localStorage.removeItem('accessroute_chat_history'); }} className="rounded-lg p-2" style={{ background: 'rgba(255,255,255,0.1)' }}><Trash2 size={14} /></button>
          <button title="Close" onClick={() => setOpen(false)} className="rounded-lg p-2" style={{ background: 'rgba(255,255,255,0.1)' }}><X size={17} /></button>
        </div>
      </div>

      {/* Context banner */}
      {routeName && (
        <div className="shrink-0 border-b px-4 py-2 text-xs" style={{ background: 'var(--accent-light)', borderColor: 'var(--line)', color: 'var(--accent)' }}>
          <RouteIcon size={12} className="inline mr-1" />
          <strong>Active route:</strong> {routeName}
        </div>
      )}

      {/* Messages */}
      <div className="min-h-0 flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div>
            <div className="rounded-2xl p-4 text-sm leading-6" style={{ background: 'var(--surface-muted)', color: 'var(--text-muted)' }}>
              👋 Hi! I'm your AccessRoute assistant. I can help you understand route choices, accessibility features, obstacle reports, and compare alternatives based on your profile.
            </div>
            <div className="mt-3 text-xs font-bold uppercase tracking-wide mb-2" style={{ color: 'var(--text-dim)' }}>Suggested questions</div>
            <div className="flex flex-wrap gap-2">
              {suggestions.map(q => (
                <button key={q} onClick={() => send(q)} className="rounded-full border px-3 py-1.5 text-xs font-semibold transition" style={{ borderColor: 'var(--line)', background: 'var(--surface)', color: 'var(--text-main)' }}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((item, i) => (
          <div key={i} className={`rounded-2xl p-3.5 text-sm leading-6 ${item.role === 'user' ? 'ml-8 chat-bubble-user' : 'mr-4 chat-bubble-bot'}`}>
            <div className="whitespace-pre-wrap">{item.text}</div>
            {item.role === 'assistant' && item.provider && (
              <div className="mt-2 text-[10px] font-semibold uppercase tracking-wide" style={{ color: 'var(--text-dim)' }}>
                {item.provider === 'openai' ? '🤖 AI powered' : '💡 AccessRoute local assistant'}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="mr-4 flex items-center gap-2.5 rounded-2xl p-3.5 text-sm chat-bubble-bot">
            <div className="loading-dot h-2 w-2 rounded-full" style={{ background: 'var(--accent)' }} />
            <div className="loading-dot h-2 w-2 rounded-full" style={{ background: 'var(--accent)' }} />
            <div className="loading-dot h-2 w-2 rounded-full" style={{ background: 'var(--accent)' }} />
            <span style={{ color: 'var(--text-muted)' }}>Analyzing your route context…</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions when messages exist */}
      {messages.length > 0 && !loading && (
        <div className="shrink-0 flex gap-2 overflow-x-auto px-4 pb-1 pt-2" style={{ borderTop: `1px solid var(--line)` }}>
          {suggestions.slice(0, 4).map(q => (
            <button key={q} onClick={() => send(q)} className="shrink-0 rounded-full border px-2.5 py-1 text-[11px] font-semibold whitespace-nowrap transition" style={{ borderColor: 'var(--line)', background: 'var(--surface-muted)', color: 'var(--text-muted)' }}>
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="shrink-0 border-t p-3" style={{ borderColor: 'var(--line)' }}>
        <form onSubmit={e => { e.preventDefault(); send(); }} className="flex gap-2">
          <input
            className="field flex-1"
            aria-label="Ask AccessRoute Assistant"
            placeholder="Ask about routes, accessibility, obstacles…"
            value={message}
            onChange={e => setMessage(e.target.value)}
          />
          <button disabled={loading || !message.trim()} className="rounded-xl px-4 text-white transition disabled:opacity-40" style={{ background: 'var(--accent)' }}>
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}


// ─── AI Accessible Travel Planner Page ──────────────────────────────────────────────

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
      const res = await fetch(`${API}/api/ai-travel-plan`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: formData.origin, destination: formData.destination,
          start_date: formData.startDate || new Date().toISOString().split('T')[0],
          end_date: formData.endDate || new Date().toISOString().split('T')[0],
          travelers: formData.travelers, accessibility_profile: "general", preferences: formData.preferences
        })
      });
      const data = await res.json();
      if (data.status === 'success') setPlan(data);
      else setError(data.message || (data.detail ? JSON.stringify(data.detail) : "Unknown error"));
    } catch (err) { setError("Failed to generate plan. Please try again."); }
    finally { setLoading(false); }
  }

  return (
    <div className="flex flex-col gap-6 max-w-[1400px] mx-auto w-full pb-20">
      
      {/* HERO BANNER */}
      <div className="relative w-full h-[280px] rounded-2xl shadow-md flex-shrink-0" style={{ background: 'linear-gradient(to right, #001f3f, #003366)' }}>
        <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/60 rounded-2xl pointer-events-none"></div>
        
        <div className="absolute top-8 left-8 text-white z-10 pointer-events-none">
          <h1 className="text-4xl font-extrabold flex items-center gap-3 tracking-tight"><Sparkles className="text-blue-300" size={32}/> AI Travel Planner</h1>
          <p className="mt-3 text-[15px] opacity-90 max-w-lg font-medium leading-relaxed">
            Plan your accessible journey with personalized recommendations,<br/>real-time information and AI-powered insights.
          </p>
        </div>
      </div>

      {/* SEARCH BAR (Floating via negative margin) */}
      <div className="relative z-20 -mt-12 mx-auto w-[95%] max-w-6xl bg-white rounded-xl shadow-xl p-3 flex flex-col xl:flex-row gap-3 border border-gray-200">
        <div className="flex-1 w-full">
          <LocationSearchField required placeholder="From (e.g. Chennai)" value={formData.origin} onChange={val => setFormData({...formData, origin: val})} />
        </div>
        <div className="flex-1 w-full">
          <LocationSearchField required placeholder="Destination (e.g. Mahabalipuram)" value={formData.destination} onChange={val => setFormData({...formData, destination: val})} />
        </div>
        <div className="flex-[1.2] w-full flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400"><Clock size={16}/></div>
            <input type="date" title="Start Date" required className="w-full pl-9 pr-2 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-gray-700 h-full text-xs" value={formData.startDate} onChange={e => setFormData({...formData, startDate: e.target.value})} />
          </div>
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400"><Clock size={16}/></div>
            <input type="date" title="End Date" required className="w-full pl-9 pr-2 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-gray-700 h-full text-xs" value={formData.endDate} onChange={e => setFormData({...formData, endDate: e.target.value})} />
          </div>
        </div>
        <button onClick={generatePlan} disabled={loading} className="shrink-0 w-full xl:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 whitespace-nowrap text-sm">
          {loading ? <LoadingDots text="Planning" /> : <><Sparkles size={16}/> Generate Plan</>}
        </button>
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

export default App;

