import { useShouldReduceMotion } from '@animate-ui/react/utils/motion';
import { motion, useScroll, useTransform } from 'motion/react';
import { useEffect, useRef, useState, type MouseEvent } from 'react';

// Exercise the shipped graph in development too. An external source checkout
// remains available explicitly while editing the standalone graph application.
const graphUrl = new URL(
  import.meta.env.DEV && import.meta.env.VITE_GRAPH_URL
    ? import.meta.env.VITE_GRAPH_URL
    : './graph/viewer/index.html?home-hero=1&v=graph-startup-3',
  document.baseURI,
).href;

export function CitationGraphHero() {
  const reduceMotion = useShouldReduceMotion();
  const [graphRequested, setGraphRequested] = useState(() =>
    !location.hash || ['#inicio', '#conteudo'].includes(location.hash),
  );
  const [graphReady, setGraphReady] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);
  const graphFrameRef = useRef<HTMLIFrameElement>(null);
  const graphVisibleRef = useRef(false);
  const { scrollYProgress } = useScroll({ target: sectionRef, offset: ['start start', 'end start'] });
  const transitionOpacity = useTransform(scrollYProgress, [0, .02, .12, .3], [0, .72, 1, 0]);
  const scrollAnimation = useRef<number | null>(null);

  useEffect(() => {
    const frame = graphFrameRef.current;
    if (!frame) return;
    const graphOrigin = new URL(graphUrl, window.location.href).origin;

    const handleGraphMessage = (event: MessageEvent) => {
      if (event.source !== frame.contentWindow || event.origin !== graphOrigin) return;
      if (event.data?.type !== 'vademecum-graph-ready') return;
      setGraphReady(true);
    };
    window.addEventListener('message', handleGraphMessage);

    const publishVisibility = () => {
      frame.contentWindow?.postMessage({
        type: 'vademecum-graph-visibility',
        visible: graphVisibleRef.current && !document.hidden,
      }, '*');
    };
    if (!('IntersectionObserver' in window)) graphVisibleRef.current = true;
    const visibilityThreshold = 0.35;
    let observer: IntersectionObserver | null = null;
    let observationFrame = 0;
    const observeGraph = () => {
      if (!('IntersectionObserver' in window)) {
        setGraphRequested(true);
        return;
      }
      observer = new IntersectionObserver(([entry]) => {
          graphVisibleRef.current = entry.isIntersecting && entry.intersectionRatio >= visibilityThreshold;
          if (graphVisibleRef.current) setGraphRequested(true);
          publishVisibility();
        }, { threshold: visibilityThreshold });
      observer.observe(frame);
    };
    // Initial hash navigation settles in IntroProvider before observing the hero.
    observationFrame = requestAnimationFrame(() => {
      observationFrame = requestAnimationFrame(() => {
        observationFrame = requestAnimationFrame(observeGraph);
      });
    });
    document.addEventListener('visibilitychange', publishVisibility);
    publishVisibility();

    const interrupt = () => {
      if (!scrollAnimation.current) return;
      cancelAnimationFrame(scrollAnimation.current);
      scrollAnimation.current = null;
    };
    window.addEventListener('wheel', interrupt, { passive: true });
    window.addEventListener('touchstart', interrupt, { passive: true });
    window.addEventListener('pointerdown', interrupt, { passive: true });
    window.addEventListener('keydown', interrupt);
    return () => {
      observer?.disconnect();
      cancelAnimationFrame(observationFrame);
      window.removeEventListener('message', handleGraphMessage);
      document.removeEventListener('visibilitychange', publishVisibility);
      window.removeEventListener('wheel', interrupt);
      window.removeEventListener('touchstart', interrupt);
      window.removeEventListener('pointerdown', interrupt);
      window.removeEventListener('keydown', interrupt);
      if (scrollAnimation.current !== null) cancelAnimationFrame(scrollAnimation.current);
    };
  }, []);

  const continueToSkill = (event: MouseEvent<HTMLAnchorElement>) => {
    if (reduceMotion) return;
    const target = document.getElementById('skill');
    if (!target) return;
    event.preventDefault();
    if (scrollAnimation.current !== null) cancelAnimationFrame(scrollAnimation.current);
    const scrollMargin = Number.parseFloat(getComputedStyle(target).scrollMarginTop) || 0;
    const top = Math.max(0, target.getBoundingClientRect().top + window.scrollY - scrollMargin);
    const start = window.scrollY;
    const startedAt = performance.now();
    const tick = (now: number) => {
      const progress = Math.min(1, (now - startedAt) / 1050);
      const eased = progress < .5
        ? 4 * progress ** 3
        : 1 - (-2 * progress + 2) ** 3 / 2;
      window.scrollTo(0, start + (top - start) * eased);
      if (progress < 1) scrollAnimation.current = requestAnimationFrame(tick);
      else {
        scrollAnimation.current = null;
        history.pushState(null, '', '#skill');
      }
    };
    scrollAnimation.current = requestAnimationFrame(tick);
  };

  return (
    <section
      ref={sectionRef}
      id="inicio"
      aria-label="Grafo de citações do VadeMecum MD"
      data-slot="graph-hero"
      className="graph-hero-section"
    >
      <h1 className="sr-only">Explore o grafo de citações do VadeMecum MD</h1>
      <motion.iframe
        ref={graphFrameRef}
        title="Grafo interativo de citações do VadeMecum MD"
        src={graphRequested ? graphUrl : undefined}
        className="graph-hero-frame"
        loading="eager"
        allow="fullscreen"
        onLoad={() => {
          if (!graphRequested) return;
          // Reveal the document while the graph prepares its first camera fit.
          setGraphReady(true);
          graphFrameRef.current?.contentWindow?.postMessage({
            type: 'vademecum-graph-visibility',
            visible: graphVisibleRef.current && !document.hidden,
          }, '*');
        }}
        onError={() => setGraphReady(true)}
        initial={reduceMotion ? false : { opacity: 0, scale: 1.008 }}
        animate={{ opacity: graphReady || reduceMotion ? 1 : 0, scale: 1 }}
        transition={{ duration: reduceMotion ? 0 : 0.9, ease: [0.22, 1, 0.36, 1] }}
      />
      <motion.div
        aria-hidden="true"
        className="graph-scroll-transition"
        style={{ opacity: reduceMotion ? 0 : transitionOpacity }}
      />
      <a
        href="#skill"
        className="graph-continue-link"
        onClick={continueToSkill}
      >
        <span className="graph-continue-copy">
          <span className="graph-continue-kicker">Próxima seção</span>
          <span className="graph-continue-title">Instale a skill</span>
        </span>
        <svg aria-hidden="true" viewBox="0 0 16 16" fill="none">
          <path d="M8 2.75v10.5m0 0 4-4m-4 4-4-4" />
        </svg>
      </a>
    </section>
  );
}
