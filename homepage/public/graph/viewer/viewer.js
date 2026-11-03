const root = document.querySelector('#network');
const countBox = document.querySelector('#counts');
const viewCount = document.querySelector('#view-count');
const search = document.querySelector('#search');
const suggestions = document.querySelector('#suggestions');
const themeToggle = document.querySelector('#theme-toggle');
const detailsPanel = document.querySelector('#details');
const contextExpand = document.querySelector('#context-expand');
const motionHint = document.querySelector('#motion-hint');
const record = document.querySelector('#record');
const appMain = document.querySelector('main');
const welcomeLayer = document.querySelector('#welcome-sequence');
const homepageEmbed = new URLSearchParams(window.location.search).has('home-hero');
if (homepageEmbed) {
  welcomeLayer?.remove();
  appMain?.removeAttribute('aria-busy');
  if (appMain) appMain.inert = false;
}
const welcomeStartedAt = performance.now();
let welcomeExitScheduled = false;
function dismissWelcome({failed = false} = {}) {
  if (!welcomeLayer || welcomeExitScheduled) return;
  welcomeExitScheduled = true;
  if (failed) {
    welcomeLayer.querySelector('.welcome-title').textContent = 'O mapa não abriu.';
    welcomeLayer.querySelector('.welcome-copy').textContent = 'Confira os detalhes de carregamento na tela.';
  }
  const minimumDuration = reducedMotion.matches || failed ? 0 : 1450;
  const remaining = Math.max(0, minimumDuration - (performance.now() - welcomeStartedAt));
  window.setTimeout(() => {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      welcomeLayer.classList.add('is-exiting');
      appMain?.removeAttribute('aria-busy');
      if (appMain) appMain.inert = false;
      const removeLayer = () => welcomeLayer.remove();
      welcomeLayer.addEventListener('transitionend', event => {
        if (event.propertyName === 'opacity') removeLayer();
      }, {once: true});
      window.setTimeout(removeLayer, reducedMotion.matches ? 50 : 820);
    }));
  }, remaining);
}
function finishWelcomeWhenReady() {
  if (rotationReady && graphViewportVisible) dismissWelcome();
}
const VADEMECUM_READER_URL = 'https://lucmolero.github.io/vademecum-md/biblioteca/#documento=';
const esc = value => String(value ?? '—').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
const idOf = value => typeof value === 'object' ? value.id : value;
const EDGE_COLORS = {candidate_unverified: '#91836d', validated_deterministically: '#268f67', snapshot_structure: '#71839b'};
const DRAWER_ICONS = {
  law: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 3.75h8l4 4v12.5H6z" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"/><path d="M14 3.75v4h4M9 12h6M9 15.5h6" stroke="currentColor" stroke-width="1.35" stroke-linecap="round"/></svg>',
  reader: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4.5 5.5c2.8-.7 5.3-.2 7.5 1.4v12c-2.2-1.6-4.7-2.1-7.5-1.4zM19.5 5.5c-2.8-.7-5.3-.2-7.5 1.4v12c2.2-1.6 4.7-2.1 7.5-1.4z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path class="drawer-icon-travel" d="M7.5 9h2m-2 3h2m5-3h2m-2 3h2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  source: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 19.5h16M6 19V9l6-4 6 4v10M9 19v-5h6v5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><path class="drawer-icon-travel" d="M3.5 9.5 12 4l8.5 5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path class="drawer-icon-travel" d="M9 6s6 4.4189 6 6-6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  cite: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="5" cy="18.5" r="2" stroke="currentColor" stroke-width="1.6"/><circle cx="18.5" cy="5.5" r="2" stroke="currentColor" stroke-width="1.6"/><path class="drawer-icon-travel" d="M7 17 17 7m-5 0h5v5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  cited: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="19" cy="18.5" r="2" stroke="currentColor" stroke-width="1.6"/><circle cx="5.5" cy="5.5" r="2" stroke="currentColor" stroke-width="1.6"/><path class="drawer-icon-travel" d="M7 7 17 17m-5 0h5v-5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  calendar: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="4.5" y="6" width="15" height="14" rx="2" stroke="currentColor" stroke-width="1.3"/><path d="M8 4v4m8-4v4M4.5 10h15" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>'
};
function drawerIcon(name, className = 'drawer-icon') {
  const icon = document.createElement('span');
  icon.className = className;
  icon.innerHTML = DRAWER_ICONS[name] || DRAWER_ICONS.law;
  icon.setAttribute('aria-hidden', 'true');
  return icon;
}
let graph3d, fullNodes = [], fullLinks = [], nodeById = new Map(), linkById = new Map(), incident = new Map(), neighborIndex = new Map(), searchIndex = null, searchPromise = null, firstFit = true, rotationReady = false, reheatFrame = 0, graphFitTimer = 0, drawerGeneration = 0, drawerFrame = 0, drawerCloseTimer = 0, visibleNodes = new Map(), selectedNodeId = null, relatedNodeIds = new Set();
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let graphPageVisible = !document.hidden;
let graphViewportVisible = !homepageEmbed;
const GRAPH_VISIBILITY_MESSAGE = 'vademecum-graph-visibility';
function notifyHomepageGraphReady(error = false) {
  if (!homepageEmbed) return;
  window.parent.postMessage({type: 'vademecum-graph-ready', ready: true, error}, '*');
}
let previousMobileLayout = window.matchMedia('(max-width: 640px)').matches;
// Keep identical geometry, antialiasing and pixel-ratio policy across viewport sizes.
const graphPixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);
let rotationEnabled = !reducedMotion.matches;
let activeTheme = document.body.dataset.theme || 'dark';
function syncGraphActivity() {
  if (!graph3d) return;
  const active = graphPageVisible && graphViewportVisible;
  const controls = graph3d.controls();
  if (!active) {
    if (controls) controls.autoRotate = false;
    graph3d.pauseAnimation?.();
    return;
  }
  graph3d.resumeAnimation?.();
  if (controls) controls.autoRotate = rotationEnabled && rotationReady && !pointerInteractionActive;
}
window.addEventListener('message', event => {
  if (event.source !== window.parent || event.data?.type !== GRAPH_VISIBILITY_MESSAGE || typeof event.data.visible !== 'boolean') return;
  graphViewportVisible = event.data.visible;
  syncGraphActivity();
  finishWelcomeWhenReady();
});
document.addEventListener('visibilitychange', () => {
  graphPageVisible = !document.hidden;
  syncGraphActivity();
});
const graphTooltip = document.createElement('div');
graphTooltip.id = 'graph-tooltip';
graphTooltip.className = 'graph-tooltip';
graphTooltip.setAttribute('role', 'tooltip');
graphTooltip.hidden = true;
document.body.append(graphTooltip);
let graphPointer = {x: 0, y: 0};
let graphTooltipWidth = 0;
let graphTooltipHeight = 0;
let graphTooltipContent = '';
function positionGraphTooltip() {
  if (graphTooltip.hidden) return;
  const margin = 12;
  const offset = 16;
  const left = Math.max(margin, Math.min(graphPointer.x + offset, window.innerWidth - graphTooltipWidth - margin));
  const top = Math.max(margin, Math.min(graphPointer.y + offset, window.innerHeight - graphTooltipHeight - margin));
  graphTooltip.style.transform = `translate3d(${left}px, ${top}px, 0)`;
}
function hideGraphTooltip() {
  graphTooltip.hidden = true;
  graphTooltipContent = '';
}
function showGraphTooltip(title, meta, target) {
  const contentKey = JSON.stringify([title || 'Norma sem título', meta || '', target || '']);
  if (contentKey === graphTooltipContent) {
    graphTooltip.hidden = false;
    positionGraphTooltip();
    return;
  }
  const titleLine = document.createElement('div');
  titleLine.className = 'graph-tooltip-title';
  titleLine.textContent = title || 'Norma sem título';
  if (target) {
    const direction = document.createElement('span');
    direction.className = 'graph-tooltip-direction';
    direction.textContent = ' → ';
    titleLine.append(direction, document.createTextNode(target));
  }
  graphTooltip.replaceChildren(titleLine);
  if (meta) {
    const metadata = document.createElement('div');
    metadata.className = 'graph-tooltip-meta';
    metadata.textContent = meta;
    graphTooltip.append(metadata);
  }
  graphTooltip.hidden = false;
  graphTooltipContent = contentKey;
  const rect = graphTooltip.getBoundingClientRect();
  graphTooltipWidth = rect.width;
  graphTooltipHeight = rect.height;
  positionGraphTooltip();
}
root.addEventListener('pointermove', event => {
  graphPointer = {x: event.clientX, y: event.clientY};
  positionGraphTooltip();
}, {passive: true});
root.addEventListener('pointerleave', hideGraphTooltip, {passive: true});
window.addEventListener('blur', hideGraphTooltip);
let interactionSlow = false, interactionTimer = 0, rotationRampFrame = 0, rotationRampEndTime = 0, pointerInteractionActive = false;
const NORMAL_ROTATION_SPEED = .42;
const INTERACTION_ROTATION_SPEED = .14;
const ROTATION_RAMP_HALF_MS = 520;
const ROTATION_IDLE_DELAY_MS = 0;
let rotationSpeed = NORMAL_ROTATION_SPEED;
let rotationTargetSpeed = NORMAL_ROTATION_SPEED;
let contextHeightCleanupTimer = 0;

