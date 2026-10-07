import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_tab_block = """            {activeTab !== 'Itinerary' && (
              <div className="p-8 text-center text-gray-500">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-50 mb-4 text-gray-400">
                  <MapPinned size={32}/>
                </div>
                <h3 className="text-lg font-medium text-gray-700">Detailed {activeTab} view</h3>
                <p className="text-sm mt-1">This section is available in the full release.</p>
              </div>
            )}"""

new_tab_block = """            {activeTab === 'Hotels' && plan.hotels && (
              <div className="p-6">
                <h3 className="text-lg font-bold mb-4 text-gray-800">Accessible Hotels Nearby</h3>
                <div className="grid gap-4 md:grid-cols-2">
                  {plan.hotels.map((h, i) => (
                    <div key={i} className="border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition bg-white">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-bold text-gray-800">{h.name}</h4>
                        <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-xs font-bold shrink-0">{h.accessibility_score}/100</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-3">{h.source || "OpenStreetMap"}</p>
                      <div className="flex gap-2 text-[10px] uppercase font-bold text-gray-400">
                        {h.accessibility?.wheelchair === 'yes' && <span className="text-blue-500"><Building size={12} className="inline mr-1"/>Wheelchair Access</span>}
                        {h.accessibility?.tactile_paving === 'yes' && <span className="text-orange-500"><Eye size={12} className="inline mr-1"/>Tactile Paving</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'Restaurants' && plan.restaurants && (
              <div className="p-6">
                <h3 className="text-lg font-bold mb-4 text-gray-800">Accessible Dining</h3>
                <div className="grid gap-4 md:grid-cols-2">
                  {plan.restaurants.map((r, i) => (
                    <div key={i} className="border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition bg-white">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-bold text-gray-800">{r.name}</h4>
                        <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-xs font-bold shrink-0">{r.accessibility_score}/100</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-3">{r.source || "OpenStreetMap"}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'Attractions' && plan.attractions && (
              <div className="p-6">
                <h3 className="text-lg font-bold mb-4 text-gray-800">Accessible Attractions</h3>
                <div className="grid gap-4 md:grid-cols-2">
                  {plan.attractions.map((a, i) => (
                    <div key={i} className="border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition bg-white">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-bold text-gray-800">{a.name}</h4>
                        <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-xs font-bold shrink-0">{a.accessibility_score}/100</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-3">{a.source || "OpenStreetMap"}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'Route Map' && (
              <div className="p-8 text-center text-gray-500">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-50 mb-4 text-gray-400">
                  <MapPinned size={32}/>
                </div>
                <h3 className="text-lg font-medium text-gray-700">Detailed Route Map</h3>
                <p className="text-sm mt-1">Interactive map view is being generated.</p>
              </div>
            )}"""

content = content.replace(old_tab_block, new_tab_block)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Tabs rendered!")
