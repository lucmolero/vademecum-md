import { readdir, readFile, writeFile, mkdir, cp, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import MarkdownIt from 'markdown-it';
import sanitize from 'sanitize-html';
import matter from 'gray-matter';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'dist');
const md = new MarkdownIt({ html: false, linkify: true, typographer: false });
const articleLine = /^\s*(?:\*\*)?(Art\.\s+\d+(?:\s*[ºª°])?(?:\s*-\s*[A-Za-z])?\.?)(?:\*\*)?(.*)$/i;
const articleHeadingId = label => {
  const match = /^Art\.\s*(\d+)(?:\s*([ºª°]))?(?:\s*-\s*([A-Za-z]))?\.?$/i.exec(label.trim());
  if (!match) return '';
  const ordinal = match[2] === 'ª' ? 'a' : match[2] ? 'o' : '';
  return `art-${Number(match[1])}${ordinal}${match[3] ? `-${match[3].toLowerCase()}` : ''}`;
};
const asText = value => value == null ? '' : String(value).trim();
const asList = value => Array.isArray(value) ? value.map(asText).filter(Boolean) : typeof value === 'string' ? value.split(',').map(item => item.trim()).filter(Boolean) : [];
const readable = value => asText(value).replaceAll('_', ' ').replace(/\s+/g, ' ').replace(/^\p{L}/u, first => first.toLocaleUpperCase('pt-BR'));
const documentTypeLabels = {
  constituicao: 'Constituição', lei_ordinaria: 'Lei ordinária', lei_complementar: 'Lei complementar',
  decreto_lei: 'Decreto-lei', decreto: 'Decreto', emenda_constitucional: 'Emenda constitucional',
  ato_constitucional: 'Ato constitucional', resolucao: 'Resolução', medida_provisoria: 'Medida provisória',
};
function promoteVademecumArticles(content) {
  return content.split(/\r?\n/).flatMap(line => {
    const match = articleLine.exec(line);
    if (!match) return [line];
    const label = match[1].trim().replace(/\.$/, '');
    const remainder = match[2].trim();
    return [`### ${label}`, '', ...(remainder ? [remainder] : [])];
  }).join('\n');
}
const hasChapterContent = tokens => {
  if (!tokens.length) return false;
  const firstHeading = tokens.findIndex(token => token.type === 'heading_open');
  if (firstHeading !== 0) return true;
  let lastClose = -1;
  for (let index = 0; index < tokens.length; index++) if (tokens[index].type === 'heading_close') lastClose = index;
  return lastClose >= 0 && tokens.length > lastClose + 1;
};
export function compile(source, filename, options = {}) {
  const { data, content: sourceContent } = matter(source.replace(/^\uFEFF/, ''));
  const isVademecum = options.origin === 'vademecum';
  const content = isVademecum ? promoteVademecumArticles(sourceContent) : sourceContent;
  const tokens = md.parse(content, {});
  const headingIndex = tokens.findIndex(token => token.type === 'heading_open');
  const firstHeading = headingIndex === -1 ? '' : tokens[headingIndex + 1]?.content || '';
  const title = asText(isVademecum ? data.titulo : data.title) || asText(data.title) || firstHeading || path.basename(filename, '.md');
  const ids = new Map();
  const toc = [];
  const groups = [];
  let chunk = [];
  let label = title;
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.type === 'heading_open') {
      const text = tokens[i + 1].content;
      const base = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'secao';
      const n = (ids.get(base) || 0) + 1;
      ids.set(base, n);
      const id = (isVademecum ? articleHeadingId(text) : '') || (n === 1 ? base : `${base}-${n}`);
      token.attrSet('id', id);
      if (token.level === 0 && Number(token.tag.slice(1)) <= 2 && hasChapterContent(chunk)) {
        groups.push({ label, tokens: chunk });
        chunk = [];
      }
      if (!chunk.length) label = text;
      toc.push({ label: text, level: Number(token.tag.slice(1)), section: groups.length, id });
    }
    chunk.push(token);
  }
  if (chunk.length) groups.push({ label, tokens: chunk });
  if (!groups.length) throw new Error(`Markdown vazio: ${filename}`);
  const sections = groups.map(({ label, tokens }, index) => {
    const html = sanitize(md.renderer.render(tokens, md.options, {}), {
      allowedTags: sanitize.defaults.allowedTags.concat(['img']),
      allowedAttributes: { ...sanitize.defaults.allowedAttributes, '*': ['id'], img: ['src', 'alt', 'title', 'width', 'height'] },
      allowedSchemes: ['https', 'http', 'mailto'],
    });
    return { id: `s${index}`, label, html, size: Buffer.byteLength(html) };
  });
  const tags = [...new Set([
    ...asList(data.tags),
    ...(isVademecum ? [readable(data.esfera), documentTypeLabels[data.tipo] || readable(data.tipo), readable(data.dominio)].filter(Boolean) : []),
  ])];
  const officialSources = asList(isVademecum ? data.fonte_oficial : (data.officialSources || data.officialUrl || data.official_url));
  const type = asText(isVademecum ? data.tipo : data.type);
  const typeLabel = isVademecum ? (documentTypeLabels[type] || readable(type)) : readable(type);
  const number = asText(isVademecum ? data.numero : data.number);
  const year = asText(isVademecum ? data.ano : data.year);
  const dataCutoff = asText(isVademecum ? data.data_corte : data.cutoff);
  const titleId = asText(data.id);
  const cardLabel = isVademecum ? [typeLabel, number ? `${number}/${year}` : year].filter(Boolean).join(' · ') : '';
  return {
    title, description: asText(isVademecum ? data.ementa : data.description), language: asText(data.language) || 'pt-BR',
    author: asText(data.author || data.autor || data.orgao_emissor || data.orgao), tags,
    number, year, aliases: asList(data.aliases), officialUrl: officialSources[0] || '', officialSources,
    sourceDate: asText(isVademecum ? (data.baixado_em || data.source_snapshot_date) : (data.sourceDate || data.source_date)),
    legalStatus: readable(isVademecum ? data.situacao : (data.legalStatus || data.legal_status)),
    type, typeLabel, domain: readable(data.dominio || data.domain), jurisdiction: asText(data.jurisdicao || data.jurisdiction),
    cutoff: dataCutoff, consolidationStatus: asText(data.consolidacao_status || data.consolidationStatus),
    fidelityStatus: asText(data.fidelity_status || data.fidelityStatus), vademecumId: isVademecum ? titleId : '',
    vademecumSourceHash: asText(data.sha256_origem || data.sha256_source_raw), cardLabel,
    relations: Array.isArray(data.relations) ? data.relations : [], toc, sections,
  };
}

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const result = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    if (entry.name.startsWith('.')) continue;
    const name = path.join(dir, entry.name);
    if (entry.isDirectory()) result.push(...await walk(name));
    else if (entry.isFile() && /\.md$/i.test(entry.name)) result.push(name);
  }
  return result;
}

