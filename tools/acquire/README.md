# Aquisição

O fluxo de aquisição é dividido em três operações autônomas e reproduzíveis:

- `collect_legislation.py`: planeja a coleta dos 375 itens e, em modo de proposta, captura snapshots e hashes em armazenamento técnico privado;
- `monitor_legislation.py`: classifica a defasagem por prioridade (`P0`/`P1`/`P2`), sem alterar o corpus;
- `discover_legislation.py`: consulta catálogos oficiais e coloca novos candidatos na fila editorial, sem inclusão automática por mera descoberta.

As fontes são verificadas contra `manifests/sources-registry.json`. Indisponibilidade, conflito ou resposta fora da allowlist preservam a versão pública atual e geram evidência para o próximo ciclo; nunca há redação presumida. Nenhum coletor escreve diretamente na branch padrão ou promove texto ao corpus sem a análise jurídica autônoma e os gates determinísticos.

A cadência operacional do lançamento é trimestral para P0, P1 e P2, com execução manual apenas como disparo técnico do mesmo fluxo autônomo.
