<p align="center">
  <img src="homepage/public/assets/favicon.svg" width="72" height="72" alt="Símbolo do VadeMecum MD">
</p>

<h1 align="center">VadeMecum MD</h1>

<p align="center"><strong>Legislação federal brasileira para leitura humana e consulta com evidência.</strong></p>

<p align="center">
  <a href="https://lucmolero.github.io/vademecum-md/">Página inicial</a> ·
  <a href="https://lucmolero.github.io/vademecum-md/biblioteca/">Biblioteca</a> ·
  <a href="https://lucmolero.github.io/vademecum-md/demos/">Demonstrações</a> ·
  <a href="https://github.com/lucmolero/vademecum-md/releases/tag/v1.1.3">Baixar acervo</a>
</p>

<p align="center">
  <img src="docs/media/launch/banner.png" alt="VadeMecum MD: normas em contexto, com biblioteca, leitor e grafo de citações" width="100%">
</p>

Cada diploma publicado em Markdown tem identidade estável, metadados de
curadoria, data de corte, fonte indicada e informações de proveniência.

> **Snapshot v1.1.3:** 375 diplomas federais · data de corte: 21/10/2026.
> O corte identifica esta coleção; o corpus não é atualizado em tempo real.

## O projeto

O VadeMecum MD reúne texto, leitura e relações normativas em um mesmo acervo.

- **Leitura:** busca no texto integral, navegação por dispositivos, marcadores e anotações.
- **Relações:** grafo interativo de citações entre normas, com busca e exploração dos nós.
- **Integração:** Markdown, manifestos e uma skill de consulta para trabalhar com a mesma release.

A tela completa do grafo está disponível em [`/graph/`](https://lucmolero.github.io/vademecum-md/graph/); ela também pode ser aberta pelo menu da homepage e pelos links do projeto na Biblioteca.

Concebido e mantido por [Luciano Molero](https://github.com/lucmolero).
O projeto é estático: os dados pessoais de leitura permanecem no navegador.

## Demonstrações e telas

Os vídeos registram o produto em uso, com mouse, cliques, busca, arraste e
pausas para acompanhar cada etapa. O percurso do grafo termina com a abertura da
norma no Leitor; a demonstração da skill percorre os quatro exemplos da homepage.

- [Assistir às demonstrações](https://lucmolero.github.io/vademecum-md/demos/)
- [Grafo: busca, arraste, cartão e Leitor](homepage/public/demos/media/grafo-em-uso.webm)
- [Skill: princípios, transparência, data de corte e referência](homepage/public/demos/media/consultas-para-agentes.webm)

Capturas em alta resolução das telas reais. Selecione uma imagem para abri-la
em tamanho integral.

<p align="center">
  <a href="docs/media/launch/homepage-desktop.png"><img src="docs/media/launch/homepage-desktop.png" alt="Homepage VadeMecum MD em desktop" width="48%"></a>
  <a href="docs/media/launch/simulacao-agentes.png"><img src="docs/media/launch/simulacao-agentes.png" alt="Simulação da skill para agentes com resposta e fonte" width="48%"></a>
</p>

<p align="center"><sub>Homepage · Resposta da skill com fonte</sub></p>

<p align="center">
  <a href="docs/media/launch/biblioteca-desktop.png"><img src="docs/media/launch/biblioteca-desktop.png" alt="Biblioteca do VadeMecum MD em desktop" width="32%"></a>
  <a href="docs/media/launch/leitor-desktop.png"><img src="docs/media/launch/leitor-desktop.png" alt="Leitor com o art. 5º da Lei nº 14.133/2021 em desktop" width="32%"></a>
  <a href="docs/media/launch/grafo-desktop.png"><img src="docs/media/launch/grafo-desktop.png" alt="Grafo de citações em desktop" width="32%"></a>
</p>

<p align="center"><sub>Biblioteca · Leitor · Grafo — desktop</sub></p>

<p align="center">
  <a href="docs/media/launch/biblioteca-mobile.png"><img src="docs/media/launch/biblioteca-mobile.png" alt="Biblioteca do VadeMecum MD em celular" width="16%"></a>
  <a href="docs/media/launch/leitor-mobile.png"><img src="docs/media/launch/leitor-mobile.png" alt="Leitor do VadeMecum MD em celular" width="16%"></a>
  <a href="docs/media/launch/grafo-mobile.png"><img src="docs/media/launch/grafo-mobile.png" alt="Grafo de citações em celular" width="16%"></a>
</p>

<p align="center"><sub>Biblioteca · Leitor · Grafo — celular</sub></p>

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
