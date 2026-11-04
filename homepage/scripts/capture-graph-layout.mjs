import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { chromium, expect } from '@playwright/test';
import { RENDER_POLICY } from '../public/graph/viewer/graph-core.js';

const source = await readFile(new URL('../public/graph/data/explorer.json.gz', import.meta.url));
const data = JSON.parse(gunzipSync(source));
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ reducedMotion: 'reduce' });
  // Regeneration must exercise the original warmup, rather than recapture the cache.
  await page.route('**/initial-layout.json', route => route.fulfill({
    contentType: 'application/json',
    body: 'null',
  }));
  await page.goto(process.env.GRAPH_LAYOUT_URL || 'http://127.0.0.1:8765/graph/viewer/index.html?home-hero=1');
  await expect.poll(() => page.evaluate(async () => {
    const app = await import(document.querySelector('script[data-graph-app]').src);
    return app.getGraphDiagnostics().ready;
  }), { timeout: 30_000 }).toBe(true);
  const nodes = await page.evaluate(async ids => {
    const app = await import(document.querySelector('script[data-graph-app]').src);
    return ids.map(id => {
      const position = app.getNodePosition(id);
      return [id, ...['x', 'y', 'z'].map(axis => Number(position[axis].toFixed(6)))];
    });
  }, data.nodes.map(node => node.id));
  if (nodes.some(row => row.slice(1).some(value => !Number.isFinite(value)))) {
    throw new Error('O layout gerado contém coordenadas inválidas.');
  }
  const layout = {
    schema: 'vademecum-graph-layout/v1',
    sourceSha256: createHash('sha256').update(source).digest('hex'),
    warmupTicks: RENDER_POLICY.initialLayoutTicks,
    nodes,
  };
  await writeFile(new URL('../public/graph/viewer/initial-layout.json', import.meta.url), JSON.stringify(layout) + '\n');
  console.log(`Layout preparado para ${nodes.length} nós.`);
} finally {
  await browser.close();
}
