'use client';

import { Button } from '@animate-ui/react/primitives/buttons/button';
import { AnimateIcon } from '@animate-ui/react/icons';
import {
  Tabs,
  TabsContent,
  TabsContents,
  TabsHighlight,
  TabsHighlightItem,
  TabsList,
  TabsTrigger,
} from '@animate-ui/react/primitives/tabs';
import { ShimmeringText } from '@animate-ui/react/primitives/texts/shimmering';
import { TypingText } from '@animate-ui/react/primitives/texts/typing';
import {
  blur,
  ease,
  scale,
  spring,
  useShouldReduceMotion,
} from '@animate-ui/react/utils/motion';
import {
  FloppyDiskIcon,
  Loading03Icon,
  SparklesIcon,
  Tick02Icon,
} from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';
import { AnimatePresence, motion, useInView } from 'motion/react';
import Link from './link';
import { useEffect, useRef, useState, type ComponentType } from 'react';

import { CopyCommand, useHomeFramework } from '@/components/hero';
import { ArrowRight01 } from '@/registry/hugeicons/arrow-right-01';
import { CheckmarkCircle02 } from '@/registry/hugeicons/checkmark-circle-02';
import { Loading03 } from '@/registry/hugeicons/loading-03';
import { Notification01 } from '@/registry/hugeicons/notification-01';

const TYPE_MS = 26;
const STEP_MS = 750;
const HOLD_MS = 5600;

function Rich({ text }: { text: string }) {
  return text.split('`').map((part, index) =>
    index % 2 ? (
      <code
        key={index}
        className="rounded bg-foreground/[0.06] px-1 py-px font-mono text-[0.92em] text-foreground"
      >
        {part}
      </code>
    ) : (
      part
    ),
  );
}

type Scenario = {
  id: string;
  label: string;
  prompt: string;
  steps: string[];
  result: string;
  Preview: ComponentType<{ playing: boolean; working: boolean }>;
};

