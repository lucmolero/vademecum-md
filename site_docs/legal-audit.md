# Auditoria jurídica e fidelidade

O projeto usa duas camadas autônomas:

- `legal_curator`: interpreta vigência, relações e disposição editorial usando
  evidência oficial;
- `legal_critic`: procura inconsistências, conflitos e extrapolações.

A auditoria de fidelidade é determinística: compara a unidade normativa oficial
com a árvore de artigos publicada, calcula hashes com escopo explícito e registra
anomalias sem corrigir o texto oficial silenciosamente.
