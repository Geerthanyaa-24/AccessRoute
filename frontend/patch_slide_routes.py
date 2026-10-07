import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace the entire <div className="mb-4"> ... Load Viva Demo Routes ... </div> block
old_block_regex = r"<div className=\"mb-4\">\s*<button\s*onClick=\{\(e\) => \{\s*e\.preventDefault\(\);\s*\/\/\s*Load perfect demo routes matching the report/diagram\s*const demoRoutes = \[.*?\];\s*setStart\('Egmore, Chennai'\);\s*setDestination\('Thousand Lights, Chennai'\);\s*setRoutes\(demoRoutes\);\s*setSelectedId\('demo-route-[a-c]'\);\s*setMapCenter\(\[13\.073, 80\.265\]\);\s*\}\}\s*className=\"w-full bg-purple-100 hover:bg-purple-200 text-purple-700 font-bold py-2 px-4 rounded-xl border border-purple-200 transition-colors flex items-center justify-center gap-2 text-sm\"\s*>\s*<Sparkles size=\{16\} \/> Load Viva Demo Routes \(From Report\)\s*<\/button>\s*<\/div>"

new_block = """            <div className="mb-4">
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  // Load exact demo routes matching the user's presentation slide
                  const demoRoutes = [
                    {
                      id: 'demo-most-accessible',
                      name: 'Most Accessible',
                      provider: 'AccessRoute Engine',
                      distance_m: 2300,
                      time_mins: 15,
                      accessibility_score: 91,
                      safety_score: 88,
                      pareto_status: 'Non-dominated (most accessible)',
                      limitations: ['Slope 3.80%', '1 Obstacle'],
                      coordinates: [
                        [13.078, 80.261], [13.076, 80.263], [13.073, 80.264], [13.070, 80.266], [13.068, 80.269]
                      ]
                    },
                    {
                      id: 'demo-balanced',
                      name: 'Balanced',
                      provider: 'AccessRoute Engine',
                      distance_m: 2100,
                      time_mins: 13,
                      accessibility_score: 89,
                      safety_score: 90,
                      pareto_status: 'Non-dominated (balanced)',
                      limitations: ['Slope 3.60%', '1 Obstacle'],
                      coordinates: [
                        [13.078, 80.261], [13.075, 80.262], [13.072, 80.266], [13.068, 80.269]
                      ]
                    },
                    {
                      id: 'demo-safest',
                      name: 'Safest',
                      provider: 'AccessRoute Engine',
                      distance_m: 2200,
                      time_mins: 14,
                      accessibility_score: 84,
                      safety_score: 92,
                      pareto_status: 'Non-dominated (safest)',
                      limitations: ['Slope 4.60%', '1 Obstacle'],
                      coordinates: [
                        [13.078, 80.261], [13.077, 80.264], [13.073, 80.265], [13.068, 80.269]
                      ]
                    },
                    {
                      id: 'demo-shortest',
                      name: 'Shortest',
                      provider: 'AccessRoute Engine',
                      distance_m: 1900,
                      time_mins: 11,
                      accessibility_score: 72,
                      safety_score: 68,
                      pareto_status: 'Dominated',
                      limitations: ['Slope 7.20%', '4 Obstacles'],
                      coordinates: [
                        [13.078, 80.261], [13.073, 80.264], [13.068, 80.269]
                      ]
                    }
                  ];
                  setStart('Egmore, Chennai');
                  setDestination('Thousand Lights, Chennai');
                  setRoutes(demoRoutes);
                  setSelectedId('demo-most-accessible');
                  setMapCenter([13.073, 80.265]);
                }}
                className="w-full bg-purple-100 hover:bg-purple-200 text-purple-700 font-bold py-2 px-4 rounded-xl border border-purple-200 transition-colors flex items-center justify-center gap-2 text-sm"
              >
                <Sparkles size={16} /> Load Viva Demo Routes (Exact Slide Values)
              </button>
            </div>"""

if re.search(old_block_regex, content, re.DOTALL):
    content = re.sub(old_block_regex, new_block, content, flags=re.DOTALL)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Demo routes updated successfully.")
else:
    print("Could not find the block to replace using regex. Let me insert it directly.")
    
    # Just replace the old manual string block just in case
    if "const demoRoutes = [" in content:
        # manual replace
        content_lines = content.split('\n')
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(content_lines):
            if '<div className="mb-4">' in line and 'button' in content_lines[i+1]:
                start_idx = i
            if 'Load Viva Demo Routes' in line and '</button>' in content_lines[i+1] and start_idx != -1:
                end_idx = i + 2
                break
        
        if start_idx != -1 and end_idx != -1:
            del content_lines[start_idx:end_idx+1]
            content_lines.insert(start_idx, new_block)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content_lines))
            print("Demo routes updated successfully via fallback method.")
