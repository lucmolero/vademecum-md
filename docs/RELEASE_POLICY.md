# Política de release

Uma release é elegível quando os gates estruturais passam, todos os documentos têm texto, fonte oficial, hash e decisão editorial compatível, e nenhuma alteração foi incorporada silenciosamente.

O estado `release_candidate` é usado antes da publicação. A release `v1.1.0`
exige 100% do P0 consolidado, candidatos editoriais decididos, relações
críticas auditadas, relatório sem erro, site acessível e artefato reproduzível.
Esses critérios são medidos pelo baseline atual de 375 documentos.

Após a publicação, `manifests/release.json` deve permanecer em `status: release`.
Alterações posteriores ao corpus ou às interfaces de consumo devem gerar nova
release versionada; uma release publicada não é sobrescrita para esconder
divergências de conteúdo.

O agendamento inicia a coleta e a proposta autônoma. A análise jurídica é
executada pelo agente e a admissibilidade técnica pelos gates; nenhuma rotina
escreve diretamente na branch padrão. A proposta abre um Pull Request e não o
mescla automaticamente. A revisão de governança ocorre no merge, sem exigir
decisão humana diploma a diploma.

O ledger `manifests/legal-consensus.json` registra os passes `legal_curator` e
`legal_critic` para cada documento do corpus. A release exige cobertura completa,
consenso e evidência oficial; divergências preservam a versão pública anterior.
