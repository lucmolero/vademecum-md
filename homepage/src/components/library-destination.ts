type LibraryDestinationOptions = {
  view?: string;
  query?: string;
  documentId?: string;
};

export function libraryDestination({ view, query, documentId }: LibraryDestinationOptions = {}) {
  const url = new URL('./biblioteca/', document.baseURI);
  if (view) url.searchParams.set('view', view);
  if (query) url.searchParams.set('q', query);
  if (documentId) {
    url.searchParams.set('view', 'books');
    url.hash = `documento=${encodeURIComponent(documentId)}`;
  }
  return url;
}

export function openLibrary(options: LibraryDestinationOptions = {}) {
  window.location.assign(libraryDestination(options).href);
}
