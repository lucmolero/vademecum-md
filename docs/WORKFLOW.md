# Fluxo operacional de atualização

O corpus federal é atualizado por um fluxo autônomo, reproduzível e auditável.
A aquisição, a análise jurídica, a aplicação e a publicação permanecem separadas
por gates técnicos, mas nenhuma etapa depende de decisão ou ação do usuário.

## Ciclo autônomo

1. `monitor-legislation` verifica idade, prioridade e validade das fontes.
2. `collect-legislation` consulta fontes oficiais allowlisted e grava snapshots na área privada de aquisição.
3. O comparador calcula hash bruto, hash normalizado e hash do corpo jurídico.
4. A análise LLM do agente interpreta identidade normativa, vigência, alterações,
   revogações, vetos, retificações e escopo editorial.
5. Gates determinísticos verificam identidade, integridade, estrutura, hashes,
   URLs oficiais, encodings, IDs e relações.
6. O agente aplica somente decisões que tenham evidência oficial e passem pelos gates.
7. A validação de release bloqueia qualquer inconsistência antes da publicação.

A LLM decide o significado jurídico e editorial; os validadores determinísticos
decidem se o resultado é tecnicamente admissível. Nenhum dos dois pode inventar
vigência sem fonte oficial.

## Modos operacionais

O contrato em `manifests/operating-modes.json` torna explícita a fronteira de
mutação:

- `dry_run`: planejamento sem rede e sem escrita;
- `proposal`: coleta oficial, evidências privadas e proposta de Pull Request;
- `apply_reviewed`: aplicação autônoma de uma decisão com evidência oficial e
  gates determinísticos;
- `release`: somente validação e empacotamento do corpus aprovado.

Os nomes antigos `--fetch` e `--apply` permanecem apenas como aliases de
compatibilidade. A autoridade de decisão é sempre `autonomous_legal_agent`.

## Fila de relações não resolvidas

As 2.177 ocorrências estão agrupadas em 1.491 alvos únicos no arquivo
`bases/derived/relacoes/review-queue.json`. Elas não são documentos pendentes:
são evidências de relações normativas fora do corpus principal.

O agente decidiu autonomamente:

- 1.408 grupos: `historico`, para atos alteradores, revogadores ou regulamentadores;
- 83 grupos: `grafo`, para referências diretas ou ambíguas sem identidade oficial
  única demonstrada para promoção ao corpus vigente.

Todos os alvos possuem `review_status: approved`, `decision_scope:
autonomous_agent_legal_curation`, justificativa e evidências. Nenhum item aguarda
ação do usuário e nenhum alvo foi promovido como lei vigente por inferência.

## Segurança

- Nenhum coletor escreve diretamente no corpus curado.
- Snapshots brutos e logs ficam na área privada de aquisição, ignorada pelo Git.
- Caminhos privados e dados brutos não entram no pacote público.
- Fontes fora da allowlist são rejeitadas.
- Fonte indisponível preserva o texto vigente e gera alerta técnico.
- Revogação, conflito ou alteração estrutural nunca remove texto automaticamente.
- Workflows não usam `pull_request_target` e não escrevem diretamente na branch padrão.

## Frequência

| Prioridade | Monitoramento | Coleta | Validade máxima |
| --- | --- | --- | --- |
| P0 | diário | trimestral ou evento crítico | 100 dias |
| P1 | diário | trimestral | 100 dias |
| P2 | diário | trimestral | 180 dias |

## Auditorias jurídicas

Os relatórios públicos são:

- `editorial-legal-audit.json`: 15 documentos da expansão editorial;
- `editorial-legal-audit-p0.json`: 33 documentos P0;
- `editorial-legal-audit-p1.json`: 336 documentos P1;
- `editorial-legal-audit-p2.json`: 6 documentos P2.

Cada auditoria registra fonte oficial, hash do corpo, identidade, integridade,
situação declarada e relações no grafo. O status `pass` exige texto local
compatível com a redação oficial capturada na data de corte.
## Contrato de consenso e fidelidade

Os passes autônomos `legal_curator` e `legal_critic` precisam concordar antes de
qualquer promoção. O ledger `legal-curation-consensus/v1` registra as duas
análises, suas evidências e a decisão. Sem consenso, a versão pública anterior é
preservada e o caso é registrado para a próxima execução.

`fidelity-audit.json` verifica unidades de fonte, árvore de artigos e hashes
`norm-v3`. Constituição e ADCT possuem seletores independentes mesmo quando
compartilham a mesma página oficial.

Em uma atualização, o ledger também registra `candidate_sha256_raw` e
`candidate_sha256_body`. O aplicador só materializa o novo Markdown quando esses
hashes correspondem exatamente ao snapshot selecionado; caso contrário, a
versão pública atual é preservada.
