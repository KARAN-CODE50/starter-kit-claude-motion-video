#!/usr/bin/env python3
"""Checks a finished film against the delivery spec: python3 tools/check.py out/film.mp4 [...]
- stream spec (size, fps, codec, pix_fmt, audio), duration
- loudness (EBU R128 integrated, true peak)
- loop: first decoded frame vs last decoded frame (mean abs diff, % of pixels off by > 8/255)"""
import json, re, subprocess, sys
import numpy as np

def probe(f):
    p = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,bit_rate,sample_rate,channels'
                        ':format=duration,bit_rate', '-of', 'json', f], capture_output=True, text=True)
    return json.loads(p.stdout)

def frame(f, last=False):
    """first decoded frame, or the tail of the file (the caller keeps its final frame)"""
    pre = ['-sseof', '-0.2'] if last else []
    post = [] if last else ['-frames:v', '1']
    return subprocess.run(['ffmpeg', '-v', 'error', *pre, '-i', f, *post, '-map', '0:v', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                          capture_output=True).stdout

def main():
    for f in sys.argv[1:]:
        d = probe(f)
        v = next(s for s in d['streams'] if s['codec_type'] == 'video')
        a = next((s for s in d['streams'] if s['codec_type'] == 'audio'), None)
        W, H = v['width'], v['height']
        print(f'== {f}')
        print(f"video {v['codec_name']} {W}x{H} {v['r_frame_rate']} {v['pix_fmt']}  duration {float(d['format']['duration']):.3f} s  total {int(d['format']['bit_rate']) / 1e6:.1f} Mb/s")
        if a:
            print(f"audio {a['codec_name']} {a['sample_rate']} Hz {a['channels']} ch {int(a.get('bit_rate', 0)) // 1000} kb/s")
        if a:   # streaming target: about -14 LUFS integrated, true peak under -1 dBTP
            p = subprocess.run(['ffmpeg', '-nostats', '-i', f, '-map', '0:a', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
            tail = p.stderr[p.stderr.rfind('Summary:'):]
            I = re.search(r'I:\s+(-?[\d.]+) LUFS', tail); TP = re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail)
            print(f"loudness {I.group(1) if I else '?'} LUFS integrated, true peak {TP.group(1) if TP else '?'} dBTP")
        else:
            print('no audio track')
        n = W * H * 3
        first = np.frombuffer(frame(f)[:n], np.uint8).astype(np.int16)
        tail_raw = frame(f, last=True)
        last = np.frombuffer(tail_raw[-n:], np.uint8).astype(np.int16)
        diff = np.abs(first - last)
        print(f'loop: first vs last frame mean abs diff {diff.mean():.3f}/255, {100 * (diff.reshape(-1, 3).max(1) > 8).mean():.3f}% pixels off by > 8')

if __name__ == '__main__':
    main()
