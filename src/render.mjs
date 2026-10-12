// render.mjs: film the page in src/index.html with headless Chromium, frame by frame, and encode with ffmpeg.
//
//   node src/render.mjs stills --times 1,2.5 [--scale 0.5]                 -> out/stills/t001.00.png ...
//   node src/render.mjs sheet  [--from 0 --to 6 --step 0.5] [--cols 6]     -> out/sheet.png (one still per beat: LOOK at it)
//   node src/render.mjs video  [--fps 30 --scale 0.5] [--audio audio/mix.wav] --out out/draft.mp4   (fast draft)
//   node src/render.mjs final  [--chunk 10] [--audio audio/mix.wav] --out out/film.mp4   (60 fps, 4 sub-frames, CRF 16)
//
// Final renders go in resumable chunks: if a render is cut off, run the same command again and it skips finished chunks.
// Delete one chunk in out/chunks/ to re-render just those seconds.
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, execFileSync } from 'node:child_process';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const mode = process.argv[2];
const args = Object.fromEntries(process.argv.slice(3).reduce((a, v, i, arr) => {
  if (v.startsWith('--')) a.push([v.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]);
  return a;
}, []));
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json',
  '.woff2': 'font/woff2', '.png': 'image/png', '.jpg': 'image/jpeg', '.mp3': 'audio/mpeg' };

