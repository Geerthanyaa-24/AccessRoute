import re

filepath = 'frontend/src/App.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the {center && (...)} condition to include a fallback for !center
old_center_block = """      {center && (
        <section className="grid gap-6 xl:grid-cols-2">"""

new_center_block = """      {!center && (
        <div className="flex flex-col items-center justify-center p-12 mt-6 rounded-2xl border border-dashed border-gray-300 bg-gray-50/50">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-6 text-blue-500">
            <MapPin size={40} />
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Where are you looking?</h2>
          <p className="text-gray-500 max-w-md text-center">Search for a location above or click "My Location" to instantly discover accessible hospitals, restaurants, and facilities nearby.</p>
        </div>
      )}

      {center && (
        <section className="grid gap-6 xl:grid-cols-2">"""

if "{!center && (" not in content:
    content = content.replace(old_center_block, new_center_block)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Empty state added.")
else:
    print("Already added.")
