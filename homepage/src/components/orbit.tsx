'use client';

import { ease, useShouldReduceMotion } from '@animate-ui/react/utils/motion';
import {
  motion,
  useAnimationFrame,
  useInView,
  useMotionValue,
  useMotionValueEvent,
  useScroll,
  useSpring,
  useTransform,
  type MotionValue,
} from 'motion/react';
import {
  createContext,
  use,
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  useSyncExternalStore,
  type ComponentType,
} from 'react';

import { cn } from 'cn';

import { VademecumMark as AnimateUILogo } from '@/brand';

import { VIGNETTES } from './vignettes';

const STAGE = { width: 1200, height: 780 };
const CARD = { width: 300, height: 188 };
const GAP = 16;
const RADIUS = { x: 400, y: 240 };

type Vignettes = typeof VIGNETTES;
const VignettesContext = createContext<Vignettes>(VIGNETTES);
const columnsOf = (count: number) => (count === 4 ? 2 : 3);

/** How many cards sit in a row: the last one may be shorter, and centered. */
const rowLength = (count: number, columns: number, row: number) =>
  Math.min(columns, count - row * columns);

// A short last row of a 3-column grid starts one or two half-columns in.
const LAST_ROW_START = ['', 'md:col-start-3', 'md:col-start-2'];

const smooth = (t: number) => t * t * (3 - 2 * t);
const clamp = (t: number) => Math.min(1, Math.max(0, t));
const round = (value: number, digits: number) =>
  Math.round(value * 10 ** digits) / 10 ** digits;

function OrbitDrift({ drift, speed }: { drift: MotionValue<number>; speed: number }) {
  useAnimationFrame((_, delta) => {
    drift.set(drift.get() + delta * speed);
  });
  return null;
}

function subscribeToWide(callback: () => void) {
  const query = window.matchMedia('(min-width: 768px)');
  query.addEventListener('change', callback);
  return () => query.removeEventListener('change', callback);
}

function useWide() {
  return useSyncExternalStore(
    subscribeToWide,
    () => window.matchMedia('(min-width: 768px)').matches,
    () => true,
  );
}

