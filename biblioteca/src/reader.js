// Independent reader: DOM text ranges, horizontal CSS columns and local positions.
const foldText = text => {
  let folded = '';
  const map = [];
  for (let index = 0; index < text.length;) {
    const character = String.fromCodePoint(text.codePointAt(index));
    const normalized = character.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('pt-BR');
    for (const unit of normalized) {
      folded += unit;
      for (let i = 0; i < unit.length; i++) map.push(index);
    }
    index += character.length;
  }
  return { folded, map };
};

export class Reader extends EventTarget {
  constructor(viewport) {
    super();
    this.viewport = viewport;
    this.article = document.createElement('article');
    this.article.className = 'document-content';
    viewport.replaceChildren(this.article);
    this.section = 0; this.page = 0; this.pages = 1; this.seekToken = 0;
    this.renderedFlow = null; this.sectionElements = [];
    this.settings = { size: 18, spacing: 1.6, font: 'serif', flow: 'scroll' };
    this.observer = new ResizeObserver(() => this.layout());
    this.observer.observe(viewport);
    this.article.addEventListener('click', event => {
      const a = event.target.closest('a');
      if (!a) return;
      if (a.getAttribute('href')?.startsWith('#')) {
        event.preventDefault(); this.goAnchor(a.getAttribute('href').slice(1));
      } else { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    });
    this.article.addEventListener('pointerup', () => {
      const selection = document.getSelection();
      if (!selection?.rangeCount || selection.isCollapsed || !this.article.contains(selection.anchorNode) || !this.article.contains(selection.focusNode)) return;
      const range = selection.getRangeAt(0);
      const startElement = range.startContainer.nodeType === Node.ELEMENT_NODE ? range.startContainer : range.startContainer.parentElement;
      const endElement = range.endContainer.nodeType === Node.ELEMENT_NODE ? range.endContainer : range.endContainer.parentElement;
      const startSection = startElement?.closest('[data-reader-section]');
      const endSection = endElement?.closest('[data-reader-section]');
      if (this.settings.flow === 'scroll' && startSection !== endSection) return;
      const root = startSection || this.article;
      const section = startSection ? Number(startSection.dataset.readerSection) : this.section;
      const before = document.createRange(); before.selectNodeContents(root); before.setEnd(range.startContainer, range.startOffset);
      const start = before.toString().length;
      this.dispatchEvent(new CustomEvent('selection', { detail: { section, start, end: start + range.toString().length, text: range.toString() } }));
    });
    viewport.addEventListener('scroll', () => {
      if (this.settings.flow === 'scroll') this.emitPosition();
    });
  }
  async open(book, position) {
    this.book = book;
    this.notes = [];
    await this.goTo(position || { section: 0, page: 0 });
  }
  renderContent(index) {
    this.article.replaceChildren();
    this.sectionElements = [];
    if (this.settings.flow === 'scroll') {
      this.sectionElements = this.book.sections.map((data, section) => {
        const element = document.createElement('section');
        element.className = 'reader-section';
        element.dataset.readerSection = String(section);
        element.innerHTML = data.html;
        this.article.append(element);
        return element;
      });
    } else {
      this.article.innerHTML = this.book.sections[index].html;
    }
    if (this.book.source) {
      const base = new URL('.', new URL(this.book.source.split('/').map(encodeURIComponent).join('/'), document.baseURI));
      this.article.querySelectorAll('img[src]').forEach(img => { img.src = new URL(img.getAttribute('src'), base).href; });
    }
    for (const image of this.article.querySelectorAll('img')) image.addEventListener('load', () => this.layout(), { once: true });
    this.renderedFlow = this.settings.flow;
  }
  sectionRoot(index) {
    if (this.settings.flow === 'scroll') return this.sectionElements[index] || null;
    return index === this.section ? this.article : null;
  }
  sectionAtScroll() {
    if (this.settings.flow !== 'scroll' || !this.sectionElements.length) return this.section;
    const viewportRect = this.viewport.getBoundingClientRect();
    const marker = viewportRect.top + Math.min(64, this.viewport.clientHeight * .12);
    let current = 0;
    for (let index = 0; index < this.sectionElements.length; index++) {
      if (this.sectionElements[index].getBoundingClientRect().top <= marker) current = index;
      else break;
    }
    return current;
  }
  scrollToSection(index, within = 0) {
    const element = this.sectionElements[index];
    if (!element) return;
    const viewportRect = this.viewport.getBoundingClientRect();
    const start = element.getBoundingClientRect().top - viewportRect.top + this.viewport.scrollTop;
    const span = Math.max(0, element.offsetHeight - this.viewport.clientHeight);
    this.viewport.scrollTop = Math.max(0, Math.min(this.viewport.scrollHeight - this.viewport.clientHeight, start + Math.max(0, Math.min(1, within)) * span));
  }
  findAnchor(root, value) {
    let decoded = value;
    try { decoded = decodeURIComponent(value); } catch { /* Keep literal fragments that are not valid URI escapes. */ }
    const get = id => root.getElementById?.(id) || root.querySelector?.('#' + CSS.escape(id));
    const direct = get(decoded) || get(value);
    if (direct) return direct;
    const slug = text => text.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('pt-BR').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    const wanted = slug(decoded);
    for (const element of root.querySelectorAll?.('[id]') || []) {
      const id = element.id.replace(/^(?:doc|heading)-/, '');
      if (slug(id) === wanted || slug(element.textContent || '') === wanted) return element;
    }
    return null;
  }
  async goTo(target) {
    const index = Math.max(0, Math.min(this.book.sections.length - 1, Number(target.section) || 0));
    const rebuild = this.currentBook !== this.book || this.renderedFlow !== this.settings.flow || (this.settings.flow !== 'scroll' && this.section !== index);
    if (rebuild) {
      this.section = index; this.currentBook = this.book;
      this.renderContent(index);
      this.page = 0; this.viewport.scrollTo(0, 0);
    } else this.section = index;
    this.layout(false);
    this.page = Math.max(0, Math.min(this.pages - 1, Number(target.page) || 0));
    if (target.anchor) {
      const element = this.findAnchor(this.article, target.anchor);
      if (element && this.article.contains(element)) this.navigateToElement(element);
      else if (this.settings.flow === 'scroll') this.scrollToSection(index);
    } else if (target.offset != null) {
      const range = this.textRange(target.offset, target.offset + 1, index);
      if (range) this.navigateToRect(range.getBoundingClientRect()); else this.scrollPage();
    } else if (this.settings.flow === 'scroll' && target.scrollScope === 'document' && Number.isFinite(target.scroll)) {
      const span = this.viewport.scrollHeight - this.viewport.clientHeight;
      this.viewport.scrollTop = Math.max(0, Math.min(span, target.scroll * span));
    } else if (this.settings.flow === 'scroll') {
      this.scrollToSection(index, Number.isFinite(target.scroll) && target.scrollScope !== 'document' ? target.scroll : 0);
    } else this.scrollPage();
    this.drawNotes(); this.emitPosition();
  }
  layout(emit = true) {
    if (!this.book || !this.viewport.clientWidth) return;
    const { size, spacing, font, flow } = this.settings;
    const columns = this.viewport.clientWidth >= 750 ? 2 : 1;
    this.viewport.classList.toggle('scrolled', flow === 'scroll');
    Object.assign(this.article.style, {
      fontSize: `${size}px`, lineHeight: String(spacing),
      fontFamily: font === 'serif' ? 'var(--reading-serif)' : 'var(--reading-sans)',
      height: flow === 'scroll' ? 'auto' : `${this.viewport.clientHeight}px`,
      columnCount: flow === 'scroll' ? 'auto' : String(columns),
      columnGap: flow === 'scroll' ? 'normal' : '48px',
    });
    this.step = this.viewport.clientWidth + 48;
    this.pages = flow === 'scroll' ? 1 : Math.max(1, Math.ceil((this.article.scrollWidth + 48) / this.step));
    this.page = Math.min(this.page, this.pages - 1);
    if (flow !== 'scroll') this.scrollPage();
    if (emit) this.emitPosition();
  }
  configure(settings) {
    const changeFlow = this.book && settings.flow !== this.settings.flow;
    let section = this.section, within = 0;
    if (changeFlow) {
      if (this.settings.flow === 'scroll') {
        const element = this.sectionElements[section];
        const viewportRect = this.viewport.getBoundingClientRect();
        const start = element ? element.getBoundingClientRect().top - viewportRect.top + this.viewport.scrollTop : 0;
        const span = Math.max(0, (element?.offsetHeight || 0) - this.viewport.clientHeight);
        within = span <= 0 ? 0 : Math.max(0, Math.min(1, (this.viewport.scrollTop - start) / span));
      } else within = this.pages > 1 ? this.page / (this.pages - 1) : 0;
    }
    Object.assign(this.settings, settings);
    if (changeFlow) {
      if (this.settings.flow === 'scroll') void this.goTo({ section, scroll: within });
      else void this.goTo({ section, page: 0 }).then(() => {
        this.page = Math.round(within * (this.pages - 1));
        this.scrollPage(); this.emitPosition();
      });
    } else this.layout();
  }
  scrollPage() { if (this.settings.flow !== 'scroll') this.viewport.scrollLeft = this.page * this.step; }
  navigateToRect(rect) {
    if (!rect || !Number.isFinite(rect.left) || !Number.isFinite(rect.top)) return;
    const viewportRect = this.viewport.getBoundingClientRect();
    if (this.settings.flow === 'scroll') this.viewport.scrollTop += rect.top - viewportRect.top;
    else { this.page = Math.max(0, Math.min(this.pages - 1, Math.floor((rect.left - viewportRect.left + this.viewport.scrollLeft + 2) / this.step))); this.scrollPage(); }
  }
  navigateToElement(element) {
    const section = element.closest('[data-reader-section]');
    if (section) this.section = Number(section.dataset.readerSection);
    this.navigateToRect(element.getBoundingClientRect());
  }
  currentHeading() {
    if (!this.book) return null;
    const root = this.sectionRoot(this.settings.flow === 'scroll' ? this.sectionAtScroll() : this.section) || this.article;
    const headings = [...root.querySelectorAll('h1[id],h2[id],h3[id],h4[id],h5[id],h6[id]')];
    if (!headings.length) return null;
    if (this.settings.flow !== 'scroll') return headings.find(item => item.getBoundingClientRect().left >= this.viewport.getBoundingClientRect().left - 2) || headings[0];
    const top = this.viewport.getBoundingClientRect().top + 80;
    return headings.filter(item => item.getBoundingClientRect().top <= top).at(-1) || headings[0];
  }
  async goAnchor(id) {
    if (!this.book || !id) return;
    const anchor = this.findAnchor(this.article, id);
    if (this.settings.flow === 'scroll') {
      if (anchor) {
        this.navigateToElement(anchor);
        this.drawNotes(); this.emitPosition();
        this.dispatchEvent(new CustomEvent('anchor', { detail: { id: anchor.id } }));
        return;
      }
    }
    for (const [section, data] of this.book.sections.entries()) {
      const doc = new DOMParser().parseFromString(data.html, 'text/html');
      const element = this.findAnchor(doc, id);
      if (element) {
        await this.goTo({ section, anchor: element.id });
        this.dispatchEvent(new CustomEvent('anchor', { detail: { id: element.id } }));
        return;
      }
    }
  }
  async next() {
    if (!this.book) return;
    if (this.settings.flow === 'scroll') { this.viewport.scrollBy(0, this.viewport.clientHeight * .9); return; }
    if (this.page < this.pages - 1) { this.page++; this.scrollPage(); this.emitPosition(); }
    else if (this.section < this.book.sections.length - 1) await this.goTo({ section: this.section + 1 });
  }
  async previous() {
    if (!this.book) return;
    if (this.settings.flow === 'scroll') { this.viewport.scrollBy(0, -this.viewport.clientHeight * .9); return; }
    if (this.page > 0) { this.page--; this.scrollPage(); this.emitPosition(); }
    else if (this.section > 0) {
      await this.goTo({ section: this.section - 1 });
      if (this.settings.flow === 'scroll') {
        this.viewport.scrollTop = Math.max(0, this.viewport.scrollHeight - this.viewport.clientHeight);
        this.emitPosition();
      } else {
        this.page = this.pages - 1; this.scrollPage(); this.emitPosition();
      }
    }
  }
  async seek(fraction) {
    if (!this.book) return;
    const value = Math.max(0, Math.min(1, Number(fraction) || 0));
    if (this.settings.flow === 'scroll') {
      const span = this.viewport.scrollHeight - this.viewport.clientHeight;
      this.viewport.scrollTop = Math.max(0, Math.min(span, value * span));
      this.emitPosition();
      return;
    }
    const token = (this.seekToken = (this.seekToken || 0) + 1);
    const total = this.book.sections.length;
    const index = Math.min(total - 1, Math.floor(value * total));
    await this.goTo({ section: index });
    if (token !== this.seekToken) return;
    const local = value * total - index;
    if (this.pages > 1) {
      this.page = Math.max(0, Math.min(this.pages - 1, Math.floor(local * this.pages)));
      this.scrollPage();
    }
    this.emitPosition();
  }
  emitPosition() {
    if (!this.book) return;
    const total = this.book.sections.length || 1;
    let within, scroll = null;
    if (this.settings.flow === 'scroll') {
      this.section = this.sectionAtScroll();
      const span = this.viewport.scrollHeight - this.viewport.clientHeight;
      scroll = span <= 0 ? 0 : Math.max(0, Math.min(1, this.viewport.scrollTop / span));
      const fraction = scroll;
      const detail = { section: this.section, page: 0, pages: 1, fraction, scroll, scrollScope: 'document', label: this.book.sections[this.section].label };
      this.dispatchEvent(new CustomEvent('position', { detail }));
      return;
    } else {
      within = this.pages > 1 ? this.page / (this.pages - 1) : (this.section === total - 1 ? 1 : 0);
    }
    const fraction = Math.max(0, Math.min(1, (this.section + within) / total));
    const detail = { section: this.section, page: this.page, pages: this.pages, fraction, scroll, label: this.book.sections[this.section].label };
    this.dispatchEvent(new CustomEvent('position', { detail }));
  }
  textRange(start, end, section = this.section) {
    if (!Number.isFinite(start) || !Number.isFinite(end) || start < 0 || end <= start) return null;
    const root = this.sectionRoot(section);
    if (!root) return null;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const range = document.createRange(); let offset = 0, found = false;
    while (walker.nextNode()) {
      const text = walker.currentNode, next = offset + text.textContent.length;
      if (!found && start < next) { range.setStart(text, Math.max(0, start - offset)); found = true; }
      if (found && end <= next) { range.setEnd(text, Math.max(0, end - offset)); return range; }
      offset = next;
    }
    return null;
  }
  search(query) {
    if (!this.book || !query.trim()) return [];
    const { folded: needle } = foldText(query.trim());
    if (!needle) return [];
    const results = [];
    this.book.sections.forEach((section, index) => {
      const doc = new DOMParser().parseFromString(section.html, 'text/html');
      const text = doc.body.textContent || '';
      const { folded, map } = foldText(text);
      let offset = folded.indexOf(needle);
      while (offset !== -1 && results.length < 500) {
        const start = map[offset] ?? 0;
        const end = offset + needle.length < map.length ? map[offset + needle.length] : text.length;
        results.push({ section: index, offset: start, label: section.label, before: text.slice(Math.max(0, start - 50), start), match: text.slice(start, end), after: text.slice(end, end + 70) });
        offset = folded.indexOf(needle, offset + Math.max(1, needle.length));
      }
    });
    return results;
  }
  drawNotes() {
    if (!globalThis.CSS?.highlights || !globalThis.Highlight) return;
    const notes = Array.isArray(this.notes) ? this.notes : [];
    const ranges = notes.filter(note => this.settings.flow === 'scroll' || note.section === this.section).map(note => this.textRange(note.start, note.end, note.section)).filter(Boolean);
    CSS.highlights.set('notes', new Highlight(...ranges));
  }
  clear() { this.book = null; this.currentBook = null; this.renderedFlow = null; this.sectionElements = []; this.section = 0; this.page = 0; this.pages = 1; this.viewport.scrollTo(0, 0); this.article.replaceChildren(); globalThis.CSS?.highlights?.delete('notes'); }
}
