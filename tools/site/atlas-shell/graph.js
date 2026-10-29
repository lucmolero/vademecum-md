const escapeHTML = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));
const normalize = (value) => String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
const typeClass = (value) => String(value ?? "other").replace(/[^a-z0-9_-]/gi, "-");

export async function mountGraph(root, documents, focusId, rpc) {
  root.innerHTML = `<div class="page graph-page">
    <header class="graph-page-heading"><div><p class="eyebrow">CARTOGRAFIA NORMATIVA</p><h1>Uma norma nunca está sozinha.</h1><p>Explore as relações registradas, siga a direção de cada vínculo e abra o texto de origem.</p></div><a class="outline-button" href="#/home">← Visão geral</a></header>
    <section class="graph-controls" aria-label="Controles do grafo"><div class="graph-search-wrap"><label class="field-label" for="graph-search">Comece por uma norma</label><input id="graph-search" type="search" class="context-find" placeholder="Nome, número ou sigla" autocomplete="off" aria-controls="graph-suggestions" aria-expanded="false"><div id="graph-suggestions" class="graph-suggestions" role="listbox" hidden></div></div><label class="graph-filter"><span class="field-label">Relação</span><select data-graph-kind><option value="">Todas as relações</option></select></label><label class="graph-filter"><span class="field-label">Direção</span><select data-graph-direction><option value="all">Todas</option><option value="outgoing">Parte desta norma</option><option value="incoming">Chega a esta norma</option></select></label><button type="button" class="outline-button" data-graph-reset>Constituição Federal</button></section>
    <div class="graph-workspace"><section class="graph-map-card" aria-labelledby="graph-current-title"><div class="graph-map-top"><div><p class="context-label">NORMA EM FOCO</p><h2 id="graph-current-title"></h2><p data-graph-summary></p></div><a data-graph-open class="graph-open-law">Abrir no leitor <span aria-hidden="true">↗</span></a></div><div class="graph-canvas-scroll"><svg class="graph-canvas" viewBox="0 0 900 560" role="group" aria-label="Grafo de relações normativas"></svg></div><div class="graph-legend"><span><i class="legend-dot alteration"></i>Alteração</span><span><i class="legend-dot repeal"></i>Revogação</span><span><i class="legend-dot regulation"></i>Regulamentação</span><span><i class="legend-dot other"></i>Outras relações</span><span>Seta mantém a direção publicada</span></div><p class="graph-map-status" data-graph-status role="status" aria-live="polite"></p></section>
    <aside class="graph-side-panel" aria-label="Detalhes e relações da norma"><section class="graph-detail" data-graph-detail aria-live="polite"></section><section class="graph-list-section"><div class="graph-list-heading"><div><p class="context-label">VÍNCULOS PUBLICADOS</p><h2>Ao redor desta norma</h2></div><span data-graph-count class="graph-count"></span></div><div data-graph-list class="graph-relation-list"></div><button type="button" class="text-button graph-more" data-graph-more hidden>Mostrar mais relações ↓</button></section></aside></div>
    <p class="graph-caveat">O mapa reproduz metadados publicados no snapshot. Relações podem ser indiretas ou incompletas; não indicam, por si só, vigência ou efeito jurídico. Consulte a evidência e a fonte oficial antes de interpretar um vínculo.</p>
  </div>`;

  const [graph] = await Promise.all([rpc("graph")]);
  if (!graph || graph.schema !== "atlas-relations/1") throw new Error("O grafo deste snapshot não está disponível.");
  const docs = new Map(documents.map((document) => [document.id, document]));
  const edges = graph.edges.filter((edge) => docs.has(edge.source) && docs.has(edge.target));
  const search = root.querySelector("#graph-search");
  const suggestions = root.querySelector("#graph-suggestions");
  const kindSelect = root.querySelector("[data-graph-kind]");
  const directionSelect = root.querySelector("[data-graph-direction]");
  const svg = root.querySelector(".graph-canvas");
  const detail = root.querySelector("[data-graph-detail]");
  const relationList = root.querySelector("[data-graph-list]");
  const moreButton = root.querySelector("[data-graph-more]");
  const countLabel = root.querySelector("[data-graph-count]");
  const status = root.querySelector("[data-graph-status]");
  const types = [...new Set(edges.map((edge) => edge.type))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  for (const type of types) {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = edges.find((edge) => edge.type === type)?.label || type.replaceAll("_", " ");
    kindSelect.append(option);
  }

  let current = docs.has(focusId) ? focusId : documents.find((document) => document.aliases?.includes("CF"))?.id || documents[0]?.id;
  let selectedEdge = null;
  let listLimit = 24;
  const visibleEdges = () => edges.filter((edge) => {
    const touches = edge.source === current || edge.target === current;
    const typeMatches = !kindSelect.value || edge.type === kindSelect.value;
    const directionMatches = directionSelect.value === "all"
      || (directionSelect.value === "outgoing" && edge.source === current)
      || (directionSelect.value === "incoming" && edge.target === current);
    return touches && typeMatches && directionMatches;
  }).sort((a, b) => a.label.localeCompare(b.label, "pt-BR") || a.id.localeCompare(b.id));

  const selectEdge = (id) => {
    selectedEdge = edges.find((edge) => edge.id === id) || null;
    renderDetail();
    root.querySelectorAll("[data-edge-id]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.edgeId === selectedEdge?.id)));
  };

  function renderDetail() {
    if (!selectedEdge) {
      detail.innerHTML = `<p class="context-label">LEITURA DO GRAFO</p><h3>Siga uma ligação.</h3><p>Selecione uma aresta ou um diploma no mapa. A direção e a evidência vêm do registro publicado.</p>`;
      return;
    }
    const source = docs.get(selectedEdge.source);
    const target = docs.get(selectedEdge.target);
    const confidence = selectedEdge.confidence ? String(selectedEdge.confidence).replace("media", "média") : "não informada";
    const sourceLink = /^https?:\/\//i.test(selectedEdge.source_url || "") ? `<a href="${escapeHTML(selectedEdge.source_url)}" target="_blank" rel="noopener noreferrer">Abrir fonte indicada ↗</a>` : "Fonte não informada";
    detail.innerHTML = `<p class="context-label">RELAÇÃO SELECIONADA</p><p class="graph-edge-endpoint"><a href="#/read/${encodeURIComponent(source.id)}">${escapeHTML(source.title)}</a></p><p class="graph-edge-label">${escapeHTML(selectedEdge.label)}</p><p class="graph-edge-endpoint"><a href="#/read/${encodeURIComponent(target.id)}">${escapeHTML(target.title)}</a></p><dl><dt>Dispositivo</dt><dd>${escapeHTML(selectedEdge.device || "Não identificado no registro")}</dd><dt>Confiança registrada</dt><dd>${escapeHTML(confidence)}</dd><dt>Revisão</dt><dd>${escapeHTML(String(selectedEdge.review || "não informada").replaceAll("_", " "))}</dd><dt>Efeito</dt><dd>${escapeHTML(selectedEdge.effect || "Não informado")}</dd></dl><p class="graph-source-link">${sourceLink}</p>${selectedEdge.evidence ? `<details class="graph-evidence"><summary>Evidência textual</summary><blockquote>${escapeHTML(selectedEdge.evidence)}</blockquote>${selectedEdge.evidence_sha256 ? `<code>SHA-256 · ${escapeHTML(selectedEdge.evidence_sha256)}</code>` : ""}</details>` : "<p class=graph-muted>O registro não contém evidência textual.</p>"}`;
  }

  function drawMap(list) {
    const focus = docs.get(current);
    const grouped = new Map();
    for (const edge of list) {
      const neighborId = edge.source === current ? edge.target : edge.source;
      if (!grouped.has(neighborId)) grouped.set(neighborId, []);
      grouped.get(neighborId).push(edge);
    }
    const ranked = [...grouped.entries()].sort((a, b) => b[1].length - a[1].length || docs.get(a[0]).title.localeCompare(docs.get(b[0]).title, "pt-BR"));
    const visible = ranked.slice(0, 12);
    const center = { x: 450, y: 280 };
    const radiusX = 300;
    const radiusY = 205;
    const positions = new Map([[current, center]]);
    visible.forEach(([id], index) => {
      const angle = -Math.PI / 2 + (Math.PI * 2 * index) / Math.max(visible.length, 1);
      positions.set(id, { x: center.x + Math.cos(angle) * radiusX, y: center.y + Math.sin(angle) * radiusY });
    });
    const fragments = [`<defs><marker id="atlas-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8z" fill="context-stroke"/></marker></defs>`];
    for (const [id, connected] of visible) {
      const edge = connected[0];
      const neighbor = docs.get(id);
      const point = positions.get(id);
      const isOut = edge.source === current;
      const from = isOut ? center : point;
      const to = isOut ? point : center;
      const dx = to.x - from.x;
      const dy = to.y - from.y;
      const length = Math.hypot(dx, dy) || 1;
      const startX = from.x + (dx / length) * 59;
      const startY = from.y + (dy / length) * 39;
      const endX = to.x - (dx / length) * 59;
      const endY = to.y - (dy / length) * 39;
      const bend = Math.min(44, Math.abs(dx) * .1);
      const className = `edge-${typeClass(edge.type)}`;
      fragments.push(`<path class="graph-edge ${className}" d="M${startX.toFixed(1)} ${startY.toFixed(1)} Q${((startX + endX) / 2).toFixed(1)} ${((startY + endY) / 2 - Math.sign(dy || 1) * bend).toFixed(1)} ${endX.toFixed(1)} ${endY.toFixed(1)}" marker-end="url(#atlas-arrow)" data-edge-id="${escapeHTML(edge.id)}" tabindex="0" role="button" aria-label="${escapeHTML(docs.get(edge.source).title)} ${escapeHTML(edge.label)} ${escapeHTML(docs.get(edge.target).title)}"/>`);
      fragments.push(`<g class="graph-node ${className}" tabindex="0" role="button" data-focus-id="${escapeHTML(id)}" aria-label="Explorar ${escapeHTML(neighbor.title)}"><rect x="${(point.x - 57).toFixed(1)}" y="${(point.y - 36).toFixed(1)}" width="114" height="72" rx="13"/><text class="graph-node-title" x="${point.x.toFixed(1)}" y="${(point.y - 3).toFixed(1)}">${escapeHTML(neighbor.title.length > 18 ? `${neighbor.title.slice(0, 17)}…` : neighbor.title)}</text><text class="graph-node-meta" x="${point.x.toFixed(1)}" y="${(point.y + 17).toFixed(1)}">${connected.length} ${connected.length === 1 ? "relação" : "relações"}</text></g>`);
    }
    fragments.push(`<g class="graph-node graph-node-focus" tabindex="0" role="button" data-focus-id="${escapeHTML(current)}" aria-label="Norma em foco: ${escapeHTML(focus.title)}"><rect x="${center.x - 72}" y="${center.y - 45}" width="144" height="90" rx="18"/><text class="graph-node-title" x="${center.x}" y="${center.y - 5}">${escapeHTML(focus.title.length > 22 ? `${focus.title.slice(0, 21)}…` : focus.title)}</text><text class="graph-node-meta" x="${center.x}" y="${center.y + 18}">NORMA EM FOCO</text></g>`);
    svg.innerHTML = fragments.join("");
    if (ranked.length > visible.length) status.textContent = `O mapa mostra ${visible.length} de ${ranked.length} diplomas conectados. A lista lateral mantém todos os ${list.length} registros filtrados.`;
    else if (!ranked.length) status.textContent = "Não há relações que correspondam a estes filtros neste snapshot.";
    else status.textContent = `Mapa com ${ranked.length} diplomas conectados e ${list.length} relações registradas.`;
  }

  function renderList(list) {
    countLabel.textContent = `${list.length} ${list.length === 1 ? "registro" : "registros"}`;
    const page = list.slice(0, listLimit);
    relationList.innerHTML = page.map((edge) => `<button type="button" class="graph-relation-row relation-${typeClass(edge.type)}" data-edge-id="${escapeHTML(edge.id)}" aria-pressed="${selectedEdge?.id === edge.id}"><span><strong>${escapeHTML(docs.get(edge.source).title)}</strong><small>${escapeHTML(edge.label)}</small><strong>${escapeHTML(docs.get(edge.target).title)}</strong></span><span aria-hidden="true">↗</span></button>`).join("") || `<p class="graph-muted">Nenhum vínculo para esta combinação de filtros.</p>`;
    moreButton.hidden = page.length >= list.length;
    moreButton.textContent = `Mostrar mais ${Math.min(24, list.length - page.length)} relações ↓`;
  }

  function render() {
    const document = docs.get(current);
    if (!document) return;
    root.querySelector("#graph-current-title").textContent = document.title;
    root.querySelector("[data-graph-summary]").textContent = `${document.type} ${document.number} · ${document.domain} · ${document.year}`;
    root.querySelector("[data-graph-open]").href = `#/read/${encodeURIComponent(current)}`;
    const list = visibleEdges();
    if (!list.some((edge) => edge.id === selectedEdge?.id)) selectedEdge = list[0] || null;
    drawMap(list);
    renderList(list);
    renderDetail();
    root.querySelectorAll("[data-edge-id]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.edgeId === selectedEdge?.id)));
  }

  const choose = (id) => {
    if (!docs.has(id)) return;
    location.hash = `#/graph/${encodeURIComponent(id)}`;
  };
  function renderSuggestions() {
    const query = normalize(search.value.trim());
    if (!query) { suggestions.hidden = true; search.setAttribute("aria-expanded", "false"); return; }
    const matches = documents.filter((document) => normalize([document.title, document.canonicalTitle, document.number, document.year, ...(document.aliases || [])].join(" ")).includes(query)).slice(0, 6);
    suggestions.innerHTML = matches.map((document) => `<button type="button" role="option" data-focus-id="${escapeHTML(document.id)}"><strong>${escapeHTML(document.title)}</strong><small>${escapeHTML(document.type)} ${escapeHTML(document.number)} · ${escapeHTML(document.year)}</small></button>`).join("") || `<p>Nenhuma norma encontrada neste snapshot.</p>`;
    suggestions.hidden = false;
    search.setAttribute("aria-expanded", "true");
  }

  search.addEventListener("input", renderSuggestions);
  search.addEventListener("keydown", (event) => {
    if (event.key === "Escape") { suggestions.hidden = true; search.setAttribute("aria-expanded", "false"); }
    if (event.key === "Enter") { event.preventDefault(); suggestions.querySelector("[data-focus-id]")?.click(); }
  });
  kindSelect.addEventListener("change", () => { listLimit = 24; render(); });
  directionSelect.addEventListener("change", () => { listLimit = 24; render(); });
  root.querySelector("[data-graph-reset]").addEventListener("click", () => {
    const constitution = documents.find((document) => document.aliases?.includes("CF"));
    if (constitution) choose(constitution.id);
  });
  moreButton.addEventListener("click", () => { listLimit += 24; render(); });
  root.addEventListener("click", (event) => {
    const node = event.target.closest("[data-focus-id]");
    if (node) { choose(node.dataset.focusId); return; }
    const edge = event.target.closest("[data-edge-id]");
    if (edge) selectEdge(edge.dataset.edgeId);
  });
  root.addEventListener("keydown", (event) => {
    const interactive = event.target.closest("[data-focus-id], [data-edge-id]");
    if (interactive && (event.key === "Enter" || event.key === " ")) { event.preventDefault(); interactive.click(); }
  });
  render();
}
