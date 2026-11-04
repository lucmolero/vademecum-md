import { copyFile, mkdir, readdir, rename, stat } from 'node:fs/promises';
import { join } from 'node:path';
import { chromium } from '@playwright/test';

const captureDir = 'work/launch-film-capture-clean';
await mkdir(captureDir, { recursive: true });
const browser = await chromium.launch({ headless: true, args: ['--autoplay-policy=no-user-gesture-required'] });
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
  reducedMotion: 'no-preference',
  recordVideo: { dir: captureDir, size: { width: 1920, height: 1080 } },
});
const page = await context.newPage();
page.on('console', (message) => { if (message.text().startsWith('[film]')) console.log(message.text()); });
page.on('pageerror', (error) => console.error('Film renderer page error:', error.message));
await page.goto('http://127.0.0.1:8787/scripts/launch-film.html', { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.filmReady === true, { timeout: 30_000 });
await page.mouse.click(1908, 1068);
await page.screenshot({ path: 'work/vademecum-tour-poster.png' });
try {
  await page.waitForFunction(() => window.filmFinished === true, null, { timeout: 180_000 });
} catch (error) {
  console.error('Film renderer state:', await page.evaluate(() => ({ finished: window.filmFinished, source: document.querySelector('video').src, currentTime: document.querySelector('video').currentTime, duration: document.querySelector('video').duration, paused: document.querySelector('video').paused, readyState: document.querySelector('video').readyState, scene: document.querySelector('.stage-label').textContent })));
  throw error;
}
await context.close();
await browser.close();

const recordings = (await readdir(captureDir))
  .filter((name) => name.endsWith('.webm'))
  .map(async (name) => ({ name, size: (await stat(join(captureDir, name))).size }));
const completeRecordings = await Promise.all(recordings);
if (!completeRecordings.length) throw new Error('Playwright did not create a launch film recording');
completeRecordings.sort((a, b) => a.size - b.size);
const file = completeRecordings.at(-1)?.name;
if (!file) throw new Error('Playwright did not create a launch film recording');
await rename(join(captureDir, file), 'work/vademecum-tour-clean.webm');
await copyFile('work/vademecum-tour-poster.png', 'homepage/public/demos/media/vademecum-tour-poster.png');
console.log('Recorded the animated launch film in 1920 × 1080.');
