import re

filepath = 'backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "    except Exception as exc:"
end_str = "        ) from exc"

start_idx = content.find(start_str, content.find("def compare_routes("))
end_idx = content.find(end_str, start_idx) + len(end_str)

good_code = """    except Exception as exc:
        print(f'Exception: {exc}')
        import urllib.error
        error_msg = f"Live pedestrian routing is unavailable ({type(exc).__name__}). Check the place names and backend internet access."
        if isinstance(exc, urllib.error.HTTPError) and exc.code == 400:
            error_msg = "Live pedestrian routing failed: The distance between these locations is too large for walking."
        raise HTTPException(status_code=502, detail=error_msg) from exc"""

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + good_code + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Backend syntax fixed.")
else:
    print("Could not find the block to replace.")
