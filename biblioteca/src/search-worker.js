let indexPromise;
let latestToken = 0;

function normalizeSearch(text) {
  return String(text ?? '').normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
}

async function getIndex() {
  indexPromise ??= fetch(new URL('./search-index.json', self.location.href))
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(async books => {
      const prepared = [];
      for (let index = 0; index < books.length; index++) {
        prepared.push(prepareBook(books[index]));
        if (index % 8 === 7) await yieldToWorkerQueue();
      }
      return prepared;
    })
    .catch(error => {
      indexPromise = undefined;
      throw error;
    });
  return indexPromise;
}

function prepareBook(book) {
  let offset = 0;
  const sections = (book.sections || []).map(section => {
    const searchText = normalizeSearch(section.text);
    const start = offset;
    offset += searchText.length + 1;
    return { ...section, searchText, start, end: start + searchText.length };
  });
  return { ...book, sections, searchText: sections.map(section => section.searchText).join('\n') };
}

function originalOffsetForNormalized(text, normalizedOffset) {
  let originalOffset = 0;
  let searchOffset = 0;
  for (const character of text) {
    if (searchOffset >= normalizedOffset) break;
    searchOffset += normalizeSearch(character).length;
    originalOffset += character.length;
  }
  return originalOffset;
}

const yieldToWorkerQueue = () => new Promise(resolve => setTimeout(resolve, 0));

async function search({ token, query, visibleIds, localBooks }) {
  const officialBooks = await getIndex();
  if (token !== latestToken) return;
  const visible = new Set(visibleIds);
  const corpus = [...officialBooks, ...localBooks.map(prepareBook)];
  const matches = [];

  for (let bookIndex = 0; bookIndex < corpus.length; bookIndex++) {
    const book = corpus[bookIndex];
    if (visible.has(book.id)) {
      let sectionIndex = 0;
      let cursor = 0;
      const matchedSections = new Set();
      while (cursor < book.searchText.length) {
        const at = book.searchText.indexOf(query, cursor);
        if (at < 0) break;
        while (sectionIndex < book.sections.length && book.sections[sectionIndex].end <= at) sectionIndex++;
        const section = book.sections[sectionIndex];
        if (section && at >= section.start && at + query.length <= section.end && !matchedSections.has(sectionIndex)) {
          const sectionAt = at - section.start;
          const originalAt = originalOffsetForNormalized(section.text, sectionAt);
          const originalEnd = originalOffsetForNormalized(section.text, sectionAt + query.length);
          matchedSections.add(sectionIndex);
          matches.push({
            id: book.id,
            title: book.title,
            label: section.label,
            section: section.index,
            anchor: section.anchor,
            text: section.text,
            start: Math.max(0, originalAt - 65),
            end: Math.min(section.text.length, originalEnd + 95),
            at: originalAt,
            matchEnd: originalEnd,
          });
        }
        if (matches.length >= 200) break;
        cursor = matchedSections.has(sectionIndex) ? section.end : at + Math.max(1, query.length);
      }
    }
    if (matches.length >= 200) break;
    if (bookIndex % 8 === 7) {
      await yieldToWorkerQueue();
      if (token !== latestToken) return;
    }
  }

  if (token === latestToken) self.postMessage({ type: 'results', token, matches });
}

self.addEventListener('message', event => {
  if (event.data?.type !== 'search') return;
  latestToken = event.data.token;
  search(event.data).catch(error => {
    if (event.data.token === latestToken) {
      self.postMessage({ type: 'error', token: event.data.token, message: error?.message || 'Search failed' });
    }
  });
});