async function walkFiles(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const name = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...await walkFiles(name));
    else if (entry.isFile()) files.push(name);
  }
  return files;
}

export async function build() {
  const vademecumCorpus = asText(process.env.VADEMECUM_CORPUS_DIR || process.env.VADE_CORPUS_DIR) ? path.resolve(process.env.VADEMECUM_CORPUS_DIR || process.env.VADE_CORPUS_DIR) : '';
  const vademecumFiles = vademecumCorpus ? await walk(vademecumCorpus) : [];
  if (vademecumCorpus && !vademecumFiles.length) throw new Error(`Nenhum Markdown do VadeMecum encontrado em ${vademecumCorpus}`);
  let release = {};
  const releaseFile = asText(process.env.VADEMECUM_RELEASE_FILE || process.env.VADE_RELEASE_FILE);
  if (releaseFile) release = JSON.parse(await readFile(path.resolve(releaseFile), 'utf8'));
  if (vademecumCorpus) {
    const expected = Number(release.corpus_count ?? release.document_count ?? release.count);
    if (Number.isFinite(expected) && expected > 0 && expected !== vademecumFiles.length) {
      throw new Error(`A release declara ${expected} documentos, mas o corpus contém ${vademecumFiles.length}`);
    }
  }
  await rm(output, { recursive: true, force: true });
  await mkdir(path.join(output, 'books'), { recursive: true });
  await cp(path.join(root, 'src'), output, { recursive: true });
  await mkdir(path.join(output, 'lib'), { recursive: true });
  await cp(createRequire(import.meta.url).resolve('markdown-it/browser'), path.join(output, 'lib/markdown-it.min.js'));
  await cp(path.join(root, 'node_modules/markdown-it/LICENSE'), path.join(output, 'lib/markdown-it-LICENSE.txt'));
  if (vademecumCorpus) await cp(vademecumCorpus, path.join(output, 'leis/vademecum-md'), { recursive: true });
  else await cp(path.join(root, 'leis'), path.join(output, 'leis'), { recursive: true });
  const catalog = [];
  const searchIndex = [];
  const sources = vademecumCorpus
    ? [{ root: vademecumCorpus, sourcePrefix: 'leis/vademecum-md', origin: 'vademecum', files: vademecumFiles }]
    : [{ root: path.join(root, 'leis'), sourcePrefix: 'leis', origin: 'library', files: await walk(path.join(root, 'leis')) }];
  const seenIds = new Set();
  for (const sourceSet of sources) for (const file of sourceSet.files) {
    const relative = path.relative(sourceSet.root, file).split(path.sep).join('/');
    const sourcePath = `${sourceSet.sourcePrefix}/${relative}`;
    const raw = await readFile(file, 'utf8');
    const sourceHash = createHash('sha256').update(raw).digest('hex');
    const book = compile(raw, relative, { origin: sourceSet.origin });
    const id = sourceSet.origin === 'vademecum' ? book.vademecumId : createHash('sha256').update(relative).digest('hex').slice(0, 16);
    if (!id || !/^[a-z0-9][a-z0-9._-]*$/i.test(id)) throw new Error(`ID estável ausente ou inválido em ${sourcePath}`);
    if (seenIds.has(id)) throw new Error(`ID duplicado entre os acervos: ${id}`);
    seenIds.add(id);
    const artifactId = encodeURIComponent(id);
    for (const [index, section] of book.sections.entries()) {
      section.file = `books/${artifactId}-${index}.html`;
      const sourceDirectory = path.posix.dirname(sourcePath);
      const base = `../${sourceDirectory === '.' ? '' : `${sourceDirectory.split('/').map(encodeURIComponent).join('/')}/`}`;
      await writeFile(path.join(output, section.file), `<!doctype html><html lang="${book.language.replace(/[^a-zA-Z0-9-]/g, '')}"><head><meta charset="utf-8"><base href="${base}"></head><body>${section.html}</body></html>`);
    }
    const record = { ...book, id, collection: sourceSet.origin, title: book.title, sourceHash, file: `books/${artifactId}.json`, source: sourcePath, sections: book.sections.length };
    catalog.push(record);
    searchIndex.push({ id, title: book.title, sections: book.sections.map((section, index) => ({ index, label: section.label, anchor: book.toc.find(item => item.section === index)?.id || '', text: section.html.replace(/<[^>]*>/g, ' ').replace(/&nbsp;|&#160;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\s+/g, ' ').trim() })) });
    await writeFile(path.join(output, record.file), JSON.stringify({ ...book, source: record.source, sourceHash }));
  }
  if (vademecumCorpus) {
    await writeFile(path.join(output, 'vademecum-source.json'), JSON.stringify({
      repository: 'lucmolero/vademecum-md',
      ref: asText(process.env.VADEMECUM_SOURCE_REF || process.env.VADE_REF) || 'main',
      commit: asText(process.env.VADEMECUM_SOURCE_COMMIT || process.env.VADE_COMMIT),
      version: asText(release.version), release: asText(release.version), generatedAt: asText(release.generated_at),
      cutoff: [...new Set(catalog.filter(book => book.collection === 'vademecum').map(book => book.cutoff).filter(Boolean))].sort().at(-1) || '',
      documentCount: vademecumFiles.length,
    }, null, 2));
  }
  await writeFile(path.join(output, 'catalog.json'), JSON.stringify(catalog, null, 2));
  await writeFile(path.join(output, 'search-index.json'), JSON.stringify(searchIndex));
  await writeFile(path.join(output, '.nojekyll'), '');
  const outputFiles = await walkFiles(output);
  const manifest = outputFiles.map(file => path.relative(output, file).split(path.sep).join('/').split('/').map(encodeURIComponent).join('/'));
  await writeFile(path.join(output, 'offline-manifest.json'), JSON.stringify(manifest));
  const releaseHash = createHash('sha256').update(JSON.stringify(manifest));
  for (const file of outputFiles) releaseHash.update(path.relative(output, file)).update(await readFile(file));
  const cacheVersion = releaseHash.digest('hex').slice(0, 12);
  await writeFile(path.join(output, 'sw.js'), `const VERSION=${JSON.stringify(cacheVersion)};
const SHELL='biblioteca-shell-'+VERSION, CONTENT='biblioteca-content-'+VERSION;
const scope=self.registration.scope;
self.addEventListener('install',event=>event.waitUntil((async()=>{const cache=await caches.open(SHELL);await cache.addAll([new URL('./',scope).href,new URL('./index.html',scope).href]);await self.skipWaiting();})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const key of await caches.keys())if(key.startsWith('biblioteca-')&&key!==SHELL&&key!==CONTENT)await caches.delete(key);await self.clients.claim();})()));
self.addEventListener('message',event=>{if(event.data?.type!=='CACHE_LIBRARY')return;const client=event.source;event.waitUntil((async()=>{try{const response=await fetch(new URL('./offline-manifest.json',scope));if(!response.ok)throw new Error('Manifesto offline indisponível');const files=await response.json(),cache=await caches.open(CONTENT);for(let i=0;i<files.length;i+=40){await cache.addAll(files.slice(i,i+40).map(file=>new URL(file,scope).href));client?.postMessage({type:'OFFLINE_PROGRESS',done:Math.min(i+40,files.length),total:files.length});}client?.postMessage({type:'OFFLINE_READY',total:files.length});}catch(error){client?.postMessage({type:'OFFLINE_ERROR',message:error.message});}})());});
self.addEventListener('fetch',event=>{if(event.request.method!=='GET'||new URL(event.request.url).origin!==location.origin)return;event.respondWith((async()=>{const cached=await caches.match(event.request);if(cached)return cached;try{const response=await fetch(event.request);if(response.ok&&new URL(event.request.url).pathname.startsWith(new URL(scope).pathname)){const cache=await caches.open(CONTENT);cache.put(event.request,response.clone());}return response;}catch(error){const fallback=await caches.match(new URL('./index.html',scope).href);if(fallback&&event.request.mode==='navigate')return fallback;throw error;}})());});
`);
  console.log(`Site gerado: ${catalog.length} documento(s) em dist/`);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await build();
