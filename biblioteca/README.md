# Biblioteca de leis

Aplicativo estático para organizar e ler documentos Markdown, em português. Não precisa de servidor de aplicação: o build gera `dist/`, e o navegador guarda a biblioteca local. Não inclui conteúdo de demonstração.

## Desenvolvimento

Requer Node.js 22 ou posterior:

```sh
npm ci
npm test
npm run build
npm start
```

Abra http://127.0.0.1:4173. Os arquivos publicáveis são gerados em `dist/`.

## Build no Vademecum MD

O workflow único de Pages compila esta biblioteca em `/biblioteca/` e usa diretamente `bases/curated/legislacao/federal` e `manifests/release.json` do checkout atual. A homepage e a biblioteca recebem a mesma versão, contagem e data de corte do acervo. Não há checkout de uma branch externa da biblioteca nem publicação separada.

Quando `VADE_CORPUS_DIR` está definido, o build inclui apenas esse corpus oficial. Arquivos Markdown locais de teste não são copiados nem entram no catálogo. O manifesto `vademecum-source.json` registra a versão e o commit que alimentaram o leitor; histórico e dados brutos não são publicados.

> **Dados locais:** marcadores, anotações e progresso ficam no IndexedDB/localStorage do navegador de cada usuário — não são enviados a nenhum servidor.

Em ambientes que bloqueiam subprocessos (alguns sandboxes), `npm test` pode falhar com `spawn EPERM`; nesse caso rode os arquivos diretamente: `node tests/compiler.test.mjs` e `node tests/library-store.test.mjs`.

## Conteúdo

Coloque seus arquivos `.md` em `leis/`. Subpastas são reconhecidas. O acervo pode combinar esses documentos com o corpus curado do VadeMecum MD. Também é possível importar Markdown pelo botão de importação ou arrastando arquivos para a estante — os arquivos ficam salvos apenas neste navegador.

Cada arquivo é um documento. Títulos de primeiro e segundo nível separam capítulos. Os demais títulos aparecem no sumário. Metadados opcionais no início do arquivo:

```yaml
---
title: Nome do documento
author: Autor ou órgão
language: pt-BR
tags: [Federal, Tributário]
aliases: [sigla, nome alternativo]
number: 13.709
year: 2018
officialUrl: https://www.planalto.gov.br/...
sourceDate: 2018-08-14
legalStatus: Em vigor
---
```

O leitor oferece paginação em colunas, rolagem, sumário, busca no documento, marcadores, destaques, notas e ajustes de aparência. No cabeçalho, **Link** copia um endereço direto para a seção atual, **Citar** copia uma referência com link e **Fonte** mostra os metadados e o SHA-256 do Markdown incluído no build. Os campos de procedência são opcionais. A busca da estante ignora acentos e maiúsculas, procura também no texto das anotações e aceita siglas/números informados nos metadados. **Busca integral** pesquisa o texto de todos os documentos publicados e importados, com atalhos para abrir a seção encontrada.

O botão de disponibilidade offline registra um service worker e armazena o site e o acervo publicado no navegador. Os documentos importados já ficam disponíveis localmente no dispositivo em que foram importados.

A estante organiza documentos por estado de leitura, etiquetas e pastas, com ordenação por título, autor, última leitura, progresso ou data de importação. O progresso chega a 100% na última página; um documento de página única é considerado concluído ao ser aberto.

## Dados e backup

- IndexedDB (`biblioteca-library`): documentos importados e o estado da estante (registros, pastas e preferências).
- `localStorage`: aparência, posição de leitura, marcadores e anotações.
- O backup JSON inclui os Markdown importados, o estado da estante e os dados de leitura. Restaurar um backup mescla os dados existentes; as preferências de ordenação e o tamanho das capas também são restaurados. O tema e os ajustes tipográficos não fazem parte do backup.
- Remover um documento o oculta da estante; ele pode ser restaurado em Configurações ou voltar com um backup. Os arquivos de origem nunca são alterados.

## Estrutura

- `src/library.js`: estante, filtros, pastas, importação, diálogos, estatísticas e backup.
- `src/library-store.js`: persistência em IndexedDB e funções puras de busca, ordenação e normalização.
- `src/app.js`: integração entre estante e leitor; posição, marcadores, notas e aparência.
- `src/reader.js`: motor de leitura próprio, usando DOM e colunas CSS.
- `src/style.css` e `src/library.css`: interface do leitor e da estante.
- `scripts/build.mjs`: conversão de Markdown, sanitização e geração do catálogo.
- `tests/`: testes do compilador e das funções da biblioteca.
- `leis/`: seus documentos.

## Limitações conhecidas

- Markdown importado é renderizado com `html:false` e sem `sanitize-html` no navegador; HTML bruto é escapado, mas o build usa uma política de sanitização mais estrita.
- Um documento importado não guarda o caminho original, então imagens com caminho relativo no Markdown importado não são resolvidas.
- A busca no documento encontra o texto, mas não destaca todas as ocorrências na página.

## Dependências

Markdown-it, sanitize-html e gray-matter são usados para processar Markdown. Seus termos de licença permanecem com os pacotes. O código do projeto não recebe uma licença de redistribuição automática; a escolha de licença fica para o proprietário.
