import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Inject the Demo button in the Find Accessible Route panel
old_form = """            <form onSubmit={findRoute} className="space-y-4">
              <Field label="From">"""

new_form = """            <div className="mb-4">
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  // Load perfect demo routes matching the report/diagram
                  const demoRoutes = [
                    {
                      id: 'demo-route-c',
                      name: 'Most Accessible Route',
                      provider: 'AccessRoute Engine',
                      distance_m: 2400,
                      time_mins: 14,
                      accessibility_score: 94,
                      safety_score: 96,
                      pareto_status: 'Non-dominated (most accessible)',
                      limitations: [],
                      coordinates: [
                        [13.078, 80.261], [13.075, 80.263], [13.072, 80.265], [13.068, 80.269]
                      ]
                    },
                    {
                      id: 'demo-route-a',
                      name: 'Shortest Route',
                      provider: 'AccessRoute Engine',
                      distance_m: 1900,
                      time_mins: 11,
                      accessibility_score: 82,
                      safety_score: 80,
                      pareto_status: 'Non-dominated (shortest)',
                      limitations: [],
                      coordinates: [
                        [13.078, 80.261], [13.075, 80.265], [13.070, 80.267], [13.068, 80.269]
                      ]
                    },
                    {
                      id: 'demo-route-b',
                      name: 'Alternative Route',
                      provider: 'AccessRoute Engine',
                      distance_m: 2100,
                      time_mins: 12,
                      accessibility_score: 45,
                      safety_score: 50,
                      pareto_status: 'Dominated (Blocked Ramp)',
                      limitations: ['Blocked Ramp Detected'],
                      coordinates: [
                        [13.078, 80.261], [13.076, 80.261], [13.072, 80.268], [13.068, 80.269]
                      ]
                    }
                  ];
                  setStart('Egmore, Chennai');
                  setDestination('Thousand Lights, Chennai');
                  setRoutes(demoRoutes);
                  setSelectedId('demo-route-c');
                  setMapCenter([13.073, 80.265]);
                }}
                className="w-full bg-purple-100 hover:bg-purple-200 text-purple-700 font-bold py-2 px-4 rounded-xl border border-purple-200 transition-colors flex items-center justify-center gap-2 text-sm"
              >
                <Sparkles size={16} /> Load Viva Demo Routes (From Report)
              </button>
            </div>
            <form onSubmit={findRoute} className="space-y-4">
              <Field label="From">"""

if "Load Viva Demo Routes" not in content:
    content = content.replace(old_form, new_form)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Demo routes button injected!")
else:
    print("Already injected.")
