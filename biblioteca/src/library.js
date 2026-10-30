import { LibraryStore, filterAndSortBooks, readingStatus, normalizeMetadata, normalizeSearch } from './library-store.js';

const icons = {
  books:'<path d="M12 6v15M3 4c4-1 6 0 9 2 3-2 5-3 9-2v15c-4-1-6 0-9 2-3-2-5-3-9-2Z"/>',
  book:'<path d="M4 5.5c3.2-.8 5.8-.2 8 1.5v12.5c-2.2-1.5-4.8-2-8-1.3zM20 5.5c-3.2-.8-5.8-.2-8 1.5v12.5c2.2-1.5 4.8-2 8-1.3z"/>',
  search:'<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
  refresh:'<path d="M20 10a8 8 0 0 0-14-4L3 9m0-6v6h6m-5 5a8 8 0 0 0 14 4l3-3m0 6v-6h-6"/>',
  plus:'<path d="M12 4v16M4 12h16"/>',
  filter:'<path d="M3 6h18M3 12h12M3 18h6"/>',
  notes:'<path d="M5 3h10l4 4v14H5Zm10 0v5h4M8 12h8M8 16h6"/>',
  chart:'<path d="M3 17l6-6 4 3 8-10"/><path d="M15 4h6v6"/>',
  settings:'<circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
  info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/>',
  'book-open':'<path d="M12 6v15M3 4c3.5-.9 6.5-.3 9 2 2.5-2.3 5.5-2.9 9-2v15c-3.4-.8-6.4-.2-9 2-2.6-1.8-5.6-2.5-9-2Z"/>',
  lock:'<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 1 1 8 0v3m-4 5v2"/>',
  folder:'<path d="M3 6h7l2 3h9v11H3Z"/>',
  back:'<path d="m14 5-7 7 7 7"/>',
  more:'<circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/>',
  check:'<path d="m5 12 4 4L20 5"/>',
  close:'<path d="m6 6 12 12M18 6 6 18"/>',
  heart:'<path d="M12 21 3 12C-2 4 7 0 12 6c5-6 14-2 9 6Z"/>',
  local:'<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 4v6h8V4M8 20v-6h8v6"/>',
  download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  offline:'<path d="M5 19a4 4 0 0 1-.2-8A7 7 0 0 1 18 9a5 5 0 0 1 1 9M12 12v9m-4-4 4 4 4-4"/>',
  external:'<path d="M14 4h6v6m0-6-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/>',
  repository:'<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11M9 8h6"/>',
  github:'<path d="M12 .8a11.2 11.2 0 0 0-3.54 21.83c.56.1.76-.24.76-.54v-2.1c-3.1.68-3.76-1.32-3.76-1.32-.5-1.28-1.24-1.62-1.24-1.62-1.02-.7.08-.68.08-.68 1.12.08 1.72 1.15 1.72 1.15 1 .1.78 2.2 3.6 1.7.1-.73.4-1.23.7-1.52-2.48-.28-5.1-1.24-5.1-5.53 0-1.22.44-2.21 1.16-2.99-.12-.28-.5-1.42.11-2.96 0 0 .95-.3 3.08 1.14a10.7 10.7 0 0 1 5.6 0c2.13-1.44 3.07-1.14 3.07-1.14.61 1.54.23 2.68.12 2.96.72.78 1.15 1.77 1.15 2.99 0 4.3-2.62 5.25-5.12 5.53.4.35.75 1.02.75 2.06v3.05c0 .3.2.65.77.54A11.2 11.2 0 0 0 12 .8Z"/>',
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
  moon:'<path d="M20.4 15.3A8.5 8.5 0 0 1 8.7 3.6 8.5 8.5 0 1 0 20.4 15.3Z"/>',
};
const svg = name => `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">${icons[name] || icons.book}</svg>`;
const node = (tag, text, cls) => { const el=document.createElement(tag); if(text!=null)el.textContent=text; if(cls)el.className=cls; return el; };
const updateRangeTrack = input => {const min=Number(input.min)||0,max=Number(input.max)||100,value=Number(input.value)||0;input.style.setProperty('--range-progress',`${Math.max(0,Math.min(100,(value-min)/(max-min||1)*100))}%`);};
const appendSlidingText = (parent,text) => {let cursor=0;for(const match of String(text).matchAll(/\d+/g)){const start=match.index;if(start>cursor)parent.append(document.createTextNode(String(text).slice(cursor,start)));const accessible=node('span',match[0],'shelf-sr-only'),visual=node('span',null,'shelf-slide-number');visual.setAttribute('aria-hidden','true');for(const character of match[0]){const digit=node('span',null,'metric-digit'),track=node('span',null,'metric-digit-track');track.style.setProperty('--digit-position',`-${Number(character)}em`);for(let n=0;n<=9;n++)track.append(node('span',String(n)));digit.append(track);visual.append(digit);}parent.append(accessible,visual);cursor=start+match[0].length;}if(cursor<String(text).length)parent.append(document.createTextNode(String(text).slice(cursor)));};
const uuid = () => crypto.randomUUID();
const statusLabels = {new:'Não iniciado',reading:'Em leitura',finished:'Concluído'};
const colors = ['#c7d3cc','#d9c9b6','#b8c6d6','#d6c1c6','#c9cdb2','#c6b8d2','#d8d1c2','#bdd0cd'];
const paletteFor = title => colors[[...title].reduce((hash,c)=>(hash*31+c.codePointAt(0))>>>0,0)%colors.length];
const formatTime = seconds => seconds<60?`${Math.round(seconds)} s`:`${Math.floor(seconds/3600)} h ${Math.floor(seconds%3600/60)} min`;
const hasChapterContent = tokens => {
  if(!tokens.length)return false;
  const firstHeading=tokens.findIndex(token=>token.type==='heading_open');
  if(firstHeading!==0)return true;
  let lastClose=-1;for(let index=0;index<tokens.length;index++)if(tokens[index].type==='heading_close')lastClose=index;
  return lastClose>=0&&tokens.length>lastClose+1;
};
function findNormalizedMatch(text,needle){
  let folded='';const positions=[];
  for(let index=0;index<text.length;){const character=String.fromCodePoint(text.codePointAt(index));const normalized=character.normalize('NFD').replace(/\p{M}/gu,'').toLocaleLowerCase('pt-BR');for(const unit of normalized){folded+=unit;for(let i=0;i<unit.length;i++)positions.push(index);}index+=character.length;}
  const at=folded.indexOf(needle);if(at<0)return null;return{start:positions[at]??0,end:positions[at+needle.length]??text.length};
}
const defaultPreferences = {sort:'lastReadAt',direction:'desc',coverWidth:148};
const sortKeys = ['title','author','lastReadAt','progress','importedAt'];
const normalizePreferences = value => {
  const source = value && typeof value==='object' && !Array.isArray(value) ? value : {};
  return {
    sort: sortKeys.includes(source.sort) ? source.sort : defaultPreferences.sort,
    direction: source.direction === 'asc' ? 'asc' : defaultPreferences.direction,
    coverWidth: Number.isFinite(source.coverWidth) ? Math.max(100, Math.min(200, source.coverWidth)) : defaultPreferences.coverWidth,
  };
};

