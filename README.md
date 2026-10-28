# VadeMecum MD

Legislação federal brasileira em Markdown, organizada para consulta, leitura e verificação de proveniência. Cada diploma tem identificador estável, metadados de curadoria, data de corte e fonte indicada.

[Leitor online](https://lucmolero.github.io/vademecum-md/) · [Catálogo](https://lucmolero.github.io/vademecum-md/generated/catalog/) · [Arquivos Markdown](bases/curated/legislacao/federal/) · [Release v1.1.2](https://github.com/lucmolero/vademecum-md/releases/tag/v1.1.2)

> **Snapshot público:** 375 diplomas · corte do corpus em 21/10/2026. O corte identifica a coleção publicada e não representa atualização em tempo real.

## Consultar uma lei

Use o [catálogo online](https://lucmolero.github.io/vademecum-md/generated/catalog/) para pesquisar e ler no navegador. Para consultar o texto canônico, abra o arquivo Markdown no repositório ou baixe a [release versionada](https://github.com/lucmolero/vademecum-md/releases/tag/v1.1.2).

| Diploma | Texto canônico |
| --- | --- |
| Constituição Federal de 1988 | [Markdown](bases/curated/legislacao/federal/constituicao/1988/constituicao-da-republica-federativa-do-brasil-1988.md) |
| Código Civil — Lei nº 10.406/2002 | [Markdown](bases/curated/legislacao/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002.md) |
| Código de Processo Civil — Lei nº 13.105/2015 | [Markdown](bases/curated/legislacao/federal/leis-ordinarias/2015/lei-ordinaria-13105-2015.md) |
| Código Penal — Decreto-Lei nº 2.848/1940 | [Markdown](bases/curated/legislacao/federal/decretos-lei/1940/decreto-lei-2848-1940.md) |
| Código de Processo Penal — Decreto-Lei nº 3.689/1941 | [Markdown](bases/curated/legislacao/federal/decretos-lei/1941/decreto-lei-3689-1941.md) |
| Consolidação das Leis do Trabalho — Decreto-Lei nº 5.452/1943 | [Markdown](bases/curated/legislacao/federal/decretos-lei/1943/decreto-lei-5452-1943.md) |

Para outros diplomas, navegue pelos diretórios de [legislação federal](bases/curated/legislacao/federal/) ou pelo catálogo.

## Para agentes de IA

A [skill de consulta jurídica](skills/vademecum-consulta-juridica/SKILL.md) orienta a localização de normas, a conferência de situação e corte, a separação entre texto, metadados e relações, e a produção de citações rastreáveis.

A skill não concede acesso automático ao repositório. Disponibilize ao agente os arquivos, a release ou uma ferramenta de leitura. Para cada resposta, preserve o ID do documento, o dispositivo, a release, o corte e a fonte oficial quando esses dados estiverem disponíveis.

## Citação e proveniência

Exemplo de referência rastreável:

```text
Código Civil, art. 1º
VadeMecum MD, release v1.1.2, corte 2026-10-21.
ID: br-federal-lei_ordinaria-10406-2002.
Fonte oficial: https://normas.leg.br/?urn=urn:lex:br:federal:lei:2002-01-10;10406
```

O Markdown canônico é a referência do conteúdo publicado neste repositório. O leitor web, o catálogo e o grafo são camadas derivadas para consulta e navegação; relações do grafo fornecem contexto e não substituem o texto legal.

## Escopo

O VadeMecum MD é uma seleção curada da legislação federal, não uma cobertura integral do Direito brasileiro nem uma publicação oficial ou aconselhamento jurídico. Situação e consolidação descrevem os metadados do documento no corte declarado. Confira a fonte oficial antes de citar ou aplicar uma norma.

O código e os materiais autorais de marca e design seguem a [Licença MIT](LICENSE.md). Textos normativos e materiais de terceiros permanecem sujeitos ao regime aplicável a cada fonte.

## Projeto

- [Como contribuir](CONTRIBUTING.md)
- [Política de segurança](SECURITY.md)
- [Histórico de versões](CHANGELOG.md)
- [Arquitetura](https://lucmolero.github.io/vademecum-md/architecture/)
- [Contrato de consumo](https://lucmolero.github.io/vademecum-md/contract/)
