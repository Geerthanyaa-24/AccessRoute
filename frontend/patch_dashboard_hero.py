import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

dashboard_old = """  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-main)' }}>Dashboard</h1>
      </div>"""

dashboard_new = """  return (
    <div className="space-y-6">
      {/* Video-style Header */}
      <div className="flex flex-col gap-2 pb-4" style={{ borderBottom: '1px solid var(--border-color)' }}>
        <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-dim)' }}>
          Home &gt; Places Details &gt; Nearby Accessible Places
        </div>
        <h1 className="text-4xl font-bold" style={{ color: 'var(--text-main)' }}>Navigate Without Barriers</h1>
        <p className="text-lg" style={{ color: 'var(--text-dim)' }}>Find safer, smoother and more accessible routes</p>
      </div>
      
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold" style={{ color: 'var(--text-main)' }}>System Overview</h2>
      </div>"""

if dashboard_old in content:
    content = content.replace(dashboard_old, dashboard_new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Dashboard hero patched.")
else:
    print("Could not find dashboard old code.")
