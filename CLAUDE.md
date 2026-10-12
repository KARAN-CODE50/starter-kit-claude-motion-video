# Studio rules (Claude reads this on every step)

## Render contract
- The film is a pure function of time: `drawFrame(ctx, t)` in `src/index.html` paints frame t. Nothing else drives the picture.
- No CSS transitions, no setTimeout/setInterval, no requestAnimationFrame while rendering, no state carried between frames.
- Randomness only from a seeded function of an index, never Math.random.
- Springs are closed-form step responses (see `spring()` in the demo). A value with many targets = one spring per change, summed.
- Render with `src/render.mjs`: headless Chromium at 60 fps, 4 sub-frames blended per frame for motion blur, piped to ffmpeg. H.264 yuv420p CRF 16.
- Fonts load from `assets/fonts` and `await document.fonts.ready` before any capture.
- Real clips are frame sequences cut by `tools/clips.py`; the page draws the frame that matches t, so clips are a function of time too.

## Look
- Palette: off-black #141413, cream #F0EEE6, ONE accent #D97757. [Change these to your brand.]
- One display face, one mono face.
- Banned: centred title on a gradient, fade-ins, crossfades, blur-ins, corner labels, frame borders, glows on UI, generic particles, 3D flips, dead holds over 1.5 s.
- Something new every 2 beats. Every act uses a different technique.
- Every number shown must come from BRIEF.md (with its source and date). Never invent a stat, quote, handle or date.

## Sound
- Audio first: music, voice and effects are locked before animation (BRIEF.md, production stage 3).
- Beat grid in `audio/beats.json` (`tools/beats.py`). Cuts, stamps and type-ons land on measured beats.
- On-screen words appear when they are spoken (word timings from `tools/eleven.py voice`).
- Music ducks under the voice. Final mix at -14 LUFS, true peak under -1 dBTP.

## Loop before you show me anything
1. Render one frame per beat for the section you changed as a contact sheet (`node src/render.mjs sheet --from A --to B`). LOOK at it.
2. Score 1 to 10: hook in the first 2 s, readable at phone size (360 px wide), motion quality, variety, factual accuracy vs BRIEF.md, sound sync.
3. Fix the 3 worst problems, re-render only those seconds.
4. Repeat until every score is 8+. Only then do a full render.

## Other people's work
- Use a creator's clip only when BRIEF.md says you may. Credit the handle on screen and in `docs/credits.md` with the link to the original post.
- Quotes verbatim and attributed. No logos or characters that aren't yours to use.

## Session continuity
- After every completed step: update PROGRESS.md (CURRENT STAGE, LAST COMPLETED STEP, NEXT STEP, DECISIONS LOCKED, OPEN ISSUES) and git commit.
- On every resume: read PROGRESS.md and `git log --oneline -15` first, then continue from NEXT STEP. Never redo finished steps.
- The ElevenLabs key lives only in `.env`. Never print it, never write it anywhere else, never commit it.
