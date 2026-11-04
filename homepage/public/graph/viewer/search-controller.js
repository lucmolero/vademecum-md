import { prepareSearch, searchNorms } from './graph-core.js?v=graph-startup-3';

/** Accessible combobox: one focus target, cancellable requests, cached normalization. */
export function createSearchController({ input, list, status, load, select }) {
  let indexPromise, timer, generation = 0, rows = [], active = -1;
  const abort = new AbortController(), options = { signal: abort.signal };
  function setActive(index) {
    active = index;
    [...list.children].forEach((option, at) => option.setAttribute('aria-selected', String(at === active)));
    const option = list.children[active];
    if (option) {
      input.setAttribute('aria-activedescendant', option.id);
      option.scrollIntoView({ block: 'nearest' });
    } else input.removeAttribute('aria-activedescendant');
  }
  function close() {
    generation++; clearTimeout(timer);
    list.classList.remove('open'); input.setAttribute('aria-expanded', 'false'); setActive(-1);
  }
  function choose(index) {
    const row = rows[index];
    if (!row) return;
    input.value = row[1]; close(); select(row[0]);
  }
  function render(matches) {
    rows = matches; active = -1; list.replaceChildren();
    input.removeAttribute('aria-activedescendant');
    for (const [index, row] of rows.entries()) {
      const option = document.createElement('button');
      option.type = 'button'; option.className = 'suggestion'; option.id = `graph-option-${index}`;
      option.tabIndex = -1; option.setAttribute('role', 'option'); option.setAttribute('aria-selected', 'false');
      const title = document.createElement('span'), meta = document.createElement('small');
      title.textContent = row[1]; meta.textContent = `${row[2] || 'Norma'} · ${row[4] ? 'Com relações no recorte' : 'Sem citação direta neste recorte'}`;
      option.append(title, meta);
      option.addEventListener('mousedown', event => event.preventDefault());
      option.addEventListener('click', () => choose(index)); list.append(option);
    }
    if (!rows.length) {
      const empty = document.createElement('div'); empty.className = 'search-empty';
      empty.textContent = 'Nenhuma norma encontrada. Tente o número ou outro nome.'; list.append(empty);
    }
    list.classList.add('open'); input.setAttribute('aria-expanded', 'true');
    status.textContent = `${rows.length} ${rows.length === 1 ? 'norma encontrada' : 'normas encontradas'}.`;
  }
  input.addEventListener('input', () => {
    close();
    const query = input.value.trim();
    if (query.length < 2) { status.textContent = ''; return; }
    const token = generation;
    timer = setTimeout(async () => {
      status.textContent = 'Buscando normas…';
      try {
        indexPromise ??= load().then(prepareSearch).catch(error => { indexPromise = null; throw error; });
        const index = await indexPromise;
        if (token === generation) render(searchNorms(index, query));
      } catch {
        if (token === generation) status.textContent = 'Não foi possível buscar. Digite novamente para tentar outra vez.';
      }
    }, 120);
  }, options);
  input.addEventListener('keydown', event => {
    const open = list.classList.contains('open');
    if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && open && rows.length) {
      event.preventDefault();
      setActive(active < 0 ? (event.key === 'ArrowDown' ? 0 : rows.length - 1) : (active + (event.key === 'ArrowDown' ? 1 : -1) + rows.length) % rows.length);
    } else if ((event.key === 'Home' || event.key === 'End') && open && rows.length) {
      event.preventDefault(); setActive(event.key === 'Home' ? 0 : rows.length - 1);
    } else if (event.key === 'Enter' && open && rows.length) {
      event.preventDefault(); choose(active < 0 ? 0 : active);
    } else if (event.key === 'Escape' && open) {
      event.preventDefault(); event.stopPropagation(); close();
    } else if (event.key === 'Tab') close();
  }, options);
  document.addEventListener('pointerdown', event => {
    if (!input.parentElement.contains(event.target)) close();
  }, options);
  return { close, destroy() { close(); abort.abort(); } };
}
