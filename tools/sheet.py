#!/usr/bin/env python3
"""Contact sheet: python3 tools/sheet.py list.json out.png [cols]. list.json = [[png, label], ...]"""
import json, sys
from PIL import Image, ImageDraw, ImageFont
items = json.load(open(sys.argv[1])); out = sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
ims = [Image.open(f).convert('RGB') for f, _ in items]
w, h = ims[0].size
tw = min(w, 480 if w >= h else 240); th = int(h * tw / w)
lab = 22
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (tw + 6) + 6, rows * (th + lab + 6) + 6), (60, 60, 56))
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15)
except Exception:
    font = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for i, (im, (_, label)) in enumerate(zip(ims, items)):
    r, c = divmod(i, cols)
    x, y = 6 + c * (tw + 6), 6 + r * (th + lab + 6)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
    d.text((x + 4, y + th + 3), label, fill=(240, 238, 230), font=font)
sheet.save(out)
print('sheet', out, sheet.size)
