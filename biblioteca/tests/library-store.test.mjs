import test from 'node:test';
import assert from 'node:assert/strict';
import { LibraryStore, normalizeSearch, readingStatus, filterAndSortBooks, normalizeMetadata } from '../src/library-store.js';

const books = [
  { id: 'civil', title: 'Código Civil', author: 'União', description: 'Relações privadas', tags: ['Civil', 'Federal'], progress: 0.02, folder: '', importedAt: 100, lastReadAt: 700 },
  { id: 'penal', title: 'Código Penal', author: 'União', tags: ['Penal', 'Federal'], progress: 0.5, folder: 'Federal', importedAt: 300, lastReadAt: 900 },
  { id: 'municipal', title: 'Lei Municipal', author: 'Município', tags: [], progress: 0.98, folder: 'Local', importedAt: 200, lastReadAt: 800 },
];
const ids = list => list.map(book => book.id);

test('search is insensitive to Portuguese accents, case and surrounding spaces', () => {
  assert.equal(normalizeSearch('  CÓDIGO da União  '), 'codigo da uniao');
  assert.equal(normalizeSearch(undefined), '');
  assert.deepEqual(ids(filterAndSortBooks(books, { query: 'CODIGO', sort: 'title', direction: 'asc' })), ['civil', 'penal']);
  assert.deepEqual(ids(filterAndSortBooks(books, { query: 'relacoes' })), ['civil']);
  assert.deepEqual(ids(filterAndSortBooks(books, { query: 'MUNICIPIO' })), ['municipal']);
  assert.deepEqual(ids(filterAndSortBooks(books, { query: 'federal', sort: 'importedAt', direction: 'asc' })), ['civil', 'penal']);
});

test('reading status uses exact 2% and 98% boundaries', () => {
  assert.equal(readingStatus(0), 'new');
  assert.equal(readingStatus(0.02), 'new');
  assert.equal(readingStatus(0.020001), 'reading');
  assert.equal(readingStatus(0.979999), 'reading');
  assert.equal(readingStatus(0.98), 'finished');
  assert.equal(readingStatus(1), 'finished');
  assert.equal(readingStatus(NaN), 'new');
  assert.deepEqual(ids(filterAndSortBooks(books, { status: 'reading' })), ['penal']);
});

test('tag selection is AND; untagged finds only documents without tags', () => {
  assert.deepEqual(ids(filterAndSortBooks(books, { tags: ['Civil', 'Federal'] })), ['civil']);
  assert.deepEqual(filterAndSortBooks(books, { tags: ['Civil', 'Penal'] }), []);
  assert.deepEqual(ids(filterAndSortBooks(books, { tags: ['__untagged__'] })), ['municipal']);
  assert.deepEqual(ids(filterAndSortBooks(books, { tags: ['__untagged__', 'Civil'] })), ['municipal']);
});

test('folder null leaves folders visible; empty string selects the root', () => {
  assert.equal(filterAndSortBooks(books, { folder: null }).length, 3);
  assert.deepEqual(ids(filterAndSortBooks(books, { folder: '' })), ['civil']);
  assert.deepEqual(ids(filterAndSortBooks(books, { folder: 'Federal' })), ['penal']);
  assert.deepEqual(filterAndSortBooks(books, { folder: 'federal' }), []);
});

test('library search includes annotation quotations and notes', () => {
  const notes = { civil: [{ text: 'Responsabilidade', note: 'Revisão para audiência' }], penal: [{ text: 'Crimes', note: 'Prioritário' }] };
  assert.deepEqual(ids(filterAndSortBooks(books, { query: 'AUDIENCIA' }, notes)), ['civil']);
  assert.deepEqual(ids(filterAndSortBooks(books, { query: 'responsabilidade' }, notes)), ['civil']);
  assert.deepEqual(ids(filterAndSortBooks(books, { query: 'prioritario' }, new Map(Object.entries(notes)))), ['penal']);
  assert.deepEqual(filterAndSortBooks(books, { query: 'prioritario', tags: ['Civil'] }, notes), []);
});