function SavePreview({ playing }: { playing: boolean }) {
  const [state, setState] = useState<'idle' | 'loading' | 'saved'>('idle');
  const [pressed, setPressed] = useState(false);
  useEffect(() => {
    if (!playing) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    const run = (at: number) => {
      timers.push(setTimeout(() => setPressed(true), at));
      timers.push(
        setTimeout(() => {
          setPressed(false);
          setState('loading');
        }, at + 140),
      );
      timers.push(setTimeout(() => setState('saved'), at + 1500));
      timers.push(setTimeout(() => setState('idle'), at + 2900));
    };
    run(300);
    run(3600);
    return () => {
      timers.forEach(clearTimeout);
      setState('idle');
      setPressed(false);
    };
  }, [playing]);

  const content = {
    idle: { icon: FloppyDiskIcon, label: 'Salvar pesquisa' },
    loading: { icon: Loading03Icon, label: 'Salvando…' },
    saved: { icon: Tick02Icon, label: 'Salvo' },
  }[state];

  return (
    <motion.button
      type="button"
      tabIndex={-1}
      animate={{ scale: pressed ? scale.press : 1 }}
      transition={spring.press}
      className="inline-flex h-11 w-44 items-center justify-center gap-2 overflow-hidden rounded-lg bg-primary text-sm font-medium text-primary-foreground"
    >
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={state}
          initial={{ opacity: 0, y: 8, filter: blur.surface }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          exit={{
            opacity: 0,
            y: -8,
            filter: blur.surface,
            transition: { duration: 0.15, ease: ease.out },
          }}
          transition={{ duration: 0.3, ease: ease.out, delay: 0.06 }}
          className="inline-flex items-center gap-2"
        >
          <motion.span
            className="inline-flex"
            animate={state === 'loading' ? { rotate: 360 } : { rotate: 0 }}
            transition={
              state === 'loading'
                ? { duration: 0.8, ease: 'linear', repeat: Infinity }
                : { duration: 0 }
            }
          >
            <HugeiconsIcon icon={content.icon} strokeWidth={2} size={16} />
          </motion.span>
          {content.label}
        </motion.span>
      </AnimatePresence>
    </motion.button>
  );
}

function BellPreview({ playing }: { playing: boolean }) {
  return (
    <div className="flex flex-col items-center gap-4">
      <AnimateIcon animate={playing} loop loopDelay={700} animateOnHover>
        <span className="flex size-20 items-center justify-center rounded-xl bg-accent">
          <Notification01 size={36} />
        </span>
      </AnimateIcon>
      <span className="text-xs text-muted-foreground">
        passe o mouse · toque · explore
      </span>
    </div>
  );
}

const TASKS = [
  'Ler o documento',
  'Conectar as fontes',
  'Revisar as anotações',
  'Salvar uma descoberta',
  'Organizar a coleção',
];

function TodoPreview({ playing }: { playing: boolean }) {
  const [tasks, setTasks] = useState([TASKS[0]!, TASKS[2]!]);
  useEffect(() => {
    if (!playing) return;
    let next = 0;
    const moves: ((list: string[]) => string[])[] = [
      (list) => [...list, TASKS[1]!],
      (list) => list.filter((task) => task !== TASKS[0]),
      (list) => [...list, TASKS[3]!],
      (list) => list.filter((task) => task !== TASKS[2]),
      (list) => [TASKS[4]!, ...list],
      (list) => list.filter((task) => task !== TASKS[1]),
    ];
    const id = setInterval(() => {
      setTasks(moves[next % moves.length]!);
      next += 1;
    }, 950);
    return () => {
      clearInterval(id);
      setTasks([TASKS[0]!, TASKS[2]!]);
    };
  }, [playing]);

  return (
    <ul className="flex w-64 flex-col gap-2">
      <AnimatePresence mode="popLayout" initial={false}>
        {tasks.map((task) => (
          <motion.li
            key={task}
            layout
            initial={{ opacity: 0, y: 10, filter: blur.surface }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, filter: blur.surface }}
            transition={{
              layout: spring.reflow,
              default: { duration: 0.3, ease: ease.out },
            }}
            className="flex items-center gap-3 rounded-lg bg-accent px-3 py-2.5 text-sm"
          >
            <span className="size-4 shrink-0 rounded-[5px] border-2 border-muted-foreground/40" />
            {task}
          </motion.li>
        ))}
      </AnimatePresence>
    </ul>
  );
}

const FINDINGS = [
  {
    where: 'Legislação',
    fact: 'o texto como ponto de partida',
    verdict: 'Explorar',
    tone: 'text-red-500',
  },
  {
    where: 'Jurisprudência',
    fact: 'outros olhares para o tema',
    verdict: 'Conectar',
    tone: 'text-amber-500',
  },
  {
    where: 'Doutrina',
    fact: 'conceitos e fundamentos',
    verdict: 'Compreender',
    tone: 'text-amber-500',
  },
  {
    where: 'Anotações',
    fact: 'o que faz sentido para você',
    verdict: 'Organizar',
    tone: 'text-amber-500',
  },
  {
    where: 'Coleção',
    fact: 'descobertas no mesmo lugar',
    verdict: 'Guardar',
    tone: 'text-emerald-500',
  },
];

