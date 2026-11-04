<p align="center">

  <a href="https://lucmolero.github.io/vademecum-md/"><img src="homepage/public/assets/favicon.svg" width="64" height="64" alt="VadeMecum MD"></a>

  &nbsp;&nbsp;

  <a href="https://lucmolero.github.io/vademecum-md/biblioteca/"><img src="biblioteca/src/icon.svg" width="64" height="64" alt="Biblioteca VadeMecum MD"></a>

</p>



<h1 align="center">VadeMecum MD</h1>



<p align="center"><strong>Legislação federal para ler, explorar e consultar com agentes.</strong></p>



<p align="center">

  <a href="https://lucmolero.github.io/vademecum-md/biblioteca/"><strong>Abrir a Biblioteca</strong></a> ·

  <a href="https://lucmolero.github.io/vademecum-md/graph/">Explorar o Grafo</a> ·

  <a href="skills/vademecum-consulta-juridica/SKILL.md">Usar a Skill</a>

</p>



O VadeMecum MD organiza legislação federal em Markdown com identificadores

estáveis, fonte e data de corte. O mesmo acervo serve à leitura no navegador

e à consulta por agentes.



**Edição v1.1.3** · 375 diplomas federais · corte em 21 de outubro de 2026.

[Baixar a edição](https://github.com/lucmolero/vademecum-md/releases/tag/v1.1.3)



## Para pessoas · Biblioteca, Leitor e Grafo



1. **Encontre a norma.** Na [Biblioteca](https://lucmolero.github.io/vademecum-md/biblioteca/), pesquise pelo nome, pelo número ou pelo texto integral.

2. **Vá direto ao dispositivo.** No [Leitor](https://lucmolero.github.io/vademecum-md/biblioteca/#documento=br-federal-lei_ordinaria-14133-2021), use o sumário e o botão **Fonte** para conferir a procedência. Marcadores e anotações ficam no navegador.

3. **Siga as citações.** No [Grafo](https://lucmolero.github.io/vademecum-md/graph/), selecione uma norma para explorar suas relações e abrir o texto pelo card. O painel indica o estado de verificação das relações.



## Para agentes · Skill de consulta jurídica



A **Skill** orienta o agente a localizar o diploma no corpus, conferir o

dispositivo e responder com referência, fonte e data de corte. O Grafo oferece

uma visão interativa das relações normativas desse acervo.



- [Baixe o kit da Skill e do corpus](https://lucmolero.github.io/vademecum-md/downloads/vademecum-consulta-juridica-kit.zip) e confira o [SHA-256](https://lucmolero.github.io/vademecum-md/downloads/vademecum-consulta-juridica-kit.zip.sha256).

- Disponibilize o corpus no ambiente do agente e siga as [instruções da Skill](skills/vademecum-consulta-juridica/SKILL.md).



> **Experimente:** “Localize o art. 5º da Lei nº 14.133/2021 no acervo. Indique

> a referência, a edição consultada, a data de corte e a fonte oficial.”



Veja como esse percurso aparece na [demonstração da homepage](https://lucmolero.github.io/vademecum-md/#assistente).





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



## Executar as interfaces



Requer Node.js 22 ou posterior. A partir da raiz:



```sh

npm ci --prefix biblioteca

npm run build --prefix biblioteca

npm ci --prefix homepage

npm run dev --prefix homepage

```



Abra `http://127.0.0.1:8765/`. A Biblioteca usa o corpus e o manifesto deste

checkout por padrão. Os previews usam dados pequenos e isolados; interações

demonstrativas não alteram a biblioteca pessoal.



Para verificar as interfaces:



```sh

npm test --prefix biblioteca

npm run build --prefix homepage

npm run test:graph --prefix homepage

cd homepage

npx playwright install chromium webkit

npm run test:e2e

```



A [documentação da homepage](homepage/README.md) explica a composição do site;

a [documentação da Biblioteca](biblioteca/README.md) detalha leitura, dados locais

e backup. O [guia de contribuição](CONTRIBUTING.md) reúne os validadores do corpus.