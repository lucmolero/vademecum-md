import { chromium } from '@playwright/test';
import { readdir, rename } from 'node:fs/promises';
import { join } from 'node:path';
const outDir = 'work/library-recording';
await (await import('node:fs/promises')).mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5, reducedMotion: 'no-preference', recordVideo: { dir: outDir, size: { width: 1440, height: 900 } } });
const page = await context.newPage();
await page.addInitScript(() => {
  document.addEventListener('DOMContentLoaded', () => {
    const cursor = document.createElement('div'); cursor.id = 'recorded-pointer'; cursor.setAttribute('aria-hidden', 'true');
    Object.assign(cursor.style, { position:'fixed', left:'0', top:'0', width:'18px', height:'18px', border:'2px solid #fff', borderRadius:'50%', background:'rgba(15,118,110,.85)', boxShadow:'0 1px 5px #0008', zIndex:'2147483647', pointerEvents:'none', transform:'translate(-50%,-50%)', transition:'left .045s linear,top .045s linear', opacity:'0' }); document.body.append(cursor);
    addEventListener('mousemove', e => { cursor.style.left = e.clientX+'px'; cursor.style.top = e.clientY+'px'; cursor.style.opacity='1'; });
  }, { once:true });
});
await page.goto('http://127.0.0.1:8787/biblioteca/', { waitUntil:'domcontentloaded' });
await page.locator('.shelf-book-open').first().waitFor({ state:'visible', timeout:30000 });
await page.waitForTimeout(1800);
const search = page.locator('#library-query');
await search.click(); await search.fill('14.133'); await page.waitForTimeout(2300);
const target = page.locator('article[data-book-id="br-federal-lei_ordinaria-14133-2021"] .shelf-book-open');
await target.waitFor({ state:'visible', timeout:20000 }); await page.waitForTimeout(700); await target.click();
await page.locator('#reading:not([hidden])').waitFor({ state:'visible', timeout:20000 }); await page.waitForTimeout(1300);
const toc = page.locator('#toc button').filter({ hasText: /^Art\. 5º$/ }).first();
if (await toc.count()) { await toc.click(); await page.waitForTimeout(1600); }
const source = page.locator('#show-source');
if (await source.count()) { await source.click(); await page.waitForTimeout(2000); }
await page.waitForTimeout(1800);
await context.close(); await browser.close();
const files = await readdir(outDir); const video = files.find(f => f.endsWith('.webm'));
if (!video) throw new Error('Playwright did not create a WebM recording');
await rename(join(outDir, video), 'homepage/public/demos/media/biblioteca-e-leitor.webm');
console.log('Recorded library/reader tour:', video);
