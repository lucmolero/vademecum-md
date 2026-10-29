/**
 * VadeMecum MD — Leitor Forense de Alta Performance
 * Interatividade nativa para advogados e pesquisadores:
 * - Salto rápido de dispositivo (Ctrl + K)
 * - Botão de cópia para petição com citação forense padronizada
 * - Modo leitura / foco sem distrações
 * - Ajuste dinâmico de tamanho de fonte
 */
(() => {
  "use strict";

  const initLawReader = () => {
    const lawHero = document.querySelector(".law-hero");
    if (!lawHero) return;

    const lawId = lawHero.getAttribute("data-law-id") || "";
    const releaseVersion = lawHero.getAttribute("data-release-version") || "";
    const lawTitle = lawHero.querySelector("h1")?.textContent?.trim() || "Diploma Normativo";
    const cutoffText = Array.from(lawHero.querySelectorAll(".status-chip"))
      .map(c => c.textContent.trim())
      .find(t => t.toLowerCase().includes("corte")) || "";
    const sourceLinkEl = document.querySelector('.law-tools a[href^="http"]');
    const sourceUrl = sourceLinkEl ? sourceLinkEl.href : "";

    // 1. Injetar ações de cópia de citação em cada dispositivo (Artigo)
    const articleHeadings = document.querySelectorAll('.md-content h2[id^="art-"]');
    articleHeadings.forEach((h2) => {
      if (h2.querySelector(".article-actions")) return;

      const articleLabel = h2.textContent.replace(/^#+\s*/, "").trim();
      const articleId = h2.id;

      // Localizar o texto do artigo (parágrafos imediatos até a próxima seção)
      const getArticleBodyText = () => {
        let textParts = [];
        let next = h2.nextElementSibling;
        while (next && !["H1", "H2", "H3", "SECTION"].includes(next.tagName)) {
          if (next.tagName === "P" || next.tagName === "UL" || next.tagName === "OL" || next.tagName === "BLOCKQUOTE") {
            const cleanText = next.textContent.trim();
            if (cleanText) textParts.push(cleanText);
          }
          next = next.nextElementSibling;
        }
        return textParts.join("\n\n");
      };

      const actionsWrapper = document.createElement("span");
      actionsWrapper.className = "article-actions";

      // Copiar o texto do artigo com os metadados de proveniência disponíveis.
      const copyBtn = document.createElement("button");
      copyBtn.type = "button";
      copyBtn.className = "btn-article-action btn-copy-citation";
      copyBtn.title = "Copiar o artigo com sua referência de proveniência";
      copyBtn.innerHTML = '<span class="action-icon">📋</span> Copiar artigo e referência';

      copyBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();

        const bodyText = getArticleBodyText();
        const citation = [
          bodyText ? `"${bodyText}"` : `[${articleLabel}]`,
          `(${lawTitle}, ${articleLabel}. VadeMecum MD, release ${releaseVersion ? `v${releaseVersion}` : "não informada"}, ${cutoffText || "corte não informado"}. ID: ${lawId}${sourceUrl ? `. Fonte oficial: ${sourceUrl}` : ""}).`
        ].join("\n");

        try {
          await navigator.clipboard.writeText(citation);
          const orig = copyBtn.innerHTML;
          copyBtn.innerHTML = '<span class="action-icon">✓</span> Citação copiada!';
          copyBtn.classList.add("is-copied");
          setTimeout(() => {
            copyBtn.innerHTML = orig;
            copyBtn.classList.remove("is-copied");
          }, 2000);
        } catch (_err) {
          copyBtn.textContent = "Erro ao copiar";
        }
      });

      // Botão Link Permanente
      const linkBtn = document.createElement("a");
      linkBtn.href = `#${articleId}`;
      linkBtn.className = "btn-article-action btn-article-anchor";
      linkBtn.title = "Link permanente para este artigo";
      linkBtn.innerHTML = "#";

      actionsWrapper.appendChild(copyBtn);
      actionsWrapper.appendChild(linkBtn);
      h2.appendChild(actionsWrapper);
    });

    // 2. Criar e gerenciar a Modal de Salto Rápido de Artigo (Ctrl + K)
    createQuickJumpModal(articleHeadings);

    // 3. Gerenciar Modo Leitura / Foco e Tamanho de Fonte
    initReadingToolbarControls();
  };

  /**
   * Modal de Busca e Salto Rápido (Ctrl + K)
   */
  const createQuickJumpModal = (articleHeadings) => {
    let backdrop = document.getElementById("vmd-jump-modal");
    let returnFocusTo = null;
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.id = "vmd-jump-modal";
      backdrop.className = "vmd-modal-backdrop";
      backdrop.setAttribute("aria-hidden", "true");
      backdrop.innerHTML = `
        <div class="vmd-modal-dialog" role="dialog" aria-modal="true" aria-labelledby="vmd-jump-title" tabindex="-1">
          <div class="vmd-modal-header">
            <h3 id="vmd-jump-title">Salto rápido de artigo</h3>
            <button type="button" class="vmd-modal-close" aria-label="Fechar navegação rápida">Fechar <kbd>Esc</kbd></button>
          </div>
          <div class="vmd-modal-body">
            <input type="text" id="vmd-jump-input" aria-label="Número ou identificador do artigo" aria-controls="vmd-jump-results" placeholder="Digite o artigo (ex: 186, 5º, 300, 1)..." autocomplete="off" />
            <p class="vmd-modal-subhint">Pressione <kbd>Enter</kbd> para saltar diretamente para o artigo.</p>
            <div id="vmd-jump-results" class="vmd-jump-results" aria-live="polite"></div>
          </div>
        </div>
      `;
      document.body.appendChild(backdrop);
    }

    const input = document.getElementById("vmd-jump-input");
    const resultsContainer = document.getElementById("vmd-jump-results");

    const openModal = () => {
      returnFocusTo = document.activeElement instanceof HTMLElement ? document.activeElement : null;
      backdrop.classList.add("is-active");
      backdrop.setAttribute("aria-hidden", "false");
      input.value = "";
      renderSuggestions("");
      input.focus();
    };

    const closeModal = () => {
      if (!backdrop.classList.contains("is-active")) return;
      backdrop.classList.remove("is-active");
      backdrop.setAttribute("aria-hidden", "true");
      if (returnFocusTo?.isConnected) returnFocusTo.focus();
    };

    const jumpToArticle = (targetId) => {
      const el = document.getElementById(targetId);
      if (el) {
        closeModal();
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.classList.add("article-highlight");
        setTimeout(() => el.classList.remove("article-highlight"), 2500);
      }
    };

    const sanitizeNum = (str) => {
      return (str || "").replace(/[^0-9a-zA-Z]/g, "").toLowerCase();
    };

    const renderSuggestions = (query) => {
      const q = sanitizeNum(query);
      resultsContainer.innerHTML = "";
      const showEmptyState = (message) => {
        const emptyState = document.createElement("span");
        emptyState.className = "no-results";
        emptyState.textContent = message;
        resultsContainer.appendChild(emptyState);
      };
      if (!articleHeadings || articleHeadings.length === 0) {
        showEmptyState("Nenhum artigo encontrado nesta norma.");
        return;
      }

      let matches = [];
      articleHeadings.forEach((h2) => {
        const text = h2.textContent.replace(/📋.*$/, "").trim();
        const clean = sanitizeNum(text);
        if (!q || clean.includes(q)) {
          matches.push({ id: h2.id, label: text });
        }
      });

      const displayItems = matches.slice(0, 10);
      if (displayItems.length === 0) {
        showEmptyState(`Nenhum artigo correspondente a "${query}".`);
        return;
      }

      displayItems.forEach((item, idx) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "jump-result-item" + (idx === 0 ? " is-selected" : "");
        btn.textContent = item.label;
        btn.addEventListener("click", () => jumpToArticle(item.id));
        resultsContainer.appendChild(btn);
      });
    };

    input.addEventListener("input", (e) => {
      renderSuggestions(e.target.value);
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const first = resultsContainer.querySelector(".jump-result-item");
        if (first) first.click();
      } else if (e.key === "Escape") {
        closeModal();
      }
    });

    const dialog = backdrop.querySelector('[role="dialog"]');
    dialog.addEventListener("keydown", (e) => {
      if (e.key !== "Tab") return;
      const focusable = Array.from(dialog.querySelectorAll('input, button, a[href], [tabindex]:not([tabindex="-1"])'))
        .filter((element) => !element.hasAttribute("disabled") && element.getClientRects().length > 0);
      if (focusable.length === 0) {
        e.preventDefault();
        dialog.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
        e.preventDefault();
        first.focus();
      }
    });

    backdrop.querySelector(".vmd-modal-close").addEventListener("click", closeModal);

    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) closeModal();
    });

    // Atalho global Ctrl + K / Cmd + K
    window.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        // Se estiver num diploma, ativa o salto rápido
        if (document.querySelector(".law-hero")) {
          e.preventDefault();
          if (backdrop.classList.contains("is-active")) {
            closeModal();
          } else {
            openModal();
          }
        }
      } else if (e.key === "Escape" && backdrop.classList.contains("is-active")) {
        closeModal();
      }
    });

    // Conectar ao botão na barra de leitura
    const triggerBtn = document.getElementById("btn-quick-jump");
    if (triggerBtn) {
      triggerBtn.addEventListener("click", openModal);
    }
  };

  /**
   * Controles da barra de leitura (Modo Foco e Tamanho de Fonte)
   */
  const initReadingToolbarControls = () => {
    // 1. Modo Leitura / Foco
    const focusBtn = document.getElementById("btn-focus-mode");
    const isFocusSaved = localStorage.getItem("vmd_focus_mode") === "true";
    if (isFocusSaved) {
      document.body.classList.add("vmd-focus-mode");
      if (focusBtn) {
        focusBtn.classList.add("is-active");
        focusBtn.setAttribute("aria-pressed", "true");
      }
    }

    if (focusBtn) {
      focusBtn.addEventListener("click", () => {
        const active = document.body.classList.toggle("vmd-focus-mode");
        focusBtn.classList.toggle("is-active", active);
        focusBtn.setAttribute("aria-pressed", String(active));
        localStorage.setItem("vmd_focus_mode", active ? "true" : "false");
      });
    }

    // 2. Controle de Tamanho de Fonte
    const fontSizes = ["font-sm", "font-md", "font-lg", "font-xl"];
    let currentSizeIndex = parseInt(localStorage.getItem("vmd_font_size_idx") || "0", 10);
    if (isNaN(currentSizeIndex) || currentSizeIndex < 0 || currentSizeIndex >= fontSizes.length) {
      currentSizeIndex = 0;
    }

    const applyFontSize = () => {
      const contentEl = document.querySelector(".md-content");
      if (!contentEl) return;
      fontSizes.forEach(cls => contentEl.classList.remove(cls));
      contentEl.classList.add(fontSizes[currentSizeIndex]);
      localStorage.setItem("vmd_font_size_idx", currentSizeIndex.toString());
    };

    applyFontSize();

    const decBtn = document.getElementById("btn-font-decrease");
    const incBtn = document.getElementById("btn-font-increase");

    if (decBtn) {
      decBtn.addEventListener("click", () => {
        if (currentSizeIndex > 0) {
          currentSizeIndex--;
          applyFontSize();
        }
      });
    }

    if (incBtn) {
      incBtn.addEventListener("click", () => {
        if (currentSizeIndex < fontSizes.length - 1) {
          currentSizeIndex++;
          applyFontSize();
        }
      });
    }
  };

  /** Integrated, single-route reader: the index stays small and each law is loaded on demand. */
  const initIntegratedReader = () => {
    const app = document.querySelector("[data-reader-app]");
    if (!app) return;

    const $ = (selector) => app.querySelector(selector);
    const search = $("#reader-search");
    const domain = $("#reader-domain");
    const results = $("#reader-results");
    const articleSearch = $("#reader-article-search");
    const articleList = $("#reader-article-list");
    const documentView = $("[data-reader-document]");
    const welcome = $("[data-reader-welcome]");
    const toast = $("[data-reader-toast]");
    const state = { index: null, selected: null, articles: [], shown: 80, query: "", toastTimer: 0, saveTimer: 0 };
    const safeText = (selector, value) => { const node = $(selector); if (node) node.textContent = value || ""; };
    const notify = (message) => {
      if (!toast) return;
      toast.textContent = message;
      toast.classList.add("is-visible");
      window.clearTimeout(state.toastTimer);
      state.toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 2400);
    };
    const normalize = (value) => String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
    const setHash = (id, article = "", replace = false) => {
      const next = id ? `#/${encodeURIComponent(id)}${article ? `/${encodeURIComponent(article)}` : ""}` : "#top";
      if (location.hash === next) return;
      if (replace) history.replaceState(null, "", next); else history.pushState(null, "", next);
    };
    const getRoute = () => {
      const parts = decodeURIComponent(location.hash.replace(/^#\/?/, "")).split("/").filter(Boolean);
      return { id: parts[0] || "", article: parts[1] || "" };
    };
    const routeTo = (id, article = "") => {
      const hash = `#/${encodeURIComponent(id)}${article ? `/${encodeURIComponent(article)}` : ""}`;
      if (location.hash === hash) loadDocument(id, article);
      else { setHash(id, article); loadDocument(id, article); }
    };
    const renderResults = () => {
      if (!state.index) return;
      const query = normalize(search.value.trim());
      const selectedDomain = domain.value;
      const matches = state.index.documents.filter((item) => {
        if (selectedDomain && item.domain_key !== selectedDomain) return false;
        if (!query) return true;
        return normalize([item.title, item.canonical_title, item.type, item.number, item.year, item.domain, item.ementa, ...(item.aliases || [])].join(" ")).includes(query);
      });
      if (query) matches.sort((a, b) => {
        const rank = (item) => {
          const title = normalize(item.title); const canonical = normalize(item.canonical_title);
          if (title === query || canonical === query) return 0;
          if (title.startsWith(query) || canonical.startsWith(query)) return 1;
          if (title.includes(query) || canonical.includes(query)) return 2;
          if (normalize(`${item.number} ${item.year}`).includes(query)) return 3;
          return 4;
        };
        return rank(a) - rank(b) || a.title.localeCompare(b.title, "pt-BR");
      });
      results.replaceChildren();
      if (!matches.length) {
        const empty = document.createElement("li"); empty.className = "vmd-reader-no-results"; empty.textContent = "Nenhum diploma corresponde a esta busca."; results.appendChild(empty);
      } else matches.forEach((item, index) => {
        const li = document.createElement("li");
        li.className = "vmd-reader-result"; li.id = `reader-option-${index}`; li.dataset.documentId = item.id;
        li.setAttribute("role", "option"); li.setAttribute("aria-selected", String(state.selected?.id === item.id));
        const title = document.createElement("strong"); title.textContent = item.title;
        const meta = document.createElement("small"); meta.textContent = `${item.type} ${item.number ? `${item.number}/` : ""}${item.year} · ${item.domain}`;
        li.append(title, meta); li.addEventListener("click", () => { routeTo(item.id); app.classList.remove("show-library"); $("[data-reader-action='library']")?.setAttribute("aria-expanded", "false"); });
        results.appendChild(li);
      });
      results.removeAttribute("aria-activedescendant");
      safeText("#reader-results-count", `${matches.length} ${matches.length === 1 ? "diploma" : "diplomas"}${search.value.trim() ? " encontrados" : " no acervo"}`);
    };
    const renderArticles = () => {
      const query = normalize(articleSearch.value.trim());
      const matches = state.articles.filter((item) => !query || normalize(item.label).includes(query));
      articleList.replaceChildren();
      matches.slice(0, state.shown).forEach((item) => {
        const li = document.createElement("li"); const link = document.createElement("a");
        link.href = `#/${encodeURIComponent(state.selected.id)}/${encodeURIComponent(item.id)}`;
        link.textContent = item.label; link.addEventListener("click", (event) => { event.preventDefault(); setHash(state.selected.id, item.id); scrollToArticle(item.id); });
        li.appendChild(link); articleList.appendChild(li);
      });
      safeText("[data-article-count]", `${matches.length} ${matches.length === 1 ? "artigo identificado" : "artigos identificados"}${query ? ` · ${matches.length} correspondem` : ""}`);
      const more = $("[data-reader-more-articles]");
      if (more) { more.hidden = matches.length <= state.shown; more.textContent = `Mostrar mais artigos (${matches.length - state.shown})`; }
    };
    const scrollToArticle = (id) => {
      requestAnimationFrame(() => {
        const target = document.getElementById(id);
        if (target) { target.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }); target.focus({ preventScroll: true }); }
      });
    };
    const saveReadingPosition = () => {
      if (!state.selected || documentView.hidden) return;
      try { localStorage.setItem(`vmd_reader_position_${state.selected.id}`, String(Math.max(0, Math.round(window.scrollY)))); } catch (_) {}
    };
    const loadDocument = async (id, article = "") => {
      if (state.selected?.id === id && !documentView.hidden) { renderResults(); if (article) scrollToArticle(article); return; }
      if (state.loadingId === id) return;
      saveReadingPosition(); window.clearTimeout(state.saveTimer);
      state.loadingId = id;
      documentView.hidden = false; welcome.hidden = true;
      documentView.setAttribute("aria-busy", "true");
      safeText("[data-document-title]", "Abrindo diploma…");
      try {
        const base = new URL(app.dataset.documentRoot, location.href);
        const url = new URL(`${encodeURIComponent(id)}.json`, base);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (data.schema !== "vademecum-reader-document/v1" || data.id !== id) throw new Error("Payload inválido");
        state.selected = data;
        app.classList.add("has-document");
        safeText("[data-document-title]", data.title);
        safeText("[data-document-meta]", `${data.type} ${data.number ? `${data.number}/` : ""}${data.year} · ${data.domain}`);
        safeText("[data-document-ementa]", data.ementa || "");
        const status = $("[data-document-status]");
        if (status) {
          status.replaceChildren();
          const chips = [[`${data.status_label} no corte`, "is-active"], [data.consolidation === "consolidada_fonte_oficial" ? "Consolidada em fonte oficial" : data.consolidation.replaceAll("_", " ")], [data.fidelity === "pass" ? "Fidelidade: conforme" : `Fidelidade: ${data.fidelity}`]];
          chips.forEach(([label, klass]) => { const chip = document.createElement("span"); chip.className = `vmd-reader-status-chip ${klass || ""}`; chip.textContent = label; status.appendChild(chip); });
        }
        safeText("[data-provenance-status]", data.status_label);
        safeText("[data-provenance-cutoff]", data.cutoff);
        safeText("[data-provenance-consolidation]", data.consolidation === "consolidada_fonte_oficial" ? "Consolidada em fonte oficial" : data.consolidation.replaceAll("_", " "));
        safeText("[data-provenance-fidelity]", data.fidelity === "pass" ? "Conforme" : data.fidelity);
        safeText("[data-provenance-release]", `v${data.release}`);
        safeText("[data-provenance-id]", data.id);
        safeText("[data-provenance-source-hash]", data.sha256_source_raw);
        safeText("[data-provenance-body-hash]", data.sha256_published_body);
        safeText("[data-provenance-source-unit]", data.source_unit_id);
        safeText("[data-endnote-release]", `v${data.release}`);
        safeText("[data-endnote-cutoff]", data.cutoff);
        const source = $("[data-official-source]");
        if (source) { source.hidden = !/^https:\/\//i.test(data.source_url || ""); if (!source.hidden) source.href = data.source_url; }
        const idButton = $("[data-reader-action='copy-id']"); if (idButton) idButton.disabled = false;
        const text = $("[data-reader-text]"); text.innerHTML = data.article_html || "<p>Texto não disponível.</p>";
        const relations = $("[data-reader-relations]"); relations.innerHTML = data.relations_html || "<p>Nenhuma relação publicada para este diploma no grafo desta release.</p>";
        state.articles = Array.from(text.querySelectorAll("h2[id^='art-'], h3[id^='art-']")).map((heading) => { heading.tabIndex = -1; return { id: heading.id, label: heading.textContent.trim() }; });
        state.shown = 80; articleSearch.value = ""; articleSearch.disabled = false; renderArticles(); renderResults();
        document.title = `${data.title} · Leitor VadeMecum MD`;
        documentView.setAttribute("aria-busy", "false");
        if (article) scrollToArticle(article);
        else {
          let savedPosition = 0;
          try { savedPosition = Number(localStorage.getItem(`vmd_reader_position_${id}`) || 0); } catch (_) {}
          if (savedPosition > 0) { requestAnimationFrame(() => window.scrollTo({ top: savedPosition, behavior: "auto" })); notify("Leitura retomada de onde você parou neste navegador."); }
          else { $("[data-document-title]").focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: "auto" }); }
        }
      } catch (error) {
        documentView.hidden = true; welcome.hidden = false;
        notify("Não foi possível abrir esta norma. Confira sua conexão e tente novamente.");
        console.error("Falha ao carregar documento do leitor", error);
      } finally { state.loadingId = ""; }
    };
    const syncRoute = () => {
      const route = getRoute();
      if (route.id && state.index?.documents.some((item) => item.id === route.id)) { loadDocument(route.id, route.article); return; }
      if (!route.id) {
        state.selected = null; state.articles = []; state.shown = 80;
        documentView.hidden = true; welcome.hidden = false; app.classList.remove("has-document");
        articleSearch.value = ""; articleSearch.disabled = true; articleList.replaceChildren();
        safeText("[data-article-count]", "Escolha uma norma para ver seu índice.");
        const progress = $("[data-reading-progress]"); if (progress) { progress.style.width = "0"; progress.parentElement?.setAttribute("aria-valuenow", "0"); }
        document.title = "Leitor integral - VadeMecum MD";
        renderResults();
      } else {
        notify("Esta norma não está disponível no índice desta release.");
      }
    };
    const setPreference = (key, value) => { app.dataset[key] = value; try { localStorage.setItem(`vmd_reader_${key}`, value); } catch (_) {} };
    const applyPreferences = () => {
      ["readingTheme", "readingSize", "readingFace"].forEach((key) => {
        try { const saved = localStorage.getItem(`vmd_reader_${key}`); if (saved) app.dataset[key] = saved; } catch (_) {}
      });
      const faceButton = $("[data-reader-action='font-face']"); if (faceButton) faceButton.textContent = app.dataset.readingFace === "sans" ? "Sem serifa" : "Serifada";
    };
    app.addEventListener("click", async (event) => {
      const button = event.target.closest("[data-reader-action]"); if (!button) return;
      const action = button.dataset.readerAction;
      if (action === "theme") {
        const themes = ["paper", "sepia", "night"]; setPreference("readingTheme", themes[(themes.indexOf(app.dataset.readingTheme) + 1) % themes.length]);
        button.setAttribute("aria-label", `Aparência atual: ${{ paper: "papel", sepia: "sépia", night: "escuro" }[app.dataset.readingTheme]}. Alternar aparência`);
      } else if (action === "font-decrease" || action === "font-increase") {
        const sizes = ["small", "regular", "large", "xlarge"]; const index = sizes.indexOf(app.dataset.readingSize);
        setPreference("readingSize", sizes[Math.max(0, Math.min(sizes.length - 1, index + (action === "font-increase" ? 1 : -1)))]);
      } else if (action === "font-face") { setPreference("readingFace", app.dataset.readingFace === "serif" ? "sans" : "serif"); applyPreferences(); }
      else if (action === "focus") { const active = app.classList.toggle("focus-reading"); button.setAttribute("aria-pressed", String(active)); button.textContent = active ? "Mostrar painéis" : "Leitura sem painéis"; }
      else if (action === "context") { const active = app.classList.toggle("show-context"); button.setAttribute("aria-expanded", String(active)); }
      else if (action === "library") { const active = app.classList.toggle("show-library"); button.setAttribute("aria-expanded", String(active)); if (active) search.focus(); }
      else if (action === "copy-citation" || action === "copy-id") {
        if (!state.selected) return;
        const route = getRoute();
        const articleLabel = state.articles.find((item) => item.id === route.article)?.label;
        const legalNumber = `${state.selected.number ? `${state.selected.number}/` : ""}${state.selected.year}`;
        const value = action === "copy-id" ? state.selected.id : `${state.selected.title}, ${state.selected.type} ${legalNumber}${articleLabel ? `, ${articleLabel}` : ""}. VadeMecum MD, release v${state.selected.release}, corte em ${state.selected.cutoff}. ID: ${state.selected.id}. Fonte oficial: ${state.selected.source_url}`;
        try { await navigator.clipboard.writeText(value); notify(action === "copy-id" ? "ID do diploma copiado." : "Referência copiada."); }
        catch (_) { notify("Não foi possível copiar. Selecione a referência manualmente."); }
      } else if (action === "print") window.print();
    });
    $("[data-reader-more-articles]")?.addEventListener("click", () => { state.shown += 120; renderArticles(); });
    search.addEventListener("input", renderResults); domain.addEventListener("change", renderResults); articleSearch.addEventListener("input", renderArticles);
    search.addEventListener("keydown", (event) => { if (event.key === "ArrowDown" && results.querySelector('[role="option"]')) { event.preventDefault(); results.focus(); results.setAttribute("aria-activedescendant", results.querySelector('[role="option"]').id); } });
    results.addEventListener("keydown", (event) => {
      const options = Array.from(results.querySelectorAll('[role="option"]'));
      if (!options.length) return;
      let index = Math.max(0, options.findIndex((option) => option.id === results.getAttribute("aria-activedescendant")));
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault(); index = (index + (event.key === "ArrowDown" ? 1 : -1) + options.length) % options.length;
        results.setAttribute("aria-activedescendant", options[index].id); options[index].scrollIntoView({ block: "nearest" });
      } else if (event.key === "Enter") { event.preventDefault(); options[index].click(); }
    });
    app.querySelectorAll("[data-reader-focus-search]").forEach((button) => button.addEventListener("click", () => { app.classList.add("show-library"); $("[data-reader-action='library']")?.setAttribute("aria-expanded", "true"); search.focus(); }));
    app.querySelector("[data-reading-progress]")?.parentElement?.setAttribute("aria-hidden", "true");
    let ticking = false;
    window.addEventListener("scroll", () => {
      if (ticking) return; ticking = true;
      requestAnimationFrame(() => {
        const bar = $("[data-reading-progress]"); const text = $("[data-reader-text]");
        if (bar && text && !documentView.hidden) { const rect = text.getBoundingClientRect(); const total = Math.max(1, text.scrollHeight - innerHeight * .7); const amount = Math.max(0, Math.min(100, ((innerHeight * .3 - rect.top) / total) * 100)); bar.style.width = `${amount}%`; bar.parentElement?.setAttribute("aria-valuenow", String(Math.round(amount))); }
        ticking = false;
        window.clearTimeout(state.saveTimer); state.saveTimer = window.setTimeout(saveReadingPosition, 900);
      });
    }, { passive: true });
    window.addEventListener("hashchange", syncRoute);
    window.addEventListener("popstate", syncRoute);
    app.addEventListener("click", (event) => {
      if (event.target === app && app.classList.contains("show-library")) { app.classList.remove("show-library"); $("[data-reader-action='library']")?.setAttribute("aria-expanded", "false"); }
    });
    window.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") { event.preventDefault(); app.classList.add("show-library"); $("[data-reader-action='library']")?.setAttribute("aria-expanded", "true"); search.focus(); }
      if (event.key === "Escape" && app.classList.contains("show-library")) { app.classList.remove("show-library"); $("[data-reader-action='library']")?.setAttribute("aria-expanded", "false"); }
    });
    applyPreferences();
    fetch(new URL(app.dataset.index, location.href)).then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }).then((index) => {
      if (index.schema !== "vademecum-reader-index/v1") throw new Error("Índice inválido");
      state.index = index;
      index.domains.forEach((item) => { const option = document.createElement("option"); option.value = item.key; option.textContent = `${item.title} (${item.count})`; domain.appendChild(option); });
      safeText("[data-reader-count]", index.document_count); safeText("[data-reader-cutoff]", index.cutoff); safeText("[data-reader-version]", `v${index.release}`); safeText("[data-reader-release]", `v${index.release} · corte ${index.cutoff}`);
      const query = new URLSearchParams(location.search).get("q") || ""; if (query) search.value = query;
      renderResults(); syncRoute();
    }).catch((error) => { safeText("#reader-results-count", "Índice indisponível"); notify("O índice do acervo não carregou. Recarregue a página para tentar novamente."); console.error("Falha ao carregar índice do leitor", error); });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => { initLawReader(); initIntegratedReader(); }, { once: true });
  } else {
    initLawReader();
    initIntegratedReader();
  }
})();

