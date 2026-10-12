#!/usr/bin/env python3
"""ElevenLabs audio for a code film: music, voice lines with word timestamps, sound effects.
The key is read from .env (ELEVENLABS_API_KEY=...) and never printed. Every output is cached: if the file
exists it is not generated again, because generations cost credits.

  python3 tools/eleven.py music audio/music_plan.json audio/music.mp3
  python3 tools/eleven.py voice audio/lines.json audio/vo --voice <voice_id> [--model eleven_v3]
  python3 tools/eleven.py sfx   audio/sfx.json   audio/sfx

music  -> one track from a composition plan (sections with durations and styles; see audio/music_plan.example.json)
voice  -> one mp3 per line + <id>.json with word timings [[word, start_s, end_s], ...] to place on-screen words
sfx    -> one mp3 per effect (text prompt + duration)
"""
import base64, json, os, sys, urllib.request, urllib.error

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
API = 'https://api.elevenlabs.io/v1'


def key():
    env = os.path.join(ROOT, '.env')
    if not os.path.exists(env): sys.exit('No .env file. Copy .env.example to .env and add ELEVENLABS_API_KEY.')
    k = next((l.split('=', 1)[1].strip() for l in open(env) if l.startswith('ELEVENLABS_API_KEY=')), '')
    if not k: sys.exit('ELEVENLABS_API_KEY is empty in .env')
    return k


def post(path, body, as_json=False, timeout=600):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method='POST',
                                 headers={'xi-api-key': key(), 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f'ElevenLabs HTTP {e.code}: {e.read()[:300].decode(errors="replace")}')
    return json.loads(data) if as_json else data


def music(plan_file, out):
    if os.path.exists(out): return print('cached', out)
    plan = json.load(open(plan_file))
    body = {'composition_plan': plan, 'model_id': plan.pop('model_id', 'music_v2_5')}
    open(out, 'wb').write(post('/music?output_format=mp3_48000_192', body))
    print('music', out, f"{sum(c['duration_ms'] for c in plan['chunks']) / 1000:.1f}s")


def words_from_alignment(al):
    """character timings -> [[word, start, end], ...]"""
    words, cur, t0, t1 = [], '', None, None
    for ch, s, e in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if ch.isspace():
            if cur: words.append([cur, round(t0, 3), round(t1, 3)])
            cur, t0 = '', None
            continue
        if t0 is None: t0 = s
        cur += ch; t1 = e
    if cur: words.append([cur, round(t0, 3), round(t1, 3)])
    return words


def voice(lines_file, out_dir, voice_id, model='eleven_v3'):
    os.makedirs(out_dir, exist_ok=True)
    for line in json.load(open(lines_file)):          # [{"id": "l1", "text": "Twenty-one days."}, ...]
        mp3 = os.path.join(out_dir, line['id'] + '.mp3')
        if os.path.exists(mp3): print('cached', mp3); continue
        body = {'text': line['text'], 'model_id': model,
                'voice_settings': {'stability': 0.5, 'similarity_boost': 0.8, 'style': 0.25, 'use_speaker_boost': True}}
        d = post(f'/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_192', body, as_json=True)
        open(mp3, 'wb').write(base64.b64decode(d['audio_base64']))
        json.dump({'text': line['text'], 'words': words_from_alignment(d['alignment'])}, open(mp3[:-4] + '.json', 'w'))
        print('voice', mp3)


def sfx(sfx_file, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for s in json.load(open(sfx_file)):                # [{"id": "whoosh", "text": "fast airy whoosh", "seconds": 0.7}, ...]
        mp3 = os.path.join(out_dir, s['id'] + '.mp3')
        if os.path.exists(mp3): print('cached', mp3); continue
        open(mp3, 'wb').write(post('/sound-generation?output_format=mp3_44100_192',
                                   {'text': s['text'], 'duration_seconds': s['seconds'], 'prompt_influence': 0.6}))
        print('sfx', mp3)


if __name__ == '__main__':
    a = sys.argv[1:]
    opt = lambda name, default=None: a[a.index(name) + 1] if name in a else default
    if len(a) < 3: sys.exit(__doc__)
    if a[0] == 'music': music(a[1], a[2])
    elif a[0] == 'voice':
        if not opt('--voice'): sys.exit('pass --voice <voice_id> (pick one in the ElevenLabs voice library)')
        voice(a[1], a[2], opt('--voice'), opt('--model', 'eleven_v3'))
    elif a[0] == 'sfx': sfx(a[1], a[2])
    else: sys.exit(__doc__)
