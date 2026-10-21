# Aquisição

O fluxo de aquisição é dividido em três operações seguras:

- `collect_legislation.py`: planeja a coleta dos 360 itens e, com `--fetch`, grava snapshots e hashes somente em `.private/acquisition`;
- `monitor_legislation.py`: classifica a defasagem por prioridade (`P0` diário, `P1` semanal, `P2` mensal), sem rede e sem alterar o corpus;
- `discover_legislation.py`: consulta catálogos oficiais com `--fetch` ou recebe candidatos de fixtures e os coloca em fila de revisão, sem inclusão automática na matriz.

As fontes são verificadas contra `manifests/sources-registry.json`. Divergências entre fontes oficiais, indisponibilidade e respostas fora da allowlist bloqueiam a promoção automática. Nenhum coletor escreve em `bases/curated`.
