import test from 'node:test';
import assert from 'node:assert/strict';
import MarkdownIt from 'markdown-it';
import { compile } from '../scripts/build.mjs';

globalThis.markdownit = MarkdownIt;
const { Library } = await import('../src/library.js');
const parseBook = (raw, filename) => Library.prototype.parseMarkdown.call({}, raw, filename);

test('imported Markdown keeps front matter, inline tags and stable anchors', () => {
  const raw = '---\ntitle: "Lei de Teste"\nauthor: União\ntags: [Federal, "Tributário"]\n---\n# Abertura\n\nTexto\n\n## Regras\n\nUm\n\n## Regras\n\nDois';
  const book = parseBook(raw, 'lei.md');
  assert.equal(book.title, 'Lei de Teste');
  assert.equal(book.author, 'União');
  assert.deepEqual(book.tags, ['Federal', 'Tributário']);
  assert.deepEqual(book.toc.map(item => item.id), ['abertura', 'regras', 'regras-2']);
  assert.ok(book.sections[1].html.includes('id="regras"'));
});

test('imported and built documents generate the same heading identifiers', () => {
  const raw = '# Título com Ação!\n\nTexto\n\n## Seção — 2\n\nMais';
  assert.deepEqual(
    parseBook(raw, 'a.md').toc.map(item => item.id),
    compile(raw, 'a.md').toc.map(item => item.id),
  );
});

test('front matter accepts a block list of tags', () => {
  const raw = '---\ntags:\n  - Federal\n  - Penal\n---\n# Lei\n\nTexto';
  assert.deepEqual(parseBook(raw, 'a.md').tags, ['Federal', 'Penal']);
});

test('title prefers the first heading over a leading paragraph', () => {
  const raw = 'Prefácio\n\n# Título real\n\nTexto';
  assert.equal(parseBook(raw, 'a.md').title, 'Título real');
  assert.equal(compile(raw, 'a.md').title, 'Título real');
});

test('front matter brackets are not stripped from ordinary metadata', () => {
  const raw = '---\ntitle: [Lei]\n---\n# Seção\n\nTexto';
  assert.equal(parseBook(raw, 'a.md').title, '[Lei]');
});

test('import and build agree when a heading has no body', () => {
  const raw = '# Título\n\n## Capítulo\n\nTexto';
  const imported = parseBook(raw, 'a.md');
  const built = compile(raw, 'a.md');
  assert.equal(imported.sections.length, 1);
  assert.equal(imported.sections.length, built.sections.length);
  assert.deepEqual(imported.toc.map(item => item.section), built.toc.map(item => item.section));
});
