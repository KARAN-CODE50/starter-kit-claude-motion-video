#!/usr/bin/env python3
"""Work with real clips (only ones you are allowed to use, always credited).
  python3 tools/clips.py get   <video_url> <name>          -> raw/<name>.mp4   (a direct link to the video file)
  python3 tools/clips.py look  <name> [every_s]            -> out/clips/<name>.png  (contact sheet: pick the best seconds)
  python3 tools/clips.py cut   <name> <start_s> <dur_s>    -> frames/<name>/0000.jpg ... + meta.json
The page draws frame k of a cut as source time start_s + k / 60. Load them with an Image or createImageBitmap
and draw the one that matches t, so the clip stays a pure function of time like everything else."""
import json, os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
cmd, a = sys.argv[1], sys.argv[2:]

if cmd == 'get':
    url, name = a
    os.makedirs(os.path.join(ROOT, 'raw'), exist_ok=True)
    out = os.path.join(ROOT, 'raw', name + '.mp4')
    if not os.path.exists(out): subprocess.run(['curl', '-sSfL', url, '-o', out], check=True)
    print(out)
elif cmd == 'look':
    name, every = a[0], float(a[1]) if len(a) > 1 else 0.5
    src = os.path.join(ROOT, 'raw', name + '.mp4')
    os.makedirs(os.path.join(ROOT, 'out/clips'), exist_ok=True)
    out = os.path.join(ROOT, 'out/clips', name + '.png')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
    n = int(dur / every) + 1; cols = 8; rows = (n + cols - 1) // cols
    vf = f"fps=1/{every},scale=320:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontcolor=white:box=1:boxcolor=black@0.6:fontsize=16,tile={cols}x{rows}"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-nostdin', '-i', src, '-vf', vf, '-frames:v', '1', out], check=True)
    print(out, f'({n} stills, one every {every}s)')
elif cmd == 'cut':
    name, lo, dur = a[0], float(a[1]), float(a[2])
    d = os.path.join(ROOT, 'frames', name); os.makedirs(d, exist_ok=True)
    vf = 'fps=60,scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-nostdin', '-ss', f'{lo:.3f}', '-t', f'{dur:.3f}', '-i', os.path.join(ROOT, 'raw', name + '.mp4'),
                    '-vf', vf, '-q:v', '3', '-start_number', '0', os.path.join(d, '%04d.jpg')], check=True)
    n = len([f for f in os.listdir(d) if f.endswith('.jpg')])
    json.dump({'src_lo': lo, 'fps': 60, 'n': n, 'w': 1920, 'h': 1080}, open(os.path.join(d, 'meta.json'), 'w'))
    print(d, n, 'frames')
else:
    sys.exit(__doc__)
