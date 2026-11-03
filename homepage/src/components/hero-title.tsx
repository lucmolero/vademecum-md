'use client';

import {
  RotatingText,
  RotatingTextContainer,
} from '@animate-ui/react/primitives/texts/rotating';
import { SplittingText } from '@animate-ui/react/primitives/texts/splitting';
import { ease, useShouldReduceMotion } from '@animate-ui/react/utils/motion';
import { motion, useInView } from 'motion/react';
import { useLayoutEffect, useRef, useState } from 'react';
import { useDocumentVisible } from './use-document-visible';

const WORD_IN = {
  initial: { opacity: 1, y: 24, filter: 'blur(12px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)' },
  transition: { duration: 0.7, ease: ease.out },
  stagger: 0.07,
};

function Line({
  text,
  done,
  delay,
}: {
  text: string;
  done: boolean;
  delay: number;
}) {
  const reduce = useShouldReduceMotion();
  if (!done) return <span className="invisible">{text}</span>;
  if (reduce) return <span>{text}</span>;
  return (
    <SplittingText
      type="words"
      text={text}
      delay={delay}
      className="inline"
      {...WORD_IN}
    />
  );
}

function useOwnLine(ref: React.RefObject<HTMLElement | null>, done: boolean) {
  const [ownLine, setOwnLine] = useState(false);
  useLayoutEffect(() => {
    const element = ref.current;
    const line = element?.parentElement;
    if (!element || !line) return;
    const measure = () => {
      if (!element.isConnected) return;
      const first = line.firstElementChild as HTMLElement | null;
      if (!first) return;
      const size = parseFloat(getComputedStyle(element).fontSize);
      setOwnLine(element.offsetTop - first.offsetTop > size * 0.5);
    };
    measure();
    void document.fonts.ready.then(measure);
    const observer = new ResizeObserver(measure);
    observer.observe(line);
    observer.observe(element);
    return () => observer.disconnect();
  }, [ref, done]);
  return ownLine;
}

function Library({ done, libraries }: { done: boolean; libraries: string[] }) {
  const reduce = useShouldReduceMotion();
  const ref = useRef<HTMLSpanElement>(null);
  const ownLine = useOwnLine(ref, done);
  const inView = useInView(ref);
  const pageVisible = useDocumentVisible();
  if (reduce) return <span className="inline-block text-neutral-500 dark:text-neutral-400">{libraries[0]}</span>;
  return (
    <motion.span
      ref={ref}
      data-slot="hero-library"
      data-own-line={ownLine ? '' : undefined}
      className="inline-grid align-bottom"
      initial={WORD_IN.initial}
      animate={done ? WORD_IN.animate : WORD_IN.initial}
      transition={{ ...WORD_IN.transition, delay: 2 * WORD_IN.stagger }}
    >
      {libraries.map(library => <span key={library} aria-hidden="true" className="invisible col-start-1 row-start-1">{library}</span>)}
      <RotatingTextContainer
        text={done && inView && pageVisible ? libraries : libraries.slice(0, 1)}
        duration={2600}
        delay={1400}
        align={ownLine ? 'center' : 'start'}
        style={{ display: 'inline-block', overflow: 'clip', gridColumn: 1, gridRow: 1 }}
      >
        <RotatingText className="text-neutral-500 dark:text-neutral-400" />
      </RotatingTextContainer>
    </motion.span>
  );
}

export function HeroTitle({
  done,
  libraries,
}: {
  done: boolean;
  libraries: string[];
}) {
  return (
    <h2 className="flex max-w-[1100px] flex-col items-center text-[clamp(1.75rem,6vw,3.75rem)] font-medium md:text-6xl">
      <span className="whitespace-normal text-center lg:whitespace-nowrap">
        <Line text="Pesquisa jurídica" done={done} delay={0} />{' '}
        <Library done={done} libraries={libraries} />
      </span>
      <Line text="em um só lugar." done={done} delay={300} />
    </h2>
  );
}