test('timestamps and progress sort numerically without changing source order', () => {
  assert.deepEqual(ids(filterAndSortBooks(books)), ['penal', 'municipal', 'civil']);
  assert.deepEqual(ids(filterAndSortBooks(books, { sort: 'importedAt', direction: 'asc' })), ['civil', 'municipal', 'penal']);
  assert.deepEqual(ids(filterAndSortBooks(books, { sort: 'progress', direction: 'desc' })), ['municipal', 'penal', 'civil']);
  assert.deepEqual(ids(books), ['civil', 'penal', 'municipal']);
  const dates = [{ id: 'a', importedAt: '2026-01-01T00:00:00Z' }, { id: 'b', importedAt: Date.parse('2026-02-01T00:00:00Z') }];
  assert.deepEqual(ids(filterAndSortBooks(dates, { sort: 'importedAt', direction: 'desc' })), ['b', 'a']);
});

test('Portuguese text sort handles accents and ties have deterministic IDs', () => {
  const list = [{ id: 'z', title: 'Álgebra' }, { id: 'a', title: 'Algebra' }, { id: 'b', title: 'Código 10' }, { id: 'c', title: 'Código 2' }];
  assert.deepEqual(ids(filterAndSortBooks(list, { sort: 'title', direction: 'asc' })), ['a', 'z', 'c', 'b']);
  assert.deepEqual(ids(filterAndSortBooks(list, { sort: 'title', direction: 'desc' })), ['b', 'c', 'a', 'z']);
});

test('metadata whitelist removes unsupported fields without erasing missing metadata', () => {
  const value = normalizeMetadata({ id: 'replace-id', title: '  Código  ', tags: [' Civil ', '', 'Civil', 2, null], author: '  União ', dangerous: true, source: 'replace content', favorite: true, hidden: false, status: 'finished' });
  assert.deepEqual(value, { title: 'Código', author: 'União', tags: ['Civil'], favorite: true, hidden: false, status: 'finished' });
  assert.deepEqual(normalizeMetadata({ title: 'Novo título' }), { title: 'Novo título' });
  assert.deepEqual(normalizeMetadata(null), {});
  assert.deepEqual(normalizeMetadata([]), {});
});

test('metadata numeric limits reject nonfinite values and misleading boolean strings', () => {
  assert.deepEqual(normalizeMetadata({ progress: 1.5, rating: 10, importedAt: -5, lastReadAt: '2026-01-01T00:00:00Z' }), {
    progress: 1, rating: 5, importedAt: 0, lastReadAt: Date.parse('2026-01-01T00:00:00Z'),
  });
  assert.deepEqual(normalizeMetadata({ progress: -3, rating: -2 }), { progress: 0, rating: 0 });
  assert.deepEqual(normalizeMetadata({ progress: NaN, rating: Infinity, importedAt: 'nunca', lastReadAt: null, favorite: 'false', hidden: 1, status: 'other' }), {});
});

test('unavailable browser persistence reports an error rather than pretending to save', async () => {
  const store = new LibraryStore(null);
  await assert.rejects(store.putBook({ id: 'law', source: '# Lei' }), /IndexedDB/);
  await assert.rejects(store.getBooks(), /IndexedDB/);
});

test('measured reading time survives metadata backups without accepting invalid time', () => {
  assert.deepEqual(normalizeMetadata({ readingSeconds: 123.5 }), { readingSeconds: 123.5 });
  assert.deepEqual(normalizeMetadata({ readingSeconds: 0 }), { readingSeconds: 0 });
  assert.deepEqual(normalizeMetadata({ readingSeconds: -5 }), { readingSeconds: 0 });
  for (const readingSeconds of [NaN, Infinity, -Infinity, '300', null]) {
    assert.deepEqual(normalizeMetadata({ readingSeconds }), {});
  }
});

test('metadata import cannot set object prototype or inherit metadata from it', () => {
  const hostile = JSON.parse('{"__proto__":{"hidden":true},"constructor":{"prototype":{"hidden":true}},"title":"Lei"}');
  const normalized = normalizeMetadata(hostile);
  assert.deepEqual(normalized, { title: 'Lei' });
  assert.equal(Object.getPrototypeOf(normalized), Object.prototype);
  assert.equal(Object.hasOwn(normalized, '__proto__'), false);
  assert.deepEqual(normalizeMetadata(Object.create({ title: 'Inherited', hidden: true })), {});
});

test('search does not treat inherited object keys as annotation document IDs', () => {
  const inheritedNotes = Object.create({ document: [{ text: 'Segredo herdado' }] });
  const documents = [{ id: 'document', title: 'Lei' }];
  assert.deepEqual(filterAndSortBooks(documents, { query: 'segredo' }, inheritedNotes), []);
});