function setContextExpanded(expanded) {
  const wasCompact = detailsPanel.classList.contains('context-compact');
  if (expanded && wasCompact) {
    clearTimeout(contextHeightCleanupTimer);
    const startHeight = detailsPanel.getBoundingClientRect().height;
    const mobile = window.matchMedia('(max-width: 640px)').matches;
    const expandedLimit = Math.min(window.innerHeight * (mobile ? .56 : .60), mobile ? 500 : 560);
    detailsPanel.style.height = `${startHeight}px`;
    detailsPanel.style.removeProperty('max-height');
    detailsPanel.classList.remove('context-compact');
    const targetHeight = Math.min(detailsPanel.scrollHeight, expandedLimit);
    detailsPanel.style.height = `${startHeight}px`;
    detailsPanel.getBoundingClientRect();
    requestAnimationFrame(() => { detailsPanel.style.height = `${targetHeight}px`; });
    contextHeightCleanupTimer = setTimeout(() => {
      detailsPanel.style.removeProperty('height');
      contextHeightCleanupTimer = 0;
    }, reducedMotion.matches ? 0 : 780);
  } else {
    detailsPanel.classList.toggle('context-compact', !expanded);
    if (!expanded) requestAnimationFrame(sizeCompactCard);
  }
  contextExpand?.setAttribute('aria-expanded', String(expanded));
  const label = `${expanded ? 'Recolher' : 'Expandir'} detalhes; arraste para baixo para fechar`;
  contextExpand?.setAttribute('aria-label', label);
  contextExpand?.setAttribute('title', expanded ? 'Recolher detalhes ou arraste para baixo para fechar' : 'Expandir detalhes ou arraste para baixo para fechar');
}
function sizeCompactCard() {
  if (detailsPanel.hidden || !detailsPanel.classList.contains('context-compact')) return;
  const mobile = window.matchMedia('(max-width: 640px)').matches;
  const expandedLimit = Math.min(window.innerHeight * (mobile ? .56 : .60), mobile ? 500 : 560);
  // Measure the full card before applying the compact viewport, then show its first half.
  detailsPanel.classList.remove('context-compact');
  const fullCardHeight = Math.min(detailsPanel.scrollHeight, expandedLimit);
  detailsPanel.classList.add('context-compact');
  detailsPanel.style.setProperty('--context-compact-height', `${Math.ceil(fullCardHeight * .5)}px`);
}

