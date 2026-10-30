/** Local, browser-owned persistence. A successful write means its transaction committed. */
export class LibraryStore {
  constructor(indexedDB = globalThis.indexedDB) {
    this.indexedDB = indexedDB;
    this.database = null;
    this.opening = null;
  }

  async init() {
    if (this.database) return this;
    if (this.opening) return this.opening;
    if (!this.indexedDB) throw new Error('O armazenamento IndexedDB não está disponível neste navegador.');
    this.opening = new Promise((resolve, reject) => {
      let failed = false;
      const request = this.indexedDB.open('biblioteca-library', 1);
      const fail = error => { failed = true; reject(error); };
      request.onupgradeneeded = () => {
        const database = request.result;
        try {
          if (!database.objectStoreNames.contains('books')) database.createObjectStore('books', { keyPath: 'id' });
          if (!database.objectStoreNames.contains('state')) database.createObjectStore('state', { keyPath: 'key' });
        } catch (error) {
          request.transaction?.abort();
          fail(error);
        }
      };
      request.onerror = () => fail(request.error || new Error('Não foi possível abrir o armazenamento local.'));
      request.onblocked = () => fail(new Error('O armazenamento está bloqueado por outra aba. Feche as outras abas da biblioteca e tente novamente.'));
      request.onsuccess = () => {
        const database = request.result;
        if (failed) { database.close(); return; }
        this.database = database;
        database.onversionchange = () => {
          database.close();
          if (this.database === database) this.database = null;
        };
        database.onclose = () => { if (this.database === database) this.database = null; };
        resolve(this);
      };
    });
    try { return await this.opening; }
    finally { this.opening = null; }
  }

  async transaction(storeName, mode, operation) {
    await this.init();
    return new Promise((resolve, reject) => {
      let transaction, result;
      try {
        transaction = this.database.transaction(storeName, mode);
        transaction.oncomplete = () => resolve(result);
        transaction.onerror = event => reject(transaction.error || event.target?.error || new Error('Falha ao gravar no armazenamento local.'));
        transaction.onabort = () => reject(transaction.error || new Error('A operação de armazenamento foi cancelada. Nenhuma gravação foi confirmada.'));
        const request = operation(transaction.objectStore(storeName));
        request.onsuccess = () => { result = request.result; };
      } catch (error) {
        try { transaction?.abort(); } catch { /* It may have already completed or aborted. */ }
        reject(error);
      }
    });
  }

  async getBooks() {
    return this.transaction('books', 'readonly', store => store.getAll());
  }

  // Preserve the complete imported document, including its source content.
  async putBook(book) {
    return this.transaction('books', 'readwrite', store => store.put(book));
  }

  async deleteBook(id) {
    return this.transaction('books', 'readwrite', store => store.delete(id));
  }

  async getState() {
    const entry = await this.transaction('state', 'readonly', store => store.get('library'));
    const state = entry?.value;
    return {
      ...(isObject(state) ? state : {}),
      // Document IDs are dictionary keys, never object prototype properties.
      // Rebuild after IDB structured cloning, which does not retain null prototypes.
      records: Object.assign(Object.create(null), isObject(state?.records) ? state.records : {}),
      folders: Array.isArray(state?.folders) ? state.folders : [],
      preferences: {
        sort: 'lastReadAt', direction: 'desc', coverWidth: 120,
        ...(isObject(state?.preferences) ? state.preferences : {}),
      },
    };
  }

  async saveState(state) {
    return this.transaction('state', 'readwrite', store => store.put({ key: 'library', value: state }));
  }
}

const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const finite = value => typeof value === 'number' && Number.isFinite(value);
const collator = new Intl.Collator('pt-BR', { sensitivity: 'base', numeric: true });

/** Case- and accent-insensitive text for library search. */
export function normalizeSearch(text) {
  return String(text ?? '').normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('pt-BR').trim();
}

export function readingStatus(progress) {
  const value = finite(progress) ? clamp(progress, 0, 1) : 0;
  return value <= 0.02 ? 'new' : value >= 0.98 ? 'finished' : 'reading';
}

