import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { compile } from '../scripts/build.mjs';
test('articles retain destinations across chapters', () => {
  const book = compile('# Lei\n\nTexto\n\n## Capítulo\n\n### Art. 1º\n\nConteúdo.', 'lei.md');
  assert.equal(book.sections.length, 2);
  const article = book.toc.find(t => t.label === 'Art. 1º');
  assert.equal(article.section, 1);
  assert.ok(book.sections[article.section].html.includes(`id="${article.id}"`));
});
test('duplicate headings have unique identifiers', () => {
  assert.deepEqual(compile('# A\n\n## Regras\n\nUm\n\n## Regras\n\nDois', 'a.md').toc.map(t => t.id), ['a','regras','regras-2']);
});
test('frontmatter becomes metadata and not body text', () => {
  const book = compile('---\ntitle: Documento\nauthor: Autor\n---\nTexto', 'a.md');
  assert.equal(book.title, 'Documento');
  assert.doesNotMatch(book.sections[0].html, /author:/);
});
test('markup and unsafe links cannot become executable HTML', () => {
  const book = compile('# Teste\n\n<script>alert(1)</script>\n\n[x](javascript:alert(1))', 'a.md');
  assert.doesNotMatch(book.sections[0].html, /<script|href="javascript:/);
});
test('empty files fail clearly', () => assert.throws(() => compile(' ', 'a.md'), /Markdown vazio/));
test('a heading without body is merged into the next chapter', () => {
  const book = compile('# Título\n\n## Capítulo\n\nTexto', 'a.md');
  assert.equal(book.sections.length, 1);
  assert.deepEqual(book.toc.map(item => item.section), [0, 0]);
});
test('a comma-separated tag string becomes a tag list', () => {
  assert.deepEqual(compile('---\ntags: Federal, Penal\n---\n# Lei\n\nTexto', 'a.md').tags, ['Federal', 'Penal']);
});
test('interface IDs are unique', async () => {
  const html = await readFile(new URL('../src/index.html', import.meta.url), 'utf8');
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(ids).size, ids.length);
});