async function readGzipJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw Error(`Falha ao carregar ${path} (${response.status})`);
  // Some static servers transparently decode .gz assets before fetch exposes
  // the body. In that case a second DecompressionStream fails on valid JSON.
  if (response.headers.get('content-encoding')?.toLowerCase().includes('gzip')) return response.json();
  if (!('DecompressionStream' in window)) throw Error('Este navegador não oferece suporte à leitura gzip necessária ao grafo.');
  return await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json();
}
function addIncident(id, edge) {
  let edges = incident.get(id);
  if (!edges) incident.set(id, edges = []);
  edges.push(edge);
}
function nodeVisible(node) {
  return Boolean(node);
}
function zoomGraphToFit(duration = 850, padding = 50, onComplete) {
  if (!graph3d || !fullNodes.length || root.clientWidth < 1 || root.clientHeight < 1) return false;
  const controls = graph3d.controls();
  if (controls) controls.autoRotate = false;
  let fitPadding = padding;
  if (homepageEmbed) {
    // Keep the homepage's closer composition in the same camera tween instead
    // of chaining zoomToFit() and a second cameraPosition() animation.
    const fitScale = .62;
    fitPadding = Math.round(root.clientHeight / 2 * (1 - (1 - 2 * padding / root.clientHeight) / fitScale));
  }
  graph3d.zoomToFit(duration, fitPadding);
  setTimeout(() => {
    if (rotationReady && rotationEnabled && graphPageVisible && graphViewportVisible && controls) controls.autoRotate = true;
    onComplete?.();
    syncGraphActivity();
  }, Math.max(0, duration) + 40);
  return true;
}
function fitInitialGraph() {
  if (!firstFit || !graph3d) return;
  clearTimeout(graphFitTimer);
  graphFitTimer = 0;
  firstFit = false;
  const applied = zoomGraphToFit(1100, 50, () => {
    rotationReady = true;
    syncGraphActivity();
    notifyHomepageGraphReady();
    finishWelcomeWhenReady();
  });
  if (!applied) {
    firstFit = true;
    scheduleGraphFit(300);
  }
}
function scheduleGraphFit(delay = 1100) {
  clearTimeout(graphFitTimer);
  graphFitTimer = setTimeout(() => {
    graphFitTimer = 0;
    if (firstFit) fitInitialGraph();
    else zoomGraphToFit(850, 50);
  }, delay);
}
function updateGraph({reheat = false, fit = false} = {}) {
  if (!graph3d) return;
  // Keep one stable renderer population until filters explicitly change.
  const nodes = [...visibleNodes.values()].filter(nodeVisible);
  const ids = new Set(nodes.map(node => node.id));
  const edges = fullLinks.filter(edge => ids.has(edge.source) && ids.has(edge.target));
  graph3d.graphData({
    nodes,
    // Evidence remains indexed in fullLinks/linkById; geometry receives only the
    // fields it needs, avoiding a second set of nested occurrence records.
    links: edges.map(edge => ({
      id: edge.id, linkId: edge.id, source: edge.source, target: edge.target,
      relation: edge.relation, state: edge.state, occurrence_count: edge.occurrence_count, curvature: edge.curvature
    }))
  });
  graph3d.linkOpacity(edges.length > 15000 ? .32 : .68);
  if (selectedNodeId && !ids.has(selectedNodeId)) {
    focusNode(null);
    cancelDrawerSections();
    document.querySelector('#details .empty').hidden = false;
    record.replaceChildren();
    document.body.classList.remove('context-open');
    scheduleGraphFit();
  }
  if (selectedNodeId) focusNode(selectedNodeId);
  const focusEdges = selectedNodeId ? edges.filter(edge => edge.source === selectedNodeId || edge.target === selectedNodeId) : [];
  const focusOccurrences = focusEdges.reduce((sum, edge) => sum + (edge.occurrence_count || 1), 0);
  viewCount.textContent = selectedNodeId
    ? `${nodes.length.toLocaleString('pt-BR')} nós · ${relatedNodeIds.size.toLocaleString('pt-BR')} vizinhos · ${focusEdges.length.toLocaleString('pt-BR')} relações · ${focusOccurrences.toLocaleString('pt-BR')} ocorrências`
    : `${nodes.length.toLocaleString('pt-BR')} nós · ${edges.length.toLocaleString('pt-BR')} ligações · somente cita`;
  if (reheat) {
    cancelAnimationFrame(reheatFrame);
    reheatFrame = requestAnimationFrame(() => graph3d?.d3ReheatSimulation());
  }
  if (fit) scheduleGraphFit();
}
function renderDetails(title, fields, sectionLabel = 'Dados da norma') {
  cancelDrawerSections();
  clearTimeout(drawerCloseTimer);
  drawerCloseTimer = 0;
  detailsPanel.classList.remove('drawer-closing');
  detailsPanel.hidden = false;
  document.body.classList.add('context-open');
  detailsPanel.style.removeProperty('max-height');
  setContextExpanded(false);
  detailsPanel.querySelector('.empty').hidden = true;
  const values = new Map(fields);
  const isRelation = sectionLabel.startsWith('Relação');
  record.dataset.kind = isRelation ? 'relation' : 'norm';
  const fragment = document.createDocumentFragment();
  let revealIndex = 0;
  const reveal = (element, className) => {
    element.className = `${className} drawer-reveal`;
    element.style.setProperty('--reveal-order', revealIndex++);
    return element;
  };
  const textValue = value => typeof value === 'number' ? value.toLocaleString('pt-BR') : typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value ?? '');

  const hero = reveal(document.createElement('section'), 'drawer-hero');
  const heroTop = document.createElement('div');
  heroTop.className = 'drawer-hero-top';
  const eyebrow = document.createElement('span');
  eyebrow.className = 'drawer-eyebrow';
  eyebrow.textContent = isRelation ? 'RELAÇÃO DE CITAÇÃO' : sectionLabel.toUpperCase();
  const heroMark = document.createElement('span');
  heroMark.className = 'drawer-hero-mark';
  heroMark.append(drawerIcon(isRelation ? 'cite' : 'law'));
  heroTop.append(eyebrow, heroMark);
  const heading = document.createElement('h2');
  heading.textContent = isRelation ? 'Citação entre normas' : title;
  hero.append(heroTop, heading);

  if (isRelation) {
    const route = document.createElement('div');
    route.className = 'drawer-route';
    for (const [key, className, labelText] of [
      ['Norma citante', 'route-source', 'NORMA CITANTE'],
      ['Norma citada', 'route-target', 'NORMA CITADA']
    ]) {
      const endpoint = document.createElement('div');
      endpoint.className = `route-endpoint ${className}`;
      const label = document.createElement('span');
      label.className = 'route-label';
      label.textContent = labelText;
      const name = document.createElement('strong');
      name.textContent = textValue(values.get(key));
      endpoint.append(label, name);
      route.append(endpoint);
      if (key === 'Norma citante') {
        const arrow = document.createElement('div');
        arrow.className = 'route-arrow';
        arrow.append(drawerIcon('arrow'), document.createTextNode('cita'));
        route.append(arrow);
      }
    }
    hero.append(route);
  } else {
    const subtitle = [values.get('Espécie normativa'), values.get('Jurisdição'), values.get('Data de publicação')]
      .filter(value => value !== undefined && value !== null && value !== '').map(textValue).join(' · ');
    if (subtitle) {
      const meta = document.createElement('p');
      meta.className = 'drawer-subtitle';
      meta.textContent = subtitle;
      hero.append(meta);
    }
  }
  fragment.append(hero);

  const actions = fields.filter(([key, value]) => value && typeof value === 'object' && value.href);
  if (actions.length) {
    const actionGroup = reveal(document.createElement('div'), 'drawer-actions');
    for (const [key, value] of actions) {
      let href;
      try { href = new URL(value.href, location.href); } catch { href = null; }
      if (!href || !['http:', 'https:'].includes(href.protocol)) continue;
      const link = document.createElement('a');
      link.className = `drawer-action${key.includes('Leitor') ? ' drawer-action-primary' : ''}`;
      link.href = href.href;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      const accessibleName = key.includes('Leitor') ? 'Abrir no leitor do VadeMecum MD' : 'Abrir fonte oficial';
      const icon = drawerIcon(key.includes('Leitor') ? 'reader' : 'source');
      const copy = document.createElement('span');
      copy.className = 'drawer-action-copy';
      const name = document.createElement('strong');
      name.textContent = key.includes('Leitor') ? 'Leitor' : 'Fonte oficial';
      copy.append(name);
      link.setAttribute('aria-label', `${accessibleName}: ${value.label || key}`);
      link.title = accessibleName;
      link.append(icon, copy);
      actionGroup.append(link);
    }
    if (actionGroup.childElementCount) fragment.append(actionGroup);
  }

  const technicalKeys = new Set(['ID neste grafo', 'IRI na fonte', 'Identidade no catálogo', 'Grupo de organização', 'Caminho no snapshot VadeMecum', 'Fonte do registro acadêmico']);
  const technicalValues = fields.filter(([key, value]) => technicalKeys.has(key) && value !== undefined && value !== null && value !== '');
  const relationValues = fields.filter(([key, value]) => !['Norma citante', 'Norma citada', 'Sentido no grafo'].includes(key) && value !== undefined && value !== null && value !== '' && !(value && typeof value === 'object' && value.href));

  if (isRelation) {
    const summary = reveal(document.createElement('section'), 'relation-summary');
    const total = document.createElement('strong');
    total.className = 'relation-total';
    total.textContent = textValue(values.get('Afirmações preservadas'));
    const caption = document.createElement('span');
    caption.textContent = 'registros no corpus acadêmico';
    const source = document.createElement('small');
    source.className = 'relation-origin';
    source.textContent = `Fonte: ${textValue(values.get('Fonte do conjunto'))}`;
    const state = document.createElement('span');
    state.className = 'relation-state';
    state.textContent = values.get('Estado da relação') === 'Candidata · não verificada em fonte oficial'
      ? 'Não verificada em fonte oficial' : textValue(values.get('Estado da relação'));
    summary.append(total, caption, source, state);
    fragment.append(summary);
  }

  if (isRelation && relationValues.length) {
    const disclosure = reveal(document.createElement('details'), 'drawer-technical drawer-relation-meta');
    const summary = document.createElement('summary');
    summary.append(drawerIcon('law'), document.createTextNode('Proveniência e validação'));
    disclosure.append(summary);
    const list = document.createElement('div');
    list.className = 'drawer-technical-list';
    for (const [key, value] of relationValues) {
      const row = document.createElement('div'); row.className = 'drawer-technical-row';
      const label = document.createElement('span'); label.className = 'key'; label.textContent = key;
      const content = document.createElement('code'); content.textContent = textValue(value);
      row.append(label, content); list.append(row);
    }
    disclosure.append(list); fragment.append(disclosure);
  }
  if (technicalValues.length) {
    const disclosure = reveal(document.createElement('details'), 'drawer-technical');
    const summary = document.createElement('summary');
    summary.append(drawerIcon('source'), document.createTextNode(isRelation ? 'Identificadores' : 'Identificação e origem'));
    disclosure.append(summary);
    const list = document.createElement('div');
    list.className = 'drawer-technical-list';
    for (const [key, value] of technicalValues) {
      const row = document.createElement('div');
      row.className = 'drawer-technical-row';
      const label = document.createElement('span');
      label.className = 'key';
      label.textContent = key;
      const content = document.createElement('code');
      content.textContent = textValue(value);
      row.append(label, content);
      list.append(row);
    }
    disclosure.append(list);
    disclosure.addEventListener('toggle', () => {
    });
    fragment.append(disclosure);
  }
  record.replaceChildren(fragment);
}
function appendSnapshotAudit(node) {
  const fields = [
    ['Data de corte', displayDate(node.snapshot_cutoff)],
    ['Status documentado no corte · não verificado após essa data', node.documented_status],
    ['Consolidação registrada', node.consolidation_status === 'consolidada_fonte_oficial' ? 'Consolidada a partir de fonte oficial' : node.consolidation_status],
    ['SHA-256 da fonte', node.source_hash]
  ].filter(([, value]) => value !== undefined && value !== null && value !== '');
  if (!fields.length) return;
  const section = document.createElement('details');
  section.className = 'snapshot-audit drawer-technical drawer-reveal';
  const summary = document.createElement('summary');
  summary.append(drawerIcon('law'), document.createTextNode('Auditoria do snapshot'));
  section.append(summary);
  for (const [labelText, value] of fields) {
    const row = document.createElement('div');
    row.className = 'evidence-field';
    const label = document.createElement('span');
    label.className = 'key';
    label.textContent = labelText;
    const content = document.createElement('code');
    content.textContent = String(value);
    row.append(label, content);
    section.append(row);
  }
  record.append(section);
}
function appendEvidenceRecords(occurrences, totalCount = occurrences.length) {
  const collection = document.createElement('details');
  collection.className = 'evidence-collection drawer-reveal';
  collection.style.setProperty('--reveal-order', 5);
  const summary = document.createElement('summary');
  const summaryLabel = document.createElement('span');
  summaryLabel.append(drawerIcon('source'));
  summaryLabel.setAttribute('aria-label', 'Registros de origem');
  summaryLabel.title = 'Registros de origem';
  const summaryText = document.createElement('span');
  summaryText.className = 'disclosure-label';
  summaryText.textContent = 'Registros de origem';
  const summaryCount = document.createElement('span');
  summaryCount.className = 'disclosure-count';
  summaryCount.textContent = totalCount.toLocaleString('pt-BR');
  summary.append(summaryLabel, summaryText, summaryCount);
  collection.append(summary);
  const list = document.createElement('div');
  list.className = 'evidence-list';
  collection.append(list);
  const progress = document.createElement('p');
  progress.className = 'connection-note';
  collection.append(progress);
  const more = document.createElement('button');
  more.type = 'button';
  more.className = 'utility evidence-more';
  more.classList.add('drawer-icon-button');
  more.append(drawerIcon('plus'));
  more.setAttribute('aria-label', 'Carregar mais registros');
  more.title = more.getAttribute('aria-label');
  collection.append(more);
  let shown = 0;
  function addField(card, labelText, value) {
    if (value === undefined || value === null || value === '') return;
    const row = document.createElement('div');
    row.className = 'evidence-field';
    const label = document.createElement('span');
    label.className = 'key';
    label.textContent = labelText;
    const content = document.createElement('code');
    content.textContent = String(value);
    row.append(label, content);
    card.append(row);
  }
  function showMore() {
    const batch = occurrences.slice(shown, shown + 5);
    for (const occurrence of batch) {
      const reference = occurrence.source_record_ref || {};
      const isInverse = occurrence.orientation_in_view === 'inverse_of_cited_by';
      const card = document.createElement('article');
      card.className = 'evidence-card drawer-row-reveal';
      card.style.setProperty('--row-order', batch.indexOf(occurrence));
      const title = document.createElement('h3');
      title.textContent = `${isInverse ? 'Orientada a partir de “cited_by”' : 'Afirmação “cites”'} · ${occurrence.predicate || 'predicado sem rótulo'}`;
      card.append(title);
      const originalSource = occurrence.source_iri || occurrence.rdf_source;
      const originalTarget = occurrence.target_iri || occurrence.rdf_target;
      addField(card, 'Direção no registro de origem', `${originalSource || 'origem não informada'} —[${occurrence.predicate || '?'}]→ ${originalTarget || 'alvo não informado'}`);
      addField(card, 'Arquivo do corpus', reference.path);
      addField(card, 'Linha de origem', occurrence.source_line ?? reference.source_line);
      addField(card, 'Índice do registro', reference.record_index);
      addField(card, 'ID da afirmação', occurrence.assertion_id);
      addField(card, 'SHA-256 do snapshot', reference.sha256);
      addField(card, 'Estado da afirmação', relationStateLabel(occurrence.state));
      if (occurrence.quarantine_reason) {
        const reason = occurrence.quarantine_reason === 'relacao_academica_sem_prova_oficial_independente'
          ? 'Sem prova oficial independente.' : occurrence.quarantine_reason;
        addField(card, 'Motivo de quarentena', reason);
      }
      list.append(card);
    }
    shown += batch.length;
    progress.textContent = shown < occurrences.length ? `${shown} / ${occurrences.length}` : '';
    more.hidden = shown >= occurrences.length;
  }
  more.addEventListener('click', showMore);
  collection.addEventListener('toggle', () => {
    if (collection.open && !shown) showMore();
  });
  if (!occurrences.length) {
    progress.textContent = '';
    more.hidden = true;
  }
  record.append(collection);
}
function displayDate(value) {
  if (!value) return value;
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return String(value);
  const [year, month, day] = match.slice(1).map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return String(value);
  return new Intl.DateTimeFormat('pt-BR', {timeZone: 'UTC'}).format(date);
}
function relationStateLabel(state) {
  if (state === 'candidate_unverified') return 'Candidata · não verificada em fonte oficial';
  if (state === 'validated_deterministically') return 'Validada por regra determinística';
  if (state === 'snapshot_structure') return 'Relação estrutural do snapshot';
  return state || 'Não informado';
}
function cancelDrawerSections() {
  drawerGeneration++;
  if (drawerFrame) cancelAnimationFrame(drawerFrame);
  drawerFrame = 0;
}
function scheduleDrawerSections(sections) {
  // There are only two directional groups, each capped to eight initial rows.
  // Render both together so the drawer never appears half empty while waiting
  // for another animation frame (which browsers may throttle in background tabs).
  const generation = drawerGeneration;
  for (const [connections, title] of sections) {
    if (generation !== drawerGeneration) return;
    appendConnectionSection(connections, title);
  }
}
function colorForNode(node) {
  if (activeTheme === 'light') return node.kind === 'dispositivo' ? '#496ca5' : node.kind === 'ato' ? '#168f82' : '#a96d25';
  return node.kind === 'dispositivo' ? '#84aaff' : node.kind === 'ato' ? '#43d9c2' : '#f4b64b';
}
function colorForLink(edge) {
  if (activeTheme === 'light') return EDGE_COLORS[edge.state] || '#a96d25';
  return edge.state === 'validated_deterministically' ? '#57d6a0' : edge.state === 'snapshot_structure' ? '#90a3ba' : '#a99a80';
}
function nodeValueByDegree(node) {
  const degree = Math.max(0, Number(node.degree) || 0);
  // A logarithmic size scale keeps hubs distinct without letting them engulf
  // neighboring nodes when the user zooms into a dense cluster.
  const value = Math.max(1, Math.min(7, 1 + Math.log2(degree + 1)));
  return value;
}
function setRotation(enabled) {
  rotationEnabled = Boolean(enabled);
  if (!rotationEnabled) {
    clearTimeout(interactionTimer);
    cancelAnimationFrame(rotationRampFrame);
    interactionSlow = false;
    rotationTargetSpeed = rotationSpeed;
    rotationRampEndTime = 0;
  }
  const controls = graph3d?.controls();
  if (controls) {
    controls.autoRotate = rotationEnabled && rotationReady && graphPageVisible && graphViewportVisible && !pointerInteractionActive;
    controls.autoRotateSpeed = rotationSpeed;
  }
  if (rotationEnabled && graphPageVisible && graphViewportVisible) transitionRotationSpeed(interactionSlow ? INTERACTION_ROTATION_SPEED : NORMAL_ROTATION_SPEED, ROTATION_RAMP_HALF_MS);
  motionHint.textContent = rotationEnabled
    ? 'Rotação suave · selecione uma norma para ver relações'
    : 'Movimento reduzido · selecione uma norma para ver relações';
}
function setTheme(theme) {
  const nextTheme = theme === 'light' ? 'light' : 'dark';
  if (nextTheme === activeTheme) return;
  const applyTheme = () => {
    activeTheme = nextTheme;
    document.body.dataset.theme = activeTheme;
    document.querySelector('meta[name="theme-color"]').content = activeTheme === 'dark' ? '#05070a' : '#f4f4f1';
    const nextLabel = activeTheme === 'dark' ? 'Mudar para tema claro' : 'Mudar para tema escuro';
    themeToggle.setAttribute('aria-label', nextLabel);
    themeToggle.title = nextLabel;
    themeToggle.setAttribute('aria-pressed', String(activeTheme === 'light'));
    themeToggle.querySelector('svg').innerHTML = activeTheme === 'dark'
      ? '<circle cx="12" cy="12" r="3.8" stroke="currentColor" stroke-width="1.5"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
      : '<path d="M20.4 15.4A8.5 8.5 0 0 1 8.6 3.6 8.5 8.5 0 1 0 20.4 15.4Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>';
    const graphBackground = activeTheme === 'dark' ? '#05070a' : '#f4f4f1';
    if (graph3d) graph3d.backgroundColor(graphBackground).nodeColor(colorForNode).linkColor(colorForLink).linkDirectionalArrowColor(colorForLink).refresh();
  };
  if (document.startViewTransition && !reducedMotion.matches) {
    try { document.startViewTransition(applyTheme); }
    catch { applyTheme(); }
  } else applyTheme();
}
function transitionRotationSpeed(target, duration, onComplete) {
  if (Math.abs(target - rotationTargetSpeed) < .0001) return;
  rotationTargetSpeed = target;
  cancelAnimationFrame(rotationRampFrame);
  const startSpeed = rotationSpeed;
  const startTime = performance.now();
  const speedRange = Math.max(NORMAL_ROTATION_SPEED - INTERACTION_ROTATION_SPEED, .001);
  const transitionDuration = Math.max(280, duration * Math.min(1, Math.abs(target - startSpeed) / speedRange));
  rotationRampEndTime = startTime + transitionDuration;
  function step(now) {
    const progress = Math.min(1, (now - startTime) / transitionDuration);
    if (target < startSpeed) {
      const remaining = 1 - progress;
      rotationSpeed = target + (startSpeed - target) * remaining ** 2;
    } else {
      rotationSpeed = startSpeed + (target - startSpeed) * progress ** 2;
    }
    const controls = graph3d?.controls();
    if (controls) controls.autoRotateSpeed = rotationSpeed;
    if (progress < 1) rotationRampFrame = requestAnimationFrame(step);
    else {
      rotationSpeed = target;
      rotationRampFrame = 0;
      rotationRampEndTime = 0;
      onComplete?.();
    }
  }
  rotationRampFrame = requestAnimationFrame(step);
}
function markGraphInteraction() {
  if (window.matchMedia('(max-width: 640px)').matches) document.body.classList.add('graph-engaged');
  if (!rotationEnabled || pointerInteractionActive) return;
  interactionSlow = true;
  motionHint.textContent = 'Interação · rotação desacelerando';
  clearTimeout(interactionTimer);
  const controls = graph3d?.controls();
  if (controls) controls.autoRotate = true;
  transitionRotationSpeed(INTERACTION_ROTATION_SPEED, ROTATION_RAMP_HALF_MS, () => {
    if (interactionSlow) motionHint.textContent = 'Interação · rotação estabilizada';
  });
  const resumeRotation = () => {
    interactionSlow = false;
    motionHint.textContent = 'Retomando a rotação suave';
    transitionRotationSpeed(NORMAL_ROTATION_SPEED, ROTATION_RAMP_HALF_MS, () => {
      if (rotationEnabled && !interactionSlow) {
        motionHint.textContent = 'Rotação suave · selecione uma norma para explorar';
      }
    });
  };
  interactionTimer = setTimeout(() => {
    const rampRemaining = rotationTargetSpeed === INTERACTION_ROTATION_SPEED
      ? Math.max(0, rotationRampEndTime - performance.now())
      : 0;
    if (rampRemaining > 0) interactionTimer = setTimeout(resumeRotation, rampRemaining);
    else resumeRotation();
  }, ROTATION_IDLE_DELAY_MS);
}
function beginGraphPointerInteraction() {
  if (window.matchMedia('(max-width: 640px)').matches) document.body.classList.add('graph-engaged');
  if (!rotationEnabled || pointerInteractionActive) return;
  pointerInteractionActive = true;
  interactionSlow = true;
  clearTimeout(interactionTimer);
  transitionRotationSpeed(INTERACTION_ROTATION_SPEED, ROTATION_RAMP_HALF_MS);
  motionHint.textContent = 'Interação · órbita desacelerando';
}
function endGraphPointerInteraction() {
  if (!pointerInteractionActive) return;
  pointerInteractionActive = false;
  if (!rotationEnabled) return;
  interactionSlow = false;
  motionHint.textContent = 'Retomando a rotação suave';
  transitionRotationSpeed(NORMAL_ROTATION_SPEED, ROTATION_RAMP_HALF_MS, () => {
    if (rotationEnabled && !interactionSlow) {
      motionHint.textContent = 'Rotação suave · selecione uma norma para explorar';
    }
  });
}
function networkMetrics() {
  const visited = new Set();
  let components = 0;
  let isolates = 0;
  for (const node of fullNodes) {
    const id = node.id;
    const edges = incident.get(id) || [];
    if (!edges.length) isolates++;
    if (visited.has(id)) continue;
    components++;
    const stack = [id];
    visited.add(id);
    while (stack.length) {
      const current = stack.pop();
      for (const edge of incident.get(current) || []) {
        const neighbor = edge.source === current ? edge.target : edge.source;
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          stack.push(neighbor);
        }
      }
    }
  }
  return {components, isolates};
}
function focusNode(id) {
  selectedNodeId = id || null;
  relatedNodeIds = new Set();
  if (selectedNodeId) {
    const connections = getNeighborIndex(selectedNodeId);
    for (const neighborId of connections?.neighborIds || []) {
      if (nodeVisible(nodeById.get(neighborId))) relatedNodeIds.add(neighborId);
    }
  }
  if (selectedNodeId) {
    const nodeCount = [...visibleNodes.values()].filter(nodeVisible).length;
    const connections = getNeighborIndex(selectedNodeId);
    const edgeCount = (connections?.outgoing.relationCount || 0) + (connections?.incoming.relationCount || 0);
    const occurrenceCount = (connections?.outgoing.occurrenceCount || 0) + (connections?.incoming.occurrenceCount || 0);
    viewCount.textContent = `${nodeCount.toLocaleString('pt-BR')} nós · ${relatedNodeIds.size.toLocaleString('pt-BR')} vizinhos · ${edgeCount.toLocaleString('pt-BR')} relações · ${occurrenceCount.toLocaleString('pt-BR')} ocorrências`;
  }
}
function indexConnections(edges, neighborFor) {
  const grouped = new Map();
  for (const edge of edges) {
    const neighborId = neighborFor(edge);
    const item = grouped.get(neighborId) || {id: neighborId, count: 0, node: nodeById.get(neighborId)};
    item.count += edge.occurrence_count || 1;
    grouped.set(neighborId, item);
  }
  const rows = [...grouped.values()].sort((a, b) => (b.node?.degree || 0) - (a.node?.degree || 0) || (a.node?.label || a.id).localeCompare(b.node?.label || b.id, 'pt-BR'));
  return {
    rows,
    neighborCount: rows.length,
    relationCount: edges.length,
    occurrenceCount: edges.reduce((sum, edge) => sum + (edge.occurrence_count || 1), 0)
  };
}
function indexNodeNeighbors(node) {
    const edges = incident.get(node.id) || [];
    const outgoing = edges.filter(edge => edge.source === node.id);
    const incoming = edges.filter(edge => edge.target === node.id);
    const outgoingIndex = indexConnections(outgoing, edge => edge.target);
    const incomingIndex = indexConnections(incoming, edge => edge.source);
    const neighborIds = [...new Set([...outgoingIndex.rows, ...incomingIndex.rows].map(row => row.id))];
    return {
      outgoing: outgoingIndex,
      incoming: incomingIndex,
      neighborIds,
      neighborCount: neighborIds.length
    };
}
function getNeighborIndex(id) {
  let connections = neighborIndex.get(id);
  if (!connections) {
    const node = nodeById.get(id);
    if (node) {
      connections = indexNodeNeighbors(node);
      neighborIndex.set(id, connections);
    }
  }
  return connections;
}
function buildNeighborIndex() {
  for (const node of fullNodes) {
    if (!neighborIndex.has(node.id)) neighborIndex.set(node.id, indexNodeNeighbors(node));
  }
}
function appendConnectionSection(connections, title) {
  const {rows, neighborCount, relationCount, occurrenceCount} = connections;
  const section = document.createElement('details');
  section.className = `connection-group drawer-reveal ${title === 'Cita' ? 'connection-outgoing' : 'connection-incoming'}`;
  section.dataset.neighborCount = String(neighborCount);
  section.style.setProperty('--reveal-order', title === 'Cita' ? 3 : 4);
  const summary = document.createElement('summary');
  const direction = document.createElement('span');
  direction.className = 'connection-direction';
  direction.append(drawerIcon(title === 'Cita' ? 'cite' : 'cited'));
  const summaryText = document.createElement('span');
  summaryText.className = 'connection-summary-text';
  const name = document.createElement('strong');
  name.textContent = title;
  const counts = document.createElement('small');
  counts.textContent = `${neighborCount.toLocaleString('pt-BR')} normas · ${relationCount.toLocaleString('pt-BR')} relações · ${occurrenceCount.toLocaleString('pt-BR')} registros`;
  summaryText.append(name, counts);
  summary.append(direction, summaryText);
  summary.setAttribute('aria-label', `${title}: ${neighborCount} normas, ${relationCount} relações, ${occurrenceCount} registros do corpus`);
  section.append(summary);
  const list = document.createElement('div');
  list.className = 'connection-list';
  section.append(list);
  const note = document.createElement('p');
  note.className = 'connection-note';
  section.append(note);
  let shown = 0;
  function showMore() {
    for (const item of rows.slice(shown, shown + 8)) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'connection';
      button.dataset.nodeId = item.id;
      button.style.setProperty('--row-order', Math.min(shown + list.childElementCount, 8));
      button.title = item.node?.label || item.id;
      const name = document.createElement('span');
      name.textContent = item.node?.label || item.id;
      const count = document.createElement('span');
      count.className = 'connection-count';
      count.textContent = `${item.count.toLocaleString('pt-BR')} registros`;
      count.title = `${item.count} afirmação(ões) preservada(s) no corpus acadêmico`;
      const copy = document.createElement('span');
      copy.className = 'connection-copy';
      copy.append(name);
      const arrow = drawerIcon('arrow', 'connection-open');
      arrow.setAttribute('aria-hidden', 'true');
      button.append(copy, count, arrow);
      button.addEventListener('click', () => openNorm(item.id));
      list.append(button);
    }
    shown = Math.min(shown + 8, rows.length);
    note.textContent = shown < rows.length ? `Exibindo ${shown} de ${rows.length} normas.` : '';
    more.hidden = shown >= rows.length;
  }
  const more = document.createElement('button');
  more.type = 'button';
  more.className = 'utility drawer-more';
  more.textContent = 'Ver mais 8 normas';
  more.hidden = true;
  more.addEventListener('click', showMore);
  section.append(more);
  section.addEventListener('toggle', () => {
    if (section.open && shown === 0 && rows.length) showMore();
  });
  if (!rows.length) note.textContent = title === 'Cita' ? 'Esta norma não cita outras normas neste recorte.' : 'Nenhuma norma a cita neste recorte.';
  record.append(section);
}
function openNorm(id, interactionAlreadyMarked = false) {
  if (!interactionAlreadyMarked) markGraphInteraction();
  const node = nodeById.get(id);
  if (!node) return;
  const connections = getNeighborIndex(id) || {outgoing: indexConnections([], edge => edge.target), incoming: indexConnections([], edge => edge.source)};
  const {outgoing, incoming} = connections;
  focusNode(id);
  const identityStatus = node.identity_resolution?.status === 'catalogued_vademecum'
    ? 'Identidade catalogada no snapshot do VadeMecum MD'
    : node.identity_resolution?.status === 'unresolved'
      ? 'Identidade não resolvida contra o catálogo do VadeMecum MD'
      : node.identity_resolution?.status;
  renderDetails(node.label || node.source_label || node.id, [
    ['Acervo', node.kind === 'ato' ? 'VadeMecum MD' : 'Corpus acadêmico · norma externa'],
    ['Espécie normativa', node.normalized_type_label || node.type],
    ['Número', node.normalized_number || node.number],
    ['Jurisdição', node.normalized_jurisdiction === 'BR' ? 'Brasil (BR)' : node.normalized_jurisdiction],
    ['Data de publicação', displayDate(node.normalized_publication_date || node.source_publication_date || node.publication_date)],
    ...(node.kind === 'ato' ? [['Leitor VadeMecum MD', {href: `${VADEMECUM_READER_URL}${encodeURIComponent(node.id)}`, label: 'Abrir esta norma no leitor'}]] : []),
    ['Fonte oficial', node.official_url || node.official_sources?.[0] ? {href: node.official_url || node.official_sources[0], label: 'Abrir fonte oficial'} : undefined],
    ['ID neste grafo', node.id], ['IRI na fonte', node.external_iri],
    ['Identidade no catálogo', identityStatus],
    ['Grupo de organização', node.cluster],
    [node.kind === 'ato' ? 'Caminho no snapshot VadeMecum' : 'Fonte do registro acadêmico', node.kind === 'ato' ? node.source_path : 'br-legal-kg']
  ], node.kind === 'ato' ? 'Ato do VadeMecum MD' : 'Norma externa');
  scheduleDrawerSections([[outgoing, 'Cita'], [incoming, 'Citado por']]);
  if (node.kind === 'ato') appendSnapshotAudit(node);
}
function centerOnSearchResult(id) {
  const node = nodeById.get(id);
  if (!node || !graph3d || ![node.x, node.y, node.z].every(Number.isFinite)) return;
  const camera = graph3d.camera().position;
  let dx = camera.x - node.x;
  let dy = camera.y - node.y;
  let dz = camera.z - node.z;
  const currentDistance = Math.hypot(dx, dy, dz) || 1;
  dx /= currentDistance;
  dy /= currentDistance;
  dz /= currentDistance;
  // Preserve the user's current viewing direction while moving the selected
  // norm into the center of the viewport at a useful, readable scale.
  const distance = Math.min(240, Math.max(145, currentDistance * .3));
  graph3d.cameraPosition(
    {x: node.x + dx * distance, y: node.y + dy * distance, z: node.z + dz * distance},
    {x: node.x, y: node.y, z: node.z},
    reducedMotion.matches ? 0 : 950
  );
  motionHint.textContent = 'Norma localizada · arraste para orbitar e use o scroll para ajustar a escala';
}
function showCitation(edge, interactionAlreadyMarked = false) {
  if (!interactionAlreadyMarked) markGraphInteraction();
  const sourceId = idOf(edge.source);
  focusNode(sourceId);
  const source = nodeById.get(sourceId);
  const target = nodeById.get(idOf(edge.target));
  const occurrences = edge.occurrences || [];
  const state = relationStateLabel(edge.state);
  renderDetails('Relação de citação', [
    ['Norma citante', source?.label || idOf(edge.source)],
    ['Norma citada', target?.label || idOf(edge.target)],
    ['Sentido no grafo', `${source?.label || idOf(edge.source)} → ${target?.label || idOf(edge.target)}`],
    ['Afirmações preservadas', edge.occurrence_count || occurrences.length],
    ['Predicados originais', Object.entries(edge.original_predicates || {}).map(([predicate, count]) => `${predicate} ×${count}`).join(' · ')],
    ['Fonte do conjunto', edge.candidate_source || 'br-legal-kg'],
    ['Estado da relação', state]
  ], 'Relação · citação');
  appendEvidenceRecords(occurrences, edge.occurrence_count || occurrences.length);
}
function showPanorama(exitMotion = null) {
  if (!detailsPanel.hidden && detailsPanel.classList.contains('drawer-closing')) return;
  focusNode(null);
  cancelDrawerSections();
  clearTimeout(drawerCloseTimer);
  if (!detailsPanel.hidden) {
    detailsPanel.style.setProperty('--context-out-y', `${exitMotion?.distance || 0}px`);
    detailsPanel.style.setProperty('--context-out-opacity', String(exitMotion?.opacity ?? 1));
    detailsPanel.style.setProperty('--context-out-scale', String(exitMotion?.scale ?? 1));
    detailsPanel.classList.add('drawer-closing');
    drawerCloseTimer = setTimeout(() => {
      detailsPanel.hidden = true;
      detailsPanel.classList.remove('drawer-closing');
      detailsPanel.classList.remove('context-compact');
      detailsPanel.style.removeProperty('--context-out-y');
      detailsPanel.style.removeProperty('--context-out-opacity');
      detailsPanel.style.removeProperty('--context-out-scale');
      detailsPanel.querySelector('.empty').hidden = false;
      record.replaceChildren();
      document.body.classList.remove('context-open');
      drawerCloseTimer = 0;
    }, reducedMotion.matches ? 0 : 260);
  } else {
    detailsPanel.querySelector('.empty').hidden = false;
    record.replaceChildren();
    document.body.classList.remove('context-open');
    detailsPanel.classList.remove('context-compact');
  }
  visibleNodes = new Map(fullNodes.map(node => [node.id, node]));
  const occurrences = fullLinks.reduce((sum, edge) => sum + (edge.occurrence_count || 1), 0);
  viewCount.textContent = `${fullNodes.length.toLocaleString('pt-BR')} nós · ${fullLinks.length.toLocaleString('pt-BR')} relações · ${occurrences.toLocaleString('pt-BR')} ocorrências`;
}
function initialize(data) {
  fullNodes = data.nodes;
  fullLinks = data.links;
  nodeById = new Map(fullNodes.map(node => [node.id, node]));
  linkById = new Map(fullLinks.map(edge => [edge.id, edge]));
  const parallel = new Map();
  for (const edge of fullLinks) {
    addIncident(edge.source, edge);
    addIncident(edge.target, edge);
    const key = `${edge.source}\0${edge.target}`;
    const index = parallel.get(key) || 0;
    parallel.set(key, index + 1);
    edge.curvature = index === 0 ? 0 : (index % 2 ? 1 : -1) * (.06 + Math.floor(index / 2) * .018);
  }
  graph3d = new ForceGraph3D(root, {
    controlType: 'orbit',
    rendererConfig: {antialias: true, alpha: true}
  })
    .width(root.clientWidth).height(root.clientHeight)
    .backgroundColor(activeTheme === 'dark' ? '#05070a' : '#f4f4f1').showNavInfo(false)
    .nodeId('id').linkSource('source').linkTarget('target')
    .nodeLabel(() => '')
    .onNodeHover(node => {
      if (!node) return hideGraphTooltip();
      const title = node.label || node.source_label || node.id;
      const type = node.normalized_type_label || node.type || '';
      const typeIsInTitle = type && norm(title).includes(norm(type));
      const meta = [
        !typeIsInTitle && type,
        node.publication_date && displayDate(node.publication_date)
      ].filter(Boolean).join(' · ');
      showGraphTooltip(title, meta);
    })
    .nodeColor(colorForNode).nodeOpacity(.75)
    .nodeResolution(8)
    .nodeVal(nodeValueByDegree)
    .nodeRelSize(3.2)
    .linkLabel(() => '')
    .onLinkHover(edge => {
      if (!edge) return hideGraphTooltip();
      const sourceId = idOf(edge.source);
      const targetId = idOf(edge.target);
      const source = nodeById.get(sourceId);
      const target = nodeById.get(targetId);
      const count = Number(edge.occurrence_count) || 1;
      const state = edge.state === 'candidate_unverified' ? 'Não verificada em fonte oficial' : relationStateLabel(edge.state);
      showGraphTooltip(source?.label || source?.source_label || sourceId, `${count.toLocaleString('pt-BR')} ${count === 1 ? 'ocorrência' : 'ocorrências'} · ${state}`, target?.label || target?.source_label || targetId);
    })
    .linkColor(colorForLink).linkOpacity(.68).linkWidth(1.05)
    .linkCurvature(edge => edge.curvature || 0)
    .linkDirectionalArrowLength(edge => edge.relation !== 'cita' ? 0 : 4.4).linkDirectionalArrowRelPos(.9)
    .linkDirectionalArrowResolution(8).linkDirectionalArrowColor(colorForLink)
    .d3AlphaDecay(.08).d3VelocityDecay(.56)
    .cooldownTicks(48).warmupTicks(4)
    .onEngineStop(() => {
      if (firstFit) fitInitialGraph();
    })
    .onNodeClick(node => openNorm(node.id, true))
    .onBackgroundClick(() => {
      if (selectedNodeId) showPanorama();
    })
    .onLinkClick(link => showCitation(linkById.get(link.linkId) || link, true));
  // The bundled renderer defaults to DPR 2. Capping it preserves sharp output
  // while cutting fragment work on high-density displays, especially phones.
  graph3d.renderer()?.setPixelRatio(graphPixelRatio);
  const charge = graph3d.d3Force('charge');
  if (charge?.distanceMax) charge.distanceMax(250);
  setRotation(rotationEnabled);
  visibleNodes = new Map(fullNodes.map(node => [node.id, node]));
  const metrics = networkMetrics();
  const componentsLabel = `${metrics.components.toLocaleString('pt-BR')} componentes`;
  countBox.textContent = `${data.vademecum_node_count.toLocaleString('pt-BR')} atos VadeMecum · ${data.external_node_count.toLocaleString('pt-BR')} externas · ${data.semantic_pair_count.toLocaleString('pt-BR')} relações · ${data.citation_assertion_count.toLocaleString('pt-BR')} ocorrências · ${componentsLabel}`;
  document.querySelector('#network-summary').textContent = `${metrics.components.toLocaleString('pt-BR')} componentes na rede; ${metrics.isolates.toLocaleString('pt-BR')} atos não têm citação neste recorte. Nós sem ligação permanecem no mapa para tornar a cobertura do acervo visível.`;
  updateGraph({reheat: true});
  // Some browsers keep the force engine alive while the renderer is active.
  // A bounded fallback guarantees a useful initial framing even if its stop
  // callback is delayed; the normal callback still fits as soon as it fires.
  scheduleGraphFit(1800);
  if ('requestIdleCallback' in window) requestIdleCallback(buildNeighborIndex, {timeout: 1200});
  else setTimeout(buildNeighborIndex, 250);
  syncGraphActivity();
}
async function loadSearchIndex() {
  if (searchIndex) return searchIndex;
  if (!searchPromise) searchPromise = readGzipJson('../data/search-index.json.gz?v=audit-1').then(rows => (searchIndex = rows));
  return searchPromise;
}
function showSuggestions(rows) {
  suggestions.replaceChildren();
  for (const [id, label, type, iri, connected] of rows) {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'suggestion';
    item.dataset.nodeId = id;
    item.setAttribute('role', 'option');
    item.innerHTML = `${esc(label)}<small>${esc(type)} · ${esc(id)} · ${connected ? 'no recorte exibido' : 'sem citação direta ao VadeMecum neste snapshot'}</small>`;
    item.addEventListener('click', () => {
      search.value = label;
      suggestions.classList.remove('open');
      if (nodeById.has(id)) {
        openNorm(id);
        centerOnSearchResult(id);
      }
    });
    suggestions.append(item);
  }
  suggestions.classList.toggle('open', rows.length > 0);
}