function useStageScale() {
  const [scale, setScale] = useState(1);
  useEffect(() => {
    const update = () =>
      setScale(
        Math.min(
          1,
          window.innerWidth / STAGE.width,
          (window.innerHeight - 80) / STAGE.height,
        ),
      );
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);
  return scale;
}

function Card({ title, Vignette, active = true }: { title: string; Vignette: ComponentType<{ active?: boolean }>; active?: boolean }) {
  return (
    <div
      data-slot="orbit-card"
      className="flex size-full flex-col rounded-xl bg-accent p-1"
    >
      <div className="relative flex flex-1 flex-col rounded-lg bg-background">
        <span className="absolute top-2.5 left-3.5 text-xs font-medium text-muted-foreground">
          {title}
        </span>
        <div className="flex flex-1 items-center justify-center p-4 pt-7">
          <Vignette active={active} />
        </div>
      </div>
    </div>
  );
}

type Placement = {
  x: number;
  y: number;
  scale: number;
  opacity: number;
  rotateY: number;
  z: number;
};

function OrbitCard({
  index,
  enter,
  settle,
  turn,
  drift,
  stageVisible,
}: {
  index: number;
  enter: MotionValue<number>;
  settle: MotionValue<number>;
  turn: MotionValue<number>;
  drift: MotionValue<number>;
  stageVisible: boolean;
}) {
  const vignettes = use(VignettesContext);
  const { title, Vignette } = vignettes[index]!;
  const count = vignettes.length;
  const columns = columnsOf(count);
  const column = index % columns;
  const row = Math.floor(index / columns);
  const rows = Math.ceil(count / columns);
  const slot = {
    x: (column - (rowLength(count, columns, row) - 1) / 2) * (CARD.width + GAP),
    y: (row - (rows - 1) / 2) * (CARD.height + GAP) + 40,
  };

  const place = useTransform(
    [enter, settle, turn, drift] as MotionValue<number>[],
    ([e, s, t, d]: number[]) => {
      const angle = (index / count) * Math.PI * 2 + t! + d! * (1 - s!);
      const depth = (Math.sin(angle) + 1) / 2;
      const reach = 0.3 + 0.7 * e!;
      const orbit = {
        x: Math.cos(angle) * RADIUS.x * reach,
        y: Math.sin(angle) * RADIUS.y * reach + 30,
        scale: 0.7 + 0.3 * depth,
        opacity: (0.55 + 0.45 * depth) * e!,
        rotateY: -Math.cos(angle) * 24,
      };
      const k = smooth(s!);
      return {
        x: orbit.x + (slot.x - orbit.x) * k,
        y: orbit.y + (slot.y - orbit.y) * k,
        scale: orbit.scale + (1 - orbit.scale) * k,
        opacity: orbit.opacity + (1 - orbit.opacity) * k,
        rotateY: orbit.rotateY * (1 - k),
        z: k > 0.5 ? 30 : depth > 0.5 ? 20 : 5,
      };
    },
  );

  const ref = useRef<HTMLDivElement>(null);
  const [previewEnabled, setPreviewEnabled] = useState(false);
  const previewEnabledRef = useRef(false);
  const apply = useCallback((p: Placement) => {
    const element = ref.current;
    if (!element) return;
    element.style.transform = `perspective(900px) translate(${round(p.x, 1)}px, ${round(p.y, 1)}px) scale(${round(p.scale, 3)}) rotateY(${round(p.rotateY, 2)}deg)`;
    element.style.opacity = String(round(p.opacity, 3));
    const interactive = p.opacity > 0.35;
    element.style.pointerEvents = interactive ? 'auto' : 'none';
    element.inert = !interactive;
    element.style.zIndex = String(p.z);
    const enablePreview = stageVisible && p.opacity > 0.82;
    if (enablePreview && !previewEnabledRef.current) {
      previewEnabledRef.current = true;
      setPreviewEnabled(true);
    }
  }, [stageVisible]);
  useMotionValueEvent(place, 'change', apply);
  useLayoutEffect(() => apply(place.get()), [apply, place]);
  useEffect(() => {
    if (!stageVisible) {
      previewEnabledRef.current = false;
      setPreviewEnabled(false);
      return;
    }
    apply(place.get());
  }, [stageVisible, apply, place]);

  return (
    <div
      ref={ref}
      className="absolute top-1/2 left-1/2"
      style={{
        width: CARD.width,
        height: CARD.height,
        marginLeft: -CARD.width / 2,
        marginTop: -CARD.height / 2,
        opacity: 0,
        pointerEvents: 'none',
      }}
      inert
    >
      <Card title={title} Vignette={Vignette} active={stageVisible && previewEnabled} />
    </div>
  );
}

function Headline({
  progress,
  range,
  children,
}: {
  progress: MotionValue<number>;
  range: [number, number, number, number];
  children: string;
}) {
  const opacity = useTransform(progress, range, [0, 1, 1, 0]);
  const y = useTransform(progress, range, [24, 0, 0, -24]);
  return (
    <motion.h2
      style={{ opacity, y }}
      className="absolute inset-x-0 top-10 text-center text-4xl font-medium text-balance md:text-5xl"
    >
      {children}
    </motion.h2>
  );
}

function OrbitStage() {
  const vignettes = use(VignettesContext);
  const ref = useRef<HTMLElement>(null);
  const stageInView = useInView(ref, { amount: 0.01 });
  const scale = useStageScale();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end end'],
  });
  const progress = useSpring(scrollYProgress, {
    stiffness: 160,
    damping: 32,
    mass: 0.4,
  });
  const drift = useMotionValue(0);

  const enter = useTransform(progress, (p) => smooth(clamp((p - 0.12) / 0.25)));
  const settle = useTransform(progress, (p) => clamp((p - 0.86) / 0.12));
  const turn = useTransform(progress, (p) => clamp(p / 0.86) * Math.PI * 1.1);
  const [driftActive, setDriftActive] = useState(false);
  const driftActiveRef = useRef(false);
  const updateDrift = useCallback(() => {
    const next = enter.get() > 0 && settle.get() === 0;
    if (driftActiveRef.current === next) return;
    driftActiveRef.current = next;
    setDriftActive(next);
  }, [enter, settle]);
  useMotionValueEvent(enter, 'change', updateDrift);
  useMotionValueEvent(settle, 'change', updateDrift);
  useEffect(updateDrift, [updateDrift]);

  const logoScale = useTransform(
    progress,
    [0, 0.3, 0.86, 0.95],
    [0.8, 1, 1, 0.3],
  );
  const logoOpacity = useTransform(progress, [0, 0.86, 0.94], [1, 1, 0]);
  const logoRotate = useTransform(progress, [0, 0.95], [-60, 240]);
  const logoTilt = useTransform(progress, [0, 0.48, 0.95], [24, -12, 24]);
  const glow = useTransform(progress, [0, 0.3, 0.86, 0.95], [0.5, 1, 1, 0]);

  return (
      <section
        ref={ref}
        id="recursos"
        data-slot="home-orbit"
        className="relative mt-24 h-[300vh]"
      >
        {stageInView && driftActive && <OrbitDrift drift={drift} speed={0.00008} />}
        <div className="sticky top-20 flex h-[calc(100dvh-5rem)] items-center justify-center overflow-hidden">
          <div
            className="relative shrink-0"
            style={{
              width: STAGE.width,
              height: STAGE.height,
              transform: `scale(${scale})`,
            }}
          >
            <Headline progress={progress} range={[-0.01, 0, 0.78, 0.87]}>
              O direito se revela nas relações.
            </Headline>
            <Headline progress={progress} range={[0.9, 0.97, 1, 1.01]}>
              Encontre o contexto de cada norma.
            </Headline>

            <motion.div
              aria-hidden="true"
              style={{ opacity: glow }}
              className="absolute top-1/2 left-1/2 -mt-[240px] -ml-[240px] size-[480px] rounded-full bg-foreground/10 blur-3xl"
            />
            <motion.div
              aria-hidden="true"
              className="absolute top-1/2 left-1/2 z-10 -mt-[120px] -ml-[128px]"
              style={{
                scale: logoScale,
                opacity: logoOpacity,
                rotate: logoRotate,
                rotateX: logoTilt,
                transformPerspective: 1200,
              }}
            >
              <AnimateUILogo className="h-[240px] w-[256px] text-foreground drop-shadow-[0_30px_60px_rgb(0_0_0/0.25)]" />
            </motion.div>

            {vignettes.map(({ title }, index) => (
              <OrbitCard
                key={title}
                index={index}
                enter={enter}
                settle={settle}
                turn={turn}
                drift={drift}
                stageVisible={stageInView}
              />
            ))}
          </div>
        </div>
      </section>
  );
}

