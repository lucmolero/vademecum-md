import React from 'react';
import { createRoot } from 'react-dom/client';
import { IntroProvider } from './components/intro';
import { HomeHeader } from './components/header';
import { CitationGraphHero } from './components/citation-graph-hero';
import { Hero } from './components/hero';
import { Orbit } from './components/orbit';
import { AISection } from './components/ai-section';
import './global.css';

function App() {
  return (
    <IntroProvider>
      <a className="skip-link" href="#conteudo">Ir para o conteúdo</a>
      <HomeHeader />
      <main id="conteudo">
        <CitationGraphHero />
        <Hero />
        <Orbit />
      </main>
      <AISection />
      <footer className="mx-auto mt-24 flex w-full max-w-[1200px] flex-wrap items-center justify-between gap-4 px-5 py-8 text-sm text-muted-foreground">
        <a href="#inicio" className="font-medium text-foreground">Vademecum</a>
        <span>Conhecimento jurídico em movimento.</span>
        <a href="#inicio" className="hover:text-foreground">Voltar ao início ↑</a>
        <small className="w-full text-xs">Biblioteca oficial · legislação federal com fontes e proveniência.</small>
        <div className="flex w-full flex-wrap items-center justify-between gap-4 border-t border-border/60 pt-5">
          <p className="text-xs">
            Desenvolvido por <span className="font-medium text-foreground">Luciano Molero</span>
          </p>
          <nav aria-label="Perfis do desenvolvedor" className="flex items-center gap-4 text-xs">
            <a
              href="https://github.com/lucmolero"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 hover:text-foreground"
              aria-label="GitHub de Luciano Molero"
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" className="size-4" fill="currentColor">
                <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2.02c-3.2.7-3.87-1.55-3.87-1.55-.53-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.71.08-.71 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.69 5.4-5.26 5.68.41.36.78 1.06.78 2.14v3.18c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
              </svg>
              GitHub
            </a>
            <a
              href="https://www.linkedin.com/in/luciano-molero/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 hover:text-foreground"
              aria-label="LinkedIn de Luciano Molero"
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" className="size-4" fill="currentColor">
                <path d="M20.45 2H3.55C2.69 2 2 2.68 2 3.52v16.96c0 .84.69 1.52 1.55 1.52h16.9c.86 0 1.55-.68 1.55-1.52V3.52C22 2.68 21.31 2 20.45 2ZM8 19H5V9h3v10ZM6.5 7.63a1.75 1.75 0 1 1 0-3.5 1.75 1.75 0 0 1 0 3.5ZM19 19h-3v-4.87c0-1.16-.02-2.65-1.62-2.65-1.62 0-1.87 1.26-1.87 2.57V19h-3V9h2.88v1.37h.04c.4-.76 1.38-1.56 2.84-1.56 3.04 0 3.6 2 3.6 4.6V19Z" />
              </svg>
              LinkedIn
            </a>
          </nav>
        </div>
      </footer>
    </IntroProvider>
  );
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