let timer = 0;
search.addEventListener('input', event => {
  clearTimeout(timer);
  const query = norm(search.value.trim());
  if (query.length < 2) { showSuggestions([]); return; }
  timer = setTimeout(async () => {
    try {
      const rows = await loadSearchIndex();
      showSuggestions(rows.filter(row => norm(`${row[1]} ${row[0]} ${row[3] || ''}`).includes(query)).slice(0, 12));
    } catch (error) { viewCount.textContent = error.message; }
  }, 180);
});
search.addEventListener('keydown', event => {
  if (event.key === 'Enter' && suggestions.classList.contains('open')) {
    event.preventDefault();
    suggestions.querySelector('.suggestion')?.click();
  } else if (event.key === 'ArrowDown' && suggestions.classList.contains('open')) {
    event.preventDefault();
    suggestions.querySelector('.suggestion')?.focus();
  } else if (event.key === 'Escape') {
    const hadOpenSuggestions = suggestions.classList.contains('open');
    suggestions.classList.remove('open');
    if (hadOpenSuggestions) event.stopPropagation();
  }
});
suggestions.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  suggestions.classList.remove('open');
  search.focus({preventScroll: true});
  event.stopPropagation();
});
document.addEventListener('pointerdown', event => {
  if (detailsPanel.hidden || detailsPanel.contains(event.target) || !event.isPrimary || event.button !== 0) return;
  showPanorama();
}, true);
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !detailsPanel.hidden && !suggestions.classList.contains('open')) showPanorama();
});
document.addEventListener('click', event => {
  if (!event.target.closest('.search-wrap')) suggestions.classList.remove('open');
});
themeToggle.addEventListener('click', () => setTheme(activeTheme === 'dark' ? 'light' : 'dark'));
contextExpand?.addEventListener('click', () => {
  setContextExpanded(detailsPanel.classList.contains('context-compact'));
});
let swipeState = null;
const clearEntranceMotion = () => {
  if (!detailsPanel.getAnimations) return;
  for (const animation of detailsPanel.getAnimations()) {
    if (animation.animationName === 'context-card-in') animation.cancel();
  }
};
let skipExpandClick = false;
let skipExpandTimer = 0;
contextExpand?.addEventListener('pointerdown', event => {
  if (event.button !== 0) return;
  clearEntranceMotion();
  clearTimeout(contextHeightCleanupTimer);
  swipeState = {
    pointerId: event.pointerId,
    y: event.clientY,
    distance: 0,
    height: detailsPanel.getBoundingClientRect().height,
    compact: detailsPanel.classList.contains('context-compact')
  };
  contextExpand.setPointerCapture(event.pointerId);
  detailsPanel.classList.add('is-swiping');
});
contextExpand?.addEventListener('pointermove', event => {
  if (!swipeState || swipeState.pointerId !== event.pointerId) return;
  const upwardLimit = Math.min(Math.max(swipeState.height * 1.25, 180), window.innerHeight * .72);
  swipeState.distance = Math.max(-upwardLimit, Math.min(event.clientY - swipeState.y, swipeState.height * .8));
  detailsPanel.classList.toggle('is-swiping-down', swipeState.distance > 0);
  detailsPanel.classList.toggle('is-swiping-up', swipeState.distance < 0);
  const pullScale = 1 - Math.min(Math.abs(swipeState.distance) / swipeState.height, 1) * .024;
  if (swipeState.compact && swipeState.distance < 0) {
    const mobile = window.matchMedia('(max-width: 640px)').matches;
    const expandedLimit = Math.min(window.innerHeight * (mobile ? .56 : .60), mobile ? 500 : 560);
    const dragHeight = Math.min(swipeState.height - swipeState.distance, expandedLimit);
    detailsPanel.style.height = `${dragHeight}px`;
    detailsPanel.style.maxHeight = `${dragHeight}px`;
    detailsPanel.style.transform = '';
    detailsPanel.style.opacity = '1';
  } else if (swipeState.distance >= 0) {
    detailsPanel.style.removeProperty('max-height');
    detailsPanel.style.transform = `translate3d(0, ${swipeState.distance}px, 0) scale(${pullScale})`;
    detailsPanel.style.opacity = String(1 - swipeState.distance / swipeState.height * .4);
  } else {
    detailsPanel.style.removeProperty('max-height');
    detailsPanel.style.transform = '';
    detailsPanel.style.opacity = '1';
  }
});
const finishCardSwipe = (event, cancelled = false) => {
  if (!swipeState || swipeState.pointerId !== event.pointerId) return;
  const {distance, height, compact} = swipeState;
  const opacity = Number(detailsPanel.style.opacity || 1);
  const scale = 1 - Math.min(Math.abs(distance) / height, 1) * .024;
  swipeState = null;
  detailsPanel.classList.remove('is-swiping');
  detailsPanel.classList.remove('is-swiping-down', 'is-swiping-up');
  detailsPanel.style.transform = '';
  detailsPanel.style.opacity = '';
  clearTimeout(skipExpandTimer);
  skipExpandClick = !cancelled && Math.abs(distance) > 12;
  if (skipExpandClick) skipExpandTimer = setTimeout(() => { skipExpandClick = false; }, 500);
  if (!cancelled && distance > Math.max(82, height * .2)) {
    detailsPanel.style.removeProperty('height');
    detailsPanel.style.removeProperty('max-height');
    showPanorama({distance, opacity, scale});
  } else if (!cancelled && distance < -Math.max(48, Math.min(height * .18, 86)) && compact) {
    setContextExpanded(true);
  } else {
    detailsPanel.style.removeProperty('height');
    detailsPanel.style.removeProperty('max-height');
  }
};
contextExpand?.addEventListener('pointerup', event => finishCardSwipe(event));
contextExpand?.addEventListener('pointercancel', event => finishCardSwipe(event, true));
contextExpand?.addEventListener('click', event => {
  if (!skipExpandClick) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  skipExpandClick = false;
  clearTimeout(skipExpandTimer);
}, true);
root.addEventListener('pointerdown', beginGraphPointerInteraction, {passive: true});
root.addEventListener('pointerup', endGraphPointerInteraction, {passive: true});
root.addEventListener('pointercancel', endGraphPointerInteraction, {passive: true});
root.addEventListener('lostpointercapture', endGraphPointerInteraction, {passive: true});
root.addEventListener('wheel', markGraphInteraction, {passive: true});
root.addEventListener('keydown', markGraphInteraction);
reducedMotion.addEventListener?.('change', event => {
  if (event.matches) setRotation(false);
});
window.addEventListener('resize', () => {
  graph3d?.width(root.clientWidth).height(root.clientHeight);
  const mobileLayout = window.matchMedia('(max-width: 640px)').matches;
  if (!detailsPanel.hidden && mobileLayout !== previousMobileLayout) {
    setContextExpanded(!detailsPanel.classList.contains('context-compact'));
  }
  previousMobileLayout = mobileLayout;
});
readGzipJson('../data/explorer.json.gz?v=audit-1').then(initialize).catch(error => {
  notifyHomepageGraphReady(true);
  dismissWelcome({failed: true});
  countBox.textContent = error.message;
  detailsPanel.hidden = false;
  detailsPanel.setAttribute('aria-label', 'Erro de carregamento do grafo');
  const empty = detailsPanel.querySelector('.empty');
  empty.hidden = false;
  empty.innerHTML = `<span class="eyebrow">ERRO DE CARREGAMENTO</span><h2>O mapa não abriu</h2><p>${esc(error.message)}</p>`;
});
