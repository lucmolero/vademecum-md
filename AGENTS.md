# Repositório `lucmolero/vademecum-md`

Este é o repositório oficial que contém o corpus e também as fontes da homepage e da Biblioteca/leitor. Homepage e Biblioteca são módulos irmãos deste mesmo repositório, publicados pelo workflow conjunto de GitHub Pages.

## Limites de escopo

- Homepage: `homepage/` — aplicação React/Vite; conteúdo e componentes em `homepage/src/`.
- Biblioteca e leitor oficiais: `biblioteca/` — aplicação publicada em `/biblioteca/`; código de interface em `biblioteca/src/`.
- Dados e proveniência: `bases/`, `manifests/` e diretórios documentais. Não confundir com o código da interface.
- `biblioteca-leis` é um aplicativo independente legado, com publicação e dados próprios; não é a fonte da Biblioteca oficial integrada neste repositório.
- O grafo interativo servido em `127.0.0.1:8770/viewer/` pertence a `grafo-citacoes-mini`, fora deste repositório.

## Procedimento

1. Confirme a raiz Git, remote, branch e estado local. Preserve arquivos modificados e não rastreados existentes.
2. Para UI da homepage, trabalhe em `homepage/`; para leitor, catálogo e previews oficiais, trabalhe em `biblioteca/`.
3. Alterações de publicação devem considerar o workflow Pages do repositório, que integra homepage e Biblioteca. Não assuma publicação independente da homepage.
4. Previews leves da Biblioteca devem usar os modos de demonstração de `biblioteca/src/preview-data.js`, sem carregar o corpus completo nem persistir estado demonstrativo. A referência visual publicada é `https://lucmolero.github.io/vademecum-md/biblioteca/`.
5. O Vite em `homepage/` tem porta padrão `8765`. A instância em `8771` é uma segunda execução do mesmo checkout com override de porta, não outro projeto.
6. Não publique, faça push ou altere dados versionados sem pedido explícito.
