# Arquitetura

O sistema separa três responsabilidades: fonte normativa canônica, histórico de versões e artefatos derivados.

`bases/curated/legislacao/federal/` contém um diploma por Markdown e é a única camada normativa principal. `bases/history/` armazenará versões anteriores, atos alteradores, revogações e diffs. `bases/derived/` contém catálogos, índices e grafos regeneráveis; nunca é autoridade jurídica.

As camadas futuras de regulamentos, tratados e jurisprudência ficam no mesmo produto, mas em namespaces distintos. Cada camada terá schema e política de fonte própria antes de receber documentos.

O frontmatter é o contrato de interoperabilidade. Identidade, situação e consolidação não devem ser inferidas apenas do título ou do caminho. A data de corte é obrigatória para qualquer interpretação de atualidade.