export class Library {
  constructor(root, options) {
    this.root=root; this.options=options; this.db=new LibraryStore();
    this.catalog=[];this.local=[];this.state={records:Object.create(null),folders:[],preferences:{...defaultPreferences}};
    this.view='books';this.folder='';this.query='';this.status='all';this.tags=[];this.selected=new Set();this.selectionMode=false;this.saveTimer=null;
    this.visibleBooks=[];this.renderContext='';this.fullQuery='';this.searchIndex=null;this.searchToken=0;
    this.mount();
  }
  mount() {
    this.root.className='shelf-shell';
    this.root.innerHTML=`
      <header class="shelf-toolbar">
        <a class="shelf-brand" href="../" aria-label="Página inicial do Vademecum"><span class="shelf-brand-mark">${svg('book')}</span><span>Vademecum</span></a>
        <div class="shelf-toolbar-spacer"></div>
        <nav class="shelf-project-links" aria-label="Links do projeto">
          <a href="../" class="shelf-project-link">Início</a>
          <a href="https://github.com/lucmolero" class="shelf-project-link shelf-github-link" target="_blank" rel="noopener noreferrer" aria-label="Perfil do Vademecum no GitHub">${svg('github')}<span>GitHub</span></a>
          <a href="https://github.com/lucmolero/vademecum-md" class="shelf-project-link" target="_blank" rel="noopener noreferrer">${svg('repository')}<span>vademecum-md</span>${svg('external')}</a>
          <a href="https://github.com/lucmolero/biblioteca-leis" class="shelf-project-link" target="_blank" rel="noopener noreferrer">${svg('repository')}<span>biblioteca-leis</span>${svg('external')}</a>
        </nav>
        <label class="shelf-search">${svg('search')}<input id="library-query" type="search" placeholder="Buscar no acervo" aria-label="Buscar no acervo, autores ou anotações"><kbd class="shelf-kbd" aria-hidden="true">${/Mac|iPhone|iPad/.test(navigator.platform||'')?'⌘ K':'Ctrl K'}</kbd></label>
        <div class="shelf-toolbar-actions">
          <button class="shelf-icon" data-action="refresh" title="Atualizar biblioteca" aria-label="Atualizar biblioteca">${svg('refresh')}</button>
          <button class="shelf-icon" data-action="offline" title="Disponibilizar biblioteca offline" aria-label="Disponibilizar biblioteca offline">${svg('offline')}</button>
          <button class="shelf-icon" data-action="import" title="Importar Markdown" aria-label="Importar Markdown">${svg('plus')}</button>
          <button class="shelf-icon" data-action="sort" title="Ordenar e organizar" aria-label="Ordenar e organizar" aria-haspopup="menu" aria-expanded="false">${svg('filter')}</button>
          <button class="shelf-toolbar-motion" data-action="motion" type="button" role="switch" aria-label="Animações da interface" aria-checked="true"><span>Animações</span><i aria-hidden="true"></i></button>
          <button class="shelf-icon" data-action="theme" title="Alternar tema claro e escuro" aria-label="Alternar tema claro e escuro">${svg('moon')}</button>
        </div>
      </header>
      <div class="shelf-layout"><nav class="shelf-rail" aria-label="Navegação da biblioteca"><div class="shelf-symbol" aria-hidden="true">${svg('book')}<span>Vademecum</span></div><div class="shelf-nav-caption">Biblioteca</div><div class="shelf-destinations"></div></nav>
      <div class="shelf-workspace"><div class="shelf-filter-bar"></div><div class="shelf-selection" hidden></div><div class="shelf-breadcrumb" hidden></div><section class="shelf-content" aria-label="Biblioteca"><div class="shelf-grid"></div></section></div></div>
      <input id="library-import" type="file" accept=".md,.markdown,text/markdown,text/plain" multiple hidden>
      <div class="shelf-sort-menu" hidden></div><div class="shelf-context-menu" hidden></div>
      <div class="shelf-drop-overlay" hidden>${svg('plus')}<span>Importar documentos Markdown</span></div>`;
    this.find=selector=>this.root.querySelector(selector);
    for(const [id,label,icon] of [['books','Livros','books'],['search-all','Busca integral','search'],['statistics','Estatísticas','chart'],['notes','Anotações','notes'],['settings','Configurações','settings'],['info','Informações','info']]){
      const button=node('button',null,'shelf-destination');button.dataset.view=id;button.innerHTML=`<span>${svg(icon)}</span>`;button.append(node('small',label));button.onclick=()=>{this.view=id;this.selected.clear();this.render();};this.find('.shelf-destinations').append(button);
    }
    this.find('#library-query').oninput=event=>{this.query=event.target.value;this.selected.clear();this.render();};
    this.find('[data-action=import]').onclick=()=>this.find('#library-import').click();
    this.find('[data-action=offline]').onclick=()=>this.options.cacheOffline?.();
    this.find('[data-action=theme]').onclick=()=>{const isDark=document.documentElement.dataset.theme==='dark';this.options.setSettings({theme:isDark?'light':'dark'});this.updateThemeButton();};
    this.find('[data-action=motion]').onclick=()=>{const full=this.find('[data-action=motion]').getAttribute('aria-checked')==='true';this.options.setSettings({motion:full?'calm':'full'});this.updateMotionButton();};
    this.find('#library-import').onchange=async event=>{const files=[...event.target.files];event.target.value='';await this.importFiles(files);};
    this.find('[data-action=refresh]').onclick=()=>this.refresh().catch(error=>this.error(error,'Não foi possível atualizar a biblioteca.'));
    this.find('[data-action=sort]').onclick=event=>{event.stopPropagation();const menu=this.find('.shelf-sort-menu');const opening=menu.hidden;if(opening)this.find('.shelf-context-menu').hidden=true;menu.hidden=!opening;this.find('[data-action=sort]').setAttribute('aria-expanded',String(opening));};
    this.renderSortMenu();
    document.addEventListener('click',event=>{if(!event.target.closest('.shelf-sort-menu,[data-action=sort]')){this.find('.shelf-sort-menu').hidden=true;this.find('[data-action=sort]').setAttribute('aria-expanded','false');}if(!event.target.closest('.shelf-context-menu'))this.find('.shelf-context-menu').hidden=true;});
    document.addEventListener('keydown',event=>{
      if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k'&&!event.target.closest('dialog')){
        event.preventDefault();this.view='books';this.selected.clear();this.render();
        const input=this.find('#library-query');input.focus();input.select();
        return;
      }
      if(event.key!=='Escape'||event.target.closest('dialog'))return;
      this.find('.shelf-context-menu').hidden=true;this.find('.shelf-sort-menu').hidden=true;
      if(this.selected.size){this.selected.clear();this.render();}
    });
    let dragDepth=0;
    this.root.addEventListener('dragenter',event=>{if([...event.dataTransfer.types].includes('Files')){event.preventDefault();dragDepth++;this.find('.shelf-drop-overlay').hidden=false;}});
    this.root.addEventListener('dragleave',()=>{dragDepth=Math.max(0,dragDepth-1);if(!dragDepth)this.find('.shelf-drop-overlay').hidden=true;});
    this.root.addEventListener('dragover',event=>{if([...event.dataTransfer.types].includes('Files'))event.preventDefault();});
    this.root.addEventListener('drop',event=>{if(event.dataTransfer.files.length){event.preventDefault();dragDepth=0;this.find('.shelf-drop-overlay').hidden=true;this.importFiles([...event.dataTransfer.files]);}});
    this.root.addEventListener('dragend',()=>this.findAll('.is-drop-target').forEach(card=>card.classList.remove('is-drop-target')));
  }
  async init(){
    await this.db.init();
    const stored=await this.db.getState();
    const records=Object.create(null);
    for(const [id,value] of Object.entries(stored.records||{})){
      if(typeof id!=='string'||!id)continue;
      const metadata=normalizeMetadata(value);
      if(Object.keys(metadata).length)records[id]=metadata;
    }
    const folders=(Array.isArray(stored.folders)?stored.folders:[])
      .filter(folder=>folder&&typeof folder.id==='string'&&folder.id&&typeof folder.name==='string'&&folder.name.trim())
      .map(folder=>({id:folder.id,name:folder.name.trim()}));
    this.state={...stored,records,folders,preferences:normalizePreferences(stored.preferences)};
    await this.refresh(false);
  }
  error(error,text){console.error(error);this.options.message(text);}
  async persist(){await this.db.saveState(this.state);}
  async refresh(notify=true){
    const response=await fetch(new URL('./catalog.json',document.baseURI),{cache:'no-store'});
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    const catalog=await response.json();
    if(!Array.isArray(catalog))throw new Error('Catálogo inválido');
    this.catalog=catalog.filter(book=>book&&typeof book.id==='string'&&typeof book.title==='string'&&typeof book.file==='string');
    this.local=(await this.db.getBooks()).filter(book=>book&&typeof book.id==='string'&&Array.isArray(book.sections)&&book.sections.length);
    this.renderSortMenu();this.render();
    if(notify)this.options.message('Biblioteca atualizada.');
  }
  books(includeHidden=false){
    const bases=[...this.catalog.map(book=>({...book,kind:'static'})),...this.local.map(book=>({...book,kind:'local',sections:book.sections.length}))];
    return bases.map(book=>{
      const record=this.state.records[book.id];
      const metadata=record&&typeof record==='object'&&!Array.isArray(record)?record:{};
      return {...book,...metadata,tags:Array.isArray(metadata.tags)?metadata.tags:(Array.isArray(book.tags)?book.tags:[]),folder:metadata.folder||'',progress:metadata.progress||0};
    }).filter(book=>includeHidden||!book.hidden);
  }
  record(id){
    const current=this.state.records[id];
    if(!current||typeof current!=='object'||Array.isArray(current))this.state.records[id]={};
    return this.state.records[id];
  }
  async getBook(id){
    const summary=this.books(true).find(book=>book.id===id);if(!summary)return null;
    let data=this.local.find(book=>book.id===id);
    if(!data){const response=await fetch(new URL(summary.file,document.baseURI));if(!response.ok)throw new Error(`HTTP ${response.status}`);data=await response.json();}
    if(!data||!Array.isArray(data.sections)||!data.sections.length)throw new Error('Documento inválido');
    return {...data,...normalizeMetadata(this.state.records[id]||{}),id};
  }
  async open(id,target){
    try{
      const book=await this.getBook(id);if(!book)return;
      this.record(id).lastReadAt=Date.now();
      try{await this.persist();}catch(error){console.error('Não foi possível salvar a última leitura.',error);}
      await this.options.open(book,id,target);
    }catch(error){this.error(error,'Não foi possível abrir o documento.');}
  }
  recordPosition(id,detail){
    const record=this.record(id);record.progress=Math.max(0,Math.min(1,detail.fraction||0));record.lastReadAt=Date.now();
    clearTimeout(this.saveTimer);this.saveTimer=setTimeout(()=>this.persist().catch(error=>this.error(error,'Não foi possível salvar o progresso.')),400);
  }
  addReadingTime(id,seconds){const record=this.record(id);record.readingSeconds=(record.readingSeconds||0)+Math.max(0,seconds);this.persist().catch(error=>console.error(error));}
  show(){this.render();}
  updateThemeButton(){const button=this.find('[data-action=theme]');if(!button)return;const dark=document.documentElement.dataset.theme==='dark';const label=dark?'Usar tema claro':'Usar tema escuro';button.innerHTML=svg(dark?'sun':'moon');button.title=label;button.setAttribute('aria-label',label);}
  updateMotionButton(){const full=(this.options.getSettings().motion||'full')==='full',button=this.find('[data-action=motion]'),settingsSwitch=this.find('.shelf-motion-switch');if(button){button.setAttribute('aria-checked',String(full));button.dataset.state=full?'on':'off';button.title=full?'Animações completas':'Movimento calmo';}if(settingsSwitch){settingsSwitch.setAttribute('aria-checked',String(full));settingsSwitch.dataset.state=full?'on':'off';settingsSwitch.title=full?'Movimento completo':'Movimento calmo';}}
  render(){
    this.updateThemeButton();this.updateMotionButton();
    this.findAll('.shelf-destination').forEach(button=>button.setAttribute('aria-current',button.dataset.view===this.view?'page':'false'));
    this.root.style.setProperty('--cover-width',`${this.state.preferences.coverWidth||120}px`);
    this.find('.shelf-sort-menu').hidden=true;
    this.find('[data-action=sort]').setAttribute('aria-expanded','false');
    const booksView=this.view==='books';
    if(!booksView)this.selectionMode=false;
    this.root.classList.toggle('is-selection-mode',booksView&&this.selectionMode);
    this.find('.shelf-search').hidden=!booksView;
    this.find('[data-action=sort]').hidden=!booksView;
    this.find('.shelf-filter-bar').hidden=!booksView;this.find('.shelf-breadcrumb').hidden=true;this.find('.shelf-selection').hidden=(!this.selected.size&&!this.selectionMode)||!booksView;
    const content=this.find('.shelf-content');
    const context=[this.view,this.folder,this.query,this.status,this.tags.join('\u0000'),this.state.preferences.sort,this.state.preferences.direction].join('\u0001');
    this.animateNextRender=this.renderContext!==context;if(this.animateNextRender){this.renderContext=context;content.scrollTop=0;}
    content.className='shelf-content';
    content.replaceChildren();
    if(booksView)this.renderBooks(content);
    else if(this.view==='statistics')this.renderStatistics(content);
    else if(this.view==='notes')this.renderNotes(content);
    else if(this.view==='search-all')this.renderFullSearch(content);
    else if(this.view==='info')this.renderInformation(content);
    else this.renderSettings(content);
  }
  findAll(selector){return this.root.querySelectorAll(selector);}
  renderFilters(books=this.books()){
    const bar=this.find('.shelf-filter-bar');bar.replaceChildren();
    for(const [status,label]of [['finished','Concluídos'],['reading','Em leitura'],['new','Não iniciados']]){
      const button=node('button',label,'shelf-chip');button.setAttribute('aria-pressed',String(this.status===status));button.onclick=()=>{this.status=this.status===status?'all':status;this.render();};bar.append(button);
    }
    const allTags=[...new Set(books.flatMap(book=>book.tags))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
    const tagButton=node('button',`Etiquetas${this.tags.length?` · ${this.tags.length}`:''}`,'shelf-chip');tagButton.setAttribute('aria-pressed',String(this.tags.length>0));tagButton.onclick=()=>this.tagsDialog(allTags);bar.append(tagButton);
    if(this.status!=='all'||this.tags.length||this.query){const clear=node('button','Limpar filtros','shelf-clear');clear.onclick=()=>{this.status='all';this.tags=[];this.query='';this.find('#library-query').value='';this.render();};bar.append(clear);}
  }
  sectionHead(eyebrow,title,subtitle){
    const head=node('div',null,'shelf-section-head');
    const intro=node('div',null,'shelf-section-intro');
    const description=node('p',null,'shelf-subtitle');appendSlidingText(description,subtitle);intro.append(node('p',eyebrow,'shelf-eyebrow'),node('h1',title,'shelf-heading'),description);
    head.append(intro);
    return head;
  }
  renderBooks(content){
    const all=this.books();
    this.renderFilters(all);
    const notesByBook=Object.fromEntries(all.map(book=>[book.id,this.options.getNotes(book.id)]));
    const searching=!!this.query;
    const filtering=searching||this.tags.length>0||this.status!=='all';
    const folderScope=searching?null:(this.folder||(filtering?null:''));
    const books=filterAndSortBooks(all,{query:this.query,status:this.status,tags:this.tags,folder:folderScope,sort:this.state.preferences.sort,direction:this.state.preferences.direction},notesByBook);
    this.visibleBooks=books;
    const currentFolder=this.folder?this.state.folders.find(item=>item.id===this.folder):null;
    const counts={new:0,reading:0,finished:0};for(const book of all)counts[readingStatus(book.progress)]++;
    const plural=(value,singular,plural)=>`${value} ${value===1?singular:plural}`;
    const subtitle=searching?`${plural(books.length,'resultado','resultados')}${this.query?` para “${this.query}”`:''}`:this.folder?`${plural(books.length,'documento','documentos')} nesta pasta`:`${plural(all.length,'documento','documentos')} · ${counts.reading} em leitura`;
    const head=this.sectionHead(searching?'Busca':this.folder?'Pasta':'Acervo',searching?'Resultados':currentFolder?.name||'Biblioteca',subtitle);
    if(!searching&&!this.folder){
      const latest=[...all].filter(book=>book.lastReadAt).sort((a,b)=>b.lastReadAt-a.lastReadAt)[0];
      if(latest){
        const resume=node('button',null,'shelf-continue');
        resume.append(node('span','Continuar lendo','shelf-continue-label'),node('strong',latest.title),node('span',`${Math.round(latest.progress*100)}% · ${new Date(latest.lastReadAt).toLocaleDateString('pt-BR')}`,'shelf-continue-meta'));
        resume.onclick=()=>this.open(latest.id);head.append(resume);
      }
    }
    content.append(head);
    const grid=node('div',null,'shelf-grid');grid.setAttribute('aria-label','Documentos');
    if(this.folder&&!searching){
      const folder=this.state.folders.find(item=>item.id===this.folder);const crumb=this.find('.shelf-breadcrumb');crumb.hidden=false;crumb.replaceChildren();
      const back=node('button',null,'shelf-icon');back.innerHTML=svg('back');back.setAttribute('aria-label','Voltar para todos os documentos');back.onclick=()=>{this.folder='';this.render();};
      const title=node('strong',folder?.name||'Pasta');const edit=node('button','Renomear','shelf-clear');edit.onclick=()=>this.folderDialog(folder);const dissolve=node('button','Desfazer pasta','shelf-clear');dissolve.onclick=()=>this.dissolveFolder(folder);crumb.append(back,title,edit,dissolve);
    }
    if(!this.folder&&!filtering){
      this.state.folders.forEach((folder,index)=>{
        const members=all.filter(book=>book.folder===folder.id);
        const card=this.folderCard(folder,members);card.style.setProperty('--i',String(index));grid.append(card);
      });
    }
    books.forEach((book,index)=>{const card=this.bookCard(book);card.style.setProperty('--i',String(index));grid.append(card);});
    content.append(grid);
    if(!grid.children.length){
      const empty=node('div',null,'shelf-empty-state');
      const text=!all.length?'Sua biblioteca está vazia. Importe um arquivo Markdown para começar.':searching?'Nenhum documento encontrado.':this.folder?'Nenhum documento nesta pasta.':'Nenhum documento encontrado.';
      empty.append(node('p',text,'shelf-empty'));
      if(!all.length){const importButton=node('button','Importar Markdown','shelf-primary');importButton.onclick=()=>{this.find('#library-import').click();};empty.append(importButton);}
      content.append(empty);
    }
    if(this.query){
      const matches=this.notesMatches(books);
      if(matches.length){const area=node('section',null,'shelf-search-notes');area.append(node('h2',`Anotações · ${matches.length}`));for(const match of matches.slice(0,20))area.append(this.noteCard(match));content.append(area);}
    }
    this.renderSelection();
  }
  bookCard(book){
    const card=node('article',null,`shelf-book${this.animateNextRender?' is-entering':''}${book.favorite?' has-favorite':''}`);card.dataset.bookId=book.id;card.draggable=true;
    card.classList.toggle('is-selected',this.selected.has(book.id));
    const select=node('button',null,'shelf-book-select');select.type='button';select.setAttribute('role','checkbox');select.setAttribute('aria-checked',String(this.selected.has(book.id)));select.setAttribute('aria-label',`${this.selected.has(book.id)?'Desmarcar':'Selecionar'} ${book.title}`);select.innerHTML=this.selected.has(book.id)?svg('check'):'';select.onclick=event=>{event.stopPropagation();this.toggleSelection(book.id);};
    const open=node('button',null,'shelf-book-open');
    const cover=this.cover(book);cover.setAttribute('aria-hidden','true');open.append(cover);
    const name=node('div',null,'shelf-book-heading');name.append(node('span',book.title));
    const storage=node('span',null,'shelf-storage');storage.innerHTML=svg(book.kind==='local'?'local':'book');storage.title=book.kind==='local'?'Salvo neste navegador':'Documento do projeto';name.append(storage);
    const percent=Math.max(0,Math.min(100,Math.round((book.progress||0)*100)));
    const metadata=node('div',null,'shelf-book-meta');metadata.append(node('span',book.cardLabel||book.author||'Autor não informado'));
    open.append(name,metadata);
    const progress=node('div',null,'shelf-progress');progress.setAttribute('role','progressbar');progress.setAttribute('aria-valuemin','0');progress.setAttribute('aria-valuemax','100');progress.setAttribute('aria-valuenow',String(percent));progress.setAttribute('aria-label',`Leitura · ${percent}%`);const progressMeta=node('div',null,'shelf-progress-meta');progressMeta.append(node('span','Leitura'),node('strong',`${percent}%`));const track=node('span',null,'shelf-progress-track');const fill=node('span');fill.style.width=`${percent}%`;track.append(fill);progress.append(progressMeta,track);open.append(progress);
    open.onclick=()=>{if(this.selectionMode)this.toggleSelection(book.id);else this.open(book.id);};
    const more=node('button',null,'shelf-book-more');more.innerHTML=svg(this.selected.has(book.id)?'check':'more');more.setAttribute('aria-label',`Ações de ${book.title}`);more.title='Ações do documento';more.onclick=event=>{event.stopPropagation();this.contextMenu(book,event.currentTarget.getBoundingClientRect());};
    card.append(open,select,more);
    if(book.favorite){const heart=node('span',null,'shelf-favorite');heart.innerHTML=svg('heart');heart.title='Favorito';card.append(heart);}
    card.oncontextmenu=event=>{event.preventDefault();this.contextMenu(book,{left:event.clientX,bottom:event.clientY});};
    card.ondragstart=event=>{event.dataTransfer.setData('application/x-library-book',book.id);event.dataTransfer.effectAllowed='move';};
    let hold=null,longPressed=false,resetTimer=null,startX=0,startY=0;
    const cancelHold=()=>{if(hold){clearTimeout(hold);hold=null;}};
    card.addEventListener('pointerdown',event=>{
      if(event.pointerType!=='touch')return;
      cancelHold();startX=event.clientX;startY=event.clientY;
      hold=setTimeout(()=>{hold=null;longPressed=true;this.contextMenu(book,card.getBoundingClientRect());},650);
    });
    card.addEventListener('pointermove',event=>{
      if(hold&&(Math.abs(event.clientX-startX)>10||Math.abs(event.clientY-startY)>10))cancelHold();
    });
    card.addEventListener('pointerup',()=>{
      cancelHold();
      if(longPressed){clearTimeout(resetTimer);resetTimer=setTimeout(()=>{longPressed=false;},500);}
    });
    card.addEventListener('pointercancel',cancelHold);
    card.addEventListener('click',event=>{
      if(!longPressed)return;
      event.preventDefault();event.stopPropagation();
      longPressed=false;clearTimeout(resetTimer);
    },true);
    return card;
  }
  cover(book){
    const cover=node('div',null,'shelf-cover');cover.style.backgroundColor=paletteFor(book.title);
    if(book.cover&&/^(data:image\/(png|jpeg|webp);base64,|https?:|[^:]+$)/i.test(book.cover)){
      const image=node('img');image.alt='';image.loading='lazy';image.src=book.cover;image.onerror=()=>{image.remove();this.fillCover(cover,book);};cover.append(image);
    }else this.fillCover(cover,book);
    return cover;
  }
  fillCover(cover,book){const decoration=node('div',null,'shelf-cover-decoration');decoration.innerHTML=svg('book');cover.append(decoration,node('strong',book.title),node('small',book.author||''));}
  folderCard(folder,books){
    const card=node('article',null,'shelf-folder');const open=node('button');open.setAttribute('aria-label',`Abrir pasta ${folder.name}`);
    const previews=node('div',null,'shelf-folder-preview');if(!books.length)previews.innerHTML=svg('folder');for(const book of books.slice(0,4))previews.append(this.cover(book));
    open.append(previews,node('strong',folder.name),node('small',`${books.length} documento${books.length===1?'':'s'}`));open.onclick=()=>{this.folder=folder.id;this.render();};card.append(open);
    card.ondragover=event=>{const types=[...event.dataTransfer.types];if(types.includes('application/x-library-book')||types.includes('Files')){event.preventDefault();card.classList.add('is-drop-target');}};
    card.ondragleave=()=>card.classList.remove('is-drop-target');
    card.ondrop=async event=>{
      event.preventDefault();event.stopPropagation();card.classList.remove('is-drop-target');
      const files=[...event.dataTransfer.files];
      if(files.length){await this.importFiles(files,folder.id);return;}
      const id=event.dataTransfer.getData('application/x-library-book');
      if(id){this.record(id).folder=folder.id;await this.persist();this.render();}
    };
    return card;
  }
  toggleSelection(id){this.selectionMode=true;if(this.selected.has(id))this.selected.delete(id);else this.selected.add(id);this.render();}
  renderSelection(){
    const bar=this.find('.shelf-selection');bar.replaceChildren();bar.hidden=!this.selected.size&&!this.selectionMode;
    bar.append(node('strong',this.selected.size?`${this.selected.size} selecionado${this.selected.size===1?'':'s'}`:'Selecione os documentos'));
    if(this.selected.size){for(const [text,action]of [['Mover para pasta',()=>this.moveDialog([...this.selected])],['Remover',()=>this.removeDialog([...this.selected])]]){const button=node('button',text,'shelf-clear');button.onclick=action;bar.append(button);}}
    const cancel=node('button','Concluir','shelf-clear');cancel.onclick=()=>{this.selected.clear();this.selectionMode=false;this.render();};bar.append(cancel);
  }
  renderSortMenu(){
    const menu=this.find('.shelf-sort-menu');menu.replaceChildren();menu.setAttribute('role','menu');
    menu.append(node('strong','Ordenar por'));
    for(const [value,label]of [['title','Título'],['author','Autor'],['lastReadAt','Última leitura'],['progress','Progresso'],['importedAt','Data de importação']]){
      const button=node('button',label);button.setAttribute('role','menuitemradio');button.setAttribute('aria-checked',String(this.state.preferences.sort===value));button.onclick=async()=>{this.state.preferences.sort=value;try{await this.persist();}catch(error){this.error(error,'Não foi possível salvar as preferências.');}this.renderSortMenu();this.render();};menu.append(button);
    }
    const direction=node('button',this.state.preferences.direction==='asc'?'↑ Crescente':'↓ Decrescente');direction.setAttribute('role','menuitem');direction.onclick=async()=>{this.state.preferences.direction=this.state.preferences.direction==='asc'?'desc':'asc';try{await this.persist();}catch(error){this.error(error,'Não foi possível salvar as preferências.');}this.renderSortMenu();this.render();};menu.append(direction);
    const newFolder=node('button','Nova pasta');newFolder.setAttribute('role','menuitem');newFolder.onclick=()=>{menu.hidden=true;this.folderDialog();};menu.append(newFolder);
    const select=node('button',this.selectionMode?'Concluir seleção':'Selecionar');select.setAttribute('role','menuitem');
    select.onclick=()=>{
      if(this.selectionMode){this.selected.clear();this.selectionMode=false;}else{
        const visible=this.visibleBooks.length?this.visibleBooks:this.books();
        if(!visible.length){menu.hidden=true;this.options.message('Não há documentos para selecionar.');return;}
        this.selectionMode=true;
      }
      menu.hidden=true;this.render();
    };menu.append(select);
  }
  contextMenu(book,rect){
    const menu=this.find('.shelf-context-menu');menu.replaceChildren();menu.setAttribute('role','menu');
    this.find('.shelf-sort-menu').hidden=true;
    this.find('[data-action=sort]').setAttribute('aria-expanded','false');
    for(const [label,action]of [
      ['Abrir',()=>this.open(book.id)],['Detalhes e metadados',()=>this.detailsDialog(book)],
      [book.favorite?'Remover favorito':'Adicionar favorito',async()=>{this.record(book.id).favorite=!book.favorite;await this.persist();this.render();}],
      ['Mover para pasta',()=>this.moveDialog([book.id])],
      [readingStatus(book.progress)==='finished'?'Marcar como não iniciado':'Marcar como concluído',async()=>{this.record(book.id).progress=readingStatus(book.progress)==='finished'?0:1;await this.persist();this.render();}],
      ['Exportar Markdown',()=>this.exportMarkdown(book)],['Selecionar',()=>{this.selectionMode=true;this.toggleSelection(book.id);}],['Remover da biblioteca',()=>this.removeDialog([book.id])],
    ]){const button=node('button',label);button.setAttribute('role','menuitem');button.onclick=()=>{menu.hidden=true;Promise.resolve(action()).catch(error=>this.error(error,'Não foi possível concluir a ação.'));};menu.append(button);}
    menu.hidden=false;
    const width=menu.offsetWidth||240,height=menu.offsetHeight||360;
    menu.style.left=`${Math.max(8,Math.min(innerWidth-width-8,rect.left))}px`;
    menu.style.top=`${Math.max(8,Math.min(innerHeight-height-8,rect.bottom))}px`;
  }
  dialog(title){
    const dialog=node('dialog',null,'shelf-dialog');dialog.setAttribute('aria-label',title);const header=node('header');header.append(node('h2',title));const close=node('button',null,'shelf-icon');close.innerHTML=svg('close');close.setAttribute('aria-label','Fechar');close.onclick=()=>dialog.close();header.append(close);dialog.append(header);
    const body=node('div',null,'shelf-dialog-body'),footer=node('footer');dialog.append(body,footer);document.body.append(dialog);dialog.onclose=()=>dialog.remove();dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
    dialog.addEventListener('keydown',event=>{if(event.key!=='Enter'||event.target.closest('textarea,button,a,select'))return;const primary=dialog.querySelector('footer .shelf-primary');if(primary){event.preventDefault();primary.click();}});
    dialog.showModal();return{dialog,body,footer};
  }
  button(text,action,primary=false){const button=node('button',text,primary?'shelf-primary':'shelf-secondary');button.onclick=()=>Promise.resolve(action()).catch(error=>this.error(error,'Não foi possível salvar a alteração.'));return button;}
  field(body,label,value='',type='text'){const row=node('label',null,'shelf-field');row.append(node('span',label));const input=document.createElement(type==='textarea'?'textarea':'input');if(type!=='textarea')input.type=type;input.value=value;row.append(input);body.append(row);return input;}
  detailsDialog(book){
    const {dialog,body,footer}=this.dialog('Detalhes do documento');const preview=node('div',null,'shelf-detail-cover');preview.append(this.cover(book));body.append(preview);
    const title=this.field(body,'Título',book.title),author=this.field(body,'Autor',book.author||''),description=this.field(body,'Descrição',book.description||'','textarea'),tags=this.field(body,'Etiquetas (separadas por vírgula)',book.tags.join(', '));
    const row=node('label',null,'shelf-field');row.append(node('span','Estado da leitura'));const status=node('select');for(const [value,label]of Object.entries(statusLabels)){const option=node('option',label);option.value=value;status.append(option);}status.value=readingStatus(book.progress);row.append(status);body.append(row);
    const rating=this.field(body,'Avaliação (0 a 5)',book.rating||0,'number');rating.min=0;rating.max=5;rating.step=1;
    const coverInput=node('input');coverInput.type='file';coverInput.accept='image/png,image/jpeg,image/webp';coverInput.hidden=true;let cover=book.cover||'';
    const changeCover=this.button('Alterar capa',()=>coverInput.click());coverInput.onchange=async()=>{const file=coverInput.files[0];coverInput.value='';if(!file)return;if(!['image/png','image/jpeg','image/webp'].includes(file.type)||file.size>2*1024*1024){this.options.message('Escolha PNG, JPEG ou WebP de até 2 MB.');return;}try{cover=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(file);});preview.replaceChildren(this.cover({...book,cover}));}catch(error){this.error(error,'Não foi possível ler a imagem.');}};body.append(changeCover,coverInput);
    const clearCover=this.button('Remover capa',()=>{cover='';preview.replaceChildren(this.cover({...book,cover}));});body.append(clearCover);
    body.append(node('p',book.kind==='local'?'Armazenado neste navegador.':'Documento do projeto; alterações ficam neste navegador.','shelf-muted'));
    footer.append(this.button('Cancelar',()=>dialog.close()),this.button('Salvar',async()=>{
      if(!title.value.trim()){title.focus();return;}
      const currentStatus=readingStatus(book.progress);let progress=book.progress;
      if(status.value!==currentStatus)progress={new:0,reading:.03,finished:1}[status.value];
      Object.assign(this.record(book.id),normalizeMetadata({title:title.value.trim(),author:author.value.trim(),description:description.value,tags:tags.value.split(',').map(t=>t.trim()).filter(Boolean),cover,progress,rating:Number(rating.value)}));
      await this.persist();dialog.close();this.render();
    },true));
  }
  folderDialog(folder){
    const{dialog,body,footer}=this.dialog(folder?'Renomear pasta':'Nova pasta');const name=this.field(body,'Nome',folder?.name||'');
    footer.append(this.button('Cancelar',()=>dialog.close()),this.button('Salvar',async()=>{const value=name.value.trim();if(!value){name.focus();return;}if(this.state.folders.some(item=>item.id!==folder?.id&&item.name.localeCompare(value,'pt-BR',{sensitivity:'base'})===0)){this.options.message('Já existe uma pasta com esse nome.');name.focus();return;}if(folder)folder.name=value;else this.state.folders.push({id:uuid(),name:value});await this.persist();dialog.close();this.render();},true));name.focus();
  }
  moveDialog(ids){
    const{dialog,body,footer}=this.dialog('Mover para pasta');const select=node('select',null,'shelf-full-select');const root=node('option','Biblioteca principal');root.value='';select.append(root);for(const folder of this.state.folders){const option=node('option',folder.name);option.value=folder.id;select.append(option);}body.append(select);
    footer.append(this.button('Cancelar',()=>dialog.close()),this.button('Mover',async()=>{for(const id of ids)this.record(id).folder=select.value;await this.persist();this.selected.clear();dialog.close();this.render();},true));
  }
  dissolveFolder(folder){
    if(!folder)return;
    const{dialog,body,footer}=this.dialog('Desfazer pasta');body.append(node('p','Os documentos voltarão à biblioteca principal. Nenhum arquivo será excluído.'));
    footer.append(this.button('Cancelar',()=>dialog.close()),this.button('Desfazer pasta',async()=>{for(const book of this.books(true))if(book.folder===folder.id)this.record(book.id).folder='';this.state.folders=this.state.folders.filter(item=>item.id!==folder.id);this.folder='';await this.persist();dialog.close();this.render();},true));
  }
  removeDialog(ids){
    const{dialog,body,footer}=this.dialog('Remover da biblioteca');body.append(node('p',`Remover ${ids.length} documento${ids.length===1?'':'s'} desta biblioteca? As cópias podem ser restauradas nas configurações. Os arquivos de origem não serão alterados.`));
    footer.append(this.button('Cancelar',()=>dialog.close()),this.button('Remover',async()=>{for(const id of ids)this.record(id).hidden=true;await this.persist();this.selected.clear();dialog.close();this.render();},true));
  }
  tagsDialog(tags){
    const{dialog,body,footer}=this.dialog('Filtrar etiquetas');body.append(node('p','O documento deve ter todas as etiquetas selecionadas.','shelf-muted'));
    const choices=node('div',null,'shelf-tag-choices');let selected=[...this.tags];
    for(const tag of ['__untagged__',...tags]){const button=node('button',tag==='__untagged__'?'Sem etiqueta':tag,'shelf-chip');button.setAttribute('aria-pressed',String(selected.includes(tag)));button.onclick=()=>{if(tag==='__untagged__')selected=selected.includes(tag)?[]:[tag];else{selected=selected.filter(value=>value!=='__untagged__');if(selected.includes(tag))selected=selected.filter(value=>value!==tag);else selected.push(tag);}choices.querySelectorAll('button').forEach(el=>el.setAttribute('aria-pressed',String(selected.includes(el.dataset.tag))));};button.dataset.tag=tag;choices.append(button);}body.append(choices);
    footer.append(this.button('Limpar',()=>{this.tags=[];dialog.close();this.render();}),this.button('Aplicar',()=>{this.tags=selected;dialog.close();this.render();},true));
  }
  async importFiles(files,targetFolder=this.folder){
    const accepted=files.filter(file=>/\.(md|markdown)$/i.test(file.name));if(!accepted.length){this.options.message('Selecione arquivos .md ou .markdown.');return;}
    const folder=this.state.folders.some(item=>item.id===targetFolder)?targetFolder:'';
    let imported=0,duplicate=0,failed=files.length-accepted.length;
    const known=new Set(this.books(true).map(book=>book.contentHash).filter(hash=>typeof hash==='string'));
    for(const file of accepted){try{
      const raw=await file.text();if(!raw.trim())throw new Error('Arquivo vazio');
      const hash=await this.hash(raw);
      if(known.has(hash)){duplicate++;continue;}
      known.add(hash);
      const book=this.parseMarkdown(raw,file.name);book.id=`local-${hash}`;book.contentHash=hash;book.rawMarkdown=raw;book.importedAt=Date.now();
      await this.db.putBook(book);const existing=this.local.findIndex(item=>item.id===book.id);if(existing>=0)this.local[existing]=book;else this.local.push(book);Object.assign(this.record(book.id),{folder,importedAt:book.importedAt,progress:0});imported++;
    }catch(error){console.error(error);failed++;}}
    try{await this.persist();}catch(error){this.error(error,'Não foi possível salvar os metadados.');}
    this.view='books';this.folder=folder;this.query='';this.status='all';this.tags=[];this.selected.clear();this.find('#library-query').value='';this.render();
    this.options.message(`${imported} importado${imported===1?'':'s'}${duplicate?` · ${duplicate} duplicado${duplicate===1?'':'s'} ignorado${duplicate===1?'':'s'}`:''}${failed?` · ${failed} arquivo${failed===1?'':'s'} não importado${failed===1?'':'s'}`:''}.`);
  }
  async hash(text){const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));return[...new Uint8Array(digest)].map(byte=>byte.toString(16).padStart(2,'0')).join('');}
  parseMarkdown(raw,filename){
    let source=raw.replace(/^\uFEFF/,''),metadata={};
    const front=source.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
    if(front){
      const lines=front[1].split(/\r?\n/);source=source.slice(front[0].length);
      for(let i=0;i<lines.length;i++){
        const match=lines[i].match(/^(title|author|description|language|tags|aliases|number|year|officialUrl|official_url|sourceDate|source_date|legalStatus|legal_status):\s*(.*)$/);
        if(!match)continue;
        let value=match[2].trim();
        if(match[1]==='tags'||match[1]==='aliases'){
          if(!value){const items=[];while(i+1<lines.length&&/^\s*-\s+/.test(lines[i+1]))items.push(lines[++i].replace(/^\s*-\s+/,''));value=items.join(', ');}
          value=value.replace(/^\[|\]$/g,'');
        }
        metadata[match[1]]=value.replace(/^["']|["']$/g,'').trim();
      }
    }
    if(typeof globalThis.markdownit!=='function')throw new Error('Markdown não carregado');
    const parser=globalThis.markdownit({html:false,linkify:true});const tokens=parser.parse(source,{});const toc=[],sections=[],ids=new Map();let chunk=[],label=metadata.title||filename.replace(/\.(md|markdown)$/i,'');
    for(let i=0;i<tokens.length;i++){const token=tokens[i];if(token.type==='heading_open'){const text=tokens[i+1]?.content||'';const base=text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')||'secao';const count=(ids.get(base)||0)+1;ids.set(base,count);const id=count===1?base:`${base}-${count}`;token.attrSet('id',id);if(token.level===0&&Number(token.tag.slice(1))<=2&&hasChapterContent(chunk)){sections.push({label,html:parser.renderer.render(chunk,parser.options,{})});chunk=[];}if(!chunk.length)label=text;toc.push({label:text,level:Number(token.tag.slice(1)),section:sections.length,id});}chunk.push(token);}
    if(chunk.length)sections.push({label,html:parser.renderer.render(chunk,parser.options,{})});if(!sections.length)throw new Error('Markdown sem conteúdo');
    const title=metadata.title||toc[0]?.label||filename.replace(/\.(md|markdown)$/i,'');const list=value=>(value||'').replace(/^\[|\]$/g,'').split(',').map(item=>item.trim().replace(/^['\"]|['\"]$/g,'')).filter(Boolean);const tags=list(metadata.tags),aliases=list(metadata.aliases);
    return{title,author:metadata.author||'',description:metadata.description||'',language:metadata.language||'pt-BR',tags,aliases,number:metadata.number||'',year:metadata.year||'',officialUrl:metadata.officialUrl||metadata.official_url||'',sourceDate:metadata.sourceDate||metadata.source_date||'',legalStatus:metadata.legalStatus||metadata.legal_status||'',toc,sections,filename};
  }
  async exportMarkdown(book){const data=await this.getBook(book.id);let text=data.rawMarkdown;if(text==null&&data.source){const response=await fetch(new URL(data.source.split('/').map(encodeURIComponent).join('/'),document.baseURI));if(!response.ok)throw new Error(`HTTP ${response.status}`);text=await response.text();}if(text==null)throw new Error('Fonte não disponível');this.download(text,data.filename||`${book.title.replace(/[<>:"/\\|?*]/g,'-')}.md`,'text/markdown');}
  download(content,name,type){const url=URL.createObjectURL(new Blob([content],{type}));const a=node('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);}
  notesMatches(books=this.books()){const query=this.query.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();const matches=[];for(const book of books)for(const note of this.options.getNotes(book.id)){if(!query||`${book.title} ${note.text} ${note.note||''}`.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(query))matches.push({book,note});}return matches;}
  noteCard({book,note}){const card=node('button',null,'shelf-note-card');card.append(node('strong',book.title),node('blockquote',note.text));if(note.note)card.append(node('p',note.note));card.onclick=()=>this.open(book.id,{section:note.section,offset:note.start});return card;}
  renderNotes(content){content.className='shelf-content shelf-dashboard';const matches=this.notesMatches();content.append(this.sectionHead('Memória','Anotações',`${matches.length} anotaç${matches.length===1?'ão':'ões'} neste navegador`));if(!matches.length){const empty=node('div',null,'shelf-empty-note');const icon=node('span',null,'shelf-empty-note-icon');icon.innerHTML=svg('notes');icon.setAttribute('aria-hidden','true');empty.append(icon,node('strong','Suas anotações aparecerão aqui'),node('p','Selecione um trecho no leitor para destacar e registrar uma anotação.'));content.append(empty);}for(const match of matches)content.append(this.noteCard(match));}
  renderStatistics(content){
    content.className='shelf-content shelf-dashboard';const books=this.books();const counts={new:0,reading:0,finished:0};for(const book of books)counts[readingStatus(book.progress)]++;
    content.append(this.sectionHead('Painel','Estatísticas',`${books.length} documento${books.length===1?'':'s'} acompanhado${books.length===1?'':'s'} neste navegador`));
    const grid=node('div',null,'shelf-metrics');for(const [index,[label,value]]of [['Documentos',books.length],['Em leitura',counts.reading],['Concluídos',counts.finished],['Não iniciados',counts.new],['Anotações',books.reduce((sum,book)=>sum+this.options.getNotes(book.id).length,0)],['Tempo de leitura',formatTime(books.reduce((sum,book)=>sum+(this.state.records[book.id]?.readingSeconds||0),0))]].entries()){const card=node('div',null,'shelf-metric');card.style.setProperty('--i',String(index));const number=node('strong');number.setAttribute('aria-label',String(value));number.setAttribute('aria-live','polite');for(const character of String(value)){if(/\d/.test(character)){const digit=node('span',null,'metric-digit'),track=node('span',null,'metric-digit-track');track.style.setProperty('--digit-position',`-${Number(character)}em`);for(let n=0;n<=9;n++)track.append(node('span',String(n)));digit.append(track);number.append(digit);}else number.append(node('span',character,'metric-separator'));}card.append(node('small',label),number);grid.append(card);}content.append(grid);
    if(books.length){const distribution=node('div',null,'shelf-distribution'),track=node('div',null,'shelf-distribution-track'),legend=node('div',null,'shelf-distribution-legend');track.setAttribute('role','img');track.setAttribute('aria-label',`Distribuição de leitura: ${counts.finished} concluídos, ${counts.reading} em leitura e ${counts.new} não iniciados`);for(const [status,label]of [['finished','Concluídos'],['reading','Em leitura'],['new','Não iniciados']]){const segment=node('span',null,`is-${status}`);segment.style.flexGrow=String(Math.max(0,counts[status]));segment.title=`${label}: ${counts[status]}`;track.append(segment);const item=node('span',null,`distribution-${status}`);item.append(node('i',null,'distribution-dot'),node('span',`${label} · ${counts[status]}`));legend.append(item);}distribution.append(track,legend);content.append(distribution);}
    const recent=[...books].filter(book=>book.lastReadAt).sort((a,b)=>b.lastReadAt-a.lastReadAt).slice(0,5);if(recent.length){content.append(node('h2','Leituras recentes'));for(const book of recent){const button=node('button',null,'shelf-recent');button.append(node('strong',book.title),node('span',`${Math.round(book.progress*100)}% · ${new Date(book.lastReadAt).toLocaleDateString('pt-BR')}`));button.onclick=()=>this.open(book.id);content.append(button);}}
  }
  renderFullSearch(content){
    content.className='shelf-content shelf-dashboard shelf-full-search-view';
    content.append(this.sectionHead('Pesquisa','Busca integral','Encontre termos no texto de todos os documentos do acervo.'));
    const input=node('input');input.type='search';input.value=this.fullQuery;input.placeholder='Buscar em todas as leis e documentos';input.setAttribute('aria-label','Buscar no texto de todos os documentos');
    const field=node('label',null,'shelf-full-search');field.innerHTML=svg('search');field.append(input);content.append(field);
    const status=node('p','Digite um termo para pesquisar no acervo.','shelf-muted');status.setAttribute('aria-live','polite');content.append(status);
    const results=node('div',null,'shelf-full-results');content.append(results);
    input.oninput=()=>{this.fullQuery=input.value;this.renderFullResults(status,results);};
    if(this.fullQuery)this.renderFullResults(status,results);
  }
  async renderFullResults(status,results){
    const token=++this.searchToken,query=normalizeSearch(this.fullQuery);
    results.replaceChildren();
    if(!query){status.textContent='Digite um termo para pesquisar no acervo.';return;}
    status.textContent='Pesquisando no acervo…';
    try{
      if(!this.searchIndex){const response=await fetch(new URL('./search-index.json',document.baseURI));if(!response.ok)throw new Error(`HTTP ${response.status}`);this.searchIndex=await response.json();}
      if(token!==this.searchToken)return;
      const visible=new Map(this.books().map(book=>[book.id,book]));
      const corpus=[...this.searchIndex];
      for(const book of this.local){
        if(!visible.has(book.id))continue;
        corpus.push({id:book.id,title:book.title,sections:book.sections.map((section,index)=>{const doc=new DOMParser().parseFromString(section.html,'text/html');return{index,label:section.label,anchor:book.toc?.find(item=>item.section===index)?.id||'',text:doc.body.textContent||''};})});
      }
      const matches=[];
      for(const book of corpus){if(!visible.has(book.id))continue;for(const section of book.sections||[]){const found=findNormalizedMatch(section.text,query);if(!found)continue;const start=Math.max(0,found.start-65),end=Math.min(section.text.length,found.end+95);matches.push({id:book.id,title:book.title,label:section.label,section:section.index,anchor:section.anchor,text:section.text,start,end,at:found.start,matchEnd:found.end});if(matches.length>=200)break;}if(matches.length>=200)break;}
      if(token!==this.searchToken)return;
      status.textContent=`${matches.length}${matches.length===200?'+':''} resultado${matches.length===1?'':'s'} no texto integral`;
      if(!matches.length){results.append(node('p','Nenhuma ocorrência encontrada.','shelf-muted'));return;}
      for(const match of matches){
        const button=node('button',null,'shelf-full-result');button.append(node('strong',match.title),node('span',match.label,'shelf-full-result-label'));
        const snippet=node('span',null,'shelf-full-result-snippet'),before=match.text.slice(match.start,match.at),found=match.text.slice(match.at,match.matchEnd),after=match.text.slice(match.matchEnd,match.end);
        snippet.append(document.createTextNode(`${match.start?'…':''}${before}`));if(found)snippet.append(node('mark',found));snippet.append(document.createTextNode(`${after}${match.end<match.text.length?'…':''}`));button.append(snippet);
        button.onclick=()=>this.open(match.id,{section:match.section,anchor:match.anchor});results.append(button);
      }
    }catch(error){if(token!==this.searchToken)return;console.error(error);status.textContent='Não foi possível carregar o índice integral. Conecte-se à internet e tente novamente.';}
  }
  renderSettings(content){
    content.className='shelf-content shelf-dashboard';content.append(this.sectionHead('Preferências','Configurações','Aparência, leitura e backup dos seus dados'));
    const group=node('div',null,'shelf-settings-group');
    const theme=node('div',null,'shelf-setting shelf-theme-setting');theme.append(node('span','Tema'));const radios=node('div',null,'shelf-theme-radios');radios.setAttribute('role','radiogroup');radios.setAttribute('aria-label','Tema da biblioteca');const themeOptions=[['light','Claro'],['sepia','Sépia'],['dark','Escuro'],['auto','Automático']];for(const[value,label]of themeOptions){const button=node('button',label);button.type='button';button.dataset.theme=value;button.setAttribute('role','radio');button.setAttribute('aria-checked',String(this.options.getSettings().theme===value));button.tabIndex=this.options.getSettings().theme===value?0:-1;button.onclick=()=>{this.options.setSettings({theme:value});this.updateThemeButton();};button.onkeydown=event=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;event.preventDefault();const current=themeOptions.findIndex(([option])=>option===value),next=(current+(['ArrowRight','ArrowDown'].includes(event.key)?1:-1)+themeOptions.length)%themeOptions.length,control=radios.querySelectorAll('[role=radio]')[next];control.focus();control.click();};radios.append(button);}theme.append(radios);group.append(theme);
    const motion=node('label',null,'shelf-setting shelf-motion-setting');motion.append(node('span','Animações da interface'));const motionSwitch=node('button',null,'shelf-motion-switch');motionSwitch.type='button';motionSwitch.setAttribute('role','switch');motionSwitch.setAttribute('aria-label','Animações da interface');const updateMotion=()=>{const full=(this.options.getSettings().motion||'full')==='full';motionSwitch.setAttribute('aria-checked',String(full));motionSwitch.dataset.state=full?'on':'off';motionSwitch.title=full?'Movimento completo':'Movimento calmo';};motionSwitch.onclick=()=>{const full=motionSwitch.getAttribute('aria-checked')==='true';this.options.setSettings({motion:full?'calm':'full'});updateMotion();};updateMotion();motion.append(motionSwitch,node('small','Completo · Calmo'));group.append(motion);
    const size=node('label',null,'shelf-setting');size.append(node('span','Tamanho das capas'));const slider=node('input');slider.type='range';slider.min=100;slider.max=200;slider.step=10;slider.value=this.state.preferences.coverWidth||120;updateRangeTrack(slider);slider.oninput=()=>{updateRangeTrack(slider);this.state.preferences.coverWidth=Number(slider.value);this.root.style.setProperty('--cover-width',`${slider.value}px`);};slider.onchange=()=>this.persist().catch(error=>this.error(error,'Não foi possível salvar as preferências.'));size.append(slider);group.append(size);
    group.append(this.button('Exportar backup da biblioteca',()=>this.exportBackup()));
    const restore=node('input');restore.type='file';restore.accept='.json,application/json';restore.hidden=true;restore.onchange=async()=>{const file=restore.files[0];restore.value='';if(file)await this.importBackup(file);};group.append(this.button('Restaurar backup',()=>restore.click()),restore);
    const hidden=this.books(true).filter(book=>book.hidden).length;
    if(hidden)group.append(this.button(`Restaurar removidos (${hidden})`,async()=>{for(const record of Object.values(this.state.records))record.hidden=false;await this.persist();this.render();}));
    content.append(group,node('p','Os documentos importados, as capas e a organização ficam neste navegador. O backup permite transferir os dados para outro dispositivo.','shelf-muted'));
  }
  renderInformation(content){
    content.className='shelf-content shelf-dashboard shelf-information';
    content.append(this.sectionHead('Sobre','Informações','Como o acervo e os dados de leitura funcionam.'));
    const grid=node('div',null,'shelf-info-grid');
    const cards=[
      ['Acervo',`${this.books().length} documentos disponíveis nesta edição.`, 'book'],
      ['Dados locais','Anotações, marcadores, progresso e documentos importados permanecem neste navegador.','lock'],
      ['Leitura','O leitor oferece sumário, busca, destaques, marcadores e ajustes de aparência.','book-open'],
    ];
    for(const [index,[title,description,iconName]] of cards.entries()){const card=node('article',null,'shelf-info-card');card.style.setProperty('--i',String(index));const icon=node('span',null,'shelf-info-icon');icon.innerHTML=svg(iconName);icon.setAttribute('aria-hidden','true');card.append(icon,node('h2',title),node('p',description));grid.append(card);}
    content.append(grid);
    const links=node('nav',null,'shelf-info-links');links.setAttribute('aria-label','Links do projeto');
    for(const [label,url] of [['Página inicial Vademecum','../'],['Repositório Vademecum MD','https://github.com/lucmolero/vademecum-md'],['Código da biblioteca','https://github.com/lucmolero/biblioteca-leis']]){const link=node('a',null,'shelf-info-link');link.href=url;link.target='_blank';link.rel='noopener noreferrer';link.append(document.createTextNode(label));const icon=node('span',null,'shelf-info-link-icon');icon.innerHTML=svg('external');icon.setAttribute('aria-hidden','true');link.append(icon);links.append(link);}
    content.append(links);
  }
  async exportBackup(){const reading={};for(const book of this.books(true))reading[book.id]=this.options.getReadingData(book.id);this.download(JSON.stringify({format:'biblioteca-local',version:1,exportedAt:new Date().toISOString(),books:this.local.map(book=>({id:book.id,rawMarkdown:book.rawMarkdown,filename:book.filename,importedAt:book.importedAt})),state:this.state,reading},null,2),'biblioteca-backup.json','application/json');}
  async importBackup(file){
    try{
      const backup=JSON.parse(await file.text());if(backup.format!=='biblioteca-local'||backup.version!==1||!Array.isArray(backup.books))throw new Error('Formato inválido');
      if(backup.state?.preferences)this.state.preferences=normalizePreferences(backup.state.preferences);
      const parsed=[];for(const source of backup.books){if(typeof source.rawMarkdown!=='string'||typeof source.id!=='string')throw new Error('Documento inválido');const book=this.parseMarkdown(source.rawMarkdown,String(source.filename||'documento.md'));const hash=await this.hash(source.rawMarkdown);if(source.id!==`local-${hash}`)throw new Error('Identificador inválido');parsed.push({...book,id:source.id,contentHash:hash,rawMarkdown:source.rawMarkdown,importedAt:Number(source.importedAt)||Date.now()});}
      for(const book of parsed)await this.db.putBook(book);
      for(const[id,record]of Object.entries(backup.state?.records||{})){if(typeof id!=='string'||!id)continue;this.state.records[id]={...this.state.records[id],...normalizeMetadata(record)};}
      for(const folder of (Array.isArray(backup.state?.folders)?backup.state.folders:[])){if(!folder||typeof folder.id!=='string'||!folder.id||typeof folder.name!=='string'||!folder.name.trim())continue;if(!this.state.folders.some(item=>item.id===folder.id))this.state.folders.push({id:folder.id,name:folder.name.trim()});}
      for(const[id,data]of Object.entries(backup.reading&&typeof backup.reading==='object'?backup.reading:{}))if(this.state.records[id]||this.catalog.some(book=>book.id===id))this.options.restoreReadingData(id,data);
      this.selected.clear();this.renderSortMenu();await this.persist();this.local=(await this.db.getBooks()).filter(book=>book&&typeof book.id==='string'&&Array.isArray(book.sections)&&book.sections.length);this.render();this.options.message('Backup restaurado.');
    }catch(error){this.error(error,'Não foi possível restaurar este backup.');}
  }
}
