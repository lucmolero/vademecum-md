# Auditoria jurídica e textual

A auditoria foi separada em duas responsabilidades:

1. **Fidelidade técnica**: prova identidade, fonte, unidade de extração, hashes,
   árvore de artigos e anomalias.
2. **Curadoria jurídica assistida**: os passes `legal_curator` e `legal_critic`
   analisam vigência, alterações, revogações, efeitos temporais, relevância e
   relações normativas com evidências oficiais.

O arquivo `bases/derived/relatorios/fidelity-audit.json` é um relatório
regenerável. No estado atual, ele identifica divergências que ainda exigem
reconciliação; por isso a release pública anterior não é retroativamente
reclassificada como juridicamente validada.
