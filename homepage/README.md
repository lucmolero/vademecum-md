# Vademecum homepage

Homepage estática em React, Vite, Tailwind CSS e Motion. O Vite usa caminhos relativos para suportar tanto domínio próprio quanto repositórios de projeto no GitHub Pages (`/<nome-do-repositório>/`).

## Executar localmente

```sh
npm ci
npm run dev
```

## Build de produção

```sh
npm run build
npm run preview
```

O conteúdo pronto para hospedagem fica em `dist/`.

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
