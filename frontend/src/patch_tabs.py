import re

with open("App.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# The current itinerary block ends around here:
#                   </div>
#                 </div>
#               )}
#
#               {/* AI Assistant Banner */}
#               <div className="bg-gradient-to-r from-purple-50 to-blue-50 border-t border-purple-100 p-6 md:p-8 flex flex-col md:flex-row gap-6 items-center">

# I'll find where {activeTab === 'Itinerary' && (...)} ends and inject the other tabs.

tabs_code = """
            {activeTab === 'Hotels' && (
              <div className="p-6 md:p-8 space-y-4">
                <h3 className="font-bold text-lg mb-4 text-gray-800">Accessible Hotels</h3>
                {plan.hotels?.length > 0 ? plan.hotels.map(h => (
                  <div key={h.id} className="p-5 border border-gray-100 shadow-sm rounded-xl flex flex-col md:flex-row gap-4 bg-white">
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-800 text-lg flex items-center gap-2">{h.name} <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded font-bold">{h.rating} ★</span></h4>
                      <p className="text-sm text-gray-500 mt-1">{h.price} • {h.source}</p>
                      
                      <div className="mt-4 grid grid-cols-2 gap-2">
                        {h.accessibility?.map((a, i) => (
                          <div key={i} className="flex items-center gap-2 text-sm">
                            {a.status === 'Available' ? <CheckCircle size={14} className="text-emerald-500" /> : a.status === 'No' ? <XCircle size={14} className="text-red-500" /> : <AlertCircle size={14} className="text-amber-500" />}
                            <span className={a.status === 'No' ? 'text-gray-400 line-through' : 'text-gray-700'}>{a.label}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-col items-end justify-between border-l pl-4 border-gray-50">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{h.accessibility_score}</div>
                        <div className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">Access Score</div>
                      </div>
                      <button className="mt-4 text-sm font-bold text-blue-600 hover:text-blue-700 bg-blue-50 px-4 py-2 rounded-lg">View Details</button>
                    </div>
                  </div>
                )) : <div className="p-8 text-center text-gray-500">No hotels found for this location.</div>}
              </div>
            )}
            
            {activeTab === 'Restaurants' && (
              <div className="p-6 md:p-8 space-y-4">
                <h3 className="font-bold text-lg mb-4 text-gray-800">Accessible Dining</h3>
                {plan.restaurants?.length > 0 ? plan.restaurants.map(r => (
                  <div key={r.id} className="p-5 border border-gray-100 shadow-sm rounded-xl flex flex-col md:flex-row gap-4 bg-white">
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-800 text-lg flex items-center gap-2">{r.name}</h4>
                      <div className="mt-4 grid grid-cols-2 gap-2">
                        {r.accessibility?.map((a, i) => (
                          <div key={i} className="flex items-center gap-2 text-sm">
                            {a.status === 'Available' ? <CheckCircle size={14} className="text-emerald-500" /> : a.status === 'No' ? <XCircle size={14} className="text-red-500" /> : <AlertCircle size={14} className="text-amber-500" />}
                            <span className={a.status === 'No' ? 'text-gray-400 line-through' : 'text-gray-700'}>{a.label}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-col items-end justify-between border-l pl-4 border-gray-50">
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-600">{r.accessibility_score}</div>
                        <div className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">Score</div>
                      </div>
                    </div>
                  </div>
                )) : <div className="p-8 text-center text-gray-500">No dining options found for this location.</div>}
              </div>
            )}

            {activeTab === 'Attractions' && (
              <div className="p-6 md:p-8 space-y-4">
                <h3 className="font-bold text-lg mb-4 text-gray-800">Accessible Attractions</h3>
                {plan.attractions?.length > 0 ? plan.attractions.map(a => (
                  <div key={a.id} className="p-5 border border-gray-100 shadow-sm rounded-xl flex flex-col md:flex-row gap-4 bg-white">
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-800 text-lg flex items-center gap-2">{a.name}</h4>
                      <div className="mt-4 grid grid-cols-2 gap-2">
                        {a.accessibility?.map((ac, i) => (
                          <div key={i} className="flex items-center gap-2 text-sm">
                            {ac.status === 'Available' ? <CheckCircle size={14} className="text-emerald-500" /> : ac.status === 'No' ? <XCircle size={14} className="text-red-500" /> : <AlertCircle size={14} className="text-amber-500" />}
                            <span className={ac.status === 'No' ? 'text-gray-400 line-through' : 'text-gray-700'}>{ac.label}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-col items-end justify-between border-l pl-4 border-gray-50">
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-600">{a.accessibility_score}</div>
                        <div className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">Score</div>
                      </div>
                    </div>
                  </div>
                )) : <div className="p-8 text-center text-gray-500">No attractions found for this location.</div>}
              </div>
            )}
"""

# I need to insert this right after the Itinerary block.
itinerary_end_pattern = r"(}\s*)\n\s*{/\* AI Assistant Banner \*/}"
code = re.sub(itinerary_end_pattern, r"\1" + "\n" + tabs_code + "\n              {/* AI Assistant Banner */}", code)

with open("App.jsx", "w", encoding="utf-8") as f:
    f.write(code)
print("Tabs code inserted.")
