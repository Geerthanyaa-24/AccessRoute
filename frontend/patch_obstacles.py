import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure we set the exact obstacle counts for the UI to map to `selected.obstacles`
old_demo_block = r"const demoRoutes = \[.*?\];\s*setStart\('Egmore, Chennai'\);"

new_demo_block = """const demoRoutes = [
                    {
                      id: 'demo-most-accessible',
                      name: 'Most Accessible',
                      provider: 'AccessRoute Engine',
                      distance_m: 2300,
                      time_mins: 15,
                      accessibility_score: 91,
                      safety_score: 88,
                      obstacles: 1,
                      pareto_status: 'Non-dominated (most accessible)',
                      limitations: ['Slope 3.80%'],
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
                      obstacles: 1,
                      pareto_status: 'Non-dominated (balanced)',
                      limitations: ['Slope 3.60%'],
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
                      obstacles: 1,
                      pareto_status: 'Non-dominated (safest)',
                      limitations: ['Slope 4.60%'],
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
                      obstacles: 4,
                      pareto_status: 'Dominated (Shortest)',
                      limitations: ['Slope 7.20%'],
                      coordinates: [
                        [13.078, 80.261], [13.073, 80.264], [13.068, 80.269]
                      ]
                    }
                  ];
                  setStart('Egmore, Chennai');"""

if re.search(old_demo_block, content, re.DOTALL):
    content = re.sub(old_demo_block, new_demo_block, content, flags=re.DOTALL)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Exact slide variables mapped!")
