/** Data and presentation rules, independent of the DOM and the 3D engine. */
export const RENDER_POLICY = Object.freeze({
  maxPixelRatio: 3, maxBufferPixels: 3840 * 2160,
  nodeResolution: 10, nodeOpacity: .75,
  linkWidth: 1.05, focusedLinkWidth: 1.15,
  arrowLength: 4.4, focusedArrowLength: 5,
  initialLayoutTicks: 52, dragSettleTicks: 48, dragSettleMs: 1800,
  homeFitRatio: 2 / 3, rotationSpeed: .35,
});
export const normalizeText = value => String(value ?? '').normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('pt-BR');
export const endpointId = value => value && typeof value === 'object' ? value.id : value;

export function applyInitialLayout(nodes, layout) {
  if (layout?.schema !== 'vademecum-graph-layout/v1'
      || layout.warmupTicks !== RENDER_POLICY.initialLayoutTicks
      || !Array.isArray(layout.nodes) || layout.nodes.length !== nodes.length
      || layout.nodes.some(row => !Array.isArray(row) || row.length !== 4)) return false;
  const positions = new Map(layout.nodes.map(row => [row[0], row.slice(1)]));
  if (positions.size !== nodes.length || nodes.some(node => {
    const position = positions.get(node.id);
    return position?.length !== 3 || !position.every(Number.isFinite);
  })) return false;
  for (const node of nodes) {
    const [x, y, z] = positions.get(node.id);
    Object.assign(node, { x, y, z });
  }
  return true;
}

export function renderPixelRatio(width, height, density = 1) {
  // Native phone density up to 3×; cap the drawing buffer at 4K on large screens.
  return Math.max(1, Math.min(density || 1, RENDER_POLICY.maxPixelRatio, Math.sqrt(RENDER_POLICY.maxBufferPixels / Math.max(1, width * height))));
}

export function fitCameraToNodes(nodes, { width, height, fov, padding = 50, scale = 1 }) {
  const bounds = { x: [Infinity, -Infinity], y: [Infinity, -Infinity], z: [Infinity, -Infinity] };
  if (!nodes.length || width <= 0 || height <= 0 || fov <= 0 || fov >= 180) throw new Error('Não foi possível enquadrar o mapa.');
  for (const node of nodes) for (const axis of ['x', 'y', 'z']) {
    if (!Number.isFinite(node[axis])) throw new Error('O layout contém uma posição inválida.');
    bounds[axis][0] = Math.min(bounds[axis][0], node[axis]);
    bounds[axis][1] = Math.max(bounds[axis][1], node[axis]);
  }
  const center = Object.fromEntries(Object.entries(bounds).map(([axis, range]) => [axis, (range[0] + range[1]) / 2]));
  const tangent = Math.tan(fov * Math.PI / 360);
  const fitX = (bounds.x[1] - bounds.x[0]) / (2 * tangent * (Math.max(1, width - padding * 2) / height));
  const fitY = (bounds.y[1] - bounds.y[0]) / (2 * tangent * (Math.max(1, height - padding * 2) / height));
  const distance = Math.max(20, (Math.max(fitX, fitY) + (bounds.z[1] - bounds.z[0]) / 2) * scale);
  return { position: { x: center.x, y: center.y, z: center.z + distance }, center, bounds };
}

export function nodeValue(degree) {
  return Math.max(1, Math.min(7, 1 + Math.log2(Math.max(0, Number(degree) || 0) + 1)));
}

export function prepareSearch(rows) {
  return rows.map(row => ({ row, title: normalizeText(row[1]), text: normalizeText(`${row[1]} ${row[0]} ${row[3] || ''}`) }));
}

export function searchNorms(index, query, limit = 12) {
  const needle = normalizeText(query.trim());
  if (needle.length < 2) return [];
  const terms = needle.split(/\s+/);
  const exact = [], prefix = [], other = [];
  for (const entry of index) {
    if (!terms.every(term => entry.text.includes(term))) continue;
    (entry.title === needle ? exact : entry.title.startsWith(needle) ? prefix : other).push(entry.row);
  }
  return [...exact, ...prefix, ...other].slice(0, limit);
}

export function createGraphIndex(nodes, links) {
  if (!Array.isArray(nodes) || !Array.isArray(links)) throw new Error('O snapshot do grafo é inválido.');
  const nodeById = new Map(), linkById = new Map(), incident = new Map(), cache = new Map();
  for (const node of nodes) {
    if (!node.id || nodeById.has(node.id)) throw new Error('O snapshot contém uma norma sem identidade única.');
    nodeById.set(node.id, node);
    incident.set(node.id, []);
  }
  for (const link of links) {
    const source = endpointId(link.source), target = endpointId(link.target);
    if (!incident.has(source) || !incident.has(target)) throw new Error('O snapshot contém uma relação sem norma correspondente.');
    if (!link.id || linkById.has(link.id)) throw new Error('O snapshot contém uma relação sem identidade única.');
    linkById.set(link.id, link);
    incident.get(source).push(link);
    if (source !== target) incident.get(target).push(link);
  }
  function group(edges, neighborFor) {
    const grouped = new Map();
    let occurrenceCount = 0;
    for (const edge of edges) {
      const id = neighborFor(edge), count = edge.occurrence_count || 1;
      const row = grouped.get(id) || { id, count: 0, node: nodeById.get(id) };
      row.count += count; occurrenceCount += count; grouped.set(id, row);
    }
    const rows = [...grouped.values()].sort((a, b) => (b.node?.degree || 0) - (a.node?.degree || 0) || (a.node?.label || a.id).localeCompare(b.node?.label || b.id, 'pt-BR'));
    return { rows, neighborCount: rows.length, relationCount: edges.length, occurrenceCount };
  }
  function connections(id) {
    if (!nodeById.has(id)) return null;
    if (!cache.has(id)) {
      const edges = incident.get(id);
      const outgoing = group(edges.filter(edge => endpointId(edge.source) === id), edge => endpointId(edge.target));
      const incoming = group(edges.filter(edge => endpointId(edge.target) === id), edge => endpointId(edge.source));
      const neighborIds = [...new Set([...outgoing.rows, ...incoming.rows].map(row => row.id))];
      cache.set(id, { outgoing, incoming, neighborIds, neighborCount: neighborIds.length });
    }
    return cache.get(id);
  }
  function metrics() {
    const visited = new Set();
    let components = 0, isolates = 0;
    for (const id of nodeById.keys()) {
      if (!incident.get(id).length) isolates++;
      if (visited.has(id)) continue;
      components++; visited.add(id);
      const stack = [id];
      while (stack.length) {
        const current = stack.pop();
        for (const edge of incident.get(current)) {
          const source = endpointId(edge.source), target = endpointId(edge.target);
          const neighbor = source === current ? target : source;
          if (!visited.has(neighbor)) { visited.add(neighbor); stack.push(neighbor); }
        }
      }
    }
    return { components, isolates };
  }
  return { nodeById, linkById, incident, connections, metrics };
}
