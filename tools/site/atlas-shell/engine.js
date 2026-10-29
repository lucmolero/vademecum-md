/* Network, decompression, integrity and search run outside the rendering thread. */
const stop = new Set('a o as os de da do das dos e em no na nos nas um uma que se por para com ao aos ou art'.split(' '));
const norm = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const tokens = value => [...new Set((norm(value).match(/[a-z0-9]+/g) || []).filter(t => t.length > 1 && !stop.has(t)))];
const shard = term => [...term].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 64, 0);
const packs = new Map(), indexes = new Map(), pending = new Map();
let manifest, docs, table, graph;
const manifestURL = new URL('generated/atlas/manifest.json', self.location);
async function compressed(item) {
  const response = await fetch(new URL(item.file, manifestURL), { signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw Error(`Arquivo indisponível (${response.status}).`);
  const buffer = await response.arrayBuffer();
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', buffer))].map(v => v.toString(16).padStart(2, '0')).join('');
  if (hash !== item.sha256) throw Error('Falha de integridade: o pacote não corresponde a este acervo.');
  if (typeof DecompressionStream === 'undefined') throw Error('Este protótipo precisa de um navegador com descompressão gzip nativa.');
  return new Response(new Blob([buffer]).stream().pipeThrough(new DecompressionStream('gzip'))).json();
}
async function cached(map, key, item, limit) {
  if (map.has(key)) { const value = map.get(key); map.delete(key); map.set(key, value); return value; }
  if (!pending.has(item.file)) pending.set(item.file, compressed(item).finally(() => pending.delete(item.file)));
  const value = await pending.get(item.file);
  map.set(key, value);
  if (map.size > limit) map.delete(map.keys().next().value);
  return value;
}
async function documentById(id) {
  const meta = docs.find(d => d.id === id);
  if (!meta) throw Error('Norma não encontrada neste snapshot.');
  const pack = await cached(packs, meta.pack, manifest.packs[meta.pack], 2);
  return { ...meta, ...pack[id] };
}
async function search(query, scope) {
  const q = norm(query.trim());
  const parts = q.split(/\s+/).filter(Boolean);
  const matches = docs.map((d, index) => ({ d, index, hay: norm([d.title, d.canonicalTitle, ...d.aliases, d.number, String(d.number).replace(/\D/g, ''), d.year, d.domain].join(' ')) }))
    .filter(row => parts.every(t => row.hay.includes(t.replace(/(?<=\d)\.(?=\d)/g, '')) || row.hay.includes(t)))
    .sort((a, b) => (norm(a.d.title) === q ? -1 : 0) - (norm(b.d.title) === q ? -1 : 0));
  if (scope === 'normas' || !q) return { documents: matches.slice(0, 20).map(x => x.d), passages: [], total: matches.length };
  const terms = tokens(query);
  if (!terms.length) return { documents: matches.slice(0, 12).map(x => x.d), passages: [], total: 0 };
  if (!table) table = await compressed(manifest.table);
  const lists = await Promise.all(terms.map(async t => {
    const index = await cached(indexes, shard(t), manifest.shards[shard(t)], 12);
    let previous = 0;
    return (index[t] || []).map(delta => previous += delta);
  }));
  lists.sort((a, b) => a.length - b.length);
  let found = lists[0];
  for (const list of lists.slice(1)) { const set = new Set(list); found = found.filter(v => set.has(v)); }
  const topDocs = new Set(matches.map(x => x.index));
  found.sort((a, b) => Number(topDocs.has(table[b][0])) - Number(topDocs.has(table[a][0])));
  return { documents: matches.slice(0, 6).map(x => x.d), passages: found.slice(0, 60).map(row => {
    const [di, bi, snippet] = table[row];
    return { id: docs[di].id, title: docs[di].title, anchor: docs[di].outline[bi][0], label: docs[di].outline[bi][1], snippet };
  }), total: found.length };
}
self.onmessage = async ({ data }) => {
  try {
    let value;
    if (data.type === 'init') {
      const response = await fetch(manifestURL, { cache: 'no-cache', signal: AbortSignal.timeout(20000) });
      if (!response.ok) throw Error('Não foi possível carregar o manifesto.');
      manifest = await response.json();
      if (manifest.schema !== 'atlas-reader/1') throw Error('Formato de acervo incompatível.');
      docs = await compressed(manifest.catalog);
      value = { manifest, docs };
    } else if (!docs) throw Error('O acervo ainda está iniciando.');
    else if (data.type === 'open') value = await documentById(data.id);
    else if (data.type === 'search') value = await search(data.query, data.scope);
    else if (data.type === 'graph') value = graph || (graph = await compressed(manifest.graph));
    self.postMessage({ request: data.request, value });
  } catch (error) { self.postMessage({ request: data.request, error: error.message }); }
};
