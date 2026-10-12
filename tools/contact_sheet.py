#!/usr/bin/env python3
"""Contact sheet of a finished film, 2 stills per second, labelled with film time.
python3 tools/contact_sheet.py out/21days_16x9.mp4 out/contact_sheet.png [cols] [still_width]"""
import subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 12
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 300
probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                   '-of', 'json', src], capture_output=True, text=True).stdout)['streams'][0]
W, H = probe['width'], probe['height']
th = round(H * tw / W) // 2 * 2
# frame at t = k/2 + 1/4 s (mid-interval, never a transition's first frame), picked by frame number at 60 fps
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', f"select='not(mod(n-15\\,30))',scale={tw}:{th}:flags=lanczos",
                      '-fps_mode', 'vfr', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
n = len(raw) // (tw * th * 3)
frames = np.frombuffer(raw[:n * tw * th * 3], np.uint8).reshape(n, th, tw, 3)
lab, pad = 20, 4
rows = (n + cols - 1) // cols
sheet = Image.new('RGB', (cols * (tw + pad) + pad, rows * (th + lab + pad) + pad), (60, 60, 56))
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 13)
except Exception:
    font = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for i in range(n):
    r, c = divmod(i, cols)
    x, y = pad + c * (tw + pad), pad + r * (th + lab + pad)
    sheet.paste(Image.fromarray(frames[i]), (x, y))
    t = 0.25 + i * 0.5
    d.text((x + 3, y + th + 3), f'{int(t // 60)}:{t % 60:05.2f}  beat {t / 0.5 + 1:.1f}', fill=(240, 238, 230), font=font)
sheet.save(out, optimize=True)
print('contact sheet', out, sheet.size, n, 'stills')
