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

## Publicação no Vademecum MD

Esta homepage é compilada pelo workflow único de Pages do repositório. O mesmo build gera a biblioteca em `/biblioteca/` a partir do corpus Markdown oficial e do manifesto da release. Não há uma publicação independente da homepage nem uma versão de interface separada do acervo.

Os assets gerados usam URLs relativas, então o site funciona na raiz de projeto do GitHub Pages sem configuração específica do nome do repositório.

## Créditos

Os componentes de animação adaptados do Animate UI são distribuídos sob MIT + Commons Clause; consulte `public/ANIMATE-UI-LICENSE.md`. A família Outfit é licenciada sob SIL Open Font License; consulte `public/assets/OFL-Outfit.txt`.
