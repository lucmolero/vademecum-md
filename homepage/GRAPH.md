# Grafo oficial da homepage

O pacote estático publicado junto à homepage fica em `homepage/public/graph/` e aparece no GitHub Pages em `/graph/`. O iframe do hero abre `/graph/viewer/` na mesma origem; assim, a homepage não depende do GitHub Pages do repositório privado do grafo.

## Origem e atualização

O projeto de origem continua separado no repositório `lucmolero/grafo-citacoes-mini`. O pacote oficial versionado aqui foi gerado a partir do commit registrado em `public/graph/source.json`, com:

```powershell
python src/mini_graph.py build
python src/mini_graph.py validate
python tools/package_pages.py
```

Copie o conteúdo gerado em `site/` para `homepage/public/graph/` ao atualizar o grafo. Preserve o `source.json`, atualizando commit e contagens a partir do relatório de build.

O pacote publicado contém somente os arquivos estáticos necessários ao viewer e seus dois índices compactados, não os snapshots brutos. O mapa identifica as citações acadêmicas como relações candidatas, sem confirmação em fonte oficial. O código do mini grafo é MIT; os avisos de licença das dependências e fontes estão incluídos junto aos respectivos arquivos.
