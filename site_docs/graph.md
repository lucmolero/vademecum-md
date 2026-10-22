# Grafo normativo

<section class="graph-explorer" data-graph-explorer data-index-url="../generated/graph-index.json" aria-labelledby="graph-explorer-title">
  <h2 id="graph-explorer-title">Explore diplomas conectados</h2>
  <p class="graph-explorer-intro">Pesquise um diploma ou escolha um nó para percorrer suas relações publicadas. As setas preservam a direção registrada; cada relação também aparece em uma lista acessível com links para os dois textos.</p>

  <div class="graph-controls">
    <div class="graph-search-control">
      <label for="graph-search">Localizar diploma</label>
      <input id="graph-search" type="search" autocomplete="off" placeholder="Nome, número ou identificador" aria-controls="graph-search-results" aria-expanded="false">
      <div id="graph-search-results" class="graph-search-results" role="group" aria-label="Sugestões de diplomas" hidden></div>
    </div>
    <div class="graph-filter-control">
      <label for="graph-relation-filter">Tipo de relação</label>
      <select id="graph-relation-filter"><option value="">Todos os tipos</option></select>
    </div>
    <div class="graph-filter-control">
      <label for="graph-direction-filter">Direção</label>
      <select id="graph-direction-filter">
        <option value="both">Entradas e saídas</option>
        <option value="outgoing">Sai deste diploma</option>
        <option value="incoming">Chega a este diploma</option>
      </select>
    </div>
  </div>

  <p id="graph-explorer-status" class="graph-explorer-status" role="status" aria-live="polite">Carregando o grafo publicado…</p>

  <div class="graph-explorer-layout">
    <div class="graph-canvas-wrap">
      <svg id="normative-graph-svg" class="normative-graph-svg" viewBox="0 0 760 500" role="group" aria-label="Grafo de vizinhos diretos do diploma selecionado"></svg>
      <p class="graph-canvas-hint">Selecione um nó com mouse, toque ou teclado. O diploma selecionado fica na URL: compartilhe o link ou use Voltar/Avançar para percorrer seu histórico. As setas indicam origem → destino.</p>
    </div>
    <aside class="graph-selected-card" aria-labelledby="graph-selected-title">
      <p class="graph-card-kicker">Diploma selecionado</p>
      <h3 id="graph-selected-title">Aguardando dados</h3>
      <p id="graph-selected-meta" class="graph-selected-meta"></p>
      <a id="graph-open-law" class="md-button" href="../generated/catalog/">Abrir texto do diploma</a>
      <p id="graph-selected-degree" class="graph-selected-degree"></p>
    </aside>
  </div>

  <section class="graph-connection-section" aria-labelledby="graph-connections-title">
    <div class="graph-connection-heading">
      <div>
        <p class="graph-card-kicker">Registros direcionais</p>
        <h3 id="graph-connections-title">Relações deste diploma</h3>
      </div>
      <span id="graph-connection-count" class="graph-connection-count"></span>
    </div>
    <ul id="graph-connection-list" class="graph-connection-list"></ul>
    <button id="graph-show-more" class="graph-show-more" type="button" hidden>Mostrar mais relações</button>
    <p class="graph-data-note">Relações repetidas com a mesma origem, tipo e destino são agrupadas e identificadas por quantidade. Abra a ficha de qualquer diploma para consultar evidências, fonte e metadados de cada registro.</p>
  </section>

  <noscript>
    <p>O explorador interativo requer JavaScript. O <a href="../generated/graph-index.json">índice topológico publicado</a> e o <a href="../generated/catalog/">catálogo de leis</a> continuam disponíveis.</p>
  </noscript>
</section>

## Explore relações a partir de um diploma

No início do site, o grafo do hero é um **recorte navegável calculado a partir de `normative-graph.jsonl`**: mostra um diploma de maior conexão no corpus e até seis vizinhos efetivamente ligados a ele. Cada linha vem de uma relação publicada e cada nó abre a página de leitura do diploma correspondente. O desenho resume registros repetidos do mesmo par para continuar legível; não representa todos os nós nem substitui as fichas completas. As setas preservam a direção do registro; o tipo e os diplomas ligados ficam disponíveis no nome acessível da conexão.

Para consultar as relações e evidências do diploma escolhido, abra o [catálogo de legislação](generated/catalog.md) e entre na página do ato. A seção **Relações normativas contextualizadas** lista os registros disponíveis, direção, tipo, dispositivo, fonte e evidência. [Voltar ao início e abrir o recorte do grafo](index.md).

O grafo registra relações publicadas entre diplomas. Cada registro preserva a direção `source_id` → `target_id`; portanto, tipos como `altera` e `alterada_por` não são intercambiáveis. As fichas exibidas nas páginas dos diplomas mantêm essa direção explícita e incluem a evidência, a fonte, a confiança e o estado de revisão disponíveis no registro.

As relações são metadados derivados para contextualização. Não integram o texto da norma e não substituem a consulta à publicação oficial. A ausência de relação ou de dispositivo identificado não permite concluir que não haja vínculo jurídico.

## Como interpretar as fichas

- **Diplomas e direção:** a ficha mostra o documento de origem, o tipo da relação e o documento de destino, na ordem registrada no grafo.
- **Dispositivo:** uma nota junto ao artigo só é criada quando o registro identifica um artigo e o tipo da relação permite associá-lo ao diploma afetado. Nas relações ativas (`altera`, `revoga`, `regulamenta`, `suspende`, `retifica`), o alvo é tratado como afetado; nas formas passivas (`alterada_por`, `revogada_por`, `regulamentada_por`, `suspensa_por`, `retificada_por`), a origem. Relações sem dispositivo ficam apenas no contexto do diploma.
- **Evidência e fonte:** o trecho registrado, quando disponível, é apresentado como evidência da classificação e acompanhado do link de fonte informado no grafo.
- **Confiança:** reproduz o valor do registro (`alta`, `media`, `baixa` ou não informado); não é uma medida de força jurídica nem de vigência.
- **Revisão:** reproduz o estado publicado. Não significa validação oficial pelo órgão emissor da norma.
- **Efeito:** a data é mostrada somente quando está presente no registro; sua ausência não é preenchida por inferência.

## Tipos de relação publicados

O vocabulário inclui alteração, revogação, regulamentação e suspensão, com tipos direcionais correspondentes. A interface conserva o tipo original e apresenta a relação entre os dois diplomas; ela não reescreve o conteúdo normativo nem presume o efeito além dos campos registrados.

## Limites da visualização

O grafo pode conter referências indiretas, detalhes incompletos ou relações sem dispositivo identificado. Marcadores junto ao texto servem apenas como atalhos para a ficha contextual da relação. Consulte a evidência e a publicação oficial antes de usar uma relação em análise jurídica.
