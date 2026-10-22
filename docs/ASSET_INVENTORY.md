# Inventário de ativos visuais

Este registro distingue origem técnica, licença e escopo de cada ativo. O `LICENSE.md` aplica MIT ao código e aos ativos de marca/design criados para o projeto. Textos normativos e dados de terceiros não passam a ser licenciados pelo MIT do projeto.

## Ativos de marca e publicação

| Arquivo | Uso / origem | Escopo de licença |
| --- | --- | --- |
| `site_docs/assets/brand-mark.svg` | Favicon e marca compacta; `aefec1c` | Vetor autoral do projeto, MIT. |
| `site_docs/assets/logo-lockup.svg` | Lockup claro e README; `aefec1c` | Vetor autoral do projeto, MIT. O lettering usa Georgia instalada no cliente; a fonte não está incorporada. |
| `site_docs/assets/logo-lockup-dark.svg` | Lockup para fundo escuro; `daa04ac` | Variação autoral local, MIT. |
| `site_docs/assets/og-card.svg` | Estudo estático de cartão social; `aefec1c` | Vetor autoral do projeto, MIT. |
| `site_docs/assets/release-cover.svg` | Capa estática de release; `daa04ac` | Vetor autoral do projeto, MIT. |
| `site_docs/assets/normative-graph-preview.svg` | Prévia de navegação no README; gerada por `tools/site/build_site.py` de `bases/derived/relacoes/normative-graph.jsonl` | O gerador e a estrutura vetorial são do projeto, MIT. Os nomes, IDs, relações e demais dados exibidos mantêm a licença e a proveniência das respectivas fontes; esta linha não relicencia o corpus. |
| `site/assets/images/social/**/*.png` | Cartões Open Graph/Twitter gerados no build pelo plugin social do Material for MkDocs | Artefatos raster gerados. A fonte Source Serif 4 usada no build é vendorizada separadamente sob SIL OFL 1.1; o arquivo de fonte não é incluído na publicação Pages. |

Os arquivos foram conferidos como SVGs locais, sem scripts, `foreignObject` ou chamadas/links externos. Lockups e cartões contêm texto SVG que usa fontes disponíveis; não há arquivo de fonte embutido. Histórico Git identifica quem registrou cada versão, mas não prova titularidade independente nem substitui a confirmação final de autoria/autorização pelo responsável do projeto.

Os três estudos em `docs/brand-directions/` (`01-indice-normativo.svg`, `02-registro-evidencia.svg`, `03-atlas-relacoes.svg`) são estudos conceituais criados para esta candidata e estão sob MIT. Não representam uma identidade pública aprovada; a direção final ainda depende da revisão e da avaliação formativa descritas no plano mestre.

## Fonte de terceiros para cartões sociais

- Família: **Source Serif 4**, versão **4.005R**, Adobe; reposit?rio `adobe-fonts/source-serif`, commit `2823e993c53fca27c5c8749f529b56a5a7c77b6b`.
- Licença: SIL Open Font License 1.1, copiada em `tools/site/fonts/source-serif-4/LICENSE.md`. O MIT do projeto não substitui nem relicencia essa fonte.
- O repositório inclui apenas os arquivos TTF Regular e Bold necessários aos cartões, com os nomes internos originais preservados. SHA-256: Regular `e5a4ee6a3d87bb9024796be390c6771e2a0eb1883dae25effaf57ca01668e24b`; Bold `7cf4f4e1ad74f45058d5bc61716b82560442fbdcd9d3654d2dea96bf6c683d86`.
- `tools/site/prepare_social_fonts.py` valida os hashes e semeia o cache do plugin antes de cada build social. O build não baixa a fonte da rede. A fonte serve somente para rasterizar os cartões; não é uma fonte de runtime nem vai para o artefato Pages.
- Se a fonte ou versão for trocada, atualizar os dois arquivos, a licença, os hashes e este inventário no mesmo PR. Não modificar a fonte nem reutilizar o nome reservado em derivados.

## Dependências externas visíveis

- O README usa badges de `img.shields.io`. São complementares; links para o leitor, índice, grafo e Markdown continuam acessíveis se o serviço de badges falhar.
- O site define `font: false` e usa pilhas locais de sistema no navegador. Não carrega Google Fonts como recurso de runtime.
- O plugin social do Material gera cartões estáticos no build e os hospeda junto com o Pages; a fonte local e versionada torna esse passo independente do Google Fonts.
- O grafo do hero é HTML/SVG estático derivado do JSONL versionado; não há API de visualização, biblioteca ou serviço externo em runtime.

## Gate de direitos e manutenção

1. O responsável do projeto confirma autoria ou autorização para o uso público dos lockups, símbolo, capas, estudos e variações; registrar a decisão e eventuais atribuições.
2. Manter a declaração MIT para código/marca autoral e manter a licença OFL 1.1 junto aos TTFs de terceiros. As normas e dados do corpus permanecem fora da concessão MIT.
3. Manter fontes vetoriais, arquivos de fonte e origem/hash junto da licença correspondente sempre que novos ativos forem adicionados.
4. Atualizar este inventário para qualquer novo ativo, família tipográfica, biblioteca de visualização ou serviço externo.
