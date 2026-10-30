import { motion } from 'motion/react';
import { useIntroPlaying, LOGO_GLIDE } from './intro';
import { VademecumMark } from '@/brand';
import { useState } from 'react';

export function HomeHeader() {
  const playing = useIntroPlaying();
  const [dark, setDark] = useState(false);
  function toggleTheme() {
    const next = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', next);
    setDark(next);
  }
  return <header data-slot="home-header" className="fixed inset-x-0 top-0 z-[70] h-20 bg-background/80 backdrop-blur-md">
    <div className="mx-auto flex h-full max-w-[1200px] items-center gap-3 px-5">
      <a href="#inicio" aria-label="Vademecum início" className="flex items-center text-foreground">
        {!playing && <motion.div layoutId="home-logo" transition={{layout:LOGO_GLIDE}} className="flex items-center gap-2.5">
          <VademecumMark className="size-7"/><span className="text-[17px] font-semibold tracking-tight">vademecum</span>
        </motion.div>}
      </a>
      <motion.div className="ml-auto flex items-center gap-1" initial={false} animate={playing?{opacity:0,x:24,filter:'blur(6px)'}:{opacity:1,x:0,filter:'blur(0px)'}} transition={{duration:.6,ease:[.23,1,.32,1],delay:.25}}>
        <nav className="mr-1 flex items-center">
          <a href="#recursos" className="hidden h-8 items-center rounded-md px-3 text-sm text-neutral-700 transition-colors hover:text-black sm:inline-flex dark:text-neutral-200 dark:hover:text-white">Recursos</a>
          <a href="#assistente" className="hidden h-8 items-center rounded-md px-3 text-sm text-neutral-700 transition-colors hover:text-black sm:inline-flex dark:text-neutral-200 dark:hover:text-white">Assistente</a>
          <a href="./biblioteca/" className="hidden h-8 items-center rounded-md px-3 text-sm text-neutral-700 transition-colors hover:text-black sm:inline-flex dark:text-neutral-200 dark:hover:text-white">Biblioteca</a>
        </nav>
        <button type="button" onClick={toggleTheme} aria-label={dark?'Ativar tema claro':'Ativar tema escuro'} className="flex size-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
        </button>
      </motion.div>
    </div>
  </header>
}
