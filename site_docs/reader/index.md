<div class="vmd-reader-app" id="vmd-reader-app" data-reader-app data-index="../generated/reader-data/index.json" data-document-root="../generated/reader-data/documents/" data-reading-theme="paper" data-reading-size="regular" data-reading-face="serif">
  <header class="vmd-reader-bar">
    <a class="vmd-reader-brand" href="../" aria-label="VadeMecum MD — página inicial"><span aria-hidden="true">V/</span><strong>VadeMecum MD<small>LEITOR INTEGRAL</small></strong></a>
    <div class="vmd-reader-release" aria-label="Versão do acervo"><span>SNAPSHOT</span><strong data-reader-release>Carregando acervo…</strong></div>
    <div class="vmd-reader-bar-actions">
      <button type="button" data-reader-action="library" aria-expanded="false" aria-controls="reader-library">Acervo</button>
      <button type="button" data-reader-focus-search aria-label="Buscar diploma" title="Buscar diploma (Ctrl ou Cmd + K)">⌕ <span>Buscar</span><kbd>Ctrl K</kbd></button>
      <button type="button" data-reader-action="theme" aria-label="Alternar aparência da leitura" title="Alternar papel, sépia e escuro">◐ <span>Aparência</span></button>
      <a href="../generated/catalog/">Catálogo</a>
      <a href="https://github.com/lucmolero/vademecum-md" target="_blank" rel="noreferrer" aria-label="Repositório do projeto no GitHub">GitHub ↗</a>
    </div>
  </header>

  <div class="vmd-reader-layout">
    <aside class="vmd-reader-library" id="reader-library" aria-labelledby="reader-library-heading">
      <div class="vmd-panel-heading"><p class="vmd-reader-kicker">ACERVO FEDERAL</p><h2 id="reader-library-heading">Encontrar uma norma</h2></div>
      <label class="vmd-reader-search-label" for="reader-search">Nome, número ou tipo</label>
      <div class="vmd-reader-search-wrap"><span aria-hidden="true">⌕</span><input id="reader-search" type="search" placeholder="Ex.: Código Civil" autocomplete="off" aria-controls="reader-results" aria-describedby="reader-search-help" /></div>
      <p id="reader-search-help" class="vmd-reader-help">A busca encontra diplomas pelo nome e número. Depois de abrir uma norma, use o índice para ir ao artigo.</p>
      <label class="vmd-reader-search-label" for="reader-domain">Área do direito</label>
      <select id="reader-domain" class="vmd-reader-domain"><option value="">Todas as áreas</option></select>
      <p id="reader-results-count" class="vmd-reader-results-count" role="status" aria-live="polite">Preparando o índice…</p>
      <div class="vmd-reader-results-scroll"><ul id="reader-results" class="vmd-reader-results" role="listbox" tabindex="0" aria-label="Diplomas encontrados"></ul></div>
      <div class="vmd-reader-library-footer"><a href="../generated/catalog/">Ver catálogo por área ↗</a><span>Markdown canônico nas releases</span></div>
    </aside>

    <section class="vmd-reader-stage" id="reader-stage" aria-label="Leitor do diploma">
      <section class="vmd-reader-welcome" data-reader-welcome aria-labelledby="reader-title">
        <p class="vmd-reader-kicker"><span aria-hidden="true"></span> LEITURA NORMATIVA · CORTE VERSIONADO</p>
        <h1 id="reader-title">O acervo inteiro.<br><em>Um só lugar para ler.</em></h1>
        <p class="vmd-reader-welcome-copy">Escolha uma norma para abrir o texto, navegar pelos artigos e conferir a fonte e o corte sem perder a página.</p>
        <button type="button" class="vmd-reader-start" data-reader-focus-search>Buscar no acervo <span aria-hidden="true">→</span></button>
        <p class="vmd-reader-welcome-note">A leitura é contínua e ajustável. A publicação oficial continua sendo a autoridade textual.</p>
        <div class="vmd-reader-welcome-facts"><div><strong data-reader-count>375</strong><span>diplomas no índice</span></div><div><strong data-reader-cutoff>—</strong><span>data de corte</span></div><div><strong data-reader-version>—</strong><span>release fixada</span></div></div>
      </section>

      <section class="vmd-reader-document" data-reader-document hidden aria-labelledby="reader-document-title">
        <header class="vmd-reader-document-heading">
          <p class="vmd-reader-document-meta" data-document-meta></p>
          <h1 id="reader-document-title" data-document-title tabindex="-1"></h1>
          <p class="vmd-reader-ementa" data-document-ementa></p>
          <div class="vmd-reader-status-row" data-document-status></div>
        </header>
        <div class="vmd-reading-toolbar" role="toolbar" aria-label="Preferências de leitura">
          <div class="vmd-reading-toolbar-group"><span>Texto</span><button type="button" data-reader-action="font-decrease" aria-label="Diminuir o tamanho do texto">A−</button><button type="button" data-reader-action="font-increase" aria-label="Aumentar o tamanho do texto">A+</button><button type="button" data-reader-action="font-face" aria-label="Alternar fonte serifada e sem serifa">Serifada</button></div>
          <div class="vmd-reading-toolbar-group"><button type="button" data-reader-action="context" aria-expanded="false" aria-controls="reader-provenance-title">Índice e fonte</button><button type="button" data-reader-action="focus" aria-pressed="false">Leitura sem painéis</button><button type="button" data-reader-action="copy-citation">Copiar citação</button><button type="button" data-reader-action="print">Imprimir</button></div>
        </div>
        <div class="vmd-reading-progress" role="progressbar" aria-label="Progresso de leitura no diploma" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span data-reading-progress></span></div>
        <article class="vmd-reader-text" id="reader-text" tabindex="-1" data-reader-text></article>
        <section class="vmd-reader-relations" aria-labelledby="reader-relations-title">
          <h2 id="reader-relations-title">Relações normativas</h2>
          <p>Contexto derivado do grafo publicado. Consulte a evidência e a fonte oficial antes de interpretar uma relação.</p>
          <div data-reader-relations></div>
        </section>
        <p class="vmd-reader-endnote">Este texto pertence ao snapshot <span data-endnote-release></span>, com corte em <span data-endnote-cutoff></span>. Verifique a publicação oficial antes de citar ou aplicar a norma.</p>
      </section>
    </section>

    <aside class="vmd-reader-context" aria-label="Índice de artigos e proveniência">
      <section class="vmd-reader-contents">
        <p class="vmd-reader-kicker">NESTE DIPLOMA</p><h2>Ir ao artigo</h2>
        <label class="vmd-reader-search-label" for="reader-article-search">Número ou texto do artigo</label>
        <input id="reader-article-search" class="vmd-article-search" type="search" placeholder="Ex.: 5º ou igualdade" aria-controls="reader-article-list" disabled />
        <p class="vmd-reader-help" data-article-count>Escolha uma norma para ver seu índice.</p>
        <ol id="reader-article-list" class="vmd-article-list"></ol>
        <button type="button" class="vmd-show-more" data-reader-more-articles hidden>Mostrar mais artigos</button>
      </section>
      <section class="vmd-reader-provenance" aria-labelledby="reader-provenance-title">
        <p class="vmd-reader-kicker">RASTREABILIDADE</p><h2 id="reader-provenance-title">Fonte e estado</h2>
        <dl><dt>Situação no corte</dt><dd data-provenance-status>—</dd><dt>Data de corte</dt><dd data-provenance-cutoff>—</dd><dt>Consolidação</dt><dd data-provenance-consolidation>—</dd><dt>Fidelidade</dt><dd data-provenance-fidelity>—</dd><dt>Release</dt><dd data-provenance-release>—</dd></dl>
        <a class="vmd-official-source" data-official-source hidden target="_blank" rel="noreferrer">Abrir fonte oficial ↗</a>
        <button type="button" class="vmd-copy-id" data-reader-action="copy-id" disabled>Copiar ID do diploma</button>
        <details class="vmd-reader-hashes"><summary>Hashes e unidade da fonte</summary><dl><dt>ID estável</dt><dd><code data-provenance-id>—</code></dd><dt>SHA-256 da fonte</dt><dd><code data-provenance-source-hash>—</code></dd><dt>SHA-256 do texto</dt><dd><code data-provenance-body-hash>—</code></dd><dt>Unidade extraída</dt><dd><code data-provenance-source-unit>—</code></dd></dl></details>
      </section>
    </aside>
  </div>
  <p class="vmd-reader-toast" data-reader-toast role="status" aria-live="polite"></p>
</div>

<noscript><div class="vmd-reader-noscript"><h2>O leitor integrado precisa de JavaScript</h2><p>Você ainda pode navegar pela <a href="../generated/catalog/">lista do catálogo</a> ou acessar o Markdown canônico nas <a href="https://github.com/lucmolero/vademecum-md/releases">releases do projeto</a>.</p></div></noscript>
