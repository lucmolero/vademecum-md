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

  const boot = () => {
    reveal();
    copyIds();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