function ReviewPreview({
  playing,
  working,
}: {
  playing: boolean;
  working: boolean;
}) {
  return (
    <div className="flex min-h-[18rem] w-full max-w-sm flex-col justify-center text-sm">
      <AnimatePresence mode="popLayout" initial={false}>
        {playing ? (
          <motion.div
            key="report"
            initial="hidden"
            animate="shown"
            exit="hidden"
            variants={{
              hidden: { opacity: 0, filter: blur.surface },
              shown: {
                opacity: 1,
                filter: 'blur(0px)',
                transition: { staggerChildren: 0.12 },
              },
            }}
            className="flex flex-col gap-1"
          >
            <motion.div
              variants={ROW}
              className="mb-2 flex items-center justify-between px-1 text-xs text-muted-foreground"
            >
              <span>5 temas ilustrativos</span>
              <span>4 perspectivas</span>
            </motion.div>
            {FINDINGS.map((finding) => (
              <motion.div
                key={finding.where}
                variants={ROW}
                className="flex items-center gap-3 rounded-lg bg-accent px-3 py-2"
              >
                <div className="flex min-w-0 flex-1 flex-col">
                  <span className="font-medium">{finding.where}</span>
                  <span className="truncate text-xs text-muted-foreground">
                    {finding.fact}
                  </span>
                </div>
                <span
                  className="shrink-0 text-xs font-medium text-muted-foreground"
                >
                  {finding.verdict}
                </span>
              </motion.div>
            ))}
          </motion.div>
        ) : working ? (
          <motion.div
            key="working"
            initial={{ opacity: 0, filter: blur.surface }}
            animate={{ opacity: 1, filter: 'blur(0px)' }}
            exit={{ opacity: 0, filter: blur.surface }}
            transition={{ duration: 0.3, ease: ease.out }}
            className="text-center"
          >
            <ShimmeringText text="Explorando conexões…" />
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}

const ROW = {
  hidden: { opacity: 0, y: 8, filter: blur.surface },
  shown: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: { duration: 0.35, ease: ease.out },
  },
};

const SCENARIOS: Scenario[] = [
{id:'button',label:'Salvar pesquisa',prompt:'Guarde esta descoberta para continuar a pesquisa depois.',steps:['Escolha um tema no `acervo ilustrativo`','Explore o documento e suas conexões','Organize a descoberta em uma `coleção`','Retome a leitura do seu ponto de partida'],result:'Uma nova descoberta na sua coleção · simulação',Preview:SavePreview},
{id:'icon',label:'Acompanhar',prompt:'Dê atenção aos temas que fazem parte da sua rotina.',steps:['Comece com uma questão da sua prática','Escolha os assuntos que quer acompanhar','Conecte fontes e perspectivas diferentes','Mantenha seu repertório em movimento'],result:'Um novo olhar para o mesmo tema · simulação',Preview:BellPreview},
{id:'list',label:'Organizar',prompt:'Transforme uma boa pergunta em um roteiro de pesquisa.',steps:['Defina o ponto de partida da sua pesquisa','Separe leitura, contexto e anotações','Adicione e reorganize os próximos passos','Construa seu próprio caminho de estudo'],result:'Um roteiro para a próxima descoberta · simulação',Preview:TodoPreview},
{id:'review',label:'Conectar',prompt:'Explore diferentes perspectivas para uma questão jurídica.',steps:['Encontre o tema no acervo de demonstração','Compare os tipos de fonte disponíveis','Dê contexto à descoberta com anotações','Reúna os caminhos em uma visão organizada'],result:'Perspectivas conectadas · conteúdo ilustrativo',Preview:ReviewPreview},
];

const VUE_SCENARIOS: Scenario[] = SCENARIOS.map((scenario) => {
  const vue: Partial<Record<string, Partial<Scenario>>> = {
    button: {
      steps: [
        'Read `components.json`: shadcn-vue on Reka UI',
        ...scenario.steps.slice(1),
      ],
      result: 'Edited `components/SaveButton.vue`',
    },
    icon: { result: 'Created `components/icons/Notification.vue`' },
    list: {
      steps: [
        'Read `package.json`: Vue and Motion for Vue',
        ...scenario.steps.slice(1),
      ],
      result: 'Edited `components/TodoList.vue`',
    },
  };
  return { ...scenario, ...vue[scenario.id] };
});

function useScenarioClock(
  scenario: Scenario,
  running: boolean,
  onDone: () => void,
) {
  const reduce = useShouldReduceMotion();
  const total = scenario.steps.length;
  const [progress, setProgress] = useState(-1);
  const doneRef = useRef(onDone);
  useEffect(() => {
    doneRef.current = onDone;
  });

  useEffect(() => {
    if (!running || reduce) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    const typed = scenario.prompt.length * TYPE_MS + 450;
    for (let step = 0; step <= total; step++)
      timers.push(setTimeout(() => setProgress(step), typed + step * STEP_MS));
    timers.push(
      setTimeout(() => doneRef.current(), typed + total * STEP_MS + HOLD_MS),
    );
    return () => {
      timers.forEach(clearTimeout);
      setProgress(-1);
    };
  }, [running, reduce, scenario, total]);

  if (!running) return -1;
  return reduce ? total : progress;
}

function StepIcon({ done }: { done: boolean }) {
  return (
    <span className="relative flex h-5 w-4 shrink-0 items-center justify-center">
      <AnimatePresence mode="popLayout" initial={false}>
        {done ? (
          <motion.span
            key="done"
            initial={{ opacity: 0, scale: scale.icon, filter: blur.icon }}
            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
            transition={spring.pop}
            className="inline-flex text-foreground"
          >
            <CheckmarkCircle02 animate size={16} />
          </motion.span>
        ) : (
          <motion.span
            key="running"
            exit={{ opacity: 0, scale: scale.icon, filter: blur.icon }}
            transition={{ duration: 0.15, ease: ease.out }}
            className="inline-flex text-muted-foreground"
          >
            <Loading03 animate size={16} />
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  );
}

const STEP_IN = {
  initial: { opacity: 0, y: 6, filter: blur.icon },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)' },
  transition: { duration: 0.35, ease: ease.out },
};

function ScenarioPane({
  scenario,
  running,
  onDone,
}: {
  scenario: Scenario;
  running: boolean;
  onDone: () => void;
}) {
  const progress = useScenarioClock(scenario, running, onDone);
  const total = scenario.steps.length;
  const finished = progress >= total;
  const { Preview } = scenario;

  return (
    <div className="grid min-h-[380px] gap-1 md:grid-cols-[1.05fr_1fr]">
      <div className="flex h-[27rem] flex-col gap-4 rounded-lg bg-background p-5 md:h-auto md:p-6">
        <div className="flex items-start gap-2.5 rounded-lg bg-accent px-4 py-3 text-sm leading-5">
          <span className="flex h-5 shrink-0 items-center text-muted-foreground">
            <ArrowRight01
              animate={progress >= 0}
              animation="default-loop"
              size={16}
            />
          </span>
          {running ? (
            <TypingText
              key={`${scenario.id}-typing`}
              text={scenario.prompt}
              duration={TYPE_MS}
              className="font-medium"
            />
          ) : (
            <span className="font-medium">{scenario.prompt}</span>
          )}
        </div>
        <ol className="flex flex-col gap-3 text-sm">
          {scenario.steps.map((step, index) =>
            progress >= index ? (
              <motion.li
                key={step}
                {...STEP_IN}
                className="flex items-start gap-3 leading-5 text-muted-foreground"
              >
                <StepIcon done={progress > index} />
                <span className={progress > index ? 'text-foreground' : ''}>
                  <Rich text={step} />
                </span>
              </motion.li>
            ) : null,
          )}
        </ol>
        <AnimatePresence>
          {finished && (
            <motion.div
              {...STEP_IN}
              className="mt-auto flex items-center gap-2 rounded-lg bg-accent px-3 py-2 text-xs text-muted-foreground"
            >
              <HugeiconsIcon
                icon={SparklesIcon}
                strokeWidth={2}
                size={14}
                className="text-foreground"
              />
              <span>
                <Rich text={scenario.result} />
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <div className="relative flex h-[25rem] flex-col rounded-lg bg-background md:h-auto bg-[radial-gradient(var(--color-border)_1px,transparent_1px)] [background-size:16px_16px]">
        <div className="absolute top-4 left-5 flex items-center gap-2">
          <span className="rounded-md bg-accent px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
            vademecum · demonstração
          </span>
        </div>
        <div className="flex flex-1 items-center justify-center px-6 py-11">
          <Preview
            playing={running && finished}
            working={running && !finished}
          />
        </div>
      </div>
    </div>
  );
}

const reveal = (index: number) => ({
  initial: { opacity: 0, y: 24, filter: 'blur(8px)' },
  whileInView: { opacity: 1, y: 0, filter: 'blur(0px)' },
  viewport: { once: true, margin: '-80px' },
  transition: { duration: 0.7, ease: ease.out, delay: index * 0.09 },
});

export function AISection() {
  const framework = useHomeFramework();
  const scenarios = framework === 'vue' ? VUE_SCENARIOS : SCENARIOS;
  const docs = framework === 'vue' ? '/docs/vue' : '/docs';
  const [active, setActive] = useState(SCENARIOS[0]!.id);
  const [auto, setAuto] = useState(true);
  const windowRef = useRef<HTMLDivElement>(null);
  const started = useInView(windowRef, { margin: '-120px', once: true });

  const advance = () => {
    if (!auto) return;
    const index = scenarios.findIndex((scenario) => scenario.id === active);
    setActive(scenarios[(index + 1) % scenarios.length]!.id);
  };

  return (
    <section
      id="assistente"
      data-slot="home-ai"
      className="mx-auto mt-32 flex w-full max-w-[1100px] flex-col items-center px-5 text-center"
    >
      <motion.span
        {...reveal(0)}
        className="inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs text-muted-foreground"
      >
        <HugeiconsIcon icon={SparklesIcon} strokeWidth={2} size={14} />
        Vademecum · experiência interativa
      </motion.span>
      <motion.h2
        {...reveal(1)}
        className="mt-5 text-4xl font-medium text-balance md:text-6xl"
      >
        Uma ideia. Novas possibilidades.
      </motion.h2>
      <motion.p
        {...reveal(2)}
        className="mt-5 max-w-[620px] text-lg text-balance text-muted-foreground"
      >
        Da primeira pergunta à próxima descoberta. Explore esta proposta para
        pesquisar, conectar e organizar o conhecimento jurídico no seu ritmo.
      </motion.p>

      <motion.div
        {...reveal(3)}
        ref={windowRef}
        data-slot="ai-demo"
        className="mt-10 w-full text-left"
      >
        <Tabs
          value={active}
          onValueChange={(value) => {
            setAuto(false);
            setActive(value);
          }}
          className="flex flex-col items-center gap-4"
        >
          <TabsHighlight className="absolute inset-0 z-0 rounded-lg bg-accent">
            <TabsList
          aria-label="Demonstração interativa"
              className="inline-flex flex-wrap items-center justify-center gap-1 text-sm"
            >
              {scenarios.map((scenario) => (
                <TabsHighlightItem key={scenario.id} value={scenario.id}>
                  <TabsTrigger
                    value={scenario.id}
                    className="relative z-10 rounded-md px-3 py-1.5 text-muted-foreground transition-colors duration-300 hover:text-foreground data-[state=active]:text-foreground"
                  >
                    {scenario.label}
                  </TabsTrigger>
                </TabsHighlightItem>
              ))}
            </TabsList>
          </TabsHighlight>
          <div className="w-full overflow-hidden rounded-xl bg-accent p-1">
            <div className="flex items-center gap-3 px-3 pt-1.5 pb-2.5">
              <span className="flex gap-1.5" aria-hidden="true">
                <span className="size-2.5 rounded-full bg-foreground/15" />
                <span className="size-2.5 rounded-full bg-foreground/15" />
                <span className="size-2.5 rounded-full bg-foreground/15" />
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                ~/minha-pesquisa
              </span>
            </div>
            <TabsContents className="rounded-lg">
              {scenarios.map((scenario) => (
                <TabsContent key={scenario.id} value={scenario.id}>
                  <ScenarioPane
                    scenario={scenario}
                    running={started && active === scenario.id}
                    onDone={advance}
                  />
                </TabsContent>
              ))}
            </TabsContents>
          </div>
        </Tabs>
      </motion.div>

      <motion.div
        {...reveal(4)}
        className="mt-12 flex max-w-full flex-col items-center gap-4"
      >
        <span className="text-sm text-muted-foreground">
          Explore os exemplos. Tudo acontece nesta demonstração.
        </span>
        <CopyCommand command={(source) => `buscar --fontes "${source.toLowerCase()}" "responsabilidade civil"`} />
        <div className="flex gap-3">
          <Button
            asChild
            className="inline-flex h-10 items-center rounded-lg bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/85"
          >
          <Link href="#recursos">Explorar recursos</Link>
          </Button>
          <Button
            asChild
            className="inline-flex h-10 items-center rounded-lg bg-accent px-5 text-sm font-medium transition-colors hover:bg-accent/70"
          >
            <Link href="#inicio">Voltar ao início</Link>
          </Button>
        </div>
      </motion.div>
    </section>
  );
}
