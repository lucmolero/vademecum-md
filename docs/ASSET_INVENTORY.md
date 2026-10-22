# Inventário de ativos visuais

Este registro distingue proveniência técnica, escopo da licença do projeto e dependências de terceiros. O `LICENSE.md` cobre sob MIT o código e os ativos autorais de marca e design do projeto; textos normativos oficiais e materiais de terceiros estão excluídos.

## Ativos do projeto

| Arquivo | Uso | Origem rastreável | Chamadas externas no arquivo | Estado de licença |
| --- | --- | --- | --- | --- |
| `site_docs/assets/brand-mark.svg` | Favicon e marca compacta | SVG versionado desde `aefec1c` | Nenhuma | MIT, como ativo de marca/design autoral do projeto; titular indicado no `LICENSE.md`. |
| `site_docs/assets/logo-lockup.svg` | Lockup para fundo claro e README | SVG versionado desde `aefec1c` | Nenhuma; lettering usa Georgia instalada no cliente | MIT para o vetor autoral. Georgia é apenas uma fonte instalada no cliente; não está incorporada no SVG. |
| `site_docs/assets/logo-lockup-dark.svg` | Lockup para fundo escuro e hero | Variação local derivada do lockup claro nesta revisão | Nenhuma | MIT para a variação autoral do ativo do projeto. |
| `site_docs/assets/og-card.svg` | Cartão social SVG de referência | SVG versionado desde `aefec1c` | Nenhuma | MIT para o SVG autoral do projeto. |
| `site_docs/assets/release-cover.svg` | Capa estática de release | SVG versionado desde `aefec1c` | Nenhuma | MIT para o SVG autoral do projeto. |
| `site/assets/images/social/**/*.png` | Open Graph e Twitter para páginas-chave | Gerados no CI por Material for MkDocs a partir dos metadados locais | O gerador baixa **Source Serif 4** do Google Fonts durante o build se a fonte não estiver no cache; não é servida como fonte do site | Artefato derivado. Registrar versão/configuração do gerador e revisar a licença da fonte do build se houver redistribuição da família tipográfica. |

Os quatro SVGs originais foram introduzidos em `aefec1c` (2026-10-21), commit atribuido no Git a Luciano Molero. A licença MIT cobre esses ativos como parte do projeto; o histórico registra proveniência, não constitui prova externa independente de titularidade. Os arquivos não contêm fontes, imagens ou chamadas externas incorporadas.

## Estudos conceituais

Os SVGs em `docs/brand-directions/` são estudos conceituais autorais cobertos pela MIT. São estudos, não identidade final aprovada; não substituem os ativos em `site_docs/assets`.

## Dependências visuais externas

- O README carrega badges de status de `img.shields.io`; os badges são decorativos e têm texto alternativo. A falha do serviço não deve esconder a navegação para leitor, índice ou arquivos Markdown.
- O site usa `font: false` e pilhas locais de sistema. Não carrega Google Fonts no navegador.
- O plugin social está configurado com `Source Serif 4`, obtida de Google Fonts no **build** quando necessário. Isso é dependência de geração de cartões, não chamada de fonte em runtime. Cache, rede e integridade da fonte do build devem ser considerados na migração do CI.
- O grafo do hero é HTML/SVG gerado a partir do grafo normativo versionado; não há serviço de visualização, biblioteca ou endpoint externo.

## Gate antes de publicação promocional

1. Confirmar na revisão final da marca que o titular autoriza os lockups e o símbolo atuais para o uso pretendido.
2. Declarar explicitamente no `LICENSE.md` se os ativos de marca originais e derivados seguem MIT ou outra licença aprovada.
3. Guardar os fontes vetoriais e, se houver fonte baixada para os cartões, registrar versão e licença dela.
3. Atualizar este inventário quando um novo ativo, fonte, biblioteca de visualização ou serviço externo entrar no produto.

\n