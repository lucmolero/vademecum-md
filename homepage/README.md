# Homepage VadeMecum MD

Homepage estática em React, Vite, Tailwind CSS e Motion. O Vite usa caminhos relativos para suportar tanto domínio próprio quanto repositórios de projeto no GitHub Pages (`/<nome-do-repositório>/`).

## Executar localmente

```sh
npm ci
npm ci --prefix ../biblioteca
npm run build --prefix ../biblioteca
npm run dev
```

## Build de produção

```sh
npm run build
npm run preview
```

O conteúdo pronto para hospedagem fica em `dist/`.

O build executa a checagem TypeScript estrita antes de gerar os arquivos. Para verificar separadamente, use `npm run typecheck`; os testes de navegador ficam em `npm run test:e2e` e requerem o build da Biblioteca com o corpus oficial.

```sh
npm run test:graph
npx playwright install chromium webkit
npm run test:e2e
```

Os testes cobrem arraste e setas do grafo, busca, pausa de renderização, recuperação de WebGL, os nove previews, navegação, acessibilidade e o leitor em desktop e mobile. `npm run preview` também serve a Biblioteca já compilada na mesma origem; a publicação final adiciona as páginas documentais e os downloads.

A suíte executa as jornadas de interface em Chromium e WebKit. Os testes completos
de gestos e recuperação do grafo usam Chromium, incluindo seu protocolo nativo
de toque. Para executar apenas um projeto, acrescente `-- --project=chromium`
ou `-- --project=webkit` a `npm run test:e2e`. A emulação não substitui a
homologação em aparelhos físicos.

## Organização

- `src/components/`: seções da página e integração com a Biblioteca.
- `src/components/orbit.tsx`: composição e interação dos cartões de recursos.
- `src/components/vignettes.tsx`: carregamento, confirmação de prontidão e recuperação dos previews reais.
- `public/graph/`: pacote oficial do grafo, com proveniência e licenças.
- `tests/`: testes da lógica do grafo e jornadas de navegador.

Os nove previews são preparados quando a seção se aproxima da tela e permanecem montados para preservar as interações. O grafo pausa sua renderização quando está oculto. As animações respeitam a preferência de movimento reduzido do sistema.

O hero carrega o mesmo pacote local de grafo em desenvolvimento e produção, sem depender de outro servidor. Para editar o aplicativo do grafo em um checkout separado, defina `VITE_GRAPH_URL=http://127.0.0.1:8770/viewer/?home-hero=1` antes de iniciar o Vite. Os previews da Biblioteca também usam os estilos locais deste checkout.

## Instalar a skill e acessar o corpus

O hero oferece uma instrução copiável para Codex, Claude Code, Cursor ou OpenCode. O agente pode baixar o kit completo, validar SHA-256, instalar a skill no escopo de projeto ou pessoal e posicionar a release correspondente do corpus. O ZIP e o manifesto de download são gerados por `../tools/package_skill_kit.py` a partir do manifesto e dos arquivos canônicos.

O kit também pode ser baixado sem terminal e aberto como workspace. Ele não exige Node.js ou `npx`. O CLI `npx skills` permanece disponível como alternativa para instalar somente as instruções da skill; nesse caso, o corpus deve ser fornecido em separado.

Para gerar o pacote durante o desenvolvimento ou publicação, execute na raiz do repositório:

```sh
python tools/package_skill_kit.py
```

## Publicação no Vademecum MD

Esta homepage é compilada pelo workflow único de Pages do repositório. O mesmo build gera a biblioteca em `/biblioteca/` a partir do corpus Markdown oficial e do manifesto da release. Não há uma publicação independente da homepage nem uma versão de interface separada do acervo.

Os assets gerados usam URLs relativas, então o site funciona na raiz de projeto do GitHub Pages sem configuração específica do nome do repositório.

## Créditos

Os componentes de animação adaptados do Animate UI são distribuídos sob MIT + Commons Clause; consulte `public/ANIMATE-UI-LICENSE.md`. A família Outfit é licenciada sob SIL Open Font License; consulte `public/assets/OFL-Outfit.txt`.
