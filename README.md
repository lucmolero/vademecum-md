# VadeMecum MD

**Legislação federal brasileira para leitura humana e consulta com evidência.**
Cada diploma publicado em Markdown tem identidade estável, metadados de
curadoria, data de corte, fonte indicada e informações de proveniência.

[Página inicial](https://lucmolero.github.io/vademecum-md/) ·
[Biblioteca e leitor](https://lucmolero.github.io/vademecum-md/biblioteca/) ·
[Explorar o catálogo](https://lucmolero.github.io/vademecum-md/generated/catalog/) ·
[Baixar a release v1.1.3](https://github.com/lucmolero/vademecum-md/releases/tag/v1.1.3) ·
[Consultar o contrato de consumo](manifests/consumer-contract.json)

> **Snapshot v1.1.3:** 375 diplomas federais · data de corte: 21/10/2026.
> O corte identifica esta coleção; o corpus não é atualizado em tempo real.

## Escolha como consultar

| Objetivo | Comece aqui |
| --- | --- |
| **Ler e localizar uma norma** | Use a [biblioteca e o leitor](https://lucmolero.github.io/vademecum-md/biblioteca/) ou o [catálogo](https://lucmolero.github.io/vademecum-md/generated/catalog/). Confira ID, situação do texto, fonte e data de corte. |
| **Consultar com um agente de IA** | Forneça os arquivos ou a release ao agente e use a [skill de consulta jurídica](skills/vademecum-consulta-juridica/SKILL.md). A skill orienta a consulta e a citação; não concede acesso automático ao GitHub. |
| **Integrar em dados ou ferramentas** | Comece por [`manifests/corpus.csv`](manifests/corpus.csv), [`manifests/consumer-contract.json`](manifests/consumer-contract.json) e o [grafo normativo](bases/derived/relacoes/normative-graph.jsonl). Fixe uma release para resultados reproduzíveis. |

## Texto, evidência e camadas derivadas

O Markdown em [`bases/curated/legislacao/federal/`](bases/curated/legislacao/federal/)
é a camada canônica de conteúdo deste projeto. Cada documento identifica a
norma e registra os metadados disponíveis, como fonte, corte, situação,
consolidação e hash.

O leitor web, o catálogo, os índices e as relações ajudam a encontrar e navegar
no corpus. São artefatos derivados e não substituem o texto canônico nem a
publicação oficial. Para verificar uma norma, abra a fonte oficial indicada no
documento.

A release [v1.1.3](https://github.com/lucmolero/vademecum-md/releases/tag/v1.1.3)
inclui o corpus versionado, manifesto, checksums e SBOM. Use o pacote e os
[`SHA256SUMS.txt`](https://github.com/lucmolero/vademecum-md/releases/download/v1.1.3/SHA256SUMS.txt)
para fixar e verificar os arquivos consultados.

## Citar uma consulta

Preserve o diploma, o dispositivo, o ID, a release, a data de corte e a fonte
oficial. Por exemplo:

```text
Código Civil, art. 1º
VadeMecum MD, release v1.1.3, corte 2026-10-21.
ID: br-federal-lei_ordinaria-10406-2002.
Fonte oficial: https://normas.leg.br/?urn=urn:lex:br:federal:lei:2002-01-10;10406
```

## Mapa do repositório

| Caminho | Papel |
| --- | --- |
| [`bases/curated/`](bases/curated/) | Textos canônicos publicados em Markdown. |
| [`bases/derived/`](bases/derived/) | Catálogos, relações e outros artefatos regeneráveis. |
| [`manifests/`](manifests/) | Inventário do corpus, contratos de consumo e dados de release. |
| [`skills/`](skills/) | Instruções portáteis para consulta por agentes. |
| [`site_docs/`](site_docs/) | Fontes do site editorial, que é gerado a partir do corpus. |
| [`homepage/`](homepage/) · [`biblioteca/`](biblioteca/) | Fontes da homepage e do leitor oficial; o workflow as compila junto com o corpus da release. |
| [`tools/`](tools/) · [`tests/`](tests/) | Ferramentas de aquisição, geração e validação; verificações automatizadas. |
| [`docs/`](docs/) | Especificações, arquitetura e políticas do projeto. |

## Escopo e limites

O VadeMecum MD é uma seleção curada de legislação federal, não uma cobertura
integral do Direito brasileiro, publicação oficial ou aconselhamento jurídico.
A situação e a consolidação descrevem os metadados publicados no corte indicado;
confirme a fonte oficial antes de citar ou aplicar uma norma. Relações e estados
incertos não bastam, por si só, para afirmar vigência atual.

## Projeto e governança

- [Metodologia e arquitetura](https://lucmolero.github.io/vademecum-md/architecture/)
- [Limites jurídicos](https://lucmolero.github.io/vademecum-md/legal-limits/)
- [Como contribuir e manter](CONTRIBUTING.md)
- [Política de segurança](SECURITY.md) · [Histórico de versões](CHANGELOG.md)

O código e os materiais autorais seguem a [licença MIT](LICENSE). O escopo da
licença e a exclusão dos textos normativos e materiais de terceiros estão
descritos em [licenças e materiais](LICENSE.md).
