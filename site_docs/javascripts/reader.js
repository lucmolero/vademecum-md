/**
 * VadeMecum MD — controles do leitor de diplomas.
 * A interação é progressiva: o conteúdo legal permanece disponível sem este script.
 */
(() => {
  "use strict";

  const normalize = (value) =>
    (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^0-9a-z]/gi, "")
      .toLowerCase();

  const readPreference = (key, fallback) => {
    try {
      const value = window.localStorage.getItem(key);
      return value === null ? fallback : value;
    } catch (_error) {
      return fallback;
    }
  };

  const writePreference = (key, value) => {
    try {
      window.localStorage.setItem(key, value);
    } catch (_error) {
      // Preferências são opcionais; o controle continua funcionando nesta página.
    }
  };

  const copyText = async (value) => {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return true;
    }

    const field = document.createElement("textarea");
    field.value = value;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    field.style.pointerEvents = "none";
    document.body.appendChild(field);
    field.select();
    let copied = false;
    try {
      copied = document.execCommand("copy");
    } catch (_error) {
      copied = false;
    }
    field.remove();
    return copied;
  };

  const headingLabel = (heading) => {
    const clone = heading.cloneNode(true);
    clone.querySelector(".article-actions")?.remove();
    return (clone.innerText || clone.textContent || "").replace(/\s+/g, " ").trim();
  };

  const articleText = (heading) => {
    const parts = [];
    let element = heading.nextElementSibling;
    while (element) {
      if (element.matches("h2[id^='art-']") || element.matches(".law-relations")) break;
      if (element.matches("p, ul, ol, blockquote, table")) {
        const text = (element.innerText || element.textContent || "").trim();
        if (text) parts.push(text);
      }
      element = element.nextElementSibling;
    }
    return parts.join("\n\n");
  };

  const announceButtonResult = (button, success, successLabel, failureLabel) => {
    const original = button.dataset.originalLabel || button.textContent.trim();
    button.dataset.originalLabel = original;
    button.textContent = success ? successLabel : failureLabel;
    window.setTimeout(() => {
      button.textContent = original;
    }, 2200);
  };

  const addArticleActions = (headings, context) => {
    headings.forEach((heading) => {
      if (heading.querySelector(".article-actions")) return;

      const label = headingLabel(heading);
      const wrapper = document.createElement("span");
      wrapper.className = "article-actions";

      const copyButton = document.createElement("button");
      copyButton.type = "button";
      copyButton.className = "btn-article-action btn-copy-citation";
      copyButton.textContent = "Copiar texto e referência";
      copyButton.setAttribute("aria-label", "Copiar " + label + " com a referência do diploma");

      copyButton.addEventListener("click", async () => {
        const text = articleText(heading);
        const citation = [
          text,
          context.title + ", " + label + ". VadeMecum MD, " + context.cutoff +
            ". ID: " + context.id +
            (context.source ? ". Fonte oficial: " + context.source : ". Fonte oficial não identificada") +
            ". Release: " + context.release + ".",
        ].filter(Boolean).join("\n\n");

        try {
          const success = await copyText(citation);
          announceButtonResult(
            copyButton,
            success,
            "Texto e referência copiados",
            "Cópia indisponível; selecione o texto manualmente",
          );
        } catch (_error) {
          announceButtonResult(
            copyButton,
            false,
            "Cópia indisponível",
            "Cópia indisponível; selecione o texto manualmente",
          );
        }
      });

      const anchor = document.createElement("a");
      anchor.href = "#" + heading.id;
      anchor.className = "btn-article-action btn-article-anchor";
      anchor.textContent = "#";
      anchor.setAttribute("aria-label", "Link permanente para " + label);

      wrapper.append(copyButton, anchor);
      heading.appendChild(wrapper);
    });
  };

  const createQuickJumpModal = (headings, trigger) => {
    let backdrop = document.getElementById("vmd-jump-modal");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.id = "vmd-jump-modal";
      backdrop.className = "vmd-modal-backdrop";
      backdrop.hidden = true;
      backdrop.setAttribute("aria-hidden", "true");
      backdrop.innerHTML =
        '<div class="vmd-modal-dialog" role="dialog" aria-modal="true" ' +
        'aria-labelledby="vmd-jump-title" aria-describedby="vmd-jump-description" tabindex="-1">' +
        '<div class="vmd-modal-header"><h2 id="vmd-jump-title">Ir para dispositivo</h2>' +
        '<button type="button" class="vmd-modal-close" aria-label="Fechar navegação rápida">Fechar</button></div>' +
        '<label class="vmd-sr-only" for="vmd-jump-input">Buscar número ou rótulo do artigo</label>' +
        '<input type="search" id="vmd-jump-input" placeholder="Ex.: 186, licitação, processo" autocomplete="off" />' +
        '<p id="vmd-jump-description" class="vmd-modal-subhint">Busque um número de dispositivo ou expressão no texto desta norma.</p>' +
        '<p id="vmd-jump-status" class="vmd-sr-only" role="status" aria-live="polite"></p>' +
        '<div id="vmd-jump-results" class="vmd-jump-results"></div></div>';
      document.body.appendChild(backdrop);
    }

    const dialog = backdrop.querySelector('[role="dialog"]');
    const input = backdrop.querySelector("#vmd-jump-input");
    const status = backdrop.querySelector("#vmd-jump-status");
    const results = backdrop.querySelector("#vmd-jump-results");
    const closeButton = backdrop.querySelector(".vmd-modal-close");
    let returnFocus = null;
    let priorOverflow = "";
    let articleIndex = null;

    const close = () => {
      if (backdrop.hidden) return;
      backdrop.classList.remove("is-active");
      backdrop.hidden = true;
      backdrop.setAttribute("aria-hidden", "true");
      document.body.style.overflow = priorOverflow;
      if (returnFocus && document.contains(returnFocus)) returnFocus.focus();
    };

    const jumpTo = (id) => {
      const target = document.getElementById(id);
      if (!target) return;
      close();
      target.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "start",
      });
      target.classList.add("article-highlight");
      window.setTimeout(() => target.classList.remove("article-highlight"), 1800);
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
      target.addEventListener("blur", () => target.removeAttribute("tabindex"), { once: true });
    };

    const render = (query) => {
      results.replaceChildren();
      const needle = normalize(query);
      if (!articleIndex) {
        articleIndex = headings.map((heading) => {
          const label = headingLabel(heading);
          const text = articleText(heading);
          return { heading, label, text, search: normalize(label + " " + text) };
        });
      }
      const matches = articleIndex
        .filter((item) => !needle || item.search.includes(needle))
        .slice(0, 30);

      if (!matches.length) {
        const empty = document.createElement("p");
        empty.className = "no-results";
        empty.textContent = "Nenhum dispositivo correspondente nesta página.";
        results.appendChild(empty);
      } else {
        matches.forEach(({ heading, label, text }) => {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "jump-result-item";
          const title = document.createElement("strong");
          title.textContent = label;
          button.appendChild(title);
          if (needle && !normalize(label).includes(needle)) {
            const snippet = document.createElement("span");
            snippet.className = "jump-result-snippet";
            const paragraph = text.split(/\n+/).find((part) => normalize(part).includes(needle)) || text;
            snippet.textContent = paragraph.slice(0, 180).trim();
            button.appendChild(snippet);
          }
          button.addEventListener("click", () => jumpTo(heading.id));
          results.appendChild(button);
        });
      }

      status.textContent = matches.length
        ? matches.length + (matches.length === 1 ? " dispositivo encontrado." : " dispositivos encontrados.")
        : "Nenhum dispositivo correspondente nesta página.";
    };

    const open = (source) => {
      returnFocus = source || document.activeElement;
      priorOverflow = document.body.style.overflow;
      backdrop.hidden = false;
      backdrop.removeAttribute("aria-hidden");
      backdrop.classList.add("is-active");
      document.body.style.overflow = "hidden";
      input.value = "";
      render("");
      window.requestAnimationFrame(() => input.focus());
    };

    input.addEventListener("input", () => render(input.value));
    input.addEventListener("keydown", (event) => {
      const options = Array.from(results.querySelectorAll(".jump-result-item"));
      if (event.key === "ArrowDown" && options.length) {
        event.preventDefault();
        options[0].focus();
      }
    });

    results.addEventListener("keydown", (event) => {
      const options = Array.from(results.querySelectorAll(".jump-result-item"));
      const index = options.indexOf(document.activeElement);
      if (event.key === "ArrowDown" && index < options.length - 1) {
        event.preventDefault();
        options[index + 1].focus();
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        if (index > 0) options[index - 1].focus();
        else input.focus();
      } else if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    });

    dialog.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close();
        return;
      }
      if (event.key !== "Tab") return;
      const focusable = Array.from(
        dialog.querySelectorAll('button:not([disabled]), input:not([disabled]), a[href], [tabindex="0"]'),
      ).filter((element) => !element.hidden);
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    closeButton.addEventListener("click", close);
    backdrop.addEventListener("click", (event) => {
      if (event.target === backdrop) close();
    });

    const globalKeyHandler = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (backdrop.hidden) open(document.activeElement);
        else close();
      }
    };
    window.addEventListener("keydown", globalKeyHandler);

    trigger?.addEventListener("click", () => open(trigger));
    return { open, close };
  };

  const initReadingToolbarControls = () => {
    const focusButton = document.getElementById("btn-focus-mode");
    const focusActive = readPreference("vmd_focus_mode", "false") === "true";
    document.body.classList.toggle("vmd-focus-mode", focusActive);
    if (focusButton) {
      focusButton.setAttribute("aria-pressed", String(focusActive));
      focusButton.addEventListener("click", () => {
        const active = document.body.classList.toggle("vmd-focus-mode");
        focusButton.setAttribute("aria-pressed", String(active));
        writePreference("vmd_focus_mode", String(active));
      });
    }

    const sizes = ["font-sm", "font-md", "font-lg", "font-xl"];
    const storedSize = Number.parseInt(readPreference("vmd_font_size_idx_v2", "1"), 10);
    let sizeIndex = Number.isInteger(storedSize) && storedSize >= 0 && storedSize < sizes.length
      ? storedSize
      : 1;
    const content = document.querySelector(".md-content");
    const applySize = () => {
      if (!content) return;
      sizes.forEach((className) => content.classList.remove(className));
      content.classList.add(sizes[sizeIndex]);
      writePreference("vmd_font_size_idx_v2", String(sizeIndex));
      if (decrease) decrease.disabled = sizeIndex === 0;
      if (increase) increase.disabled = sizeIndex === sizes.length - 1;
    };
    const decrease = document.getElementById("btn-font-decrease");
    const increase = document.getElementById("btn-font-increase");
    applySize();
    decrease?.addEventListener("click", () => {
      if (sizeIndex > 0) {
        sizeIndex -= 1;
        applySize();
      }
    });
    increase?.addEventListener("click", () => {
      if (sizeIndex < sizes.length - 1) {
        sizeIndex += 1;
        applySize();
      }
    });
  };

  const init = () => {
    const hero = document.querySelector(".law-hero");
    if (!hero) return;

    const headings = Array.from(document.querySelectorAll(".md-content h2[id^='art-']"));
    const getSource = () => {
      const link = document.querySelector(".law-tools a[href^='https://']");
      return link ? link.href : "";
    };

    addArticleActions(headings, {
      id: hero.dataset.lawId || "",
      title: hero.querySelector("h1")?.textContent.trim() || "Diploma normativo",
      cutoff: Array.from(hero.querySelectorAll(".status-chip"))
        .map((chip) => chip.textContent.trim())
        .find((text) => text.toLowerCase().startsWith("corte")) || "corte não informado",
      release: hero.dataset.release || "não informada",
      source: getSource(),
    });

    const trigger = document.getElementById("btn-quick-jump");
    createQuickJumpModal(headings, trigger);
    initReadingToolbarControls();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