function serve() {   // a tiny static server, so the page can load fonts, JSON and frame images
  return new Promise((res) => {
    const srv = http.createServer((req, rsp) => {
      let requested;
      try { requested = decodeURIComponent(req.url.split('?')[0]); }
      catch { rsp.writeHead(400); rsp.end(); return; }
      const p = path.resolve(ROOT, '.' + requested);
      const relative = path.relative(ROOT, p);
      const allowed = ['src', 'assets', 'audio', 'frames'].includes(relative.split(path.sep)[0]);
      if (!allowed || relative.startsWith('..') || !fs.existsSync(p) || !fs.statSync(p).isFile()) { rsp.writeHead(404); rsp.end(); return; }
      rsp.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

async function open(scale) {
  const srv = await serve();
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-lcd-text', '--force-color-profile=srgb'] });
  const probe = await browser.newPage();
  await probe.goto(`http://127.0.0.1:${srv.address().port}/src/index.html?scale=1`);
  await probe.evaluate(() => window.ready);
  const film = await probe.evaluate(() => window.FILM);
  await probe.close();
  const page = await browser.newPage({ viewport: { width: Math.round(film.W * scale), height: Math.round(film.H * scale) }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
  await page.goto(`http://127.0.0.1:${srv.address().port}/src/index.html?scale=${scale}`);
  await page.evaluate(() => window.ready);
  return { browser, srv, page, film };
}
const grab = (page, t, sub, fps, type) =>
  page.evaluate(async ([t, sub, fps, type]) => { await window.renderFrame(t, sub, fps); return window.grab(type, 0.92); }, [t, sub, fps, type]);
const bytes = (d) => Buffer.from(d.slice(d.indexOf(',') + 1), 'base64');

async function main() {
  const scale = +(args.scale || (mode === 'final' ? 1 : 0.5));
  const { browser, srv, page, film } = await open(scale);
  const started = Date.now();
  fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });

  if (mode === 'stills') {
    const dir = path.join(ROOT, 'out/stills'); fs.mkdirSync(dir, { recursive: true });
    for (const t of String(args.times || '1').split(',').map(Number)) {
      const f = path.join(dir, `t${t.toFixed(2).padStart(6, '0')}.png`);
      fs.writeFileSync(f, bytes(await grab(page, t, +(args.sub || 1), 60, 'image/png'))); console.log(f);
    }
  } else if (mode === 'sheet') {
    const from = +(args.from || 0), to = +(args.to || film.DURATION), step = +(args.step || 0.5);
    const dir = path.join(ROOT, 'out/tmp/sheet'); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const list = [];
    for (let t = from + step / 2; t < to; t += step) {          // mid-beat, so a still never lands on a cut
      const f = path.join(dir, `t${t.toFixed(2).padStart(6, '0')}.jpg`);
      fs.writeFileSync(f, bytes(await grab(page, t, 1, 60, 'image/jpeg'))); list.push([f, `${t.toFixed(2)}s`]);
    }
    fs.writeFileSync(path.join(dir, 'list.json'), JSON.stringify(list));
    execFileSync('python3', [path.join(ROOT, 'tools/sheet.py'), path.join(dir, 'list.json'), args.out || path.join(ROOT, 'out/sheet.png'), String(args.cols || 6)], { stdio: 'inherit' });
  } else if (mode === 'video' || mode === 'final') {
    const fps = +(args.fps || (mode === 'final' ? 60 : 30)), sub = +(args.sub || (mode === 'final' ? 4 : 1));
    const from = +(args.from || 0), to = +(args.to || film.DURATION), chunk = +(args.chunk || (mode === 'final' ? 10 : 0));
    const out = path.resolve(args.out || path.join(ROOT, mode === 'final' ? 'out/film.mp4' : 'out/draft.mp4'));
    const enc = mode === 'final' ? ['-preset', 'medium', '-crf', '16'] : ['-preset', 'veryfast', '-crf', '20'];
    const type = mode === 'final' ? 'image/png' : 'image/jpeg';
    const segs = [];
    for (let s0 = from; s0 < to - 1e-6; s0 += chunk || to - from) {
      const s1 = Math.min(to, s0 + (chunk || to - from));
      const seg = path.join(path.dirname(out), 'chunks', `${path.basename(out, '.mp4')}_${String(Math.round(s0 * 10)).padStart(5, '0')}.mp4`);
      segs.push(seg);
      if (fs.existsSync(seg) && !args.force) { console.log('skip', path.relative(ROOT, seg)); continue; }
      fs.mkdirSync(path.dirname(seg), { recursive: true });
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', type === 'image/png' ? 'png' : 'mjpeg', '-i', '-',
        '-c:v', 'libx264', ...enc, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', seg + '.part.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
      for (let n = Math.round(s0 * fps); n < Math.round(s1 * fps); n++) {
        if (!ff.stdin.write(bytes(await grab(page, n / fps, sub, fps, type)))) await new Promise((r) => ff.stdin.once('drain', r));
        if (n % fps === 0) process.stdout.write(`\r${(n / fps).toFixed(0)}s of ${to}s rendered, ${((Date.now() - started) / 1000).toFixed(0)}s elapsed   `);
      }
      const encoded = new Promise((resolve, reject) => {
        ff.once('error', reject);
        ff.once('close', (code) => code === 0 ? resolve() : reject(new Error(`ffmpeg exited with code ${code}`)));
      });
      ff.stdin.end(); await encoded;
      fs.renameSync(seg + '.part.mp4', seg);
    }
    process.stdout.write('\n');
    const list = path.join(path.dirname(out), 'chunks', 'list.txt');
    fs.writeFileSync(list, segs.map((s) => `file '${s}'`).join('\n'));
    const video = args.audio ? out.replace('.mp4', '_silent.mp4') : out;
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', video]);
    if (args.audio) {
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-ss', String(from), '-t', String(to - from), '-i', args.audio,
        '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-aac_coder', 'fast', '-b:a', '320k', '-shortest', '-movflags', '+faststart', out]);
      fs.rmSync(video);
    }
    if (mode === 'video') fs.rmSync(path.join(path.dirname(out), 'chunks'), { recursive: true, force: true });
    console.log('wrote', path.relative(ROOT, out), `in ${((Date.now() - started) / 1000).toFixed(0)}s`);
  } else {
    console.log('modes: stills | sheet | video | final (see the top of this file)');
  }
  await browser.close(); srv.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
