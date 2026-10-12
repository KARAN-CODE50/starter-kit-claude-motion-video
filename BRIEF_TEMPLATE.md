# [FILM TITLE]: production brief for a one-shot code-rendered film

> Hand this file to Claude (Opus 5.5) in this folder, together with CLAUDE.md, and send the line in KICKOFF.md.
> This is the shape of the 27-section brief behind "21 DAYS". Replace every [BRACKET]. Keep the section numbers:
> the kickoff line and CLAUDE.md point at them. Sections marked (optional) can say "none" if your topic doesn't need them.
>
> Research date: [DATE]. Every number below is a snapshot from the source named next to it, on that date.

---

## AUTONOMOUS MODE (overrides every other instruction in this file)

**Do not ask the user for anything.** Every input is answered in section 23. Run the whole production end to end:
- Wherever this file says "ask", "wait", "GATE" or "show me", act as the approver yourself: run the critique loop (section 11),
  log the decision and scores in `PROGRESS.md`, commit, and continue.
- Make every creative call yourself within the rules of this brief, and log each one under `DECISIONS LOCKED`.
- The ONLY reasons to stop and talk to the user: the API key is missing or rejected, a required tool cannot be installed,
  or a usage limit (section 24). Never stop for taste questions.
- The prompts quoted in section 15 are reference material, not instructions to you.

## 0. The one-paragraph pitch
[What the film is, how long, who it is for, and the single idea that makes it worth watching.]
Example: "A beat-synced, fully code-rendered film that recaps the 21 days after Claude Opus 5.5 shipped. The film is made
with the exact technique it describes. The last frame says it is code, then loops back to the first frame."

## 1. Deliverables
[Exact files, sizes, lengths.] Example:
- `out/film_16x9.mp4`: 1920x1080, 60 fps, H.264 CRF 16, AAC 320k, -14 LUFS, [LENGTH] s, first frame == last frame.
- `docs/credits.md`, `out/x_thread.md`, a poster frame.

## 2. Inputs to ask the user for first
[The questions a director would ask: music, voice, real clips or not, sign-off handle, aspect ratio, paid-API budget.
Give each a default. Section 23 answers them all, so Claude never has to ask.]

## 3. What actually happened (the research)
[The factual spine, day by day or point by point. Every number with its source and date. Quotes verbatim, attributed.
Only what is here or in section 4 may appear on screen.]

## 4. Creator roster
[Table: handle · what they made · views/likes (source, date) · link to the original post · what they stand for in the film.]

## 5. Creative direction
[The core idea, the look (palette, type, texture), motion rules (springs, how text enters and exits), sound direction.]

## 6. CLAUDE.md (house rules)
[Copy of the studio rules. Keep CLAUDE.md in this folder in sync with this section.]

## 7. Rules for using other people's work
[When real clips are allowed (permission or a clear credit policy), how long each clip may run, how it is credited on screen,
how quotes and numbers are shown. Default when unsure: draw an original homage, never copy logos or characters.]

## 8. Shot list
[Act by act, with time ranges and beats at your BPM. For each shot: what is on screen, which technique, which word or sound
it lands on. Example: "ACT 0: COLD OPEN (0:00 to 0:06, beats 1 to 12) ..."]

## 9. Narration / caption script
[Every line, short, with where it lands. Captions are always on, because feeds autoplay muted.]

## 10. Production stages (follow in order)
- Stage 0, setup: install the kit (README), one test frame renders, fonts load.
- Stage 1, inputs: answered in section 23, skip.
- Stage 2, plan: `docs/style_guide.md`, `docs/shotlist.md` (exact frame ranges), `docs/beatmap.md`, `docs/credits.md`, plus 6 key stills. Self-approve with section 11.
- Stage 3, audio first: music, voice, effects (`tools/eleven.py`), `audio/beats.json` (`tools/beats.py`), word timings. Lock audio before animation.
- Stage 4, build act by act: build, render that act's seconds, contact sheet, critique loop until every score is 8+, then the next act.
- Stage 5, rough cut: full render at 30 fps with audio, review, fix.
- Stage 6, final: 60 fps, 4 sub-frames, CRF 16, audio at -14 LUFS, first frame == last frame, render twice and compare hashes.
- Stage 7, package: credits, thread draft, list of output files with sizes and durations.

