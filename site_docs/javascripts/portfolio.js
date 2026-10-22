(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const canAnimate = !reduceMotion && "IntersectionObserver" in window;
  if (canAnimate) document.documentElement.classList.add("js-motion");

  const reveal = () => {
    const elements = document.querySelectorAll(".reveal");
    if (!canAnimate) {
      elements.forEach((element) => element.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries, currentObserver) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          currentObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 },
    );
    elements.forEach((element) => observer.observe(element));
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

  const copyIds = () => {
    document.querySelectorAll("[data-copy-id]").forEach((button) => {
      if (button.dataset.copyReady === "true") return;
      button.dataset.copyReady = "true";
      const status = document.createElement("span");
      status.className = "vmd-sr-only";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      button.insertAdjacentElement("afterend", status);
      button.addEventListener("click", async () => {
        const value = button.getAttribute("data-copy-id") || "";
        const original = button.dataset.originalLabel || button.textContent.trim();
        button.dataset.originalLabel = original;
        try {
          const copied = await copyText(value);
          status.textContent = copied
            ? "Identificador copiado."
            : "Não foi possível copiar. Selecione o identificador exibido ao lado.";
          button.textContent = copied ? "Copiado" : "Cópia indisponível";
        } catch (_error) {
          status.textContent = "Não foi possível copiar. Selecione o identificador exibido ao lado.";
          button.textContent = "Cópia indisponível";
        }
        window.setTimeout(() => { button.textContent = original; }, 2200);
      });
    });
  };

  const normalize = (value) =>
    (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^0-9a-z]/gi, "")
      .toLowerCase();

  const initGlobalSearch = () => {
    const form = document.getElementById("vmd-global-search");
    const input = document.getElementById("vmd-global-search-input");
    const panel = document.getElementById("vmd-global-search-results");
    const list = document.getElementById("vmd-global-search-list");
    const status = document.getElementById("vmd-global-search-status");
    const allLink = document.getElementById("vmd-global-search-all");
    if (!form || !input || !panel || !list || !status || !allLink) return;

    let indexPromise;
    let records = [];

    const loadIndex = () => {
      if (!indexPromise) {
        const indexUrl = new URL(input.dataset.indexUrl, document.baseURI);
        indexPromise = fetch(indexUrl, { credentials: "same-origin" })
          .then((response) => {
            if (!response.ok) throw new Error("Índice indisponível");
            return response.json();
          })
          .then((data) => {
            if (data.schema !== "vademecum-search/v1" || !Array.isArray(data.documents)) {
              throw new Error("Formato de índice desconhecido");
            }
            records = data.documents.flatMap((document) => {
              const { articles, ...fields } = document;
              const entries = [{ ...fields, kind: "document" }];
              (articles || []).forEach(([article, anchor]) => {
                entries.push({
                  ...fields,
                  kind: "article",
                  article,
                  href: fields.href + "#" + anchor,
                });
              });
              return entries;
            });
            return records;
          });
      }
      return indexPromise;
    };

    const setExpanded = (expanded) => {
      input.setAttribute("aria-expanded", String(expanded));
      panel.hidden = !expanded;
    };

    const scoreRecord = (record, query, queryTerms) => {
      const label = record.kind === "article" ? record.article : record.popular_title;
      const number = record.number && record.year ? record.number + record.year : record.number;
      const fields = [label, record.title, record.popular_title, record.id, number, record.year, record.domain, record.type];
      const normalized = fields.map(normalize);
      const phraseMatch = normalized.some((field) => field.includes(query));
      const termMatch = queryTerms.length > 1 && queryTerms.every((term) =>
        normalized.some((field) => field.includes(term)),
      );
      if (!phraseMatch && !termMatch) return -1;
      if (record.kind === "article") {
        const articleLabel = normalize(record.article);
        const explicitArticleQuery = queryTerms.some((term) => ["art", "artigo"].includes(term));
        const articleNumberMatch = explicitArticleQuery && queryTerms.some((term) =>
          /^\d+$/.test(term) && articleLabel.includes(term),
        );
        const articleMatch = articleLabel.includes(query) || articleNumberMatch;
        if (!articleMatch) return -1;
      }

      let score = 10;
      if (termMatch) score += queryTerms.length * 8;
      if (normalize(record.id) === query) score += 100;
      if (normalize(number) === query) score += 95;
      if (normalize(label) === query) score += 90;
      if (normalize(label).startsWith(query)) score += 50;
      if (normalize(record.popular_title).startsWith(query)) score += 45;
      if (record.kind === "article" && normalize(record.article).includes(query)) score += 30;
      if (record.kind === "document") score += 5;
      return score;
    };

    const render = async () => {
      const rawQuery = input.value.trim();
      const query = normalize(rawQuery);
      const queryTerms = rawQuery.split(/\s+/).map(normalize).filter(Boolean);
      list.replaceChildren();
      allLink.hidden = !rawQuery;
      allLink.href = "generated/catalog/";
      if (!rawQuery) {
        status.textContent = "";
        setExpanded(false);
        return;
      }
      setExpanded(true);
      if (query.length < 2) {
        status.textContent = "Digite ao menos dois caracteres.";
        return;
      }

      status.textContent = "Pesquisando no catálogo…";
      try {
        const index = await loadIndex();
        if (input.value.trim() !== rawQuery) return;
        const matches = index
          .map((record) => ({ record, score: scoreRecord(record, query, queryTerms) }))
          .filter((item) => item.score >= 0)
          .sort((a, b) => b.score - a.score || a.record.title.localeCompare(b.record.title, "pt-BR"))
          .slice(0, 7);

        if (!matches.length) {
          status.textContent = "Nenhuma correspondência rápida. Tente a busca completa ou explore o catálogo.";
          return;
        }

        matches.forEach(({ record }) => {
          const link = document.createElement("a");
          link.className = "home-search-result";
          link.href = record.href;
          const title = document.createElement("strong");
          title.textContent = record.kind === "article"
            ? record.article + " — " + record.popular_title
            : record.popular_title;
          const detail = document.createElement("span");
          const documentNumber = record.number && record.year
            ? record.type + " nº " + record.number + "/" + record.year
            : record.id;
          detail.textContent = record.kind === "article"
            ? documentNumber + " · " + record.id
            : documentNumber + " · " + record.domain;
          link.append(title, detail);
          list.appendChild(link);
        });
        status.textContent = matches.length + (matches.length === 1
          ? " resultado rápido."
          : " resultados rápidos.");
      } catch (_error) {
        status.textContent = "A busca rápida não carregou. Use a busca completa ou abra o catálogo.";
      }
    };

    let timer = 0;
    input.addEventListener("input", () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(render, 100);
    });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      await render();
      const firstResult = list.querySelector("a");
      if (firstResult) firstResult.focus();
      else input.focus();
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown") {
        const first = list.querySelector("a");
        if (first) {
          event.preventDefault();
          first.focus();
        }
      } else if (event.key === "Escape") {
        list.replaceChildren();
        input.value = "";
        status.textContent = "";
        setExpanded(false);
      }
    });
    list.addEventListener("keydown", (event) => {
      const links = Array.from(list.querySelectorAll("a"));
      const index = links.indexOf(document.activeElement);
      if (event.key === "ArrowDown" && index < links.length - 1) {
        event.preventDefault();
        links[index + 1].focus();
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        if (index > 0) links[index - 1].focus();
        else input.focus();
      } else if (event.key === "Escape") {
        input.focus();
        input.value = "";
        render();
      }
    });

    window.addEventListener("keydown", (event) => {
      const editable = event.target instanceof HTMLElement &&
        (event.target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName));
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k" &&
          (!editable || event.target === input)) {
        event.preventDefault();
        input.focus();
        input.select();
      }
    });
  };

  const boot = () => {
    reveal();
    copyIds();
    initGlobalSearch();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
