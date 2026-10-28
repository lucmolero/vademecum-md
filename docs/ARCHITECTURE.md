# Arquitetura

O sistema separa três responsabilidades: fonte normativa canônica, histórico de versões e artefatos derivados.

`bases/curated/legislacao/federal/` contém um diploma por Markdown e é a única camada normativa publicada. `bases/history/` preserva versões anteriores, atos alteradores e diffs. `bases/derived/` contém catálogos, índices e grafos regeneráveis; nunca é autoridade jurídica.

Regulamentos, tratados e jurisprudência não integram o escopo atual e não têm namespaces vazios no repositório. Uma decisão futura de expansão deve primeiro definir schema, política de fontes, evidência e validação para a camada.

O frontmatter é o contrato de interoperabilidade. Identidade, situação e consolidação não devem ser inferidas apenas do título ou do caminho. A data de corte é obrigatória para qualquer interpretação de atualidade.
