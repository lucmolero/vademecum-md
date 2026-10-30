(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!reduceMotion) document.documentElement.classList.add("js-motion");

  const reveal = () => {
    const elements = document.querySelectorAll(".reveal");
    if (reduceMotion || !("IntersectionObserver" in window)) {
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

  const copyIds = () => {
    document.querySelectorAll("[data-copy-id]").forEach((button) => {
      button.addEventListener("click", async () => {
        const value = button.getAttribute("data-copy-id") || "";
        try {
          await navigator.clipboard.writeText(value);
          const original = button.textContent;
          button.textContent = "Copiado";
          window.setTimeout(() => { button.textContent = original; }, 1400);
        } catch (_error) {
          button.textContent = "Selecione o ID";
        }
      });
    });
  };

  const homeReaderSearch = () => {
    const form = document.querySelector("[data-reader-home-search]");
    if (!form) return;
    const input = form.querySelector("input[type='search']");
    const results = form.querySelector("[role='listbox']");
    if (!input || !results) return;
    let documents = [];
    let timer = 0;
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const siteRoot = pathParts[0] === "vademecum-md" ? `/${pathParts[0]}/` : "/";
    const normalize = (value) => String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
    const close = () => { results.hidden = true; input.setAttribute("aria-expanded", "false"); };
    const render = () => {
      const query = normalize(input.value.trim());
      results.replaceChildren();
      if (!query || !documents.length) { close(); return; }
      const matches = documents.filter((item) => normalize([item.title, item.canonical_title, item.type, item.number, item.year, item.domain, ...(item.aliases || [])].join(" ")).includes(query));
      matches.sort((a, b) => {
        const rank = (item) => { const title = normalize(item.title); const canonical = normalize(item.canonical_title); return title === query || canonical === query ? 0 : title.startsWith(query) || canonical.startsWith(query) ? 1 : title.includes(query) || canonical.includes(query) ? 2 : 3; };
        return rank(a) - rank(b) || a.title.localeCompare(b.title, "pt-BR");
      });
      matches.splice(6);
      if (!matches.length) { close(); return; }
      matches.forEach((item) => {
        const link = document.createElement("a");
        link.className = "vmd-home-suggestion";
        link.href = `${siteRoot}biblioteca/#${new URLSearchParams({ documento: item.id })}`;
        link.setAttribute("role", "option");
        const title = document.createElement("strong"); title.textContent = item.title;
        const meta = document.createElement("small"); meta.textContent = `${item.typeLabel || item.type} ${item.number}/${item.year} · ${item.domain}`;
        link.append(title, meta); results.appendChild(link);
      });
      results.hidden = false; input.setAttribute("aria-expanded", "true");
    };
    input.addEventListener("input", () => {
      window.clearTimeout(timer);
      if (!documents.length) {
        timer = window.setTimeout(() => fetch(`${siteRoot}biblioteca/catalog.json`).then((response) => { if (!response.ok) throw new Error("Índice indisponível"); return response.json(); }).then((catalog) => { documents = catalog.filter((item) => item.collection === "vademecum"); render(); }).catch(() => close()), 120);
      } else render();
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "Escape") close();
      if (event.key === "ArrowDown" && !results.hidden) { event.preventDefault(); results.querySelector("a")?.focus(); }
    });
    results.addEventListener("keydown", (event) => {
      if (event.key === "Escape") { close(); input.focus(); }
    });
    document.addEventListener("click", (event) => { if (!form.contains(event.target)) close(); });
    window.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k" && !document.querySelector("[data-reader-app]")) { event.preventDefault(); input.focus(); }
    });
  };

  const boot = () => {
    reveal();
    copyIds();
    homeReaderSearch();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
