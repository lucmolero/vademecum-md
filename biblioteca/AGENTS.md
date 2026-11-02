# Biblioteca e leitor oficiais

Este diretório contém a aplicação visual publicada em `https://lucmolero.github.io/vademecum-md/biblioteca/`. Não é o repositório de dados `lucmolero/biblioteca-leis`.

- Fontes da aplicação: `src/`; estilos da Biblioteca e do Leitor fazem parte desta aplicação oficial.
- A homepage irmã usa modos `?preview=...` com dados simulados pequenos definidos em `src/preview-data.js`; os modos não devem buscar o corpus integral, registrar service worker nem persistir as interações demonstrativas.
- Mantenha a navegação dos previews na mesma aba ao sair do iframe, direcionando à Biblioteca oficial e preservando consulta/documento quando aplicável.
- `biblioteca/dist/` é saída gerada. Não a trate como fonte editável; siga o workflow de build do repositório pai, que também precisa dos artefatos/manifests do corpus.
- Para mudança de aparência, confira a página publicada acima como referência e verifique light/dark e leitor quando relevantes.
