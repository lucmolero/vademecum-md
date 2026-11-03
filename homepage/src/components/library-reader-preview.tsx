import { useEffect, useRef } from 'react';
import { Library } from '../../../biblioteca/src/library.js';
import { Reader } from '../../../biblioteca/src/reader.js';
import { PREVIEW_BOOKS, PREVIEW_CATALOG } from '../../../biblioteca/src/preview-data.js';
import { openLibrary } from './library-destination';
import './library-reader-preview.css';

const previewSettings = { theme: 'light', size: 16, spacing: 1.65, font: 'sans-serif', flow: 'scroll', flowVersion: 3, motion: 'full' };
const initialBook = PREVIEW_BOOKS['br-federal-lei_ordinaria-14133-2021'];
const libraryStyles = ['style.css', 'library.css', 'glass.css', 'home-visual.css'];

const previewMarkup = `
  <svg class="symbols" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><defs>
    <symbol id="i-books" viewBox="0 0 24 24"><path d="M12 6v15M3 4c3.5-.9 6.5-.3 9 2 2.5-2.3 5.5-2.9 9-2v15c-3.4-.8-6.4-.2-9 2-2.6-1.8-5.6-2.5-9-2Z"/></symbol>
    <symbol id="i-search" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></symbol>
    <symbol id="i-bookmark" viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4-6 4Z"/></symbol>
    <symbol id="i-list" viewBox="0 0 24 24"><path d="M8 6h13M8 12h13M8 18h13M3 6h1M3 12h1M3 18h1"/></symbol>
    <symbol id="i-note" viewBox="0 0 24 24"><path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5M9 12h7M9 16h7"/></symbol>
    <symbol id="i-prev" viewBox="0 0 24 24"><path d="m15 5-7 7 7 7"/></symbol>
    <symbol id="i-next" viewBox="0 0 24 24"><path d="m9 5 7 7-7 7"/></symbol>
    <symbol id="i-close" viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18"/></symbol>
    <symbol id="i-panel" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></symbol>
    <symbol id="i-repository" viewBox="0 0 24 24"><path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11M9 8h6"/></symbol>
    <symbol id="i-github" viewBox="0 0 24 24"><path d="M12 .8a11.2 11.2 0 0 0-3.54 21.83c.56.1.76-.24.76-.54v-2.1c-3.1.68-3.76-1.32-3.76-1.32-.5-1.28-1.24-1.62-1.24-1.62-1.02-.7.08-.68.08-.68 1.12.08 1.72 1.15 1.72 1.15 1 .1.78 2.2 3.6 1.7.1-.73.4-1.23.7-1.52-2.48-.28-5.1-1.24-5.1-5.53 0-1.22.44-2.21 1.16-2.99-.12-.28-.5-1.42.11-2.96 0 0 .95-.3 3.08 1.14a10.7 10.7 0 0 1 5.6 0c2.13-1.44 3.07-1.14 3.07-1.14.61 1.54.23 2.68.12 2.96.72.78 1.15 1.77 1.15 2.99 0 4.3-2.62 5.25-5.12 5.53.4.35.75 1.02.75 2.06v3.05c0 .3.2.65.77.54A11.2 11.2 0 0 0 12 .8Z"/></symbol>
  </defs></svg>
  <div class="live-preview-stage">
    <section class="live-library-panel" aria-label="Biblioteca real">
      <div class="live-library-mount"></div>
    </section>
    <section class="live-reader-panel" aria-label="Leitor real">
      <div id="reading" class="live-reading">
        <aside id="sidebar">
          <header class="side-header"><div class="button" aria-hidden="true"><svg><use href="#i-books"/></svg><span>Biblioteca</span></div><div class="spacer"></div><span class="reader-demo-label">LEITOR</span></header>
          <div class="book-info"><div class="mini-cover">V</div><div><strong data-reader-title></strong><small data-reader-author></small></div></div>
          <div id="toc-panel" class="side-panel"><nav data-reader-toc aria-label="Sumário"></nav></div>
          <div class="side-tabs" aria-label="Recursos do leitor"><button aria-label="Sumário" aria-selected="true"><svg><use href="#i-list"/></svg></button><button aria-label="Anotações" disabled><svg><use href="#i-note"/></svg></button><button aria-label="Marcadores" disabled><svg><use href="#i-bookmark"/></svg></button></div>
        </aside>
        <div class="reader-area">
          <header class="reader-header"><button id="preview-toggle-toc" class="button" type="button" aria-label="Ocultar sumário" aria-expanded="true"><svg><use href="#i-panel"/></svg></button><span data-reader-context aria-live="polite"></span><div class="spacer"></div></header>
          <div class="page-padding"><div id="viewport" tabindex="0" aria-label="Conteúdo do documento"></div></div>
          <footer class="reader-footer"><span data-reader-section></span><span class="reader-progress-label" data-reader-progress>0%</span></footer>
        </div>
      </div>
    </section>
  </div>`;

