import React from 'react';
import {createRoot} from 'react-dom/client';
import {IntroProvider} from './components/intro';
import {HomeHeader} from './components/header';
import {Hero} from './components/hero';
import {Orbit} from './components/orbit';
import {AISection} from './components/ai-section';
import './global.css';
function App(){return <IntroProvider><a className="skip-link" href="#conteudo">Ir para o conteúdo</a><HomeHeader/><main id="conteudo"><Hero/><Orbit/></main><AISection/><footer className="mx-auto mt-24 flex w-full max-w-[1200px] flex-wrap items-center justify-between gap-4 px-5 py-8 text-sm text-muted-foreground"><a href="#inicio" className="font-medium text-foreground">Vademecum</a><span>Conhecimento jurídico em movimento.</span><a href="#inicio" className="hover:text-foreground">Voltar ao início ↑</a><small className="w-full text-xs">Biblioteca oficial · legislação federal com fontes e proveniência.</small></footer></IntroProvider>}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
