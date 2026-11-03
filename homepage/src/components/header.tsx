import { motion } from 'motion/react';
import { useIntroPlaying, LOGO_GLIDE } from './intro';
import { VademecumMark } from '@/brand';
import { lazy, Suspense, useEffect, useState } from 'react';
import { useShouldReduceMotion } from '@animate-ui/react/utils/motion';

const MobileNavigation = lazy(() =>
  import('./mobile-navigation').then(({ MobileNavigation: Navigation }) => ({ default: Navigation })),
);

const mobileLinks = [
  ['Skill', '#skill'],
  ['Recursos', '#recursos'],
  ['Assistente', '#assistente'],
  ['Biblioteca', './biblioteca/'],
] as const;

function MobileNavigationFallback() {
  return <details className="relative sm:hidden">
    <summary aria-label="Abrir navegação" className="flex size-9 cursor-pointer list-none items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground [&::-webkit-details-marker]:hidden">
      <svg aria-hidden="true" viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </summary>
    <nav aria-label="Navegação principal" className="absolute top-[calc(100%+8px)] right-0 z-[80] min-w-48 rounded-xl border border-border bg-background p-1.5 text-foreground shadow-lg">
      {mobileLinks.map(([label, href]) => <a key={href} href={href} className="flex min-h-10 items-center rounded-lg px-3 text-sm outline-none hover:bg-accent focus-visible:bg-accent">{label}</a>)}
    </nav>
  </details>;
}

export function HomeHeader() {
  const playing = useIntroPlaying();
  const reduce = useShouldReduceMotion();
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'));
  const [mobile, setMobile] = useState(() => window.matchMedia('(max-width: 639px)').matches);
  useEffect(() => {
    const media = window.matchMedia('(max-width: 639px)');
    const update = () => setMobile(media.matches);
    update();
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);
  function toggleTheme() {
    const next = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', next);
    setDark(next);
  }
  return <header data-slot="home-header" className="fixed inset-x-0 top-0 z-[70] h-20 bg-background text-foreground">
    <div className="mx-auto flex h-full max-w-[1200px] items-center gap-3 px-5">
      <a href="#inicio" aria-label="vademecum.md início" className="flex items-center text-foreground">
        {!playing && <motion.div layoutId="home-logo" transition={{layout:LOGO_GLIDE}} className="flex items-center gap-2.5">
          <VademecumMark className="size-7"/><span className="text-[17px] font-semibold tracking-tight">vademecum.md</span>
        </motion.div>}
      </a>
      <motion.div className="ml-auto flex items-center gap-1" initial={playing&&!reduce?{opacity:0,x:24,filter:'blur(6px)'}:false} animate={playing&&!reduce?{opacity:0,x:24,filter:'blur(6px)'}:{opacity:1,x:0,filter:'blur(0px)'}} transition={{duration:reduce?0:.24,ease:[.23,1,.32,1],delay:playing||reduce?0:.12}}>
        {mobile && <Suspense fallback={<MobileNavigationFallback />}><MobileNavigation /></Suspense>}
        <nav className="mr-1 flex items-center">
          <a href="#recursos" className="hidden h-8 items-center rounded-md px-3 text-sm text-muted-foreground transition-colors hover:text-foreground sm:inline-flex">Recursos</a>
          <a href="#assistente" className="hidden h-8 items-center rounded-md px-3 text-sm text-muted-foreground transition-colors hover:text-foreground sm:inline-flex">Assistente</a>
          <a href="#skill" className="hidden h-8 items-center rounded-md px-3 text-sm text-muted-foreground transition-colors hover:text-foreground sm:inline-flex">Skill</a>
          <a href="./biblioteca/" className="hidden h-8 items-center rounded-md px-3 text-sm text-muted-foreground transition-colors hover:text-foreground sm:inline-flex">Biblioteca</a>
        </nav>
        <button type="button" onClick={toggleTheme} aria-pressed={dark} aria-label={dark?'Ativar tema claro':'Ativar tema escuro'} className="flex size-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
        </button>
      </motion.div>
    </div>
  </header>
}
