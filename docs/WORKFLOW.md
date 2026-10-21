# Fluxo operacional de atualização

O fluxo monitora os 360 itens da matriz, mas mantém aquisição, reconciliação e publicação separadas.

## Ciclo

1. `monitor-legislation` executa diariamente, sem rede, e classifica a idade de cada fonte.
2. `collect-legislation` executa semanalmente, consulta as fontes oficiais allowlisted e grava snapshots fora do corpus curado.
3. O comparador calcula hash bruto e hash normalizado. Divergências entre fontes são bloqueadas como `source_conflict`.
4. `prepare-update-pr` gera uma proposta de revisão com os candidatos alterados, conflitos e indisponibilidades.
5. A reconciliação humana revisa o snapshot, o diff estrutural, a vigência e as relações normativas.
6. Só depois da revisão o código de atualização pode alterar Markdown, manifests e grafo em uma branch de trabalho.
7. A validação de release bloqueia fontes ausentes, hashes inválidos, texto truncado, relações inválidas e referências proibidas.

O workflow `discover-legislation` consulta catálogos oficiais e produz uma fila de candidatos. Essa fila não altera `manifests/corpus.csv` nem cria documentos curados.

## Políticas de segurança

- Nenhum coletor escreve em `bases/curated`.
- Snapshots brutos, logs e comandos ficam em `.private/acquisition`, ignorado pelo Git.
- Snapshots brutos não são enviados como artefatos de um repositório público; o armazenamento histórico exige um destino privado configurado separadamente.
- `tools/history/build_private_ledger.py` exporta a evidência para um diretório ou checkout privado explicitamente informado.
- Todos os workflows têm `contents: read` e não podem usar `git push`, `contents: write` ou `pull_request_target`.
- A descoberta de novos atos alimenta `manifests/discovery-queue.json`, mas nunca amplia a matriz automaticamente.
- Indisponibilidade preserva a versão atual e gera alerta; não há promoção presumida.

## Frequência

| Prioridade | Monitoramento | Coleta | Validade máxima |
| --- | --- | --- | --- |
| P0 | diário | semanal ou manual crítico | 1 dia |
| P1 | diário | semanal | 7 dias |
| P2 | diário | mensal | 30 dias |

O workflow `release-gates` executa trimestralmente e também pode ser acionado manualmente. A publicação é condicionada aos gates técnicos e à revisão humana da reconciliação.
