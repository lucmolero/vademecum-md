# Política de release

Uma release é elegível quando os gates estruturais passam, todos os documentos têm texto, fonte oficial, hash e decisão editorial compatível, e nenhuma alteração foi incorporada silenciosamente.

O estado `pre_release` é usado somente durante a preparação. A release 1.0 exige 100% do P0 consolidado, candidatos editoriais decididos, relações críticas auditadas, relatório sem erro e artefato reproduzível. Esses critérios estão atendidos pelo baseline atual de 375 documentos.

O agendamento inicia a coleta e a proposta autônoma. A análise jurídica é executada pelo agente e a admissibilidade técnica pelos gates; nenhuma rotina escreve diretamente na branch padrão. A publicação não depende de aprovação humana de conteúdo.

O ledger `manifests/legal-consensus.json` registra os passes `legal_curator` e
`legal_critic` para cada documento do corpus. A release exige cobertura completa,
consenso e evidência oficial; divergências preservam a versão pública anterior.
