# Auditoria juridica e textual

A auditoria foi separada em duas responsabilidades:

1. **Fidelidade tecnica**: prova identidade, fonte, unidade de extracao, hashes,
   arvore de artigos e anomalias.
2. **Curadoria juridica assistida**: os passes `legal_curator` e `legal_critic`
   analisam vigencia, alteracoes, revogacoes, efeitos temporais, relevancia e
   relacoes normativas com evidencias oficiais.

O arquivo `bases/derived/relatorios/fidelity-audit.json` e um relatorio
versionado e auditavel. O ledger publico atual registra 375/375 documentos em
`pass`. A release anterior nao e retroativamente reclassificada como
juridicamente validada.

Raw acquisition snapshots remain private by design. Public CI validates the
versioned ledger and must not attempt to reconstruct private snapshots or
silently downgrade the published audit. New snapshots are evaluated in the
private acquisition workflow; only the audited ledger is promoted publicly.
