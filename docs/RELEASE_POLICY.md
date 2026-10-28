# Política de release

Uma release é elegível quando os gates estruturais passam, todos os documentos têm texto, fonte oficial, hash e decisão editorial compatível, e nenhuma alteração foi incorporada silenciosamente.

O estado `release_candidate` é usado antes da publicação. A release `v1.1.3`
exige 100% do P0 consolidado, candidatos editoriais decididos, relações
críticas auditadas, relatório sem erro, site acessível e artefato reproduzível.
Esses critérios são medidos pelo baseline atual de 375 documentos.

Após a publicação, `manifests/release.json` deve permanecer em `status: release`.
Alterações posteriores ao corpus ou às interfaces de consumo devem gerar nova
release versionada; uma release publicada não é sobrescrita para esconder
divergências de conteúdo.

O workflow de publicação é idempotente: se a versão já existir, ele encerra sem
alterar a release nem substituir seus artefatos. Uma mudança exige incremento de
versão e uma nova release.

O agendamento inicia a coleta e a proposta autônoma. Nenhuma rotina escreve
diretamente na branch padrão: a proposta passa por um Pull Request e pelo workflow
completo de qualidade antes do merge automático. Atualizações do texto normativo
só são admissíveis quando o snapshot oficial e o texto publicado têm hashes
normativos idênticos após normalização; aprovações e hashes ficam registrados em
`manifests/automatic-update-ledger.json`. Conflito de fontes, ausência de
snapshot, diferença textual ou falha de qualidade interrompe a atualização.

O ledger `manifests/legal-consensus.json` registra gates determinísticos de
identidade da fonte e fidelidade textual. Os nomes legados `legal_curator` e
`legal_critic` não significam pareceres jurídicos independentes. A aprovação
automática comprova a correspondência do texto com uma fonte oficial registrada;
ela não certifica, por si só, a vigência ou a interpretação jurídica.
