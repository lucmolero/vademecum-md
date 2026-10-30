# Fluxo operacional de atualização

O corpus federal é atualizado por um fluxo autônomo, reproduzível e auditável.
A aquisição, a análise jurídica declarada, a aplicação e a publicação permanecem
separadas por gates técnicos. Propostas são abertas automaticamente como Pull
Requests; o workflow completo de qualidade é executado no commit exato da
proposta e, se passar, a política confiável faz o merge sem ação humana. Após
confirmar o merge protegido, a política dispara explicitamente o workflow de
Pages; assim a publicação não depende de eventos `push` emitidos com o token do
GitHub Actions.

## Ciclo autônomo

1. `monitor-legislation` verifica idade, prioridade e validade das fontes.
2. `collect-legislation` consulta fontes oficiais allowlisted e grava snapshots na área privada de aquisição.
3. O comparador calcula hash bruto, hash normalizado e hash do corpo jurídico.
4. O fluxo classifica a identidade da fonte e verifica os vínculos de evidência; o
   ledger legado de consenso não representa opiniões jurídicas independentes.
5. Gates determinísticos verificam identidade, integridade, estrutura, hashes,
   URLs oficiais, encodings, IDs e relações. Para promover atualização textual, o
   hash normalizado do corpo oficial deve ser idêntico ao do texto publicado.
6. O ledger de atualização registra fonte e hashes aprovados, amarrando a decisão
   ao documento publicado.
7. A validação de release e a suíte completa bloqueiam inconsistências antes do
   merge e da publicação.

Correspondência textual e identidade da fonte são verificadas deterministicamente.
Esses gates não decidem vigência nem interpretação jurídica; a informação de
situação deve ser consultada nas fontes oficiais citadas.

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
- Atualização automática do texto exige correspondência normativa exata com
  snapshot oficial verificado; similaridade textual não autoriza promoção.
- O merge automático só ocorre após a suíte de qualidade no commit exato da PR.
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

O ledger `legal-curation-consensus/v1` preserva campos legados chamados
`legal_curator` e `legal_critic`, mas ambos são produzidos pela mesma regra
determinística de identidade da fonte e fidelidade textual. Não são análises
jurídicas independentes. Atualizações são preparadas como pull requests; o
workflow não mescla mudanças normativas na branch padrão.

`fidelity-audit.json` verifica unidades de fonte, árvore de artigos e hashes
`norm-v3`. Constituição e ADCT possuem seletores independentes mesmo quando
compartilham a mesma página oficial.

Em uma atualização, o ledger também registra `candidate_sha256_raw` e
`candidate_sha256_body`. O aplicador só materializa o novo Markdown quando esses
hashes correspondem exatamente ao snapshot selecionado; caso contrário, a
versão pública atual é preservada.
