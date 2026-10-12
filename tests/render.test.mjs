import test from 'node:test';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

test('film loads its font and renders deterministically across out-of-order frames', async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(pathToFileURL(path.resolve('src/index.html')).href);
    await page.evaluate(() => window.ready);
    assert.equal(await page.evaluate(() => document.fonts.check('900 30px "Inter Tight"')), true);
    assert.deepEqual(await page.evaluate(() => window.FILM), { W: 1920, H: 1080, DURATION: 6 });
    const grab = t => page.evaluate(t => { window.renderFrame(t); return window.grab(); }, t);
    const mid = await grab(4.8);
    await grab(2.3);
    assert.equal(await grab(4.8), mid);
    assert.equal(await grab(0), await grab(6 - 1 / 60));
    assert.notEqual(await grab(2.3), mid);
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
});
