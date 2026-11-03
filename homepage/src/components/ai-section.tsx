'use client';

import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useInView } from 'motion/react';
import {
  Tabs,
  TabsContent,
  TabsContents,
  TabsHighlight,
  TabsHighlightItem,
  TabsList,
  TabsTrigger,
} from '@animate-ui/react/primitives/tabs';
import { TypingText } from '@animate-ui/react/primitives/texts/typing';
import { useShouldReduceMotion } from '@animate-ui/react/utils/motion';
import { SparklesIcon } from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';
import release from '../../../manifests/release.json';
import { PREVIEW_BOOKS } from '../../../biblioteca/src/preview-data.js';
import { ArrowRight01 } from '../registry/hugeicons/arrow-right-01';
import { CheckmarkCircle02 } from '../registry/hugeicons/checkmark-circle-02';
import { Loading03 } from '../registry/hugeicons/loading-03';

const LibraryReaderPreview = lazy(() =>
  import('./library-reader-preview').then(({ LibraryReaderPreview: Preview }) => ({ default: Preview })),
);

const law = PREVIEW_BOOKS['br-federal-lei_ordinaria-14133-2021'];
const cutoff = law.cutoff.split('-').reverse().join('/');
const TYPE_MS = 24;
const STEP_MS = 620;
const HOLD_MS = 3600;

type Scenario = {
  id: string;
  label: string;
  prompt: string;
  steps: string[];
  result: string;
};

const scenarios: Scenario[] = [
  {
    id: 'principios',
    label: 'Princípios',
    prompt: 'Estou revisando um edital. Quais princípios orientam a Lei 14.133?',
    steps: [
      'Confirmei a release e localizei a Lei nº 14.133/2021 pelo ID estável',
      'Abri o art. 5º no Leitor da Biblioteca',
      'Conferi o texto do dispositivo e os metadados da norma',
      'Preparei uma síntese com referência e data de corte',
    ],
    result: 'O art. 5º enumera legalidade, impessoalidade, moralidade, publicidade, eficiência, interesse público, probidade, igualdade, planejamento, transparência e outros princípios. Também menciona segregação de funções, motivação, vinculação ao edital e julgamento objetivo.',
  },
  {
    id: 'transparencia',
    label: 'Transparência',
    prompt: 'A transparência aparece expressamente na Lei 14.133?',
    steps: [
      'Localizei a ocorrência no texto integral da Lei nº 14.133/2021',
      'Conferi o contexto no caput do art. 5º',
      'Separei o princípio das regras específicas de divulgação',
      'Vinculei a resposta ao artigo consultado',
    ],
    result: 'Sim. Transparência aparece expressamente no art. 5º, entre os princípios observados na aplicação da Lei. O artigo enuncia o princípio; obrigações concretas de divulgação dependem também dos dispositivos específicos aplicáveis.',
  },
  {
    id: 'atualidade',
    label: 'Data de corte',
    prompt: 'O corpus confirma que essa lei está em vigor hoje?',
    steps: [
      'Confirmei a situação registrada para o documento',
      'Verifiquei a data de corte e a release do corpus',
      'Evitei estender a confirmação para além do corte',
      'Mantive a fonte oficial disponível para conferência',
    ],
    result: `O registro consultado indica situação “em vigor”, com corte em ${cutoff}. Isso descreve o estado representado no corpus até essa data; não confirma atualizações posteriores.`,
  },
  {
    id: 'referencia',
    label: 'Referência',
    prompt: 'Como posso citar esse trecho e conferir a origem?',
    steps: [
      'Confirmei o título e o identificador estável da norma',
      'Associei a citação ao art. 5º consultado no Leitor',
      'Recuperei a release e a data de corte',
      'Conferi a indicação da fonte oficial no registro',
    ],
    result: `Lei nº 14.133, de 1º de abril de 2021, art. 5º. ID: ${law.id}. Release ${release.version}; corte em ${cutoff}. Fonte oficial indicada: Planalto.`,
  },
];

const ROW = {
  hidden: { opacity: 0, y: 7, filter: 'blur(5px)' },
  shown: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: { duration: 0.3, ease: [0.23, 1, 0.32, 1] as const },
  },
};

