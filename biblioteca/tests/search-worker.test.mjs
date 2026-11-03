import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';

const workerSource = await readFile(new URL('../src/search-worker.js', import.meta.url), 'utf8');

function createWorker(fetchIndex) {
  let listener;
  const pending = [];
  const context = {
    URL,
    fetch: fetchIndex,
    setTimeout: callback => setImmediate(callback),
    self: {
      location: { href: 'https://example.test/biblioteca/library.js' },
      addEventListener: (_type, callback) => { listener = callback; },
      postMessage: message => pending.shift()?.(message),
    },
  };
  vm.runInNewContext(workerSource, context, { filename: 'search-worker.js' });
  return {
    send(data) {
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('worker response timed out')), 5000);
        pending.push(message => {
          clearTimeout(timeout);
          resolve(message);
        });
        listener({ data });
      });
    },
  };
}

test('full-text worker preserves section and original-text offsets after accent normalization', async () => {
  const worker = createWorker(async () => ({
    ok: true,
    json: async () => [{
      id: 'lei-teste',
      title: 'Lei de teste',
      sections: [
        { index: 0, label: 'Preâmbulo', anchor: 'preambulo', text: 'á'.repeat(120) },
        { index: 1, label: 'Art. 5º', anchor: 'art-5', text: 'A Constituição assegura igualdade e princípios.' },
      ],
    }],
  }));

  const result = await worker.send({ type: 'search', token: 1, query: 'principios', visibleIds: ['lei-teste'], localBooks: [] });
  assert.equal(result.type, 'results');
  assert.equal(result.matches.length, 1);
  assert.equal(result.matches[0].label, 'Art. 5º');
  assert.equal(result.matches[0].text.slice(result.matches[0].at, result.matches[0].matchEnd), 'princípios');
});

test('full-text worker allows retry after the index fetch fails', async () => {
  let requests = 0;
  const worker = createWorker(async () => {
    requests++;
    if (requests === 1) throw new Error('temporary network error');
    return { ok: true, json: async () => [] };
  });

  const failed = await worker.send({ type: 'search', token: 1, query: 'lei', visibleIds: [], localBooks: [] });
  assert.equal(failed.type, 'error');

  const retried = await worker.send({ type: 'search', token: 2, query: 'lei', visibleIds: [], localBooks: [] });
  assert.equal(retried.type, 'results');
  assert.equal(requests, 2);
});
