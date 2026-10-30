import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { ease, useMotionTokens, motionTokens, scaleTransition } from '@animate-ui/react/utils/motion';
import { HeroTitle } from './hero-title';
import { useIntroDone } from './intro';

const RISE_EASE=[.23,1,.32,1] as const;
const rise=(index:number,done:boolean)=>({initial:{opacity:1,y:20,filter:'blur(10px)'},animate:done?{opacity:1,y:0,filter:'blur(0px)'}:{opacity:1,y:20,filter:'blur(10px)'},transition:{duration:.7,ease:RISE_EASE,delay:index*.09}});
export function useHomeFramework(){return 'react' as const}

export function CopyCommand({command:build=(source:string)=>`buscar --fontes "${source.toLowerCase()}" "responsabilidade civil"`}:{command?:(source:string)=>string}){
  const [manager,setManager]=useState<'Todas'|'Leis'|'Decisões'|'Doutrina'>('Todas');
  const [copied,setCopied]=useState(false);
  const command=build(manager);
  async function copy(){try{await navigator.clipboard.writeText(command);setCopied(true);setTimeout(()=>setCopied(false),1400)}catch{setCopied(false)}}
  return <div className="flex w-[min(100%,30rem)] flex-col items-center gap-2">
    <div className="relative inline-flex items-center gap-1 rounded-lg bg-accent p-1 text-xs" role="tablist" aria-label="Filtrar por tipo de fonte">
      {(['Todas','Leis','Decisões','Doutrina'] as const).map(item=><button key={item} type="button" role="tab" aria-selected={manager===item} onClick={()=>setManager(item)} className={`relative z-10 rounded-md px-2 py-1 transition-colors ${manager===item?'text-foreground':'text-muted-foreground hover:text-foreground'}`}><AnimatePresence>{manager===item&&<motion.span layoutId="manager-highlight" className="absolute inset-0 -z-10 rounded-md bg-background" transition={{type:'spring',stiffness:500,damping:35}}/>}</AnimatePresence>{item}</button>)}
    </div>
    <div className="relative flex h-12 w-full items-center rounded-xl bg-accent p-1"><div className="flex h-full flex-1 items-center gap-3 overflow-hidden rounded-lg bg-background px-4 font-mono text-sm"><span className="text-muted-foreground">$</span><AnimatePresence mode="wait" initial={false}><motion.span key={manager} initial={{opacity:1,y:5,filter:'blur(5px)'}} animate={{opacity:1,y:0,filter:'blur(0px)'}} exit={{opacity:1,y:-5,filter:'blur(5px)'}} transition={{duration:.22,ease:ease.out}} className="truncate">{command}</motion.span></AnimatePresence></div><button type="button" onClick={copy} aria-label={copied?'Busca copiada':'Copiar busca'} className="absolute right-2 flex size-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground">{copied?'✓':'▢'}</button></div>
  </div>
}

function CallsToAction(){return <div className="flex gap-3"><a href="./biblioteca/" className="inline-flex h-10 items-center rounded-lg bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:opacity-85">Explorar acervo</a><a href="#assistente" className="inline-flex h-10 items-center rounded-lg bg-accent px-5 text-sm font-medium transition-colors hover:bg-accent/70">Conhecer recursos</a></div>}
function Swap({children}:{children:React.ReactNode}){const {tempo}=useMotionTokens();return <AnimatePresence mode="wait" initial={false}><motion.span key="pesquisa" initial={{opacity:1,filter:motionTokens.blur.panel}} animate={{opacity:1,filter:'blur(0px)',transitionEnd:{filter:'none'},transition:scaleTransition(motionTokens.transition.panelIn,tempo)}} exit={{opacity:1,filter:motionTokens.blur.panel,transition:scaleTransition(motionTokens.transition.panelOut,tempo)}}>{children}</motion.span></AnimatePresence>}

export function Hero(){const done=useIntroDone();return <section id="inicio" className="flex scroll-mt-20 flex-col items-center px-5 pt-36 text-center md:pt-44">
  <motion.div {...rise(0,done)} className="mb-8"><div className="inline-flex h-8 items-center gap-1 rounded-full bg-accent p-1 text-xs"><span className="rounded-full bg-background px-3 py-1 font-medium text-foreground shadow-sm">Pesquisa</span><span className="px-3 py-1 text-muted-foreground">Conhecimento</span></div></motion.div>
  <HeroTitle done={done} libraries={['legislação','jurisprudência','doutrina','conhecimento jurídico']} />
  <motion.p {...rise(5,done)} className="mt-5 max-w-[620px] text-lg text-balance text-muted-foreground"><Swap>Encontre, conecte e compreenda o conhecimento jurídico em um só lugar.</Swap></motion.p>
  <motion.div {...rise(6,done)} className="mt-8 flex max-w-full flex-col items-center gap-4"><CopyCommand/><CallsToAction/></motion.div>
  <motion.div {...rise(7,done)} className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">{['Legislação','Jurisprudência','Doutrina','Anotações'].map(label=><span key={label} className="flex items-center gap-2"><span className="size-1.5 rounded-full bg-current opacity-40"/>{label}</span>)}</motion.div>
</section>}