const STEP_IN = {
  initial: { opacity: 0, y: 6, filter: 'blur(4px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)' },
  transition: { duration: 0.28, ease: [0.23, 1, 0.32, 1] as const },
};

function useScenarioClock(scenario: Scenario, running: boolean, onDone: () => void) {
  const reduce = useShouldReduceMotion();
  const [progress, setProgress] = useState(-1);
  const doneRef = useRef(onDone);
  useEffect(() => { doneRef.current = onDone; });

  useEffect(() => {
    if (!running || reduce) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    const typedDuration = scenario.prompt.length * TYPE_MS + 350;
    for (let step = 0; step <= scenario.steps.length; step++) {
      timers.push(setTimeout(() => setProgress(step), typedDuration + step * STEP_MS));
    }
    timers.push(setTimeout(
      () => doneRef.current(),
      typedDuration + scenario.steps.length * STEP_MS + HOLD_MS,
    ));
    return () => {
      timers.forEach(clearTimeout);
      setProgress(-1);
    };
  }, [running, reduce, scenario]);

  if (!running) return reduce ? scenario.steps.length : progress;
  return reduce ? scenario.steps.length : progress;
}

function StepIcon({ done, reduce }: { done: boolean; reduce: boolean }) {
  return (
    <span className="relative flex h-5 w-4 shrink-0 items-center justify-center">
      <AnimatePresence mode="popLayout" initial={false}>
        {done ? (
          <motion.span key="done" {...(reduce ? {} : STEP_IN)} className="inline-flex text-emerald-600">
            <CheckmarkCircle02 animate={!reduce} size={16} />
          </motion.span>
        ) : (
          <motion.span key="working" exit={reduce ? undefined : { opacity: 0, scale: 0.85 }} className="inline-flex text-muted-foreground">
            <Loading03 animate={!reduce} size={16} />
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  );
}

function ScenarioPane({
  scenario,
  running,
  onDone,
}: {
  scenario: Scenario;
  running: boolean;
  onDone: () => void;
}) {
  const reduce = useShouldReduceMotion();
  const progress = useScenarioClock(scenario, running, onDone);
  const finished = progress >= scenario.steps.length;

  return (
    <div className="mx-auto grid min-h-[430px] max-w-4xl gap-1">
      <div className="flex min-h-[430px] flex-col gap-4 rounded-lg bg-background p-5 md:p-8">
        <div className="flex items-start gap-2.5 rounded-lg bg-accent px-4 py-3 text-sm leading-5 sm:text-base">
          <span className="flex h-5 shrink-0 items-center text-muted-foreground"><ArrowRight01 animate={!reduce && progress >= 0} animation="default-loop" size={16} /></span>
          {running && !reduce ? <TypingText key={`${scenario.id}-prompt`} text={scenario.prompt} duration={TYPE_MS} className="font-medium" /> : <span className="font-medium">{scenario.prompt}</span>}
        </div>

        <ol aria-label="Etapas demonstrativas da consulta" className="flex flex-col gap-3 text-[13px] sm:text-sm">
          {scenario.steps.map((step, index) => progress >= index ? (
            <motion.li
              key={step}
              {...(reduce ? {} : STEP_IN)}
              className="flex items-start gap-3 leading-5 text-muted-foreground"
            >
              <StepIcon done={progress > index} reduce={reduce} />
              <span className={progress > index ? 'text-foreground' : ''}>{step}</span>
            </motion.li>
          ) : null)}
        </ol>

        <AnimatePresence initial={false}>
          {finished && (
            <motion.div
              {...(reduce ? {} : STEP_IN)}
              className="mt-auto rounded-lg bg-accent px-4 py-4 text-[13px] leading-6 text-foreground sm:px-5 sm:text-sm"
            >
              <div className="mb-2 flex items-center gap-2 text-[10px] font-medium uppercase tracking-[.12em] text-muted-foreground">
                <HugeiconsIcon icon={SparklesIcon} strokeWidth={2} size={14} className="text-foreground" />
                Resposta com fonte
              </div>
              <p>{scenario.result}</p>
              <div className="mt-3 flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-t border-border/70 pt-3 text-[10px] text-muted-foreground">
                <span>Lei 14.133/2021 · art. 5º · {law.id}</span>
                <a href="./biblioteca/" className="shrink-0 font-medium text-foreground underline decoration-border underline-offset-4 hover:decoration-foreground">Abrir na Biblioteca ↗</a>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

    </div>
  );
}

const reveal = (index: number, reduce: boolean) => ({
  initial: reduce ? false : { opacity: 0, y: 22, filter: 'blur(7px)' },
  whileInView: { opacity: 1, y: 0, filter: 'blur(0px)' },
  viewport: { once: true, margin: '-80px' },
  transition: reduce ? { duration: 0 } : { duration: 0.6, ease: [0.23, 1, 0.32, 1] as const, delay: index * 0.08 },
});

export function AISection() {
  const reduce = useShouldReduceMotion();
  const [active, setActive] = useState(scenarios[0]!.id);
  const [auto, setAuto] = useState(true);
  const [audience, setAudience] = useState<'humanos' | 'agentes'>('humanos');
  const demoRef = useRef<HTMLDivElement>(null);
  // Warm the real library/reader preview before the section reaches the viewport.
  const started = useInView(demoRef, { margin: '600px', once: true });
  const demoInView = useInView(demoRef, { margin: '-120px' });
  const [pageVisible, setPageVisible] = useState(true);

  useEffect(() => {
    const updateVisibility = () => setPageVisible(document.visibilityState === 'visible');
    updateVisibility();
    document.addEventListener('visibilitychange', updateVisibility);
    return () => document.removeEventListener('visibilitychange', updateVisibility);
  }, []);

  const advance = () => {
    if (!auto || reduce || !demoInView || !pageVisible) return;
    const index = scenarios.findIndex((scenario) => scenario.id === active);
    setActive(scenarios[(index + 1) % scenarios.length]!.id);
  };
  const loadingPulse = demoInView && pageVisible && !reduce ? 'animate-pulse' : '';

  return (
    <section id="assistente" data-slot="home-ai" className="mx-auto mt-28 flex w-full max-w-[1500px] flex-col items-center px-5 pb-8 text-center sm:mt-36">
      <motion.span {...reveal(0, reduce)} className="inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs text-muted-foreground">
        <HugeiconsIcon icon={SparklesIcon} strokeWidth={2} size={14} />
        Skill VadeMecum MD
      </motion.span>
      <motion.h2 {...reveal(1, reduce)} className="mt-5 text-4xl font-medium tracking-tight text-balance md:text-6xl">
        Do acervo à resposta, com fonte verificável.
      </motion.h2>
      <motion.p {...reveal(2, reduce)} className="mt-5 max-w-[620px] text-base leading-7 text-balance text-muted-foreground sm:text-lg">
        Explore a Biblioteca e o Leitor. Depois, acompanhe a skill consultando o corpus e citando a fonte.
      </motion.p>

      <motion.div {...reveal(3, reduce)} ref={demoRef} data-slot="ai-demo" className="mt-9 w-full text-left sm:mt-10">
        <Tabs value={audience} onValueChange={(value) => setAudience(value as 'humanos' | 'agentes')} className="flex flex-col items-center gap-5">
          <TabsHighlight className="absolute inset-0 z-0 rounded-lg bg-accent">
            <TabsList aria-label="Demonstrações para humanos e agentes" className="inline-flex max-w-full flex-wrap items-center justify-center gap-1 text-xs sm:text-sm">
              <TabsHighlightItem value="humanos"><TabsTrigger value="humanos" className="relative z-10 rounded-md px-4 py-2 text-muted-foreground transition-colors data-[state=active]:text-foreground">Para humanos</TabsTrigger></TabsHighlightItem>
              <TabsHighlightItem value="agentes"><TabsTrigger value="agentes" className="relative z-10 rounded-md px-4 py-2 text-muted-foreground transition-colors data-[state=active]:text-foreground">Para agentes</TabsTrigger></TabsHighlightItem>
            </TabsList>
          </TabsHighlight>

          <TabsContents className="w-full rounded-xl bg-accent p-1">
            <TabsContent value="humanos">
              <div className="flex items-center gap-3 px-3 pb-2.5 pt-1.5">
                <span className="flex gap-1.5" aria-hidden="true"><span className="size-2.5 rounded-full bg-foreground/15" /><span className="size-2.5 rounded-full bg-foreground/15" /><span className="size-2.5 rounded-full bg-foreground/15" /></span>
                <span className="font-mono text-[10px] text-muted-foreground sm:text-xs">~/biblioteca</span>
                <span className="ml-auto hidden text-[9px] uppercase tracking-[.12em] text-muted-foreground sm:inline">Biblioteca oficial · interface interativa</span>
              </div>
              {audience === 'humanos' && (started ? <Suspense fallback={<div className="grid min-h-[650px] grid-cols-2 gap-3 p-4" aria-hidden="true"><div className={`${loadingPulse} rounded-xl bg-background motion-reduce:animate-none`} /><div className={`${loadingPulse} rounded-xl bg-background motion-reduce:animate-none`} /></div>}><LibraryReaderPreview mode="split" /></Suspense> : <div className="grid min-h-[650px] grid-cols-2 gap-3 p-4" aria-hidden="true"><div className={`${loadingPulse} rounded-xl bg-background motion-reduce:animate-none`} /><div className={`${loadingPulse} rounded-xl bg-background motion-reduce:animate-none`} /></div>)}
            </TabsContent>
            <TabsContent value="agentes">
              <div className="flex items-center gap-3 px-3 pb-2.5 pt-1.5">
                <span className="flex gap-1.5" aria-hidden="true"><span className="size-2.5 rounded-full bg-foreground/15" /><span className="size-2.5 rounded-full bg-foreground/15" /><span className="size-2.5 rounded-full bg-foreground/15" /></span>
                <span className="font-mono text-[10px] text-muted-foreground sm:text-xs">~/consulta-juridica</span>
                <span className="ml-auto hidden text-[9px] uppercase tracking-[.12em] text-muted-foreground sm:inline">Exemplo demonstrativo · corpus v{release.version}</span>
              </div>
              {audience === 'agentes' && (
              <Tabs value={active} onValueChange={(value) => { setAuto(false); setActive(value); }} className="flex flex-col items-center gap-4">
                <TabsHighlight className="absolute inset-0 z-0 rounded-lg bg-background/80">
                  <TabsList aria-label="Conversas demonstrativas com a skill" className="inline-flex max-w-full flex-wrap items-center justify-center gap-1 text-xs sm:text-sm">
                    {scenarios.map(scenario => <TabsHighlightItem key={scenario.id} value={scenario.id}><TabsTrigger value={scenario.id} className="relative z-10 rounded-md px-3 py-1.5 text-muted-foreground transition-colors data-[state=active]:text-foreground sm:px-3.5">{scenario.label}</TabsTrigger></TabsHighlightItem>)}
                  </TabsList>
                </TabsHighlight>
                <TabsContents className="w-full rounded-lg">
                  {scenarios.map(scenario => <TabsContent key={scenario.id} value={scenario.id}><ScenarioPane scenario={scenario} running={started && demoInView && pageVisible && !reduce && audience === 'agentes' && active === scenario.id} onDone={advance} /></TabsContent>)}
                </TabsContents>
              </Tabs>
              )}
            </TabsContent>
          </TabsContents>
        </Tabs>
      </motion.div>

      <motion.div {...reveal(4, reduce)} className="mt-8 flex max-w-full flex-col items-center gap-4 sm:mt-10">
        <span className="text-sm text-muted-foreground">Consulte a legislação com uma skill compatível com Codex, Claude Code, Cursor e outros agentes.</span>
        <a href="#skill" className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/85">Instalar a skill <span aria-hidden="true">↗</span></a>
        <a href="./biblioteca/" className="text-xs text-muted-foreground underline decoration-border underline-offset-4 hover:text-foreground hover:decoration-foreground">Abrir a Biblioteca completa</a>
      </motion.div>
    </section>
  );
}