function StaticGrid() {
  const vignettes = use(VignettesContext);
  const columns = columnsOf(vignettes.length);
  return (
      <section
        id="recursos"
        data-slot="home-orbit"
        className="mx-auto mt-24 flex w-full max-w-[1000px] flex-col gap-8 px-5"
      >
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.6, ease: ease.out }}
          className="text-center text-3xl font-medium text-balance md:text-5xl"
        >
          O direito se revela nas relações.
        </motion.h2>
        <div
          className={cn(
            'grid gap-4',
            columns === 2 ? 'md:grid-cols-2' : 'md:grid-cols-6',
          )}
        >
          {vignettes.map(({ title, Vignette }, index) => (
            <motion.div
              key={title}
              className={cn(
                columns === 3 && 'md:col-span-2',
                columns === 3 &&
                  index === vignettes.length - (vignettes.length % 3) &&
                  LAST_ROW_START[vignettes.length % 3],
              )}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{
                duration: 0.6,
                ease: ease.out,
                delay: (index % columns) * 0.06,
              }}
              style={{ height: CARD.height + 20 }}
            >
              <Card title={title} Vignette={Vignette} />
            </motion.div>
          ))}
        </div>
      </section>
  );
}

function MobileOrbitCard({
  index, activeIndex, enter, settle, turn, drift, viewportWidth, viewportHeight, cardWidth, stageVisible,
}: {
  index: number;
  activeIndex: MotionValue<number>;
  enter: MotionValue<number>;
  settle: MotionValue<number>;
  turn: MotionValue<number>;
  drift: MotionValue<number>;
  viewportWidth: number;
  viewportHeight: number;
  cardWidth: number;
  stageVisible: boolean;
}) {
  const vignettes = use(VignettesContext);
  const { title, Vignette } = vignettes[index]!;
  const place = useTransform(
    [enter, settle, turn, drift, activeIndex] as MotionValue<number>[],
    ([e, s, t, d, selected]: number[]) => {
      const angle = (index / vignettes.length) * Math.PI * 2 + t! + d! * (1 - s!);
      const depth = (Math.sin(angle) + 1) / 2;
      const orbitX = Math.cos(angle) * Math.min(170, viewportWidth * .43) * (.35 + .65 * e!);
      const orbitY = Math.sin(angle) * Math.min(210, viewportHeight * .28) * (.35 + .65 * e!);
      const delta = index - selected!;
      const selectedOpacity = Math.max(0, 1 - Math.abs(delta) * 1.4);
      const k = smooth(s!);
      return {
        x: orbitX + (delta * viewportWidth - orbitX) * k,
        y: orbitY + (68 - orbitY) * k,
        scale: (.72 + .28 * depth) + ((Math.abs(delta) < .5 ? 1 : .88) - (.72 + .28 * depth)) * k,
        opacity: (.48 + .52 * depth) * e! * (1 - k) + selectedOpacity * k,
        rotateY: -Math.cos(angle) * 18 * (1 - k),
        z: k > .5 ? 30 - Math.round(Math.abs(delta)) : depth > .5 ? 20 : 5,
        interactive: k > .92 && Math.abs(delta) < .5,
        preload: Math.abs(delta) <= 1,
      };
    },
  );

  const ref = useRef<HTMLDivElement>(null);
  const [previewEnabled, setPreviewEnabled] = useState(false);
  const previewEnabledRef = useRef(false);
  const apply = useCallback((p: Placement & { interactive: boolean; preload: boolean }) => {
    const element = ref.current;
    if (!element) return;
    element.style.transform = `perspective(900px) translate(${round(p.x, 1)}px, ${round(p.y, 1)}px) scale(${round(p.scale, 3)}) rotateY(${round(p.rotateY, 2)}deg)`;
    element.style.opacity = String(round(p.opacity, 3));
    element.style.pointerEvents = p.interactive ? 'auto' : 'none';
    element.inert = !p.interactive;
    element.style.zIndex = String(p.z);
    const enablePreview = stageVisible && p.preload;
    if (previewEnabledRef.current !== enablePreview) {
      previewEnabledRef.current = enablePreview;
      setPreviewEnabled(enablePreview);
    }
  }, [stageVisible]);
  useMotionValueEvent(place, 'change', apply);
  useLayoutEffect(() => apply(place.get()), [apply, place]);
  useEffect(() => {
    if (!stageVisible) {
      previewEnabledRef.current = false;
      setPreviewEnabled(false);
      return;
    }
    apply(place.get());
  }, [stageVisible, apply, place]);

  return (
    <div
      ref={ref}
      role="group"
      aria-roledescription="slide"
      aria-label={`${index + 1} de ${vignettes.length}: ${title}`}
      className="absolute top-1/2 left-1/2"
      style={{ width: cardWidth, height: CARD.height, marginLeft: -cardWidth / 2, marginTop: -CARD.height / 2, opacity: 0, pointerEvents: 'none' }}
      inert
    >
      <Card title={title} Vignette={Vignette} active={stageVisible && previewEnabled} />
    </div>
  );
}

