import { Reader } from './reader.js';
import { Library } from './library.js';
const $ = selector => document.querySelector(selector);
const store = {
  get(key, fallback) { try { return JSON.parse(localStorage.getItem(`biblioteca:${key}`)) ?? fallback; } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(`biblioteca:${key}`, JSON.stringify(value)); } catch { /* Browser storage may be unavailable. */ } },
};
const settings = { theme:'light',size:18,spacing:1.6,font:'sans-serif',flow:'scroll',flowVersion:3,motion:'full' };
const storedSettings = store.get('settings',{});
if(storedSettings&&typeof storedSettings==='object'&&!Array.isArray(storedSettings)){
  if(['light','sepia','dark','auto'].includes(storedSettings.theme))settings.theme=storedSettings.theme;
  if(Number.isFinite(storedSettings.size))settings.size=Math.max(14,Math.min(32,storedSettings.size));
  if(Number.isFinite(storedSettings.spacing))settings.spacing=Math.max(1.2,Math.min(2.2,storedSettings.spacing));
  if(['serif','sans-serif'].includes(storedSettings.font))settings.font=storedSettings.font;
  if([2,3].includes(storedSettings.flowVersion)&&['pages','scroll'].includes(storedSettings.flow))settings.flow=storedSettings.flow;
  if(['full','calm'].includes(storedSettings.motion))settings.motion=storedSettings.motion;
}
const readList = key => { const value=store.get(key,[]); return Array.isArray(value)?value:[]; };
const validMark = mark => mark&&Number.isInteger(mark.section)&&mark.section>=0&&Number.isInteger(mark.page)&&mark.page>=0&&typeof mark.label==='string'&&(mark.scroll==null||Number.isFinite(mark.scroll)&&mark.scroll>=0&&mark.scroll<=1)&&(mark.scrollScope==null||mark.scrollScope==='document');
const validNote = note => note&&Number.isInteger(note.section)&&note.section>=0&&Number.isInteger(note.start)&&note.start>=0&&Number.isInteger(note.end)&&note.end>note.start&&typeof note.text==='string';
const reader = new Reader($('#viewport'));
let library, active=null, position=null, marks=[], notes=[], selected=null, toastTimer,toastGeneration=0,tocItems=[],tocExpanded=[];
let readingSince=0,lastInteraction=Date.now(),seeking=false,routeToken=0;
if('serviceWorker'in navigator&&location.protocol!=='file:')navigator.serviceWorker.register(new URL('./sw.js',document.baseURI)).catch(error=>console.warn('Modo offline indisponível:',error));
if('serviceWorker'in navigator)navigator.serviceWorker.addEventListener('message',event=>{
  if(event.data?.type==='OFFLINE_PROGRESS')message(`Preparando biblioteca offline · ${event.data.done} de ${event.data.total} arquivos…`);
  if(event.data?.type==='OFFLINE_READY')message(`Biblioteca disponível offline · ${event.data.total} arquivos armazenados.`);
  if(event.data?.type==='OFFLINE_ERROR')message(`Não foi possível preparar o modo offline: ${event.data.message}`);
});
async function cacheOffline(){
  if(!('serviceWorker'in navigator)){message('Este navegador não oferece suporte ao modo offline.');return;}
  message('Preparando a biblioteca para leitura offline…');
  try{const registration=await navigator.serviceWorker.ready;const worker=navigator.serviceWorker.controller||registration.active;if(!worker)throw new Error('O serviço offline ainda está iniciando. Tente novamente em alguns segundos.');worker.postMessage({type:'CACHE_LIBRARY'});}catch(error){message(error.message||'Não foi possível preparar o modo offline.');}
}
function element(tag,text,className) { const el=document.createElement(tag); if(text!=null)el.textContent=text; if(className)el.className=className; return el; }
function updateRangeTrack(input){if(!input||input.id==='progress')return;const min=Number(input.min)||0,max=Number(input.max)||100,value=Number(input.value)||0;input.style.setProperty('--range-progress',`${Math.max(0,Math.min(100,(value-min)/(max-min||1)*100))}%`);}
function motionAllowed(){return settings.motion!=='calm'&&!matchMedia('(prefers-reduced-motion: reduce)').matches;}
function dismissToast(expectedGeneration=toastGeneration){
  clearTimeout(toastTimer);
  if(expectedGeneration!==toastGeneration)return;
  const toast=$('#status');if(toast.hidden)return;
  const progress=toast.querySelector('.toast-progress-fill');
  toast.getAnimations().forEach(animation=>animation.cancel());progress.getAnimations().forEach(animation=>animation.cancel());
  if(motionAllowed()){
    const exit=toast.animate([{opacity:1,translate:'0 0',scale:1},{opacity:0,translate:'0 8px',scale:.985}],{duration:220,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});
    exit.onfinish=()=>{if(expectedGeneration===toastGeneration)toast.hidden=true;};
  }else toast.hidden=true;
}
function message(text){
  const toast=$('#status'),content=$('#status-message'),progress=toast.querySelector('.toast-progress-fill');
  clearTimeout(toastTimer);const generation=++toastGeneration;toast.getAnimations().forEach(animation=>animation.cancel());progress.getAnimations().forEach(animation=>animation.cancel());
  content.textContent=text;toast.hidden=false;
  if(motionAllowed()){
    toast.animate([{opacity:0,translate:'0 12px',scale:.985},{opacity:1,translate:'0 0',scale:1}],{duration:340,easing:'cubic-bezier(.2,.8,.2,1)'});
    progress.animate([{transform:'scaleX(1)'},{transform:'scaleX(0)'}],{duration:3600,easing:'linear',fill:'forwards'});
  }
  toastTimer=setTimeout(()=>dismissToast(generation),3600);
}
function applySettings() {
  document.documentElement.dataset.theme=settings.theme;
  document.documentElement.dataset.motion=settings.motion==='calm'?'calm':'full';
  $('#font-size').value=settings.size; $('#line-height').value=settings.spacing; $('#font').value=settings.font; $('#flow').value=settings.flow; $('#motion').value=settings.motion;
  updateRangeTrack($('#font-size'));updateRangeTrack($('#line-height'));
  document.querySelectorAll('[data-theme]').forEach(button=>{if(button.tagName==='BUTTON'){const selected=button.dataset.theme===settings.theme;button.setAttribute('aria-pressed',String(selected));button.setAttribute('aria-checked',String(selected));button.tabIndex=selected?0:-1;}});
  const resolved=settings.theme==='auto'?(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'):settings.theme;
  const themeColor=document.querySelector('meta[name=theme-color]');
  if(themeColor)themeColor.content=resolved==='dark'?'#101010':resolved==='sepia'?'#f4f4f4':'#f7f7f7';
  reader.configure(settings); store.set('settings',settings);library?.updateMotionButton();
}
function panel(name) {
  for(const id of ['toc','search','marks','notes']) {
    const selected=id===name;
    const panelElement=$(`#${id}-panel`);panelElement.hidden=!selected;if(selected&&document.documentElement.dataset.motion!=='calm'&&!matchMedia('(prefers-reduced-motion: reduce)').matches)panelElement.animate([{opacity:0,transform:'translateY(5px)'},{opacity:1,transform:'translateY(0)'}],{duration:240,easing:'cubic-bezier(.2,.8,.2,1)'});
    const tab=$(`#${id}-tab`);
    if(tab){tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1;}
  }
}
function syncTocVisibility(revealIndex=-1,changedIndex=-1){
  if(revealIndex>=0){let level=tocItems[revealIndex]?.level||1;for(let i=revealIndex-1;i>=0;i--)if(tocItems[i].level<level){tocExpanded[i]=true;level=tocItems[i].level;}}
  const animate=document.documentElement.dataset.motion!=='calm'&&!matchMedia('(prefers-reduced-motion: reduce)').matches;
  for(let i=0;i<tocItems.length;i++){
    const item=tocItems[i];let hidden=false;
    for(let parent=i-1;parent>=0;parent--){if(tocItems[parent].level<item.level){if(!tocExpanded[parent])hidden=true;}}
    if(item.row.hidden!==hidden){
      const currentHeight=item.row.getBoundingClientRect().height;item.row.getAnimations().forEach(animation=>animation.cancel());
      const delay=changedIndex>=0&&i>changedIndex&&item.level>tocItems[changedIndex].level?Math.min((i-changedIndex-1)*16,80):0;
      if(!animate){item.row.hidden=hidden;item.row.style.removeProperty('height');item.row.style.removeProperty('overflow');}
      else if(hidden){
        const height=currentHeight;item.row.style.height=`${height}px`;item.row.style.overflow='hidden';
        const animation=item.row.animate([{height:`${height}px`,opacity:1,transform:'translateY(0)'},{height:'0px',opacity:0,transform:'translateY(-4px)'}],{duration:220,delay,easing:'cubic-bezier(.4,0,1,1)',fill:'both'});
        animation.onfinish=()=>{item.row.hidden=true;item.row.style.removeProperty('height');item.row.style.removeProperty('overflow');animation.cancel();};
      }else{
        item.row.hidden=false;item.row.style.height='0px';item.row.style.overflow='hidden';const height=item.row.scrollHeight;
        const animation=item.row.animate([{height:'0px',opacity:0,transform:'translateY(-4px)'},{height:`${height}px`,opacity:1,transform:'translateY(0)'}],{duration:300,delay,easing:'cubic-bezier(.2,.8,.2,1)',fill:'both'});
        animation.onfinish=()=>{item.row.style.removeProperty('height');item.row.style.removeProperty('overflow');animation.cancel();};
      }
    }
    if(item.disclosure){item.disclosure.setAttribute('aria-expanded',String(tocExpanded[i]));item.disclosure.setAttribute('aria-label',`${tocExpanded[i]?'Recolher':'Expandir'} ${item.label}`);}
  }
}
function showSidebar(show=true){
  $('#sidebar').hidden=!show;
  $('#show-sidebar').setAttribute('aria-expanded',String(show));
  $('#show-sidebar').setAttribute('aria-label',show?'Ocultar sumário e biblioteca':'Mostrar sumário e biblioteca');
  $('#show-sidebar').title=show?'Ocultar sumário e biblioteca':'Mostrar sumário e biblioteca';
  if(innerWidth<701){(show?$('#close-sidebar'):$('#show-sidebar')).focus();}
}
async function jump(target){revealTocTarget(target);await reader.goTo(target);if(target?.anchor&&active){const hash=new URLSearchParams({documento:active.id,artigo:target.anchor});history.pushState(null,'',`#${hash}`);}if(innerWidth<701)showSidebar(false);}
function revealTocTarget(target){if(!target||!tocItems.length)return;const index=target.anchor?tocItems.findIndex(item=>item.row.querySelector('[data-anchor]')?.dataset.anchor===target.anchor):tocItems.findIndex(item=>Number(item.row.querySelector('[data-section]')?.dataset.section)===Number(target.section));if(index>=0)syncTocVisibility(index);}
function renderMarks(){
  $('#marks').replaceChildren();
  if(!marks.length)$('#marks').append(element('p','Nenhum marcador.','muted'));
  for(const mark of marks){
    const row=element('div',null,'mark-row'),button=element('button',mark.label,'mark-button'),remove=element('button','×','button');
    button.onclick=()=>jump(mark);remove.setAttribute('aria-label','Remover marcador');
    remove.onclick=()=>{marks=marks.filter(item=>item!==mark);store.set(`marks:${active.id}`,marks);renderMarks();};
    row.append(button,remove);$('#marks').append(row);
  }
}
function renderNotes(){
  $('#notes').replaceChildren();
  if(!notes.length)$('#notes').append(element('p','Nenhuma anotação.','muted'));
  for(const note of notes){
    const card=element('div',null,'note-card'),button=element('button'),remove=element('button','×','button');
    button.append(element('blockquote',note.text));if(note.note)button.append(element('p',note.note));
    button.onclick=()=>jump({section:note.section,offset:note.start});
    remove.setAttribute('aria-label','Remover anotação');remove.onclick=()=>{notes=notes.filter(item=>item!==note);store.set(`notes:${active.id}`,notes);reader.notes=notes;reader.drawNotes();renderNotes();};
    card.append(button,remove);$('#notes').append(card);
  }
}
async function openBook(book,id,target){
  routeToken++;
  flushReadingTime();
  active={...book,id};position=null;
  marks=readList(`marks:${id}`).filter(validMark);
  notes=readList(`notes:${id}`).filter(validNote);
  try{
    $('#reading').style.setProperty('--reading-progress','0%');
    $('#library').hidden=true;$('#reading').hidden=false;$('#appearance').hidden=true;$('#selection-popover').hidden=true;
    $('#title').textContent=book.title;$('#author').textContent=book.author||'';$('#mini-cover').textContent=book.title;$('#reader-context').textContent=book.title;$('#reader-context').title=book.title;document.title=`${book.title} — Biblioteca`;
    $('#toc').replaceChildren();
    const toc=book.toc?.length?book.toc:book.sections.map((section,index)=>({label:section.label,section:index,level:1}));
    tocItems=toc.map((item,index)=>{const row=element('div',null,'toc-row');row.id=`toc-item-${index}`;row.dataset.level=item.level;const button=element('button',item.label);button.dataset.level=item.level;button.dataset.section=item.section;if(item.id)button.dataset.anchor=item.id;button.onclick=()=>jump({section:item.section,anchor:item.id});row.append(button);const following=toc.slice(index+1),nextSibling=following.findIndex(next=>next.level<=item.level),children=following.slice(0,nextSibling<0?following.length:nextSibling),hasChildren=children.length>0;let disclosure=null;if(hasChildren){disclosure=element('button',null,'toc-disclosure');disclosure.type='button';disclosure.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';disclosure.setAttribute('aria-controls',children.map((_,childIndex)=>`toc-item-${index+1+childIndex}`).join(' '));disclosure.onclick=()=>{tocExpanded[index]=!tocExpanded[index];syncTocVisibility(-1,index);};row.append(disclosure);}$('#toc').append(row);return{label:item.label,level:item.level,row,disclosure};});tocExpanded=toc.map(()=>true);syncTocVisibility();
    panel('toc');showSidebar(innerWidth>700);renderMarks();renderNotes();
    await reader.open(book,target||store.get(`position:${id}`,null));reader.notes=notes;reader.drawNotes();applySettings();
    const params=new URLSearchParams(location.hash.slice(1));
    if(params.get('documento')!==id){const hash=new URLSearchParams({documento:id});if(target?.anchor)hash.set('artigo',target.anchor);history.pushState(null,'',`#${hash}`);}
    readingSince=Date.now();lastInteraction=Date.now();
  }catch(error){
    closeBook();
    throw error;
  }
}
function closeBook(){routeToken++;flushReadingTime();reader.clear();active=null;position=null;readingSince=0;seeking=false;$('#reader-context').textContent='';$('#reading').hidden=true;$('#library').hidden=false;$('#appearance').hidden=true;$('#selection-popover').hidden=true;document.title='Biblioteca';library?.show();}
async function route(){
  const token=++routeToken;
  const params=new URLSearchParams(location.hash.slice(1));
  const id=params.get('documento'),anchor=params.get('artigo');
  if(!id){closeBook();return;}
  if(active?.id===id){if(anchor){const item=active.toc?.find(entry=>entry.id===anchor);if(item){revealTocTarget({section:item.section,anchor});await reader.goTo({section:item.section,anchor});}}else await reader.goTo(store.get(`position:${id}`,{section:0,page:0}));return;}
  if(!library)return;
  try{const book=await library.getBook(id);if(token!==routeToken)return;if(!book){history.replaceState(null,'',location.pathname);closeBook();return;}const item=anchor&&book.toc?.find(entry=>entry.id===anchor);await openBook(book,id,item?{section:item.section,anchor}:undefined);}catch(error){console.error(error);message('Não foi possível abrir o documento.');}
}
reader.addEventListener('position',({detail})=>{
  if(!active)return;position=detail;store.set(`position:${active.id}`,{section:detail.section,page:detail.page,scroll:detail.scroll,scrollScope:detail.scrollScope});
  library?.recordPosition(active.id,detail);
  $('#chapter-label').textContent=detail.label;$('#page-label').textContent=settings.flow==='scroll'?`${Math.round(detail.fraction*100)}%`:`${detail.page+1} / ${detail.pages}`;$('#progress').setAttribute('aria-valuetext',settings.flow==='scroll'?`${Math.round(detail.fraction*100)}% do documento`:`Página ${detail.page+1} de ${detail.pages}`);if(!seeking)$('#progress').value=detail.fraction;
  $('#reading').style.setProperty('--reading-progress',`${Math.round(detail.fraction*1000)/10}%`);
  $('#previous').disabled=settings.flow==='scroll'?$('#viewport').scrollTop<=1:detail.section===0&&detail.page===0;
  $('#next').disabled=settings.flow==='scroll'?$('#viewport').scrollTop+$('#viewport').clientHeight>=$('#viewport').scrollHeight-2:detail.section===active.sections.length-1&&detail.page===detail.pages-1;
  const tocButtons=[...document.querySelectorAll('#toc button[data-section]')];
  const heading=reader.currentHeading();
  let activeToc=heading?.id?tocButtons.find(button=>button.dataset.anchor===heading.id):null;
  if(!activeToc)activeToc=tocButtons.find(button=>Number(button.dataset.section)===detail.section);
  tocButtons.forEach(button=>{const current=button===activeToc;button.classList.toggle('current',current);button.setAttribute('aria-current',current?'location':'false');});
  const activeTocIndex=activeToc?tocButtons.indexOf(activeToc):-1;if(activeTocIndex>=0)syncTocVisibility();
  if(activeToc&&!$('#toc-panel').hidden&&!$('#sidebar').hidden){const panel=$('#toc-panel'),itemRect=activeToc.getBoundingClientRect(),panelRect=panel.getBoundingClientRect();if(itemRect.top<panelRect.top)panel.scrollTop+=itemRect.top-panelRect.top-8;else if(itemRect.bottom>panelRect.bottom)panel.scrollTop+=itemRect.bottom-panelRect.bottom+8;}
  $('#add-mark').setAttribute('aria-pressed',String(marks.some(mark=>mark.section===detail.section&&mark.page===detail.page&&(settings.flow==='scroll'?mark.scrollScope==='document'&&mark.scroll===detail.scroll:mark.scrollScope!=='document'))));
});
reader.addEventListener('selection',({detail})=>{selected=detail;$('#selected-text').textContent=detail.text;$('#note-text').value='';$('#selection-popover').hidden=false;});
reader.addEventListener('anchor',({detail})=>{if(!active||!detail.id)return;const hash=new URLSearchParams({documento:active.id,artigo:detail.id});history.pushState(null,'',`#${hash}`);});
function currentArticle(){const heading=reader.currentHeading();return active?.toc?.find(item=>item.id===heading?.id)||active?.toc?.find(item=>item.section===position?.section)||active?.toc?.[0]||null;}
function articleUrl(){const hash=new URLSearchParams({documento:active.id});const article=currentArticle();if(article?.id)hash.set('artigo',article.id);return `${location.origin}${location.pathname}#${hash}`;}
async function copyText(value,success){try{await navigator.clipboard.writeText(value);message(success);}catch{message('Não foi possível copiar. Verifique a permissão da área de transferência.');}}
$('#copy-section-link').onclick=()=>{if(active)copyText(articleUrl(),'Link da seção copiado.');};
$('#copy-citation').onclick=()=>{if(!active)return;const article=currentArticle();const parts=[active.author,active.title,article?.label].filter(Boolean);const date=active.sourceDate?` Consulta em ${active.sourceDate}.`:'';copyText(`${parts.join('. ')}.${date} ${articleUrl()}`,'Citação com link copiada.');};
$('#show-source').onclick=()=>{
  if(!active)return;const root=$('#source-details');root.replaceChildren();
  const fields=[['Documento',active.title],['Autor ou órgão',active.author],['Identificação',[active.number,active.year].filter(Boolean).join(' · ')],['Situação na fonte',active.legalStatus],['Data da fonte',active.sourceDate],['Data de corte',active.cutoff],['Consolidação',active.consolidationStatus],['Fidelidade',active.fidelityStatus],['SHA-256 do Markdown de origem',active.vademecumSourceHash||active.sourceHash||active.contentHash]];
  for(const[label,value]of fields)if(value){const row=element('p');row.append(element('strong',`${label}: `),element('span',String(value)));root.append(row);}
  const sources=Array.isArray(active.officialSources)?active.officialSources:(active.officialUrl?[active.officialUrl]:[]);
  sources.forEach((source,index)=>{try{const url=new URL(source);if(['http:','https:'].includes(url.protocol)){const link=element('a',sources.length>1?`Abrir fonte oficial ${index+1}`:'Abrir fonte oficial');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';root.append(link);}}catch{}});
  if(!sources.length&&active.source){const link=element('a','Abrir arquivo de origem');try{const url=new URL(active.source.split('/').map(encodeURIComponent).join('/'),document.baseURI);if(['http:','https:'].includes(url.protocol)){link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';root.append(link);}}catch{}}
  if(!fields.some(([,value])=>value)&&!sources.length&&!active.source)root.append(element('p','Este documento não possui metadados de fonte.'));
  $('#source-dialog').showModal();
};
$('#back-library').onclick=()=>{history.replaceState(null,'',location.pathname);closeBook();};
$('#reader-back-library').onclick=()=>$('#back-library').click();
$('#show-sidebar').onclick=()=>showSidebar($('#sidebar').hidden);$('#close-sidebar').onclick=()=>showSidebar(false);
$('#toggle-search').onclick=()=>{panel('search');$('#query').focus();};
for(const name of ['toc','search','marks','notes'])$(`#${name}-tab`).onclick=event=>{panel(name);if(name==='search'&&event.detail>0)$('#query').focus();};
$('.side-tabs').addEventListener('keydown',event=>{
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
  const tabs=[...$('.side-tabs').querySelectorAll('[role=tab]')];
  const current=tabs.indexOf(document.activeElement);let next=current;
  if(event.key==='Home')next=0;else if(event.key==='End')next=tabs.length-1;else next=(current+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
  event.preventDefault();tabs[next].focus();tabs[next].click();
});
$('#next').onclick=()=>reader.next();$('#previous').onclick=()=>reader.previous();
$('#progress').oninput=event=>{if(!active)return;seeking=true;reader.seek(Number(event.target.value));};
$('#progress').onchange=()=>{seeking=false;};
$('#add-mark').onclick=()=>{
  if(!position)return;
  const markScroll=settings.flow==='scroll'?position.scroll:undefined;
  const exists=marks.some(mark=>mark.section===position.section&&mark.page===position.page&&(settings.flow==='scroll'?mark.scrollScope==='document'&&mark.scroll===markScroll:mark.scrollScope!=='document'));
  if(exists)marks=marks.filter(mark=>mark.section!==position.section||mark.page!==position.page||(settings.flow==='scroll'?mark.scrollScope!=='document'||mark.scroll!==markScroll:mark.scrollScope==='document'));
  else marks.push({section:position.section,page:position.page,...(markScroll==null?{}:{scroll:markScroll,scrollScope:'document'}),label:`${position.label} · ${settings.flow==='scroll'?`${Math.round(markScroll*100)}%`:`${position.page+1}`}`});
  store.set(`marks:${active.id}`,marks);renderMarks();reader.emitPosition();message(exists?'Marcador removido.':'Posição marcada.');
};
$('#search-form').onsubmit=event=>{
  event.preventDefault();const results=reader.search($('#query').value);$('#results').replaceChildren();$('#search-status').textContent=`${results.length} resultado${results.length===1?'':'s'}`;
  for(const result of results){const button=element('button',null,'result-button');button.append(element('strong',result.label),element('span',result.before),element('mark',result.match),element('span',result.after));button.onclick=()=>jump(result);$('#results').append(button);}
};
$('#save-note').onclick=()=>{if(!selected||!active)return;notes.push({...selected,note:$('#note-text').value});store.set(`notes:${active.id}`,notes);reader.notes=notes;reader.drawNotes();renderNotes();$('#selection-popover').hidden=true;document.getSelection()?.removeAllRanges();};
$('#cancel-note').onclick=()=>{$('#selection-popover').hidden=true;};
document.addEventListener('pointerdown',event=>{if(!event.target.closest('#selection-popover'))$('#selection-popover').hidden=true;});
$('#appearance-toggle').onclick=()=>{$('#appearance').hidden=!$('#appearance').hidden;$('#appearance-toggle').setAttribute('aria-expanded',String(!$('#appearance').hidden));};
$('#status .toast-dismiss').onclick=dismissToast;
document.addEventListener('click',event=>{if(!event.target.closest('#appearance,#appearance-toggle')){$('#appearance').hidden=true;$('#appearance-toggle').setAttribute('aria-expanded','false');}});
const themeGroup=document.querySelector('.theme-options');themeGroup?.setAttribute('role','radiogroup');themeGroup?.setAttribute('aria-label','Tema de leitura');
document.querySelectorAll('button[data-theme]').forEach((button,index,buttons)=>{button.setAttribute('role','radio');button.onclick=()=>{settings.theme=button.dataset.theme;applySettings();};button.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;event.preventDefault();const direction=['ArrowRight','ArrowDown'].includes(event.key)?1:-1;buttons[(index+direction+buttons.length)%buttons.length].focus();buttons[(index+direction+buttons.length)%buttons.length].click();});});
for(const [id,key]of [['font-size','size'],['line-height','spacing'],['font','font'],['flow','flow'],['motion','motion']])$(`#${id}`).oninput=event=>{if(key==='size')settings.size=Math.max(14,Math.min(32,Number(event.target.value)||18));else if(key==='spacing')settings.spacing=Math.max(1.2,Math.min(2.2,Number(event.target.value)||1.6));else settings[key]=event.target.value;applySettings();};
document.addEventListener('input',event=>{if(event.target.matches('input[type=range]'))updateRangeTrack(event.target);});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{if(settings.theme==='auto')applySettings();});
document.addEventListener('keydown',event=>{
  if(event.key==='Escape'){
    if($('#source-dialog').open)return;
    if(!$('#appearance').hidden){$('#appearance').hidden=true;$('#appearance-toggle').setAttribute('aria-expanded','false');$('#appearance-toggle').focus();return;}
    if(!$('#selection-popover').hidden){$('#selection-popover').hidden=true;$('#viewport').focus();return;}
    if(active&&!$('#sidebar').hidden&&innerWidth<701){showSidebar(false);return;}
    return;
  }
  if(!active||event.target.closest('input,select,textarea,button'))return;
  if(['ArrowRight','PageDown'].includes(event.key)){event.preventDefault();reader.next();}
  if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();reader.previous();}
});
function flushReadingTime(){const now=Date.now();if(active&&readingSince&&!document.hidden&&now-lastInteraction<60000)library?.addReadingTime(active.id,Math.min(20,(now-readingSince)/1000));readingSince=active?now:0;}
for(const name of ['pointerdown','keydown','wheel'])document.addEventListener(name,()=>{lastInteraction=Date.now();},{passive:true});
setInterval(flushReadingTime,15000);
window.addEventListener('pagehide',flushReadingTime);
window.addEventListener('hashchange',route);
window.addEventListener('popstate',route);
applySettings();
library=new Library($('#library'),{
  open:openBook,message,cacheOffline,
  getNotes:id=>readList(`notes:${id}`).filter(validNote),
  getSettings:()=>settings,
  setSettings:patch=>{Object.assign(settings,patch);applySettings();},
  getReadingData:id=>({position:store.get(`position:${id}`,null),marks:readList(`marks:${id}`).filter(validMark),notes:readList(`notes:${id}`).filter(validNote)}),
  restoreReadingData:(id,data)=>{
    if(!data||typeof data!=='object')return;
    if(data.position&&Number.isInteger(data.position.section)&&data.position.section>=0)store.set(`position:${id}`,{section:data.position.section,page:Math.max(0,Number(data.position.page)||0),...(Number.isFinite(data.position.scroll)?{scroll:Math.max(0,Math.min(1,data.position.scroll)),...(data.position.scrollScope==='document'?{scrollScope:'document'}:{})}:{})});
    if(Array.isArray(data.marks))store.set(`marks:${id}`,data.marks.filter(validMark).map(mark=>({section:mark.section,page:mark.page,...(Number.isFinite(mark.scroll)?{scroll:mark.scroll,scrollScope:mark.scrollScope==='document'?'document':undefined}:{}),label:mark.label})));
    if(Array.isArray(data.notes))store.set(`notes:${id}`,data.notes.filter(validNote).map(note=>({section:note.section,start:note.start,end:note.end,text:note.text,note:typeof note.note==='string'?note.note:''})));
  },
});
try{await library.init();await route();}catch(error){console.error(error);message('Não foi possível carregar a biblioteca. Verifique se o armazenamento do navegador está disponível.');}
