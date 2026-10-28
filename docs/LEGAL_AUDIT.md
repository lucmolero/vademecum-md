# Auditoria juridica e textual

A auditoria foi separada em duas responsabilidades:

1. **Fidelidade técnica**: compara identidade, fonte, unidade de extração,
   hashes, árvore de artigos e anomalias.
2. **Gate determinístico de fonte e texto**: o ledger mantém campos legados
   `legal_curator` e `legal_critic`, mas ambos são gerados pela mesma regra
   determinística. Eles não são pareceres jurídicos independentes e não avaliam
   vigência, efeitos temporais nem mérito jurídico.

O relatório `bases/derived/relatorios/fidelity-audit.json` é versionado e
auditável. O gate compara o hash canônico do texto publicado com o hash
vinculado ao relatório em cada validação. O status `pass` pode representar hash
exato ou árvore de artigos compatível com similaridade textual mínima de 98,5%;
o campo `equivalence_basis` distingue esses casos. Similaridade não certifica
igualdade textual nem correção jurídica. Alterações de texto são propostas em
pull requests e não são mescladas automaticamente.

Snapshots brutos de aquisição permanecem privados. A CI pública valida a
correspondência entre o texto atual e o hash publicado no ledger; ela não
reconstrói snapshots privados nem substitui a comparação com a fonte oficial.