function timestamp(value) {
  if (finite(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    const parsed = Date.parse(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return 0;
}

function noteText(notes) {
  if (typeof notes === 'string') return notes;
  if (Array.isArray(notes)) return notes.map(noteText).join(' ');
  if (isObject(notes)) return [notes.text, notes.note].filter(text => typeof text === 'string').join(' ');
  return '';
}

/** Return a new list; filters never mutate the books or the caller's list. */
export function filterAndSortBooks(books, options = {}, notesByBook = {}) {
  const {
    query = '', status = 'all', tags = [], folder = null,
    sort = 'lastReadAt', direction = 'desc',
  } = options;
  const needle = normalizeSearch(query);
  const selectedTags = Array.isArray(tags) ? tags : [];
  const sign = direction === 'asc' ? 1 : -1;
  const numericFields = new Set(['importedAt', 'lastReadAt', 'progress']);
  return books.filter(book => {
    const bookTags = Array.isArray(book.tags) ? book.tags : [];
    if (status !== 'all' && readingStatus(book.progress) !== status) return false;
    if (folder !== null && (book.folder ?? '') !== folder) return false;
    if (selectedTags.includes('__untagged__')) {
      if (bookTags.length) return false;
    } else if (!selectedTags.every(tag => bookTags.includes(tag))) return false;
    if (needle) {
      const notes = notesByBook instanceof Map ? notesByBook.get(book.id)
        : notesByBook && own(notesByBook, book.id) ? notesByBook[book.id] : undefined;
      const aliases = Array.isArray(book.aliases) ? book.aliases : [];
      const haystack = normalizeSearch([book.title, book.author, book.description, book.number, book.year, ...aliases, ...bookTags, noteText(notes)].join(' '));
      if (!haystack.includes(needle)) return false;
    }
    return true;
  }).sort((a, b) => {
    let comparison;
    if (numericFields.has(sort)) {
      const first = sort === 'progress' ? (finite(a[sort]) ? a[sort] : 0) : timestamp(a[sort]);
      const second = sort === 'progress' ? (finite(b[sort]) ? b[sort] : 0) : timestamp(b[sort]);
      comparison = first - second;
    } else {
      comparison = collator.compare(String(a[sort] ?? ''), String(b[sort] ?? ''));
    }
    if (comparison) return comparison * sign;
    // A deterministic ID tie-break is independent of the selected sort direction.
    const firstId = String(a.id ?? '');
    const secondId = String(b.id ?? '');
    return collator.compare(firstId, secondId) || (firstId < secondId ? -1 : firstId > secondId ? 1 : 0);
  });
}

/** Normalize a metadata patch, retaining only supplied, supported fields. */
export function normalizeMetadata(value) {
  if (!isObject(value)) return {};
  const result = {};
  for (const key of ['title', 'author', 'description', 'folder', 'cover']) {
    if (own(value, key) && typeof value[key] === 'string') result[key] = value[key].trim();
  }
  if (own(value, 'tags') && Array.isArray(value.tags)) {
    result.tags = [...new Set(value.tags.filter(tag => typeof tag === 'string').map(tag => tag.trim()).filter(Boolean))];
  }
  if (own(value, 'progress') && finite(value.progress)) result.progress = clamp(value.progress, 0, 1);
  if (own(value, 'rating') && finite(value.rating)) result.rating = clamp(value.rating, 0, 5);
  if (own(value, 'readingSeconds') && finite(value.readingSeconds)) result.readingSeconds = Math.max(0, value.readingSeconds);
  for (const key of ['favorite', 'hidden']) {
    if (own(value, key) && typeof value[key] === 'boolean') result[key] = value[key];
  }
  for (const key of ['importedAt', 'lastReadAt']) {
    if (!own(value, key)) continue;
    if (finite(value[key])) result[key] = Math.max(0, value[key]);
    else if (typeof value[key] === 'string' && value[key].trim()) {
      const parsed = Date.parse(value[key]);
      if (Number.isFinite(parsed)) result[key] = Math.max(0, parsed);
    }
  }
  if (own(value, 'status') && ['new', 'reading', 'finished'].includes(value.status)) result.status = value.status;
  return result;
}
