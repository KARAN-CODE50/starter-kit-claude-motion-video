# Claude Motion Video Starter Kit

Create motion graphics with HTML Canvas, then render them into an MP4 with Playwright and FFmpeg. Each frame is a function of time, so you can reproduce a shot, inspect individual frames, and render sections independently.

The included six-second demo uses a 1920 × 1080 canvas, beat-driven typography, a tile animation, and a seamless loop. It needs no API key and contains no audio. Draft renders default to 960 × 540 at 30 fps; final renders default to 1920 × 1080 at 60 fps with four blended subframes for motion blur.

## Requirements and setup

Use Node.js 20 or later, Python 3.10 or later, and FFmpeg/FFprobe on your PATH. Commands below run from the repository root. On macOS, install system tools with `brew install node python ffmpeg`; on other systems, use your package manager.

```bash
npm ci --ignore-scripts
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npx playwright install chromium
npm run check
npm test
npm run demo
npm run sheet
```

On Linux, use `npx playwright install --with-deps chromium` if browser system dependencies are missing. On Windows, activate the virtual environment with `.venv\Scripts\Activate.ps1`; the renderer invokes `python3`, so that command must be available.

The demo is saved to `out/demo.mp4` and the contact sheet to `out/sheet.png`. Generated media is excluded from Git.

## Contents

| Path | Purpose |
| --- | --- |
| `src/index.html` | Demo animation, deterministic helpers and frame capture API |
| `src/render.mjs` | Still images, contact sheets, draft and final MP4 rendering |
| `RESEARCH_PROMPT.md` | Research instructions for developing a sourced brief |
| `BRIEF_TEMPLATE.md` | 27-section production brief template |
| `CLAUDE.md` | Studio rules for animation, audio, review and continuity |
| `KICKOFF.md` | Prompt to begin production with Claude |
| `tools/eleven.py` | Optional ElevenLabs music, speech, word timings and effects |
| `tools/beats.py` | Estimate an audio track's beat grid |
| `tools/clips.py` | Download, inspect and extract authorized video clips |
| `tools/sheet.py`, `tools/contact_sheet.py` | Visual contact sheets |
| `tools/check.py` | Video metadata, loudness and first/last-frame comparison |
| `tools/repo_check.py` | Source syntax, JSON and common credential checks |
| `tests/` | Browser checks for font loading, deterministic frames and the loop |
| `audio/*.example.json` | Example inputs for optional audio generation |
| `docs/credits_template.md` | Attribution template for third-party footage |

## Make your own film

1. Use `RESEARCH_PROMPT.md` and `BRIEF_TEMPLATE.md` to prepare a sourced `BRIEF.md`.
2. Read and adapt the studio rules in `CLAUDE.md`, then use `KICKOFF.md` to start working with Claude.
3. Set your canvas dimensions and duration in `src/index.html`. Implement the visuals in `drawFrame(ctx, t)` and keep frames independent of playback order.
4. For sound, generate or supply audio, measure beats, and synchronize shots and on-screen text. Pass a finished audio mix to the renderer; it does not mix or master audio for you.
5. Inspect stills and contact sheets, revise individual sections, then render and check the completed MP4.

Templates contain examples and model references; adapt them to your available tools. Running this kit does not require a particular Claude model.

```bash
node src/render.mjs stills --times 1,2.5
node src/render.mjs sheet --from 0 --to 6 --step 0.5
node src/render.mjs video --out out/draft.mp4 --audio audio/mix.wav
node src/render.mjs final --out out/film.mp4 --audio audio/mix.wav
python3 tools/check.py out/film.mp4
ffmpeg -v error -xerror -i out/film.mp4 -f null -
```

Final rendering retains completed segments in `out/chunks/` so interrupted jobs can resume. After changing visuals, duration, FPS, scale or subframe settings, pass `--force` or remove the affected chunks before rerendering. Use different output names for different render configurations. `tools/check.py` reports measurements; it does not enforce delivery thresholds.

## Optional ElevenLabs audio

Copy `.env.example` to `.env` and set `ELEVENLABS_API_KEY` locally. `.env.example` contains no credential. Audio generation uses your account and may consume paid credits. The helpers cache existing output files; remove only the files you intend to regenerate.

```bash
cp .env.example .env
# Edit .env locally; never paste credentials into source files.
python3 tools/eleven.py music audio/music_plan.example.json audio/music.mp3
python3 tools/eleven.py voice audio/lines.example.json audio/vo --voice YOUR_VOICE_ID
python3 tools/eleven.py sfx audio/sfx.example.json audio/sfx
python3 tools/beats.py audio/music.mp3 --bpm 120
```

## Checks and security

```bash
npm run check                 # JavaScript/Python syntax, JSON, common credential patterns
npm test                      # Browser rendering regression checks
npm audit --audit-level=high  # Known npm dependency vulnerabilities
npm run demo                  # Complete render smoke test
python3 tools/check.py out/demo.mp4
ffmpeg -v error -xerror -i out/demo.mp4 -f null -
```

GitHub Actions runs these checks on pushes and pull requests without API credentials. Review the Actions results after pushing; a local pass does not establish a hosted CI pass. The credential scanner is best effort and cannot detect every secret. Review staged files before committing. See [SECURITY.md](SECURITY.md) for local credential handling and reporting.

The renderer serves assets on localhost only. Use trusted film code and inputs. Its server is for rendering, not production hosting.

## Fonts and third-party material

Inter Tight Black is bundled under the SIL Open Font License; its license is in `assets/fonts/OFL-InterTight.txt`. Monospace text uses the system font, so its appearance may vary by operating system.

Use third-party clips only with appropriate rights and attribution. Keep the original source links and creator credits in `docs/credits.md` using the provided template. No project-wide software license has been added; the bundled font's license applies to that font separately.
