# Skills para consulta do VadeMecum MD

Esta pasta publica instruções portáteis para agentes que consultam o corpus. As
skills orientam recuperação, leitura crítica e citação; não incluem ferramentas
de acesso automático, chamadas fictícias de function calling, scripts de escrita
ou ações externas.

## Skill disponível

- [`vademecum-consulta-juridica/SKILL.md`](vademecum-consulta-juridica/SKILL.md):
  localizar e analisar normas com corte temporal, estado, proveniência e citações
  verificáveis.

O arquivo segue o formato Agent Skills (`SKILL.md` com metadados YAML) e pode ser
usado em ambientes compatíveis, incluindo Codex e Claude. Consulte
[`vademecum-consulta-juridica/README.md`](vademecum-consulta-juridica/README.md)
para ativação e exemplos. A skill não instala nem conecta o agente ao
repositório: o agente precisa receber acesso aos arquivos, ao site ou a uma
ferramenta de leitura já disponível no ambiente.

## Limites comuns

- A cobertura é a publicada na release consultada; não representa todo o Direito
  brasileiro.
- A publicação oficial indicada em cada diploma é a autoridade textual. Site,
  metadados, índices, histórico e grafo do projeto têm papéis distintos.
- Uma resposta que use o corpus deve informar diploma, dispositivo, ID estável,
  release, data de corte e fonte oficial, conforme aplicável e disponível.
- As skills apoiam consulta e análise; não prestam aconselhamento jurídico nem
  substituem conferência da fonte oficial.

Os cenários de avaliação manual e seus resultados esperados estão em
[`vademecum-consulta-juridica/evals.md`](vademecum-consulta-juridica/evals.md).
