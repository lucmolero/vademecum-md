# Schema Markdown

Cada documento deve começar e terminar o frontmatter YAML com `---`. Os campos mínimos são `id`, `titulo`, `esfera`, `jurisdicao`, `tipo`, `numero`, `ano`, `data_assinatura`, `ementa`, `situacao`, `versao_texto`, `consolidacao_status`, `data_corte`, `fonte_oficial`, `fonte_publicacao`, `origem_formato`, `baixado_em`, `sha256_origem`, as listas de relações e `observacoes_proveniencia`.

`id` é estável e não depende do caminho. `fonte_oficial` é uma lista de URLs públicas oficiais. `sha256_origem` identifica os bytes consultados antes da normalização. `observacoes_proveniencia` não deve conter caminhos locais, commits privados ou nomes de fontes de descoberta.

Os estados jurídicos e relacionais estão em [manifests/vocabulary.json](../manifests/vocabulary.json). O texto não deve ser resumido para preencher campos ausentes.
