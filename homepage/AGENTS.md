# Aplicação homepage

Este diretório é a homepage de `lucmolero/vademecum-md`, não um repositório independente. A Biblioteca/leitor oficiais ficam no diretório irmão `../biblioteca/`.

- Execute comandos npm a partir de `homepage/`.
- `npm run dev` usa `127.0.0.1:8765`; confirme processos antes de iniciar outra instância. `:8771` pode ser o mesmo Vite iniciado com `--port 8771`.
- Os cartões interativos de recursos são mini previews dos modos reais de `../biblioteca/`, isolados em iframes e alimentados por fixtures leves. Não substitua por screenshots ou por uma cópia da página inteira.
- Para navegação de saída dos previews, encaminhe ao destino oficial da Biblioteca na mesma aba; não abra outra aba.
- O hero usa `127.0.0.1:8770/viewer/` em desenvolvimento e o pacote estático oficial em `public/graph/` na mesma origem em produção. A origem do pacote e o commit sincronizado ficam em `public/graph/source.json`; preserve a proveniência e os avisos de licença ao atualizar.
- O build/publicação final da homepage está integrado ao workflow Pages do repositório pai. Considere a compatibilidade dos módulos `../biblioteca/` e `public/graph/` antes de modificar URLs.
