# Grafo normativo

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