export function LibraryReaderPreview({ mode = 'split' }: { mode?: 'split' | 'library' | 'reader' }) {
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const shadow = element.shadowRoot || element.attachShadow({ mode: 'open' });
    shadow.replaceChildren();
    const base = new URL('https://lucmolero.github.io/vademecum-md/biblioteca/');
    const previewTemplate = document.createElement('template');
    previewTemplate.innerHTML = previewMarkup;
    shadow.append(previewTemplate.content);

    const overrides = document.createElement('style');
    overrides.textContent = `
      :host{display:block;--paper:#f7f7f7;--paper-2:#f0f0f0;--surface:#fff;--surface-2:#f5f5f5;--ink:#111;--ink-2:#363636;--muted:#707070;--line:rgba(0,0,0,.1);--line-strong:rgba(0,0,0,.18);--accent:#171717;--accent-2:#555;--accent-soft:#ececec;--on-accent:#fff;--gold:#555;--hover:rgba(0,0,0,.045);--active:rgba(0,0,0,.075);--panel:#f1f1f1;--reading-sans:Outfit,"Segoe UI",system-ui,sans-serif;--ui-font:Outfit,"Segoe UI",system-ui,sans-serif;--display-font:Outfit,"Segoe UI",system-ui,sans-serif;--reading-serif:Georgia,"Times New Roman",serif;--ease:cubic-bezier(.23,1,.32,1);--ease-out:cubic-bezier(.23,1,.32,1);--shadow-1:0 4px 14px -9px rgba(0,0,0,.18);--shadow-2:0 12px 30px -19px rgba(0,0,0,.2);--shadow-3:0 22px 52px -32px rgba(0,0,0,.24);--shadow-4:0 34px 76px -42px rgba(0,0,0,.28);color-scheme:light;font:14px/1.5 var(--ui-font);color:var(--ink)}
      .live-preview-stage{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;min-height:650px;padding:14px;border:1px solid var(--line);border-radius:18px;background:var(--paper-2);overflow:hidden}
      :host([data-preview-mode="library"]) .live-preview-stage,:host([data-preview-mode="reader"]) .live-preview-stage{grid-template-columns:minmax(0,1fr)}
      :host([data-preview-mode="library"]) .live-reader-panel,:host([data-preview-mode="reader"]) .live-library-panel{display:none}
      .live-library-panel,.live-reader-panel{position:relative;min-width:0;min-height:620px;overflow:hidden;border:1px solid var(--line);border-radius:12px;background:var(--surface)}
      .live-library-panel>.shelf-shell{position:absolute;inset:0;overflow:hidden}
      .live-library-panel>.shelf-shell .shelf-brand,.live-library-panel>.shelf-shell .shelf-project-links{display:none!important}
      .live-library-panel>.shelf-shell .shelf-toolbar{display:flex;min-height:52px;padding:8px 14px;gap:8px}
      .live-library-panel>.shelf-shell .shelf-toolbar-spacer{display:none}
      .live-library-panel>.shelf-shell .shelf-search{width:100%;max-width:none;height:40px}
      .live-library-panel>.shelf-shell .shelf-toolbar-actions{display:none!important}
      .live-library-panel>.shelf-shell .shelf-kbd{display:none!important}
      .live-library-panel>.shelf-shell .shelf-layout{min-height:0;height:calc(100% - 52px);gap:0;padding:4px}
      .live-library-panel>.shelf-shell .shelf-rail{display:none!important}
      .live-library-panel>.shelf-shell .shelf-workspace{width:100%;min-width:0}
      .live-library-panel>.shelf-shell .shelf-heading{font-size:clamp(26px,3vw,38px)}
      .live-library-panel>.shelf-shell .shelf-content{padding:10px 14px 36px}
      .live-library-panel>.shelf-shell .shelf-section-head{display:block;padding:8px 4px 14px}
      .live-library-panel>.shelf-shell .shelf-continue{display:none!important}
      .live-library-panel>.shelf-shell .shelf-eyebrow{margin-bottom:6px}
      .live-library-panel>.shelf-shell .shelf-subtitle{margin-top:6px;font-size:10px}
      .live-library-panel>.shelf-shell .shelf-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important}
      .live-library-panel>.shelf-shell .shelf-book-heading{margin-top:8px;font-size:11px}
      #reading.live-reading{width:100%;height:100%;min-width:0;position:relative;gap:0;padding:0;background:var(--paper);animation:none}
      #reading.live-reading:before,#reading.live-reading:after{display:none}
      #reading.live-reading>#sidebar{width:34%;min-width:150px;max-width:230px;flex:none;min-height:0;padding:8px;border:0;border-right:1px solid var(--line);border-radius:0;background:var(--paper);box-shadow:none}
      .side-header{height:40px;min-height:40px}.side-header>.button{font-size:11px}.reader-demo-label{font-size:8px;letter-spacing:.12em;color:var(--muted)}
      .book-info{min-height:72px;padding:8px;border-radius:10px}.book-info strong{font:500 11px/1.3 var(--display-font)}.book-info small{font-size:8px}
      .mini-cover{display:grid;place-items:center;flex:none;width:30px;height:42px;border-radius:5px;background:var(--accent-soft);color:var(--ink);font:600 14px var(--display-font)}
      .side-panel{padding:6px 2px}.side-panel nav button{padding:7px 8px;font-size:10px}.side-panel nav button[data-level="2"]{padding-left:17px;font-size:9px}
      .side-tabs{padding:5px}.side-tabs button{height:34px}.side-tabs button svg{width:15px;height:15px}
      #reading.live-reading>.reader-area{display:block;min-width:0;min-height:0;flex:1;border-radius:0;box-shadow:none}
      #reading.live-reading .reader-header{left:10px;right:10px;top:4px;height:42px;display:grid;grid-template-columns:34px minmax(0,1fr);align-items:center;gap:1px;padding:0}
      #reading.live-reading .reader-header .button{min-width:30px;min-height:30px;padding:5px;font-size:9px}
      #reading.live-reading .reader-header>.spacer{display:none}
      #reading.live-reading #reader-context{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:9px;color:var(--muted)}
      #reading.live-reading.is-sidebar-hidden>#sidebar{display:none!important}
      #reading.live-reading .page-padding{inset:54px 8px 42px}
      #reading.live-reading #viewport.scrolled .document-content{width:min(100%,560px);padding:16px 12px 30px;font-size:13px;line-height:1.65}
      #reading.live-reading #viewport.scrolled .document-content h2{font-size:17px}
      #reading.live-reading .reader-footer{left:10px;right:10px;bottom:2px;height:34px;gap:6px;font-size:8px}
      .reader-progress-label{font-variant-numeric:tabular-nums}
      @media(max-width:760px){.live-preview-stage{grid-template-columns:minmax(0,1fr);gap:12px;padding:8px}.live-library-panel,.live-reader-panel{min-height:570px}.live-library-panel>.shelf-shell{padding:0}.live-library-panel>.shelf-shell .shelf-layout{padding:4px}.live-library-panel>.shelf-shell .shelf-heading{font-size:29px}#reading.live-reading>#sidebar{width:33%;min-width:120px;padding:6px}}
    `;
    shadow.append(overrides);

    let library: Library | null = null;
    let reader: Reader | null = null;
    let active = true;
    const readerRoot = shadow.querySelector<HTMLElement>('#viewport')!;
    const readerTitle = shadow.querySelector<HTMLElement>('[data-reader-title]')!;
    const readerAuthor = shadow.querySelector<HTMLElement>('[data-reader-author]')!;
    const toc = shadow.querySelector<HTMLElement>('[data-reader-toc]')!;
    const sectionLabel = shadow.querySelector<HTMLElement>('[data-reader-section]')!;
    const progressLabel = shadow.querySelector<HTMLElement>('[data-reader-progress]')!;
    const contextLabel = shadow.querySelector<HTMLElement>('[data-reader-context]')!;
    const readingShell = shadow.querySelector<HTMLElement>('#reading')!;
    const tocToggle = shadow.querySelector<HTMLButtonElement>('#preview-toggle-toc')!;
    const routeLibraryInteraction = (event: Event) => {
      const target = event.target instanceof Element ? event.target : null;
      if (!target) return;
      const search = target.closest('.shelf-search, #library-query');
      const book = target.closest('.shelf-book-open');
      if (!search && !book) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      if (book) {
        const documentId = book.closest<HTMLElement>('[data-book-id]')?.dataset.bookId;
        openLibrary(documentId ? { documentId } : {});
        return;
      }
      openLibrary({ view: 'books' });
    };
    shadow.addEventListener('click', routeLibraryInteraction, true);
    shadow.addEventListener('focusin', routeLibraryInteraction, true);
    tocToggle.addEventListener('click', () => {
      const isOpen = tocToggle.getAttribute('aria-expanded') === 'true';
      readingShell.classList.toggle('is-sidebar-hidden', isOpen);
      tocToggle.setAttribute('aria-expanded', String(!isOpen));
      tocToggle.setAttribute('aria-label', isOpen ? 'Mostrar sumário' : 'Ocultar sumário');
    });

    const stylesReady = Promise.all(libraryStyles.map(async file => {
      const stylesheetUrl = new URL(file, base);
      const response = await fetch(stylesheetUrl);
      if (!response.ok) throw new Error(`Não foi possível carregar o estilo publicado ${file} (${response.status}).`);
      return { file, stylesheetUrl, css: await response.text() };
    })).then(styles => {
      if (!active) return;
      for (const { file, stylesheetUrl, css } of styles) {
      const style = document.createElement('style');
      style.dataset.libraryStylesheet = file;
      style.textContent = css.replace(/url\((['"]?)([^)'\"]+)\1\)/g, (match, _quote: string, path: string) => {
        if (/^(?:data:|https?:|\/|#|%23)/i.test(path)) return match;
        return `url("${new URL(path, stylesheetUrl).href}")`;
      });
      shadow.insertBefore(style, overrides);
      }
    });

    stylesReady.then(async () => {
      if (!active) return;
      const libraryRoot = shadow.querySelector<HTMLElement>('.live-library-mount')!;
      reader = new Reader(readerRoot);
      reader.configure(previewSettings);
      reader.addEventListener('position', event => {
        const detail = (event as CustomEvent<{ fraction: number; label: string }>).detail;
        progressLabel.textContent = `${Math.round((detail.fraction || 0) * 100)}%`;
        sectionLabel.textContent = detail.label || '';
      });
      const selectBook = async (book: PreviewBook) => {
        if (!active || !reader) return;
        readerTitle.textContent = book.title;
        readerAuthor.textContent = book.author || '';
        contextLabel.textContent = book.cardLabel || 'Demonstração';
        toc.replaceChildren();
        for (const item of book.toc || []) {
          const button = document.createElement('button');
          button.textContent = item.label;
          button.dataset.level = String(item.level || 1);
          button.onclick = () => reader?.goTo({ section: item.section, anchor: item.id });
          toc.append(button);
        }
        await reader.open(book, { section: book.id === initialBook.id ? 1 : 0, page: 0 });
      };
      library = new Library(libraryRoot, {
        previewData: { catalog: PREVIEW_CATALOG, books: PREVIEW_BOOKS },
        getNotes: () => [],
        getSettings: () => previewSettings,
        setSettings: () => {},
        getReadingData: () => ({}),
        message: () => {},
        open: book => selectBook(book),
      });
      await library.init();
      await selectBook(initialBook);
    }).catch(error => {
      console.error('Falha ao carregar o visual publicado da Biblioteca.', error);
      const errorLabel = document.createElement('p');
      errorLabel.className = 'preview-load-error';
      errorLabel.textContent = 'Não foi possível carregar o visual publicado da Biblioteca.';
      shadow.querySelector('.live-library-panel')?.append(errorLabel);
    });

    return () => {
      active = false;
      shadow.removeEventListener('click', routeLibraryInteraction, true);
      shadow.removeEventListener('focusin', routeLibraryInteraction, true);
      library?.destroy?.();
      reader?.destroy?.();
      shadow.replaceChildren();
    };
  }, []);

  return <div ref={host} data-preview-mode={mode} className="library-reader-preview" aria-label="Prévia interativa da Biblioteca e do Leitor" />;
}
