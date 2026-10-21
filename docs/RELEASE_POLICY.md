# Política de release

Uma release é elegível quando os gates estruturais passam, todos os documentos têm texto, fonte oficial e hash, e nenhuma alteração foi incorporada silenciosamente.

O estado `pre_release` é permitido enquanto houver P0 pendente. A release 1.0 exige 100% do P0 consolidado, relações críticas resolvidas, relatório sem erro e artefato reproduzível.

O agendamento trimestral apenas inicia a validação. Publicação automática só ocorre depois que o workflow gerar os índices e aprovar todos os gates aplicáveis à versão.
