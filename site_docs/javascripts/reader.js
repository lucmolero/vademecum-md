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
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.id = "vmd-jump-modal";
      backdrop.className = "vmd-modal-backdrop";
      backdrop.innerHTML = `
        <div class="vmd-modal-dialog" role="dialog" aria-modal="true" aria-label="Navegação rápida de artigo">
          <div class="vmd-modal-header">
            <h3>Salto Rápido de Dispositivo</h3>
            <span class="vmd-modal-hint"><kbd>ESC</kbd> para fechar</span>
          </div>
          <div class="vmd-modal-body">
            <input type="text" id="vmd-jump-input" placeholder="Digite o artigo (ex: 186, 5º, 300, 1)..." autocomplete="off" />
            <p class="vmd-modal-subhint">Pressione <kbd>Enter</kbd> para saltar diretamente para o artigo.</p>
            <div id="vmd-jump-results" class="vmd-jump-results"></div>
          </div>
        </div>
      `;
      document.body.appendChild(backdrop);
    }

    const input = document.getElementById("vmd-jump-input");
    const resultsContainer = document.getElementById("vmd-jump-results");

    const openModal = () => {
      backdrop.classList.add("is-active");
      input.value = "";
      renderSuggestions("");
      setTimeout(() => input.focus(), 80);
    };

    const closeModal = () => {
      backdrop.classList.remove("is-active");
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
      if (!articleHeadings || articleHeadings.length === 0) {
        resultsContainer.innerHTML = `<span class="no-results">Nenhum artigo encontrado nesta norma.</span>`;
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
        resultsContainer.innerHTML = `<span class="no-results">Nenhum artigo correspondente a "${query}".</span>`;
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
      if (focusBtn) focusBtn.classList.add("is-active");
    }

    if (focusBtn) {
      focusBtn.addEventListener("click", () => {
        const active = document.body.classList.toggle("vmd-focus-mode");
        focusBtn.classList.toggle("is-active", active);
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

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLawReader, { once: true });
  } else {
    initLawReader();
  }
})();

