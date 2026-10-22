(() => {
  "use strict";

  const root = document.querySelector("[data-graph-explorer]");
  if (!root) return;

  const svg = root.querySelector("#normative-graph-svg");
  const search = root.querySelector("#graph-search");
  const suggestions = root.querySelector("#graph-search-results");
  const typeFilter = root.querySelector("#graph-relation-filter");
  const directionFilter = root.querySelector("#graph-direction-filter");
  const status = root.querySelector("#graph-explorer-status");
  const title = root.querySelector("#graph-selected-title");
  const meta = root.querySelector("#graph-selected-meta");
  const openLaw = root.querySelector("#graph-open-law");
  const degree = root.querySelector("#graph-selected-degree");
  const connectionTitle = root.querySelector("#graph-connections-title");
  const connectionCount = root.querySelector("#graph-connection-count");
  const connectionList = root.querySelector("#graph-connection-list");
  const showMore = root.querySelector("#graph-show-more");
  const SVG_NS = "http://www.w3.org/2000/svg";
  const PAGE_SIZE = 24;
  const NODE_LIMIT = 18;
  const relationLabels = {
    altera: "altera",
    alterada_por: "é alterada por",
    revoga: "revoga",
    revogada_por: "é revogada por",
    regulamenta: "regulamenta",
    regulamentada_por: "é regulamentada por",
    suspende: "suspende",
    suspensa_por: "tem a eficácia suspensa por",
    retifica: "retifica",
    retificada_por: "é retificada por",
    related_to: "relaciona-se a",
  };

  let nodes = [];
  let byId = new Map();
  let edges = [];
  let focusedId = "";
  let visibleGroups = PAGE_SIZE;
  let groups = [];

  const normalize = (value) => (value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR");

  const relationLabel = (type) => relationLabels[type] || type.replaceAll("_", " ");
  const setSuggestionsVisible = (visible) => {
    suggestions.hidden = !visible;
    search.setAttribute("aria-expanded", String(visible));
  };
  const numberLabel = (node) => node.number && node.year
    ? `${node.type} nº ${node.number}/${node.year}`
    : [node.type, node.number, node.year].filter(Boolean).join(" · ");

  const siteHref = (node) => {
    const destination = new URL(node.href, document.baseURI);
    if (destination.origin !== window.location.origin || !destination.pathname.includes("/generated/laws/")) {
      return "../generated/catalog/";
    }
    return destination.href;
  };

  const groupEdges = (records) => {
    const grouped = new Map();
    records.forEach((edge) => {
      const key = `${edge.source_id}\u0000${edge.type}\u0000${edge.target_id}`;
      if (!grouped.has(key)) grouped.set(key, { ...edge, count: 0 });
      grouped.get(key).count += 1;
    });
    return Array.from(grouped.values()).sort((left, right) => {
      const source = byId.get(left.source_id).label.localeCompare(byId.get(right.source_id).label, "pt-BR");
      if (source) return source;
      const relation = relationLabel(left.type).localeCompare(relationLabel(right.type), "pt-BR");
      return relation || byId.get(left.target_id).label.localeCompare(byId.get(right.target_id).label, "pt-BR");
    });
  };

  const makeSvgElement = (name, attributes = {}) => {
    const element = document.createElementNS(SVG_NS, name);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, String(value)));
    return element;
  };

  const renderSearchResults = () => {
    suggestions.replaceChildren();
    const query = normalize(search.value.trim());
    if (!query) {
      setSuggestionsVisible(false);
      return [];
    }
    const matches = nodes.filter((node) => normalize([
      node.label, node.title, node.id, node.number, node.year, node.type,
    ].join(" ")).includes(query)).slice(0, 8);
    if (!matches.length) {
      const empty = document.createElement("p");
      empty.className = "graph-search-empty";
      empty.textContent = "Nenhum diploma encontrado no índice publicado.";
      suggestions.append(empty);
      setSuggestionsVisible(true);
      return matches;
    }
    matches.forEach((node) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "graph-search-option";
      button.textContent = `${node.label}${numberLabel(node) ? ` · ${numberLabel(node)}` : ""}`;
      button.addEventListener("click", () => {
        search.value = node.label;
        setSuggestionsVisible(false);
        focusNode(node.id, { recordHistory: true, focusAfter: "search" });
      });
      suggestions.append(button);
    });
    setSuggestionsVisible(true);
    return matches;
  };

  const makeNodeButton = (node, x, y, central = false) => {
    const group = makeSvgElement("g", {
      class: `graph-node${central ? " is-central" : ""}`,
      role: "button",
      tabindex: 0,
      "aria-label": `${central ? "Diploma selecionado" : "Percorrer relações de"} ${node.label}`,
      "aria-pressed": central ? "true" : "false",
      "data-node-id": node.id,
      transform: `translate(${x} ${y})`,
    });
    const tooltip = makeSvgElement("title");
    tooltip.textContent = `${node.label} · ${node.id}`;
    const circle = makeSvgElement("circle", { r: central ? 28 : 21 });
    const text = makeSvgElement("text", { y: central ? 48 : 40, "text-anchor": "middle" });
    text.textContent = node.label.length > 23 ? `${node.label.slice(0, 21)}…` : node.label;
    group.append(tooltip, circle, text);
    const select = () => focusNode(node.id, { recordHistory: true, focusAfter: "graph" });
    group.addEventListener("click", select);
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
    return group;
  };

  const renderDiagram = (records) => {
    svg.replaceChildren();
    const marker = makeSvgElement("marker", {
      id: "graph-arrow", markerWidth: 9, markerHeight: 9, refX: 8, refY: 4.5,
      orient: "auto", markerUnits: "strokeWidth",
    });
    marker.append(makeSvgElement("path", { d: "M0 0L9 4.5L0 9Z" }));
    const defs = makeSvgElement("defs");
    defs.append(marker);
    svg.append(defs);

    const focal = byId.get(focusedId);
    const byNeighbor = new Map();
    records.forEach((edge) => {
      const neighborId = edge.source_id === focusedId ? edge.target_id : edge.source_id;
      if (!byNeighbor.has(neighborId)) byNeighbor.set(neighborId, []);
      byNeighbor.get(neighborId).push(edge);
    });
    const ranked = Array.from(byNeighbor, ([id, items]) => ({ id, items }))
      .sort((left, right) => right.items.length - left.items.length
        || byId.get(left.id).label.localeCompare(byId.get(right.id).label, "pt-BR"));
    const visible = ranked.slice(0, NODE_LIMIT);
    const center = { x: 380, y: 225 };
    const points = new Map([[focusedId, center]]);
    visible.forEach(({ id }, index) => {
      const angle = -Math.PI / 2 + (2 * Math.PI * index) / Math.max(visible.length, 1);
      points.set(id, { x: center.x + Math.cos(angle) * 270, y: center.y + Math.sin(angle) * 165 });
    });

    visible.forEach(({ id, items }) => {
      const neighborPoint = points.get(id);
      const directedGroups = groupEdges(items);
      directedGroups.forEach((edge, index) => {
        const sourcePoint = edge.source_id === focusedId ? center : neighborPoint;
        const targetPoint = edge.target_id === focusedId ? center : neighborPoint;
        const dx = targetPoint.x - sourcePoint.x;
        const dy = targetPoint.y - sourcePoint.y;
        const distance = Math.max(Math.hypot(dx, dy), 1);
        const bend = (index - (directedGroups.length - 1) / 2) * 13;
        const controlX = (sourcePoint.x + targetPoint.x) / 2 - (dy / distance) * bend;
        const controlY = (sourcePoint.y + targetPoint.y) / 2 + (dx / distance) * bend;
        const path = makeSvgElement("path", {
          class: "graph-edge",
          d: `M ${sourcePoint.x} ${sourcePoint.y} Q ${controlX} ${controlY} ${targetPoint.x} ${targetPoint.y}`,
          "marker-end": "url(#graph-arrow)",
          "aria-hidden": "true",
        });
        svg.append(path);
      });
    });

    visible.forEach(({ id }) => {
      const point = points.get(id);
      svg.append(makeNodeButton(byId.get(id), point.x, point.y));
    });
    svg.append(makeNodeButton(focal, center.x, center.y, true));

    if (ranked.length > visible.length) {
      const note = makeSvgElement("text", { x: 380, y: 480, class: "graph-svg-note", "text-anchor": "middle" });
      note.textContent = `Visualização: ${visible.length} de ${ranked.length} vizinhos; a lista abaixo mantém todas as relações filtradas.`;
      svg.append(note);
    }
  };

  const renderConnections = (records) => {
    groups = groupEdges(records);
    connectionTitle.textContent = `Relações de ${byId.get(focusedId).label}`;
    connectionCount.textContent = `${records.length} registros · ${groups.length} relações distintas · ${new Set(records.map((edge) => edge.source_id === focusedId ? edge.target_id : edge.source_id)).size} vizinhos`;
    connectionList.replaceChildren();

    const visibleGroups = groups.slice(0, visibleGroupsCount());
    if (!visibleGroups.length) {
      const empty = document.createElement("li");
      empty.className = "graph-empty-state";
      empty.textContent = "Não há relações para este diploma com os filtros selecionados.";
      connectionList.append(empty);
    }
    visibleGroups.forEach((edge) => {
      const item = document.createElement("li");
      item.className = "graph-connection-item";
      const sourceLink = document.createElement("a");
      sourceLink.href = siteHref(byId.get(edge.source_id));
      sourceLink.textContent = byId.get(edge.source_id).label;
      const relation = document.createElement("span");
      relation.className = "graph-connection-type";
      relation.textContent = ` ${relationLabel(edge.type)} → `;
      const targetLink = document.createElement("a");
      targetLink.href = siteHref(byId.get(edge.target_id));
      targetLink.textContent = byId.get(edge.target_id).label;
      item.append(sourceLink, relation, targetLink);
      if (edge.count > 1) {
        const count = document.createElement("span");
        count.className = "graph-edge-count";
        count.textContent = ` · ${edge.count} registros`;
        item.append(count);
      }
      connectionList.append(item);
    });
    showMore.hidden = groups.length <= visibleGroups.length;
    showMore.textContent = `Mostrar mais relações (${groups.length - visibleGroups.length} restantes)`;
  };

  const visibleGroupsCount = () => visibleGroups;

  const currentEdges = () => edges.filter((edge) => {
    const direction = directionFilter.value;
    if (direction === "outgoing" && edge.source_id !== focusedId) return false;
    if (direction === "incoming" && edge.target_id !== focusedId) return false;
    if (direction === "both" && edge.source_id !== focusedId && edge.target_id !== focusedId) return false;
    return !typeFilter.value || edge.type === typeFilter.value;
  });

  const renderFocus = () => {
    const node = byId.get(focusedId);
    if (!node) return;
    const records = currentEdges();
    title.textContent = node.label;
    meta.textContent = `${numberLabel(node)}${numberLabel(node) ? " · " : ""}${node.id}`;
    openLaw.href = siteHref(node);
    openLaw.textContent = `Abrir ${node.label}`;
    degree.textContent = `${node.degree} diplomas vizinhos no grafo completo.`;
    renderDiagram(records);
    renderConnections(records);
    const omitted = Math.max(new Set(records.map((edge) => edge.source_id === focusedId ? edge.target_id : edge.source_id)).size - NODE_LIMIT, 0);
    status.textContent = `${graphNodeCount} diplomas e ${graphEdgeCount} registros carregados. ${records.length} registros ligados a ${node.label} correspondem aos filtros.${omitted ? ` ${omitted} vizinhos adicionais estão na lista.` : ""}`;
  };

  const focusNode = (identifier, { recordHistory = false, focusAfter = null } = {}) => {
    if (!byId.has(identifier)) return;
    if (identifier === focusedId) {
      if (focusAfter === "search") search.focus({ preventScroll: true });
      return;
    }
    if (recordHistory && identifier !== focusedId) {
      const destination = new URL(window.location.href);
      destination.searchParams.set("node", identifier);
      window.history.pushState(window.history.state, "", destination);
    }
    focusedId = identifier;
    visibleGroups = PAGE_SIZE;
    renderFocus();
    if (focusAfter === "search") search.focus({ preventScroll: true });
    if (focusAfter === "graph") {
      const activeNode = Array.from(svg.querySelectorAll("[data-node-id]")).find(
        (element) => element.getAttribute("data-node-id") === identifier,
      );
      activeNode?.focus({ preventScroll: true });
    }
  };

  let graphNodeCount = 0;
  let graphEdgeCount = 0;

  search.addEventListener("input", renderSearchResults);
  search.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      const first = suggestions.querySelector("button");
      if (first && !suggestions.hidden) {
        event.preventDefault();
        first.focus();
      }
    } else if (event.key === "Enter") {
      const first = suggestions.querySelector("button");
      if (first && !suggestions.hidden) {
        event.preventDefault();
        first.click();
      }
    } else if (event.key === "Escape") {
      search.value = "";
      setSuggestionsVisible(false);
    }
  });
  typeFilter.addEventListener("change", () => { visibleGroups = PAGE_SIZE; renderFocus(); });
  directionFilter.addEventListener("change", () => { visibleGroups = PAGE_SIZE; renderFocus(); });
  showMore.addEventListener("click", () => { visibleGroups += PAGE_SIZE; renderFocus(); });

  window.addEventListener("popstate", () => {
    const requestedId = new URL(window.location.href).searchParams.get("node");
    if (requestedId && byId.has(requestedId)) focusNode(requestedId);
    else if (nodes.length) focusNode(nodes.find((node) => node.id === initialNodeId)?.id || nodes[0].id);
  });

  let initialNodeId = "";
  const loadGraph = async () => {
    try {
      const response = await fetch(new URL(root.dataset.indexUrl, document.baseURI), { credentials: "same-origin" });
      if (!response.ok) throw new Error("Não foi possível carregar o índice do grafo.");
      const data = await response.json();
      if (data.schema !== "vademecum-graph/v1" || !Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
        throw new Error("O formato do índice do grafo é inválido.");
      }
      nodes = data.nodes;
      byId = new Map(nodes.map((node) => [node.id, node]));
      edges = data.edges.filter((edge) => byId.has(edge.source_id) && byId.has(edge.target_id) && edge.source_id !== edge.target_id);
      graphNodeCount = nodes.length;
      graphEdgeCount = edges.length;
      if (graphNodeCount !== data.node_count || graphEdgeCount !== data.edge_count) {
        throw new Error("A contagem do índice não corresponde aos registros carregados.");
      }
      Array.from(new Set(edges.map((edge) => edge.type))).sort().forEach((type) => {
        const option = document.createElement("option");
        option.value = type;
        option.textContent = relationLabel(type);
        typeFilter.append(option);
      });
      const defaultNode = nodes.find((node) => node.id === data.featured.center_id) || nodes[0];
      if (!defaultNode) throw new Error("O grafo publicado não contém diplomas para exibir.");
      initialNodeId = defaultNode.id;
      const requestedId = new URL(window.location.href).searchParams.get("node");
      focusNode(requestedId && byId.has(requestedId) ? requestedId : defaultNode.id);
    } catch (error) {
      status.textContent = `${error.message} Use o catálogo ou o índice topológico como alternativa.`;
      connectionList.replaceChildren();
      const fallback = document.createElement("li");
      fallback.className = "graph-empty-state";
      const link = document.createElement("a");
      link.href = "../generated/catalog/";
      link.textContent = "Abrir catálogo de diplomas";
      fallback.append(link);
      connectionList.append(fallback);
    }
  };

  loadGraph();
})();
