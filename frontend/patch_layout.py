import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change default theme to light to match the video
content = content.replace("const ThemeContext = createContext('dark');", "const ThemeContext = createContext('light');")
# Also look for any hardcoded defaultTheme initialization
content = content.replace("useState(() => localStorage.getItem('accessroute_theme') || 'dark')", "useState(() => localStorage.getItem('accessroute_theme') || 'light')")

# 2. Update Sidebar (navGroups) to match the video exactly
old_nav = """const navGroups = [
  { label: 'Explore', items: [
    ['/travel-planner', 'dY 3 AI Travel Planner', Sparkles],

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
];"""

new_nav = """const navGroups = [
  { label: 'Main', items: [
    ['/', 'Home', Home],
    ['/nearby-places?category=hospital', 'Hospitals', Hospital],
    ['/nearby-places?category=restaurant', 'Restaurants', Utensils],
    ['/nearby-places?category=pharmacy', 'Pharmacies', Plus],
    ['/travel-planner', 'Travel Planner', Sparkles],
    ['/find-route', 'Find Route', Map],
  ]},
  { label: 'System', items: [
    ['/reports', 'Reports & Heatmap', MapPinned],
    ['/settings', 'Settings', Settings],
  ]},
];"""

content = content.replace(old_nav, new_nav)

# 3. Update the Sidebar rendering to look like the dark blue sidebar in the video
sidebar_old = """      <aside className={`fixed inset-y-0 left-0 z-40 w-64 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`} style={{ background: 'var(--surface-main)', borderRight: '1px solid var(--border-color)' }}>
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between p-4 lg:p-6" style={{ borderBottom: '1px solid var(--border-color)' }}>
            <Link to="/" className="flex items-center gap-2 font-bold text-lg" style={{ color: 'var(--route-optimized)' }}>
              <Navigation className="h-6 w-6" /> AccessRoute
            </Link>"""

sidebar_new = """      <aside className={`fixed inset-y-0 left-0 z-40 w-64 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`} style={{ background: '#0f172a', borderRight: '1px solid #1e293b' }}>
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between p-4 lg:p-6" style={{ borderBottom: '1px solid #1e293b' }}>
            <Link to="/" className="flex items-center gap-2 font-bold text-xl text-white">
              <Navigation className="h-6 w-6 text-blue-500" /> <span className="text-white">Navigate</span>
            </Link>"""

content = content.replace(sidebar_old, sidebar_new)

# 4. Make sidebar links look like the video (white text on dark blue)
navlink_old = """                  <Link
                    key={path}
                    to={path}
                    onClick={() => { if (window.innerWidth < 1024) setSidebarOpen(false); }}
                    className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
                    style={{
                      background: active ? 'var(--route-optimized-bg)' : 'transparent',
                      color: active ? 'var(--route-optimized)' : 'var(--text-dim)',
                    }}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                  </Link>"""

navlink_new = """                  <Link
                    key={path}
                    to={path}
                    onClick={() => { if (window.innerWidth < 1024) setSidebarOpen(false); }}
                    className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
                    style={{
                      background: active ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                      color: active ? '#60a5fa' : '#94a3b8',
                    }}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                  </Link>"""

content = content.replace(navlink_old, navlink_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Sidebar and Theme patched to match video structure.")
