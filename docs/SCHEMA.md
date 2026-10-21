# Schema Markdown

Cada documento deve começar e terminar o frontmatter YAML com `---`. Os campos mínimos são `id`, `titulo`, `esfera`, `jurisdicao`, `tipo`, `numero`, `ano`, `data_assinatura`, `ementa`, `situacao`, `versao_texto`, `consolidacao_status`, `data_corte`, `fonte_oficial`, `fonte_publicacao`, `origem_formato`, `baixado_em`, `sha256_origem`, as listas de relações e `observacoes_proveniencia`.

`id` é estável e não depende do caminho. `fonte_oficial` é uma lista de URLs públicas oficiais. `sha256_origem` identifica os bytes consultados antes da normalização. `observacoes_proveniencia` não deve conter caminhos locais, commits privados ou nomes de fontes de descoberta.

Os estados jurídicos e relacionais estão em [manifests/vocabulary.json](../manifests/vocabulary.json). O texto não deve ser resumido para preencher campos ausentes.
## Fidelidade normativa v2

Além do hash de origem legado, todo documento possui `source_unit_id`,
`source_unit_selector`, `canonicalization_version: norm-v2`,
`sha256_source_raw`, `sha256_source_normalized`, `sha256_source_body` e
`sha256_published_body`. Campos vazios são acompanhados por estados explícitos,
como `numero_status: nao_aplicavel` ou
`fonte_publicacao_status: indisponivel_na_fonte_publica`.

`fidelity_status: pass` só pode ser promovido quando a unidade oficial e a árvore
normativa publicada forem equivalentes. A auditoria não altera ortografia ou
redação oficial silenciosamente.
