import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { applyInitialLayout, createGraphIndex, fitCameraToNodes, prepareSearch, searchNorms, renderPixelRatio } from '../public/graph/viewer/graph-core.js';
import { createRenderScheduler } from '../public/graph/viewer/render-scheduler.js';

test('packaged initial layout matches the graph snapshot and rejects incomplete caches atomically', () => {
  const compressed = readFileSync(new URL('../public/graph/data/explorer.json.gz', import.meta.url));
  const { nodes } = JSON.parse(gunzipSync(compressed));
  const layout = JSON.parse(readFileSync(new URL('../public/graph/viewer/initial-layout.json', import.meta.url)));
  assert.equal(layout.sourceSha256, createHash('sha256').update(compressed).digest('hex'));
  assert.equal(applyInitialLayout(nodes, layout), true);
  assert.deepEqual(nodes.map(node => [node.id, node.x, node.y, node.z]), layout.nodes);
  for (const rows of [layout.nodes.slice(1), [null, ...layout.nodes.slice(1)], [['missing', 1, 2, 3], ...layout.nodes.slice(1)]]) {
    const before = structuredClone(nodes);
    assert.equal(applyInitialLayout(nodes, { ...layout, nodes: rows }), false);
    assert.deepEqual(nodes, before);
  }
});

test('HD pixel budget preserves phone density without allocating an unbounded desktop buffer', () => {
  assert.equal(renderPixelRatio(390, 790, 3), 3);
  assert.equal(renderPixelRatio(1440, 824, 2), 2);
  assert.equal(renderPixelRatio(3840, 2160, 3), 1);
  assert.equal(renderPixelRatio(300, 200, 1), 1);
});

test('desktop layout on a phone stays within physical density and GPU dimensions', () => {
  const ratio = renderPixelRatio(980, 2120, 3, { screenWidth: 390, viewportWidth: 980 });
  assert.ok(ratio <= 3 * 390 / 980);
  assert.ok(980 * 2120 * ratio ** 2 <= 390 * 844 * 9 + 1);
  const tall = renderPixelRatio(980, 6000, 3);
  assert.ok(6000 * tall <= 4096);
  assert.ok(tall < 1);
  const limitedGpu = renderPixelRatio(390, 844, 3, { maxDimension: 2048 });
  assert.ok(844 * limitedGpu <= 2048);
  // A normal phone viewport still receives its native density.
  assert.equal(renderPixelRatio(390, 844, 3, { screenWidth: 390, viewportWidth: 390 }), 3);
});

test('search ignores accents, prioritizes titles and requires all query terms', () => {
  const index = prepareSearch([
    ['lei', 'Lei de organização da Constituição', 'Lei'],
    ['cf', 'Constituição Federal', 'Constituição'],
    ['civil', 'Código Civil de 2002', 'Código'],
  ]);
  assert.deepEqual(searchNorms(index, 'constituição').map(row => row[0]), ['cf', 'lei']);
  assert.deepEqual(searchNorms(index, 'CIVIL 2002').map(row => row[0]), ['civil']);
  assert.deepEqual(searchNorms(index, 'inexistente'), []);
  assert.deepEqual(searchNorms(index, 'c'), []);
});

test('camera framing uses settled node positions and accounts for narrow viewports', () => {
  const nodes = [{ x: -500, y: -400, z: -450 }, { x: 470, y: 430, z: 480 }];
  const desktop = fitCameraToNodes(nodes, { width: 1440, height: 824, fov: 50, scale: 2 / 3 });
  const mobile = fitCameraToNodes(nodes, { width: 390, height: 790, fov: 50, scale: 2 / 3 });
  assert.ok(desktop.position.z > 900);
  assert.ok(mobile.position.z > desktop.position.z);
  assert.deepEqual(desktop.center, { x: -15, y: 15, z: 15 });
  assert.throws(() => fitCameraToNodes([{ x: 0, y: NaN, z: 0 }], { width: 390, height: 790, fov: 50 }), /inválida/);
});

test('connection index counts self references once and preserves direction and isolated norms', () => {
  const nodes = [{ id: 'a' }, { id: 'b' }, { id: 'c' }].map(Object.freeze);
  const links = [
    { id: 'ab', source: 'a', target: 'b', occurrence_count: 3 },
    { id: 'aa', source: 'a', target: 'a', occurrence_count: 1 },
  ].map(Object.freeze);
  const index = createGraphIndex(nodes, links);
  assert.equal(index.incident.get('a').length, 2);
  assert.equal(index.connections('a').outgoing.occurrenceCount, 4);
  assert.equal(index.connections('b').incoming.rows[0].id, 'a');
  assert.deepEqual(index.metrics(), { components: 2, isolates: 1 });
  assert.equal(index.connections('missing'), null);
  assert.throws(() => createGraphIndex(nodes, [{ id: 'bad', source: 'a', target: 'missing' }]), /correspondente/);
  assert.throws(() => createGraphIndex([{ id: 'a' }, { id: 'a' }], []), /única/);
});

function schedulerHarness() {
  let clock = 0, scheduled, resumes = 0, pauses = 0;
  const scheduler = createRenderScheduler({
    resume: () => resumes++, pause: () => pauses++, now: () => clock,
    setTimer: (callback, delay) => { scheduled = { callback, at: clock + delay }; return 1; },
    clearTimer: () => { scheduled = null; },
  });
  return { scheduler, counts: () => ({ resumes, pauses }), advance(milliseconds) {
    clock += milliseconds;
    if (scheduled && scheduled.at <= clock) { const callback = scheduled.callback; scheduled = null; callback(); }
  } };
}

test('static graph draws on interaction and sleeps after the last invalidation', () => {
  const { scheduler, advance, counts } = schedulerHarness();
  scheduler.setSettled(true);
  assert.equal(scheduler.isRunning(), false);
  scheduler.invalidate(100);
  assert.equal(scheduler.isRunning(), true);
  advance(80); scheduler.invalidate(100); advance(80);
  assert.equal(scheduler.isRunning(), true);
  advance(20);
  assert.equal(scheduler.isRunning(), false);
  assert.deepEqual(counts(), { resumes: 1, pauses: 2 });
});

test('hidden pages and lost WebGL contexts override rotation and pointer interaction', () => {
  const { scheduler } = schedulerHarness();
  scheduler.setContinuous(true); scheduler.setDragging(true);
  scheduler.setVisible(false);
  assert.equal(scheduler.isRunning(), false);
  scheduler.setVisible(true);
  assert.equal(scheduler.isRunning(), true);
  scheduler.setContextAvailable(false);
  assert.equal(scheduler.isRunning(), false);
  scheduler.setContextAvailable(true);
  assert.equal(scheduler.isRunning(), true);
  scheduler.destroy(); scheduler.invalidate(100);
  assert.equal(scheduler.isRunning(), false);
});