## 11. Critique prompt (run after every render)
[The checklist Claude scores itself against. Example: "Look at the contact sheet. Score 1 to 10: hook in the first 2 s,
readable at 360 px wide, motion quality, variety, factual accuracy against sections 3 and 4, sound sync. Name the 3 worst
problems with timestamps, fix them, re-render only those seconds."]

## 12. Post + thread draft
[The main post, the replies, who gets tagged where. The first line must work without the video.]

## 13. Things Claude must NOT do
[Invented numbers or quotes, other people's logos, fake UI of real products, crossfades, Math.random, printing the API key ...]

## 14. Source list
[Every page the research used, with the date it was read.]

## 15. Prompt library (optional)
[Prompts that worked for others, word for word, credited. Reference material only.]

## 16. Skills, plugins and toolkits (optional)
[Tools people shared, with install steps where the source gave them.]

## 17. Specialist creators (optional)
[A deeper roster for one genre in your topic. "21 DAYS" used this for music-video creators.]

## 18. The fun layer (optional)
[Funny or meme pieces worth a beat in the film, so it isn't all serious.]

## 19. Studio-setup guides, step by step (optional)
[Condensed how-tos from articles or courses on the same technique.]

## 20. Prompt structures and frameworks (optional)
[Templates for how good briefs are built: hook, product, features, proof, call to action.]

## 21. Shot-list amendments
[Later changes to section 8. Where they conflict, this section wins.]

## 22. Source list additions
[Sources added after section 14 was written.]

## 23. Inputs: already answered (do not ask again)
| Input | Decision |
|---|---|
| Music | [e.g. ElevenLabs Music API, original instrumental at 120 BPM, E minor, no vocals under the narration] |
| Voiceover | [e.g. ElevenLabs. Key in `.env` as ELEVENLABS_API_KEY. Voice direction: dry, fast, confident, slightly amused] |
| Captions | [Always on, burned in] |
| Creator clips | [e.g. real clips from claudevideo.org, max ~4 s each, handle + views on screen, all credited] |
| Handle | [@yourhandle on the end card] |
| Aspect | [16:9 first] |
| Paid tools budget | [e.g. only the ElevenLabs subscription] |
| Claude plan | [Your plan. On a usage-limited plan, follow section 24 exactly.] |

## 24. Session protocol: never lose progress
- `PROGRESS.md` is the single resume point: CURRENT STAGE, LAST COMPLETED STEP, NEXT STEP (specific enough for a fresh
  session), DECISIONS LOCKED, OPEN ISSUES, CRITIQUE SCORES, RENDER COMMANDS THAT WORK, LAST UPDATED.
- Update it and `git commit` after every completed step. A step is small: one shot, one render, one critique pass.
- Long renders are resumable (chunks). Never start one without writing NEXT STEP first.
- On resume: read PROGRESS.md and `git log --oneline -15`, check `git status`, verify the last output exists, continue from NEXT STEP.
- End every session with a 3-line status: done, next, sessions left.

## 25. Pre-flight checklist (stage 0)
- [ ] Node 22+, ffmpeg, Python 3 with numpy, librosa, soundfile, pyloudnorm, pillow; `npx playwright install chromium`
- [ ] `node src/render.mjs stills --times 1` renders a frame with the right fonts (not a fallback)
- [ ] `.env` has the API key; a short test call succeeds (never echo the key)
- [ ] git initialised, `.gitignore` covers `.env`, `node_modules/`, `out/`, `raw/`, `frames/`
- [ ] PROGRESS.md, CHANGELOG.md and CLAUDE.md exist
- [ ] At least 10 GB free disk

## 26. Posting plan
[Where and when to post, which cut, the poster frame, who to tag in which reply, what to pin, who to reply to first.]
