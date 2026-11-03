import { useEffect, useRef, useState, type ComponentType } from 'react';
import { libraryDestination } from './library-destination';
import './vignettes.css';

const documentId = 'br-federal-lei_ordinaria-14133-2021';
type PreviewMode = 'catalog' | 'search' | 'toc' | 'marks' | 'notes' | 'citation' | 'source' | 'appearance' | 'resume';

type FeaturePreviewProps = {
  mode: PreviewMode;
  title: string;
  view?: string;
  panel?: string;
  sidebar?: boolean;
  query?: string;
  appearance?: boolean;
  sourceDialog?: boolean;
  article?: boolean;
  activationEnabled?: boolean;
};

function FeaturePreview({ mode, title, view, panel, sidebar, query, appearance, sourceDialog, article = true, activationEnabled = true }: FeaturePreviewProps) {
  const iframeCleanup = useRef<(() => void) | null>(null);
  const iframe = useRef<HTMLIFrameElement>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [attempt, setAttempt] = useState(0);
  const libraryBase = import.meta.env.DEV
    ? new URL('/biblioteca-demo/', document.baseURI)
    : new URL('biblioteca/', document.baseURI);
  const previewUrl = new URL(libraryBase);
  previewUrl.searchParams.set('preview', mode);
  if (view) previewUrl.searchParams.set('view', view);
  if (panel) previewUrl.searchParams.set('panel', panel);
  if (sidebar) previewUrl.searchParams.set('sidebar', '1');
  if (query) previewUrl.searchParams.set('q', query);
  if (appearance) previewUrl.searchParams.set('appearance', '1');
  if (sourceDialog) previewUrl.searchParams.set('dialog', 'source');
  if (mode === 'resume') {
    previewUrl.hash = `documento=${documentId}`;
  } else if (!['catalog', 'search', 'settings'].includes(mode)) {
    previewUrl.hash = `documento=${documentId}${article ? '&artigo=art-5o' : ''}`;
  }

  const destination = libraryDestination();
  const searchDestination = libraryDestination({
    view: mode === 'search' ? 'search-all' : 'books',
    query: mode === 'search' ? query : undefined,
  });
  if (view) destination.searchParams.set('view', view);
  if (panel) destination.searchParams.set('panel', panel);
  if (sidebar) destination.searchParams.set('sidebar', '1');
  if (query) destination.searchParams.set('q', query);
  if (appearance) destination.searchParams.set('appearance', '1');
  if (sourceDialog) destination.searchParams.set('dialog', 'source');
  if (mode === 'resume' || !['catalog', 'search', 'settings'].includes(mode)) {
    destination.hash = `documento=${documentId}${article && mode !== 'resume' ? '&artigo=art-5o' : ''}`;
  }

  useEffect(() => () => iframeCleanup.current?.(), []);

  const routePreviewInteraction = (event: React.SyntheticEvent<HTMLIFrameElement>) => {
    iframeCleanup.current?.();
    const frameDocument = event.currentTarget.contentDocument;
    if (!frameDocument) return;
    const route = (interaction: Event) => {
      const target = interaction.target as Element | null;
      if (!target || typeof target.closest !== 'function') return;
      const search = target.closest('.shelf-search, #library-query');
      const book = target.closest('.shelf-book-open');
      if (!search && !book) return;
      interaction.preventDefault();
      interaction.stopImmediatePropagation();
      const documentId = book?.closest<HTMLElement>('[data-book-id]')?.dataset.bookId;
      const next = documentId ? libraryDestination({ documentId }) : searchDestination;
      window.location.assign(next.href);
    };
    frameDocument.addEventListener('click', route, true);
    frameDocument.addEventListener('focusin', route, true);
    iframeCleanup.current = () => {
      frameDocument.removeEventListener('click', route, true);
      frameDocument.removeEventListener('focusin', route, true);
    };
  };

  useEffect(() => {
    if (!activationEnabled) return;
    const receive = (event: MessageEvent) => {
      if (event.origin !== location.origin || event.source !== iframe.current?.contentWindow) return;
      if (event.data?.type === 'vademecum-preview-ready') setStatus('ready');
    };
    window.addEventListener('message', receive);
    const timeout = window.setTimeout(() => setStatus(current => current === 'ready' ? current : 'error'), 15000);
    return () => {
      window.removeEventListener('message', receive);
      window.clearTimeout(timeout);
      iframeCleanup.current?.();
    };
  }, [activationEnabled, attempt]);

  return (
    <div className="library-mini-preview" data-preview-state={status}>
      {activationEnabled && <iframe
        ref={iframe}
        key={attempt}
        className="library-mini-preview-frame"
        src={previewUrl.href}
        title={`Prévia interativa: ${title}`}
        loading="eager"
        referrerPolicy="strict-origin-when-cross-origin"
        allow="clipboard-write"
        onLoad={event => {
          if (!activationEnabled) return;
          if (event.currentTarget.contentDocument?.documentElement.dataset.previewReady === 'true') setStatus('ready');
          routePreviewInteraction(event);
        }}
      />}
      {status === 'loading' && <div className="library-mini-preview-loading" aria-hidden="true"><i /><i /><i /></div>}
      {status === 'error' && <div className="library-mini-preview-error" role="status">
        <span>Não foi possível carregar a prévia.</span>
        <button type="button" onClick={() => { setStatus('loading'); setAttempt(value => value + 1); }}>Tentar novamente</button>
      </div>}
      <a className="library-mini-preview-open" href={destination.href}>
        Abrir na biblioteca <span aria-hidden="true">↗</span>
      </a>
    </div>
  );
}

type VignetteProps = { active?: boolean };

const feature = (props: FeaturePreviewProps) => function LibraryFeature({ active = true }: VignetteProps = {}) {
  return <FeaturePreview {...props} activationEnabled={active} />;
};

export const VIGNETTES: { title: string; Vignette: ComponentType<VignetteProps> }[] = [
  { title: 'Acervo', Vignette: feature({ mode: 'catalog', title: 'Acervo', view: 'books' }) },
  { title: 'Busca integral', Vignette: feature({ mode: 'search', title: 'Busca integral', view: 'search-all', query: 'igualdade' }) },
  { title: 'Sumário do leitor', Vignette: feature({ mode: 'toc', title: 'Sumário do leitor', panel: 'toc', sidebar: true }) },
  { title: 'Marcadores', Vignette: feature({ mode: 'marks', title: 'Marcadores', panel: 'marks', sidebar: true }) },
  { title: 'Anotações', Vignette: feature({ mode: 'notes', title: 'Anotações', panel: 'notes', sidebar: true }) },
  { title: 'Citação', Vignette: feature({ mode: 'citation', title: 'Citação' }) },
  { title: 'Procedência', Vignette: feature({ mode: 'source', title: 'Procedência', sourceDialog: true }) },
  { title: 'Aparência', Vignette: feature({ mode: 'appearance', title: 'Aparência', appearance: true }) },
  { title: 'Retomar leitura', Vignette: feature({ mode: 'resume', title: 'Retomar leitura', article: false }) },
];
