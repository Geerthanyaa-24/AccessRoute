import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The string to search for
old_block = """      <section className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
        <MetricCard icon={<MapPin />} color="bg-blue-500" title="Analyzed Places" value={metrics?.data_summary?.records ?? '—'} change="Dataset records" />
        <MetricCard icon={<RouteIcon />} color="bg-emerald-500" title="Safe Nodes" value={metrics?.safe_nodes ?? '—'} change="Accessibility signals" />
        <MetricCard icon={<Star />} color="bg-purple-500" title="Avg. Accessibility" value={metrics?.average_accessibility_score ?? '—'} change="Out of 100" />
        <MetricCard icon={<Users />} color="bg-orange-500" title="Community Reports" value={metrics?.report_count ?? '—'} change="Submitted reports" />
      </section>

      {/* Route finder + map */}"""

new_block = """      <section className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
        <MetricCard icon={<MapPin />} color="bg-blue-500" title="Analyzed Places" value={metrics?.data_summary?.records ?? '—'} change="Dataset records" />
        <MetricCard icon={<RouteIcon />} color="bg-emerald-500" title="Safe Nodes" value={metrics?.safe_nodes ?? '—'} change="Accessibility signals" />
        <MetricCard icon={<Star />} color="bg-purple-500" title="Avg. Accessibility" value={metrics?.average_accessibility_score ?? '—'} change="Out of 100" />
        <MetricCard icon={<Users />} color="bg-orange-500" title="Community Reports" value={metrics?.report_count ?? '—'} change="Submitted reports" />
      </section>

      {/* System Validation Table (From Report) */}
      <Panel title="System Validation & Regression Tests" icon={<ShieldCheck size={17} />} className="border-emerald-500/30 bg-emerald-50/10">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left border-collapse rounded-lg overflow-hidden border border-gray-200">
            <thead className="bg-gray-100 text-gray-700 uppercase text-xs">
              <tr>
                <th className="px-6 py-3 border border-gray-200">Module</th>
                <th className="px-6 py-3 border border-gray-200 text-center">Test cases</th>
                <th className="px-6 py-3 border border-gray-200 text-center">Checks passed / executed</th>
              </tr>
            </thead>
            <tbody className="bg-white">
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Accessibility scoring</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-01 to UT-06 (6)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">13,851 / 13,851</td>
              </tr>
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Data confidence</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-07 to UT-11 (5)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">8 / 8</td>
              </tr>
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Route evaluation</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-12 to UT-18 (7)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">12,021 / 12,021</td>
              </tr>
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Obstacle module</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-19 to UT-22 (4)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">4 / 4</td>
              </tr>
              <tr className="bg-gray-50 font-bold text-gray-900">
                <td className="px-6 py-3 border border-gray-200 uppercase">Total</td>
                <td className="px-6 py-3 text-center border border-gray-200">22</td>
                <td className="px-6 py-3 text-center border border-gray-200 flex justify-center items-center gap-2"><CheckCircle2 size={16} className="text-emerald-500"/> 25,884 / 25,884</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="mt-2 text-right text-xs text-gray-500 italic">Reference: Table 7.1 Property and Regression Tests of the Reference Implementation</div>
      </Panel>

      {/* Route finder + map */}"""

# Note: The search block has to exactly match, whitespace might vary, so using regex is safer.
old_block_regex = r"<section className=\"grid gap-4 xl:grid-cols-4 md:grid-cols-2\">[\s\S]*?<\/section>\s*\{\/\* Route finder \+ map \*\/\}"
import re

if not re.search(old_block_regex, content):
    print("Could not find the block to replace!")
else:
    # Need to preserve the existing MetricCard block
    existing_metric_block = re.search(r"<section className=\"grid gap-4 xl:grid-cols-4 md:grid-cols-2\">[\s\S]*?<\/section>", content).group(0)
    
    new_content = existing_metric_block + """

      {/* System Validation Table (From Report) */}
      <Panel title="System Validation & Regression Tests" icon={<ShieldCheck size={17} />} className="border-emerald-500/30 bg-emerald-50/10">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left border-collapse rounded-lg overflow-hidden border border-gray-200">
            <thead className="bg-gray-100 text-gray-700 uppercase text-xs">
              <tr>
                <th className="px-6 py-3 border border-gray-200">Module</th>
                <th className="px-6 py-3 border border-gray-200 text-center">Test cases</th>
                <th className="px-6 py-3 border border-gray-200 text-center">Checks passed / executed</th>
              </tr>
            </thead>
            <tbody className="bg-white">
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Accessibility scoring</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-01 to UT-06 (6)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">13,851 / 13,851</td>
              </tr>
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Data confidence</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-07 to UT-11 (5)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">8 / 8</td>
              </tr>
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Route evaluation</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-12 to UT-18 (7)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">12,021 / 12,021</td>
              </tr>
              <tr className="hover:bg-gray-50 border border-gray-200">
                <td className="px-6 py-3 font-medium text-gray-900 border border-gray-200">Obstacle module</td>
                <td className="px-6 py-3 text-center border border-gray-200">UT-19 to UT-22 (4)</td>
                <td className="px-6 py-3 text-center font-mono border border-gray-200 text-emerald-600 font-bold">4 / 4</td>
              </tr>
              <tr className="bg-gray-50 font-bold text-gray-900">
                <td className="px-6 py-3 border border-gray-200 uppercase">Total</td>
                <td className="px-6 py-3 text-center border border-gray-200">22</td>
                <td className="px-6 py-3 text-center border border-gray-200 flex justify-center items-center gap-2"><CheckCircle2 size={16} className="text-emerald-500"/> 25,884 / 25,884</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="mt-2 text-right text-xs text-gray-500 italic">Reference: Table 7.1 Property and Regression Tests of the Reference Implementation</div>
      </Panel>

      {/* Route finder + map */}"""
    
    content = content.replace(existing_metric_block + "\n\n      {/* Route finder + map */}", new_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Validation table injected!")
