import { useEffect, useRef, useState, type ComponentType } from 'react';
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
};

function FeaturePreview({ mode, title, view, panel, sidebar, query, appearance, sourceDialog, article = true }: FeaturePreviewProps) {
  const previewRef = useRef<HTMLDivElement>(null);
  const [previewActive, setPreviewActive] = useState(false);
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

  const destination = new URL('https://lucmolero.github.io/vademecum-md/biblioteca/');
  if (view) destination.searchParams.set('view', view);
  if (panel) destination.searchParams.set('panel', panel);
  if (sidebar) destination.searchParams.set('sidebar', '1');
  if (query) destination.searchParams.set('q', query);
  if (appearance) destination.searchParams.set('appearance', '1');
  if (sourceDialog) destination.searchParams.set('dialog', 'source');
  if (mode === 'resume' || !['catalog', 'search', 'settings'].includes(mode)) {
    destination.hash = `documento=${documentId}${article && mode !== 'resume' ? '&artigo=art-5o' : ''}`;
  }

  useEffect(() => {
    const element = previewRef.current;
    if (!element) return;
    if (!('IntersectionObserver' in window)) {
      setPreviewActive(true);
      return;
    }
    const observer = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return;
      setPreviewActive(true);
      observer.disconnect();
    }, { rootMargin: '160px 0px' });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={previewRef} className="library-mini-preview">
      <iframe
        className="library-mini-preview-frame"
        src={previewActive ? previewUrl.href : undefined}
        title={`Prévia interativa: ${title}`}
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
        allow="clipboard-write"
      />
      <a className="library-mini-preview-open" href={destination.href}>
        Abrir na biblioteca <span aria-hidden="true">↗</span>
      </a>
    </div>
  );
}

const feature = (props: FeaturePreviewProps) => function LibraryFeature() {
  return <FeaturePreview {...props} />;
};

export const VIGNETTES: { title: string; Vignette: ComponentType }[] = [
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
