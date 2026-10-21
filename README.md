# vademecum-md

Corpus autoral de legislação federal brasileira em Markdown, estruturado para leitura humana, validação automatizada e consumo futuro por agentes de IA.

O produto principal é um diploma por arquivo em `bases/curated/legislacao/federal/`. O texto normativo permanece separado dos índices, relações e relatórios derivados.

## Estado do corpus

- 360 documentos federais materializados;
- texto integral preservado em Markdown;
- fonte oficial, data de corte e hash em cada documento;
- 241 documentos consolidados por fonte oficial;
- 119 documentos marcados como `requer_reconciliacao`;
- relações normativas geradas em `bases/derived/relacoes/`;
- RAG deliberadamente adiado até a estabilização da release 1.0.

O estado reproduzível está em [docs/COMPLETENESS.md](docs/COMPLETENESS.md) e nos manifests de [manifests/](manifests/).

## Arquitetura

```text
bases/curated/legislacao/federal/  # fonte normativa canônica
bases/curated/regulamentos/        # camada regulatória futura
bases/curated/tratados/            # tratados futuros
bases/curated/jurisprudencia/      # jurisprudência futura
bases/history/                     # versões, alterações e revogações
bases/derived/                     # catálogos e grafos regeneráveis
manifests/                         # contratos de dados e release
tools/                             # aquisição, normalização, validação e release
tests/                             # testes unitários e de integração
docs/                              # arquitetura, governança e operação
```

## Contrato dos documentos

Cada Markdown possui frontmatter com identidade estável, classificação, ementa, situação, consolidação, data de corte, fontes oficiais e hash. `consolidacao_status` controla o que pode ser interpretado como vigente; texto presente não significa vigência confirmada.

Os estados permitidos estão em [manifests/vocabulary.json](manifests/vocabulary.json). A matriz de cobertura é [manifests/corpus.csv](manifests/corpus.csv), com cobertura, integridade e atualidade como dimensões independentes.

## Desenvolvimento local

```powershell
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
python tools/check_markdown.py
python tools/build_public_indexes.py --apply
```

Os artefatos técnicos de aquisição e transformação ficam em `.private/` e `bases/raw/`, ambos ignorados pelo Git. O repositório público contém somente a proveniência oficial necessária para auditar o corpus.

## Publicação

A publicação deve ocorrer apenas após os gates locais e do workflow passarem. O workflow não promove documentos sem fonte oficial, hash, texto integral ou consolidação verificável. Alterações ambíguas permanecem pendentes; não são convertidas em uma redação presumida.
