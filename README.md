# VadeMecum MD

> Legislação federal brasileira estruturada para leitura humana, validação auditável e uso por máquinas.

[![Qualidade](https://github.com/lucmolero/vademecum-md/actions/workflows/quality.yml/badge.svg)](https://github.com/lucmolero/vademecum-md/actions/workflows/quality.yml)
[![Site](https://img.shields.io/badge/site-GitHub%20Pages-13243A)](https://lucmolero.github.io/vademecum-md/)
[![Release](https://img.shields.io/badge/release-1.1.0-B48A3C)](https://github.com/lucmolero/vademecum-md/releases/tag/v1.1.0)
[![License](https://img.shields.io/badge/code%20and%20docs-MIT-2D7659)](LICENSE.md)

O VadeMecum MD é um corpus autoral de legislação federal brasileira em Markdown,
com fontes oficiais, hashes, metadados jurídicos, histórico normativo e grafo de
relações. O projeto transforma documentos normativos em uma base legível por
pessoas e consumível por ferramentas, agentes e pipelines de dados.

> **Limite jurídico:** este projeto não é publicação oficial, não substitui a
> consulta às fontes governamentais e não oferece aconselhamento jurídico. A
> autoridade textual continua sendo da fonte oficial indicada em cada diploma.

## Produto

O site [VadeMecum MD](https://lucmolero.github.io/vademecum-md/) oferece uma
experiência editorial derivada do corpus canônico. Cada diploma possui identidade
estável, texto integral, situação, data de corte, fonte oficial, unidade de
extração e hashes verificáveis.

### Estado da release pública `v1.1.0`

- corpus federal curado: **375 diplomas**;
- núcleo P0 consolidado: **33/33**;
- relações normativas: **1.841**;
- ocorrências externas classificadas: **2.177**;
- testes automatizados: **51**;
- data de corte do snapshot: **2026-10-21**;
- RAG e índices semânticos: deliberadamente fora desta release.

As métricas da homepage são regeneradas a partir dos manifests; não são números
digitados manualmente.

## Um corpus, três modos de trabalho

O produto atende três públicos sem duplicar ou reinterpretar o texto normativo:

- **advogados e pesquisadores jurídicos:** leitura integral, situação, fonte,
  data de corte, navegação por artigo e citação reproduzível;
- **cientistas de dados:** CSV, frontmatter, JSONL, hashes, IDs estáveis e
  releases comparáveis para pipelines determinísticos;
- **desenvolvedores de agentes de IA:** contrato de evidência, relações
  rastreáveis e regras explícitas para não inventar texto ou vigência.

O [guia de públicos e consumo](https://lucmolero.github.io/vademecum-md/audiences/)
contém os protocolos de uso e exemplos para cada perfil. O Markdown canônico e
os manifestos são as interfaces públicas primárias; o site é uma camada derivada.

## Arquitetura

```text
fontes oficiais
      ↓
aquisição privada
      ↓
normalização determinística
      ↓
auditoria de fidelidade
      ↓
curadoria jurídica autônoma
      ↓
corpus Markdown + histórico + grafo
      ↓
site editorial + release reproduzível
```

O corpus canônico vive em `bases/curated`. O histórico, as relações e os
relatórios são camadas separadas. O site é sempre derivado e regenerável; nunca
é fonte normativa.

## Como uma alteração chega ao corpus

```text
fonte oficial alterada
→ snapshot privado
→ comparação estrutural
→ evidência e diff
→ análise jurídica dupla
→ Pull Request
→ gates técnicos
→ merge governado
→ release
```

O fluxo não escreve diretamente na branch padrão. Fontes indisponíveis, conflitos
ou alterações ambíguas preservam a versão pública anterior e produzem evidência
para a próxima proposta.

## Comece localmente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[docs]"
python tools/site/build_site.py
mkdocs serve
```

CLI operacional:

```text
vademecum acquire
vademecum normalize
vademecum audit
vademecum graph
vademecum site
vademecum release
```

Validação completa:

```powershell
python tools/check_markdown.py
python tools/validate/validate_workflows.py
python tools/build_public_indexes.py --apply
python tools/site/build_site.py
mkdocs build --strict
python tools/validate/validate_site.py
python tools/validate_release.py --stabilization
python -m unittest discover -s tests -v
```

## Estrutura pública

```text
bases/curated/       corpus canônico
bases/history/       versões, alterações e diffs
bases/derived/       catálogos, relações e relatórios
manifests/            contratos, fontes e métricas
tools/                aquisição, normalização e validação
site_docs/            documentação e site derivado
tests/                testes unitários, integração, release e site
```

## Qualidade e proveniência

Cada documento registra, quando aplicável:

- fonte oficial e unidade de extração;
- hash da resposta bruta;
- hash do texto selecionado;
- hash do corpo normativo;
- hash do corpo publicado;
- versão de normalização;
- data de corte;
- status de fidelidade;
- relações normativas;
- limitações editoriais.

A fidelidade estrutural não é uma declaração de oficialidade. O agente jurídico
faz curadoria assistida com evidências públicas; os validadores determinísticos
verificam admissibilidade técnica e não inventam significado jurídico.

## Documentação

- [Site editorial](https://lucmolero.github.io/vademecum-md/)
- [Públicos e consumo](https://lucmolero.github.io/vademecum-md/audiences/)
- [Contratos de consumo](docs/AUDIENCE_CONTRACTS.md)
- [Especificação do produto](docs/PRODUCT_SPEC.md)
- [Metodologia jurídica](docs/LEGAL_AUDIT.md)
- [Arquitetura](docs/SCHEMA.md)
- [Qualidade](docs/QUALITY.md)
- [Fluxo de atualização](docs/WORKFLOW.md)
- [Governança de dados](docs/DATA_GOVERNANCE.md)
- [Segurança](SECURITY.md)
- [Contribuição](CONTRIBUTING.md)
- [Citação](CITATION.cff)

## Licença e citação

Scripts, schemas, manifests e documentação autoral são distribuídos sob MIT.
Os textos normativos permanecem sujeitos ao regime jurídico aplicável às
publicações oficiais. Cite sempre a release específica utilizada.

Veja [CITATION.cff](CITATION.cff) e o [changelog](CHANGELOG.md).
