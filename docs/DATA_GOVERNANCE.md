# Governança de dados

O corpus é governado por quatro dimensões independentes:

1. cobertura: o diploma está na matriz;
2. integridade: o texto está completo e não truncado;
3. atualidade: há data de corte e fonte oficial consultada;
4. consolidação: a redação vigente foi confirmada ou reconciliada.

Um documento só pode ser apresentado como vigente quando possui fonte oficial, texto integral, hash, data de corte e status de consolidação compatível. Ambiguidades são preservadas como pendências.

Alterações são sempre determinísticas, reproduzíveis e acompanhadas de diff. Os manifests são dados de controle; o Markdown normativo continua sendo a fonte canônica.
