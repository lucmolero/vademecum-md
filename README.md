# vademecum-md

Corpus autoral de legislação federal brasileira em Markdown, estruturado para leitura humana, validação automatizada e consumo futuro por agentes de IA.

O produto principal é um diploma por arquivo em `bases/curated/legislacao/federal/`. O texto normativo permanece separado dos índices, relações e relatórios derivados.

## Estado do corpus

- 375 documentos federais materializados;
- texto integral preservado em Markdown;
- fonte oficial, data de corte e hash em cada documento;
- 372 documentos consolidados por fonte oficial e 3 por reconciliação;
- 33/33 documentos P0 consolidados;
- 1.841 relações normativas materializadas;
- 2.177 ocorrências de relações ainda não materializadas, agrupadas em 1.491 alvos únicos;
- entre as ocorrências, 2.088 são atos alteradores/regulamentadores e 89 são diplomas referenciados; entre os alvos únicos, 1.408 permanecem no histórico e 83 somente no grafo;
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

Os artefatos técnicos de aquisição e transformação ficam em uma área privada ignorada pelo Git. O repositório público contém somente a proveniência oficial necessária para auditar o corpus. A proveniência bruta e os logs completos devem ser sincronizados para um repositório privado separado.

## Publicação

A publicação deve ocorrer apenas após os gates locais e do workflow passarem. O fluxo de atualização gera propostas por Pull Request e não escreve diretamente na `main`. O workflow não promove documentos sem fonte oficial, hash, texto integral, análise jurídica autônoma e consolidação verificável. Alterações ambíguas recebem disposição segura no histórico ou no grafo; nunca são convertidas em uma redação presumida.