function MobileOrbitStage() {
  const vignettes = use(VignettesContext);
  const ref = useRef<HTMLElement>(null);
  const stageInView = useInView(ref, { amount: 0.01 });
  const reduce = useShouldReduceMotion();
  const [viewport, setViewport] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [selected, setSelected] = useState(0);
  const [driftActive, setDriftActive] = useState(false);
  const driftActiveRef = useRef(false);
  const selectedMotion = useMotionValue(0);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end end'] });
  const progress = useSpring(scrollYProgress, { stiffness: 160, damping: 32, mass: .4 });
  const drift = useMotionValue(0);
  const enter = useTransform(progress, p => smooth(clamp((p - .12) / .25)));
  const settle = useTransform(progress, p => clamp((p - .78) / .16));
  const turn = useTransform(progress, p => clamp(p / .78) * Math.PI * 1.1);
  const titleOpacity = useTransform(progress, [0, .08, .68, .78], [1, 1, 1, 0]);
  const finalTitleOpacity = useTransform(progress, [.76, .88], [0, 1]);
  const logoScale = useTransform(progress, [0, .3, .78, .94], [.68, .84, .84, .2]);
  const logoOpacity = useTransform(progress, [0, .78, .9], [1, 1, 0]);
  const logoRotate = useTransform(progress, [0, .9], [-35, 170]);
  const controlsOpacity = useTransform(progress, [.78, .9], [0, 1]);
  const cardWidth = Math.min(340, Math.max(240, viewport.width - 32));

  useEffect(() => {
    const resize = () => setViewport({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener('resize', resize, { passive: true });
    return () => window.removeEventListener('resize', resize);
  }, []);
  useEffect(() => selectedMotion.set(selected), [selected, selectedMotion]);
  const updateDrift = useCallback(() => {
    const next = enter.get() > 0 && settle.get() < 1;
    if (driftActiveRef.current === next) return;
    driftActiveRef.current = next;
    setDriftActive(next);
  }, [enter, settle]);
  useMotionValueEvent(enter, 'change', updateDrift);
  useMotionValueEvent(settle, 'change', updateDrift);
  useEffect(updateDrift, [updateDrift]);

  const step = (direction: -1 | 1) => setSelected(current => Math.min(vignettes.length - 1, Math.max(0, current + direction)));

  return (
    <section ref={ref} id="recursos" data-slot="home-orbit" className="relative mt-16 h-[300vh]" aria-label="Recursos do VadeMecum">
      {stageInView && driftActive && <OrbitDrift drift={drift} speed={0.00008} />}
      <div className="sticky top-20 flex h-[calc(100dvh-5rem)] items-center justify-center overflow-hidden">
        <div className="relative h-full w-full shrink-0" style={{ perspective: 1200 }}>
          <motion.h2 style={{ opacity: titleOpacity, y: useTransform(titleOpacity, [0, 1], [-12, 0]) }} className="absolute inset-x-5 top-7 z-40 text-left text-[clamp(1.65rem,7vw,2.15rem)] font-medium leading-[1.05] tracking-tight text-balance">
            O direito se revela nas relações.
          </motion.h2>
          <motion.div style={{ opacity: finalTitleOpacity }} className="absolute inset-x-5 top-7 z-40">
            <h2 className="text-[clamp(1.65rem,7vw,2.15rem)] font-medium leading-[1.05] tracking-tight text-balance">
              Encontre o contexto de cada norma.
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">Explore as prévias interativas da Biblioteca e do Leitor.</p>
          </motion.div>
          <motion.div aria-hidden="true" style={{ scale: logoScale, opacity: logoOpacity, rotate: logoRotate }} className="absolute top-1/2 left-1/2 z-10 -mt-16 -ml-[4.5rem]">
            <AnimateUILogo className="h-32 w-36 text-foreground drop-shadow-[0_24px_48px_rgb(0_0_0/0.24)]" />
          </motion.div>
          {vignettes.map(({ title }, index) => (
            <MobileOrbitCard key={title} index={index} activeIndex={selectedMotion} enter={enter} settle={settle} turn={turn} drift={drift} viewportWidth={viewport.width} viewportHeight={viewport.height - 80} cardWidth={cardWidth} stageVisible={stageInView} />
          ))}
          <motion.div style={{ opacity: controlsOpacity, pointerEvents: 'none' }} className="absolute inset-x-5 bottom-5 z-40 flex items-center justify-between gap-3">
            <span className="text-xs font-medium text-muted-foreground" aria-live="polite" aria-atomic="true">
              {vignettes[selected]?.title} · {String(selected + 1).padStart(2, '0')} / {String(vignettes.length).padStart(2, '0')}
            </span>
            <div className="flex gap-2" style={{ pointerEvents: 'auto' }}>
              <button type="button" aria-label="Prévia anterior" disabled={selected === 0} onClick={() => step(-1)} className="flex size-10 items-center justify-center rounded-full border border-border bg-background/90 text-foreground shadow-sm transition-colors hover:bg-accent disabled:opacity-35">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" aria-hidden="true"><path d="m14.5 5-7 7 7 7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </button>
              <button type="button" aria-label="Próxima prévia" disabled={selected >= vignettes.length - 1} onClick={() => step(1)} className="flex size-10 items-center justify-center rounded-full border border-border bg-background/90 text-foreground shadow-sm transition-colors hover:bg-accent disabled:opacity-35">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" aria-hidden="true"><path d="m9.5 5 7 7-7 7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

/** `only`: the vignettes to show, by title (the components a framework has). */
export function Orbit({ only }: { only?: string[] }) {
  const wide = useWide();
  const reduce = useShouldReduceMotion();
  const vignettes = only
    ? VIGNETTES.filter(({ title }) => only.includes(title))
    : VIGNETTES;
  return (
    <VignettesContext value={vignettes}>
      {wide && !reduce ? <OrbitStage /> : !wide && !reduce ? <MobileOrbitStage /> : <StaticGrid />}
    </VignettesContext>
  );
}
