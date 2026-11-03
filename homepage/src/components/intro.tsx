'use client';

import { ease, useShouldReduceMotion } from '@animate-ui/react/utils/motion';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from 'cn';

import { createContext, use, useEffect, useState, type ReactNode } from 'react';




const MARK = "M175 30H650Q795 30 795 175V650Q795 795 650 795H175Q30 795 30 650V175Q30 30 175 30ZM205 215 365 620Q383 665 420 665Q457 665 475 620L635 215H510L420 490 330 215Z";

const DRAW = 1.3;
const FILL = 0.45;
const HOLD = 0.3;
const GLIDE = 0.75;

export const LOGO_GLIDE = {
  type: 'spring',
  stiffness: 150,
  damping: 24,
  mass: 0.9,
} as const;

const IntroContext = createContext({
  playing: false,
  done: true,
});

function shouldPlayIntro() {
  if (typeof window === 'undefined' || window.location.hash) return false;
  try {
    return window.sessionStorage.getItem('vademecum-home-intro-seen') !== '1';
  } catch {
    return false;
  }
}

export function useIntroDone() {
  return use(IntroContext).done;
}

export function useIntroPlaying() {
  return use(IntroContext).playing;
}

export function FullLogo({
  draw = false,
  className,
}: {
  draw?: boolean;
  className?: string;
}) {
  return <div aria-hidden="true" className={cn('flex items-center gap-[.12em] whitespace-nowrap', className)}>
    <svg viewBox="0 0 825 825" className={cn('h-[1em] w-[1em] shrink-0 transition-colors duration-300')}>
      <motion.path d={MARK} fill="currentColor" stroke="currentColor" strokeWidth="10" initial={draw?{pathLength:0,fillOpacity:0}:false} animate={{pathLength:1,fillOpacity:1}} transition={{pathLength:{duration:DRAW,ease:'easeInOut'},fillOpacity:{duration:FILL,delay:DRAW-.15,ease:ease.out}}}/>
    </svg>
    <motion.span className="font-semibold tracking-tight" initial={draw?{opacity:0,filter:'blur(8px)',y:8}:false} animate={{opacity:1,filter:'blur(0px)',y:0}} transition={{duration:.55,delay:.65,ease:ease.out}}>vademecum.md</motion.span>
  </div>;
}

export function IntroProvider({ children }: { children: ReactNode }) {
  const reduce = useShouldReduceMotion();
  const [playing, setPlaying] = useState(shouldPlayIntro);
  const [done, setDone] = useState(() => !shouldPlayIntro());

  useEffect(() => {
    if (!done || !window.location.hash) return;
    let id;
    try { id = decodeURIComponent(window.location.hash.slice(1)); } catch { return; }
    let frame = requestAnimationFrame(() => {
      frame = requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ block: 'start' }));
    });
    return () => cancelAnimationFrame(frame);
  }, [done]);

  useEffect(() => {
    if (!playing) return;
    if (reduce) {
      setPlaying(false);
      setDone(true);
      return;
    }
    try {
      window.sessionStorage.setItem('vademecum-home-intro-seen', '1');
    } catch {
      // The intro remains optional when storage is unavailable.
    }
    const finish = () => { setPlaying(false); setDone(true); };
    // A branded first visit never delays an intentional interaction.
    window.addEventListener('pointerdown', finish, { once: true });
    window.addEventListener('keydown', finish, { once: true });
    window.addEventListener('wheel', finish, { once: true, passive: true });
    const reveal = setTimeout(
      () => setPlaying(false),
      (DRAW + FILL + HOLD) * 1000,
    );
    return () => {
      clearTimeout(reveal);
      window.removeEventListener('pointerdown', finish);
      window.removeEventListener('keydown', finish);
      window.removeEventListener('wheel', finish);
    };
  }, [playing, reduce]);

  const intro = playing && !reduce;

  return (
    <IntroContext value={{
      playing: intro,
      done: done || Boolean(reduce),
    }}>
      <AnimatePresence
        onExitComplete={() => {
          if (reduce) return;
          setDone(true);
        }}
      >
        {intro && (
          <motion.div
            key="intro"
            data-slot="home-intro"
            aria-hidden="true"
            className="fixed inset-0 z-[60] flex items-center justify-center bg-background motion-reduce:hidden"
            exit={{
              opacity: 0,
              transition: { duration: GLIDE * 0.8, ease: ease.out },
            }}
          >
            <motion.div
              className="absolute size-[60vmin] rounded-full bg-foreground/10 blur-3xl"
              initial={{ opacity: 0, scale: 0.4 }}
              animate={{ opacity: [0, 0, 1, 0.6], scale: [0.4, 0.4, 1.1, 1] }}
              transition={{
                duration: DRAW + FILL + HOLD,
                times: [0, DRAW / (DRAW + FILL + HOLD), 0.85, 1],
                ease: ease.out,
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>
      {intro && (
        <div
          aria-hidden="true"
          className="pointer-events-none fixed inset-0 z-[61] flex items-center justify-center motion-reduce:hidden"
        >
          <motion.div
            layoutId="home-logo"
            transition={{ layout: LOGO_GLIDE }}
            className="w-fit text-[clamp(2.5rem,8vw,5rem)] text-foreground"
          >
            <FullLogo draw />
          </motion.div>
        </div>
      )}
      {children}
    </IntroContext>
  );
}
