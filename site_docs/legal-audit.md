# Auditoria jurídica e fidelidade

O projeto usa verificações determinísticas de identidade da fonte e fidelidade
textual:

- os campos legados `legal_curator` e `legal_critic` são gerados pelo mesmo
  gate determinístico. Não representam pareceres jurídicos independentes nem
  análise de vigência ou mérito jurídico.

A auditoria de fidelidade é determinística: compara a unidade normativa oficial
com a árvore de artigos publicada, calcula hashes com escopo explícito e registra
anomalias sem corrigir o texto oficial silenciosamente. O campo
`equivalence_basis` distingue hash canônico exato de aprovação estrutural por
similaridade de pelo menos 98,5%; similaridade não significa igualdade textual.
O CI vincula o hash do relatório à versão atual do texto publicado. Alterações
normativas seguem para pull request e não são mescladas automaticamente.
