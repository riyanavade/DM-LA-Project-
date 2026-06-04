import ast
import os
import requests

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()
start = text.index('PLAYER_PHOTOS = {')
end = text.index('}\n\nDEFAULT_PLAYER_IMG', start) + 1
src = text[start:end]
player_photos = ast.literal_eval(src[src.index('{'):])
image_folder = os.path.join(os.getcwd(), 'images')
os.makedirs(image_folder, exist_ok=True)
for name, url in player_photos.items():
    safe_name = ''.join(ch for ch in name.lower() if ch.isalnum() or ch in (' ', '_', '-')).replace(' ', '_')
    ext = os.path.splitext(url)[1].split('?')[0]
    if ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
        ext = '.jpg'
    local_path = os.path.join(image_folder, f"{safe_name}{ext}")
    if os.path.exists(local_path):
        print('skip', name, local_path)
        continue
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            with open(local_path, 'wb') as out:
                out.write(r.content)
            print('saved', name, local_path)
        else:
            print('failed', name, r.status_code, r.headers.get('Content-Type'))
    except Exception as e:
        print('error', name, e)
