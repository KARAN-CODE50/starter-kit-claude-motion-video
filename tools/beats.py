#!/usr/bin/env python3
"""Measure a track's beat grid so every cut can land on a real beat.
  python3 tools/beats.py audio/music.mp3 [--bpm 120]   ->  audio/beats.json {bpm, offset, beats: [s, ...]}
Fits one straight grid (offset + k * 60/bpm) to the track's onsets: steadier to cut on than raw tracker output.
Pass --bpm when you know the tempo (a track generated from a plan keeps the BPM you asked for)."""
import json, os, sys
import numpy as np, librosa

src = sys.argv[1]
bpm_given = float(sys.argv[sys.argv.index('--bpm') + 1]) if '--bpm' in sys.argv else None
y, sr = librosa.load(src, sr=22050, mono=True)
tempo, frames = librosa.beat.beat_track(y=y, sr=sr, start_bpm=bpm_given or 120.0, tightness=400)
bt = librosa.frames_to_time(frames, sr=sr)
bpm = bpm_given or round(60 / float(np.median(np.diff(bt))))   # pass --bpm when you know it (a song made from a plan keeps its BPM)
per = 60 / bpm
# slide a fixed grid across the track and keep the offset where the grid hits the most energy (kicks, snares)
hop = 256
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
grid = np.arange(0, len(y) / sr - per, per)
def score(off): return env[np.clip(np.round((grid + off) * sr / hop).astype(int), 0, len(env) - 1)].sum()
offset = float(max(np.arange(0, per, 0.002), key=score))
beats = [round(offset + k * per, 4) for k in range(int((len(y) / sr - offset) / per) + 1)]
out = os.path.join(os.path.dirname(src) or '.', 'beats.json')
json.dump({'bpm': bpm, 'offset': round(offset, 4), 'beats': beats}, open(out, 'w'))
print(f'{out}: {bpm} BPM, first beat at {offset:.3f}s, {len(beats)} beats')
