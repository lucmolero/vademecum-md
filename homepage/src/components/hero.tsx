import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { ease, useShouldReduceMotion } from '@animate-ui/react/utils/motion';
import { HeroTitle } from './hero-title';
import { useIntroDone } from './intro';
import { libraryDestination } from './library-destination';

const RISE_EASE=[.23,1,.32,1] as const;
const rise=(index:number,done:boolean,reduce:boolean)=>reduce?{initial:false,animate:{opacity:1,y:0,filter:'none'}}:{initial:{opacity:1,y:20,filter:'blur(10px)'},animate:done?{opacity:1,y:0,filter:'blur(0px)'}:{opacity:1,y:20,filter:'blur(10px)'},transition:{duration:.7,ease:RISE_EASE,delay:index*.09}};
const selectionTransition=(reduce:boolean)=>reduce?{duration:0}:{type:'spring' as const,stiffness:520,damping:38,mass:.7};

const AGENTS = [
  { label: 'Codex', id: 'codex', project: '.agents/skills', global: '~/.agents/skills' },
  { label: 'Claude Code', id: 'claude-code', project: '.claude/skills', global: '~/.claude/skills' },
  { label: 'Cursor', id: 'cursor', project: '.agents/skills', global: '~/.cursor/skills' },
  { label: 'OpenCode', id: 'opencode', project: '.agents/skills', global: '~/.config/opencode/skills' },
] as const;

type SkillKitInfo = { version:string; cutoff:string; documentCount:number; download:string; checksum:string; sha256:string; sizeBytes:number };
type InstallAudience = 'agent'|'human';

function AudienceTabs({audience,onChange}:{audience:InstallAudience;onChange:(value:InstallAudience)=>void}){
  const reduce=useShouldReduceMotion();
  const select=(value:InstallAudience)=>{onChange(value);requestAnimationFrame(()=>document.getElementById(`skill-tab-${value}`)?.focus())};
  const onKeyDown=(event:React.KeyboardEvent<HTMLButtonElement>,current:InstallAudience)=>{
    if(!['ArrowRight','ArrowLeft','Home','End'].includes(event.key))return;
    event.preventDefault();
    const next=event.key==='Home'?'agent':event.key==='End'?'human':current==='agent'?'human':'agent';
    select(next);
  };
  return <div role="tablist" aria-label="Escolha o modo de instalação" className="mx-auto inline-flex rounded-full bg-muted/75 p-1.5">
    <button id="skill-tab-agent" type="button" role="tab" aria-selected={audience==='agent'} tabIndex={audience==='agent'?0:-1} onClick={()=>onChange('agent')} onKeyDown={event=>onKeyDown(event,'agent')} className={`relative inline-flex items-center gap-2 rounded-full px-5 py-2 text-sm font-medium transition-colors ${audience==='agent'?'text-foreground':'text-muted-foreground hover:text-foreground'}`}>
      {audience==='agent'&&<motion.span aria-hidden="true" layoutId="skill-audience-indicator" className="absolute inset-0 rounded-full bg-background shadow-sm" transition={selectionTransition(reduce)}/>}
      <span className="relative inline-flex items-center gap-2">
      <svg aria-hidden="true" viewBox="0 0 20 20" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><rect x="3.5" y="6" width="13" height="10" rx="3"/><path d="M10 3v3M7.5 10h.01M12.5 10h.01M7.5 13h5"/></svg>Para agentes
      </span>
    </button>
    <button id="skill-tab-human" type="button" role="tab" aria-selected={audience==='human'} tabIndex={audience==='human'?0:-1} onClick={()=>onChange('human')} onKeyDown={event=>onKeyDown(event,'human')} className={`relative inline-flex items-center gap-2 rounded-full px-5 py-2 text-sm font-medium transition-colors ${audience==='human'?'text-foreground':'text-muted-foreground hover:text-foreground'}`}>
      {audience==='human'&&<motion.span aria-hidden="true" layoutId="skill-audience-indicator" className="absolute inset-0 rounded-full bg-background shadow-sm" transition={selectionTransition(reduce)}/>}
      <span className="relative inline-flex items-center gap-2">
      <svg aria-hidden="true" viewBox="0 0 20 20" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><circle cx="10" cy="6" r="3"/><path d="M4 17a6 6 0 0 1 12 0"/></svg>Para humanos
      </span>
    </button>
  </div>;
}

function CopyCommand({audience}:{audience:InstallAudience}){
  const reduce=useShouldReduceMotion();
  const [agent,setAgent]=useState<(typeof AGENTS)[number]['id']>('codex');
  const [global,setGlobal]=useState(false);
  const [copyState,setCopyState]=useState<'prompt'|'npx'|'error'|null>(null);
  const [showNpx,setShowNpx]=useState(false);
  const [kit,setKit]=useState<SkillKitInfo|null>(null);
  useEffect(()=>setCopyState(null),[audience]);
  useEffect(()=>{
    const controller=new AbortController();
    fetch(new URL('./skill-kit.json',document.baseURI),{signal:controller.signal})
      .then(response=>response.ok?response.json():null)
      .then(value=>{if(value?.download&&value?.sha256)setKit(value as SkillKitInfo)})
      .catch(()=>{});
    return ()=>controller.abort();
  },[]);
  const selectedAgent=AGENTS.find(item=>item.id===agent)!;
  const downloadUrl=kit?new URL(kit.download,document.baseURI).href:new URL('./downloads/vademecum-consulta-juridica-kit.zip',document.baseURI).href;
  const checksumUrl=kit?new URL(kit.checksum,document.baseURI).href:`${downloadUrl}.sha256`;
  const command=`npx skills add lucmolero/vademecum-md --skill vademecum-consulta-juridica --agent ${agent}${global?' --global':''} --yes`;
  const skillPath=global?selectedAgent.global:selectedAgent.project;
  const setupPrompt=`Instale a skill + corpus VadeMecum MD para ${selectedAgent.label} em ${skillPath}. Baixe ${downloadUrl}; valide SHA-256 em ${checksumUrl}; siga README.md e preserve dados existentes.`;
  async function copy(text:string,target:'prompt'|'npx'){
    try {
      await navigator.clipboard.writeText(text);
      setCopyState(target);
    } catch {
      try {
        const field=document.createElement('textarea');
        field.value=text;
        field.setAttribute('readonly','');
        field.style.position='fixed';
        field.style.opacity='0';
        document.body.appendChild(field);
        field.select();
        const copied=document.execCommand('copy');
        field.remove();
        setCopyState(copied?target:'error');
      } catch {
        setCopyState('error');
      }
    }
    window.setTimeout(()=>setCopyState(null),1800);
  }
  const downloadAction=<a href={downloadUrl} download className="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-foreground px-6 text-sm font-semibold text-background transition-opacity hover:opacity-85 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"><svg aria-hidden="true" viewBox="0 0 20 20" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M10 2v10m0 0 3.5-3.5M10 12 6.5 8.5M3 13v4h14v-4"/></svg>Baixar kit completo</a>;
  const documentationAction=(label:string)=><a href="https://github.com/lucmolero/vademecum-md/tree/main/skills/vademecum-consulta-juridica" className="inline-flex h-12 items-center justify-center rounded-xl bg-muted/75 px-6 text-sm font-semibold text-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">{label}</a>;

  return <div className="w-[min(100%,48rem)] text-center">


    <AnimatePresence mode="wait" initial={false}>
      {audience==='agent' ? <motion.div id="skill-panel-agent" aria-labelledby="skill-tab-agent" key="agent" role="tabpanel" initial={reduce?false:{opacity:0,y:8}} animate={{opacity:1,y:0}} exit={reduce?{opacity:0}:{opacity:0,y:-6}} transition={reduce?{duration:0}:{duration:.24,ease:ease.out}}>
        <div role="group" aria-label="Escolha seu agente" className="mx-auto mt-6 inline-flex max-w-full flex-wrap items-center justify-center gap-1 rounded-full bg-muted/75 p-1.5">
          {AGENTS.map(item=><button key={item.id} type="button" aria-pressed={agent===item.id} onClick={()=>{setAgent(item.id);setCopyState(null)}} className={`relative rounded-full px-3.5 py-2 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring sm:px-4 ${agent===item.id?'text-foreground':'text-muted-foreground hover:text-foreground'}`}>
            {agent===item.id&&<motion.span aria-hidden="true" layoutId="skill-agent-indicator" className="absolute inset-0 rounded-full bg-background shadow-sm" transition={selectionTransition(reduce)}/>}<span className="relative">{item.label}</span>
          </button>)}
        </div>
        <div role="group" aria-label="Onde instalar" className="mt-3 flex items-center justify-center gap-5 text-xs">
          {(['project','personal'] as const).map(value=>{const active=(value==='personal')===global;return <button key={value} type="button" aria-pressed={active} onClick={()=>{setGlobal(value==='personal');setCopyState(null)}} className={`relative rounded-full px-2.5 py-1.5 transition-colors ${active?'font-medium text-foreground':'text-muted-foreground hover:text-foreground'}`}>{active&&<motion.span aria-hidden="true" layoutId="skill-scope-indicator" className="absolute inset-0 rounded-full bg-muted/70" transition={selectionTransition(reduce)}/>}<span className="relative">{value==='project'?'Neste projeto':'Pessoal'}</span></button>})}
        </div>

        <div className="skill-copy-field mx-auto mt-5 flex h-[58px] w-full items-center gap-3 rounded-[18px] border-[5px] border-muted/70 bg-background px-3 sm:px-5">
          <span aria-hidden="true" className="shrink-0 font-mono text-sm text-muted-foreground">$</span>
          <input type="text" aria-label="Instrução para instalar a skill e o corpus com seu agente" readOnly value={setupPrompt} onFocus={event=>event.currentTarget.select()} className="h-full min-w-0 flex-1 overflow-hidden text-ellipsis whitespace-nowrap bg-transparent text-left font-mono text-[10px] text-foreground outline-none sm:text-xs" />
          <button type="button" aria-label={copyState==='prompt'?'Instrução copiada':'Copiar instrução'} title={copyState==='prompt'?'Copiado':'Copiar instrução'} onClick={()=>void copy(setupPrompt,'prompt')} className="flex size-9 shrink-0 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <AnimatePresence mode="wait" initial={false}><motion.svg key={copyState==='prompt'?'copied':'copy'} aria-hidden="true" viewBox="0 0 20 20" className="size-5" fill="none" stroke="currentColor" strokeWidth={copyState==='prompt'?2:1.6} strokeLinecap="round" strokeLinejoin="round" initial={reduce?false:{opacity:0,scale:.78}} animate={{opacity:1,scale:1}} exit={reduce?{opacity:0}:{opacity:0,scale:.82}} transition={selectionTransition(reduce)}>{copyState==='prompt'?<path d="m4 10 4 4 8-8"/>:<><rect x="7" y="7" width="9" height="10" rx="2"/><path d="M13 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2"/></>}</motion.svg></AnimatePresence>
          </button>
        </div>
        <p aria-live="polite" className="mt-2 text-[10px] text-muted-foreground">{copyState==='error'?'Não foi possível copiar automaticamente. Selecione o texto para copiar.':`Skill em ${skillPath} · ${kit?`${kit.version} · ${kit.documentCount} normas · corte ${kit.cutoff}`:'kit oficial com corpus'}`}</p>

        <div className="mt-5 flex flex-wrap items-center justify-center gap-3">{downloadAction}{documentationAction('Documentação')}</div>
        <div className="mt-2 flex items-center justify-center gap-3 text-[10px] text-muted-foreground"><span>{kit?`${(kit.sizeBytes/1024/1024).toFixed(1)} MB`:'ZIP · skill + corpus'}</span><span aria-hidden="true">·</span><a href={checksumUrl} className="underline-offset-4 hover:text-foreground hover:underline">SHA-256</a></div>

        <div className="mx-auto mt-5 w-fit text-left text-[11px] text-muted-foreground">
          <button type="button" aria-expanded={showNpx} aria-controls={showNpx?'skill-npx-command':undefined} onClick={()=>setShowNpx(value=>!value)} className="select-none underline-offset-4 hover:text-foreground hover:underline">{showNpx?'Ocultar':'Instalar apenas a skill com npx'}</button>
          <AnimatePresence initial={false}>{showNpx&&<motion.div id="skill-npx-command" key="npx" initial={reduce?false:{height:0,opacity:0,y:-4}} animate={{height:'auto',opacity:1,y:0}} exit={reduce?{opacity:0}:{height:0,opacity:0,y:-4}} transition={selectionTransition(reduce)} className="mt-2 max-w-[min(88vw,42rem)] overflow-hidden">
            <div className="flex items-center gap-2 rounded-[16px] border-[4px] border-muted/70 bg-background p-2 pl-3">
              <code className="min-w-0 flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-mono text-[9px] text-foreground sm:text-[10px]">{command}</code>
              <button type="button" aria-label={copyState==='npx'?'Comando npx copiado':'Copiar comando npx'} onClick={()=>void copy(command,'npx')} className="flex size-8 shrink-0 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground">{copyState==='npx'?'✓':'⧉'}</button>
            </div>
            <p className="mt-1.5">Node.js 22.20+ · o corpus requer download separado.</p>
          </motion.div>}</AnimatePresence>
        </div>
      </motion.div> : <motion.div id="skill-panel-human" aria-labelledby="skill-tab-human" key="human" role="tabpanel" initial={reduce?false:{opacity:0,y:8}} animate={{opacity:1,y:0}} exit={reduce?{opacity:0}:{opacity:0,y:-6}} transition={reduce?{duration:0}:{duration:.24,ease:ease.out}}>
        <h3 className="mt-6 text-[clamp(1.65rem,4vw,2.45rem)] font-semibold leading-[1.08] tracking-[-.055em] text-foreground">Explore a biblioteca <span className="text-muted-foreground">diretamente</span></h3>
        <p className="mx-auto mt-3 max-w-[40rem] text-sm leading-relaxed text-muted-foreground sm:text-base">Pesquise no acervo, abra o leitor e organize sua pesquisa jurídica. Sem instalar nada.</p>
        <div className="mx-auto mt-6 flex max-w-[40rem] flex-wrap items-center justify-center gap-x-8 gap-y-3 text-xs text-muted-foreground"><span>375 normas federais</span><span>Busca no texto integral</span><span>Leitor com referências</span></div>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3"><a href={libraryDestination().href} className="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-foreground px-6 text-sm font-semibold text-background transition-opacity hover:opacity-85 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"><svg aria-hidden="true" viewBox="0 0 20 20" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M2.5 5.2c2.8-.7 5.2-.2 7.5 1.5v11c-2.3-1.7-4.7-2.2-7.5-1.5zM17.5 5.2c-2.8-.7-5.2-.2-7.5 1.5v11c2.3-1.7 4.7-2.2 7.5-1.5z"/></svg>Abrir a Biblioteca <span aria-hidden="true">↗</span></a></div>
      </motion.div>}
    </AnimatePresence>
  </div>
}

export function Hero(){const done=useIntroDone();const reduce=useShouldReduceMotion();const [audience,setAudience]=useState<InstallAudience>('agent');return <section id="skill" className="flex scroll-mt-20 flex-col items-center px-5 pb-8 pt-20 text-center md:pb-10 md:pt-28">
  <motion.div {...rise(0,done,reduce)} className="mb-5"><AudienceTabs audience={audience} onChange={setAudience}/></motion.div>
  <HeroTitle done={done} libraries={['conectada','contextualizada','verificável']} />
  <motion.p {...rise(5,done,reduce)} className="mt-3 max-w-[620px] text-base text-balance text-muted-foreground sm:text-lg">Instale a skill e o corpus para consultar normas, fontes e relações no seu fluxo de trabalho.</motion.p>
  <motion.div {...rise(6,done,reduce)} className="mt-6 flex max-w-full flex-col items-center gap-3"><CopyCommand audience={audience}/></motion.div>
</section>}
