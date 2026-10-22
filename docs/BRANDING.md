# Sistema de marca — VadeMecum MD

> **Versão:** 2.3 · **Estado:** diretriz canônica para README, GitHub Pages e materiais de release.

## Marca

**VadeMecum MD**

Descritor: *Legislação federal brasileira estruturada para leitura humana,
validação auditável e uso por máquinas.*

## Direção visual

- ink `#13243A`: confiança e navegação;
- marfim `#FBF8F0`: leitura prolongada;
- dourado `#B48A3C`: camada editorial;
- verde `#2D7659`: evidência confirmada;
- âmbar `#A96D19`: atualização pendente;
- vermelho: reservado para erro ou conflito.

O sistema evita sugerir oficialidade governamental ou oferecer aconselhamento
jurídico. A marca usa livro aberto e estrutura de dados para representar a ponte
entre leitura jurídica e consumo por máquinas.

## Sistema editorial da interface

O site usa serifas para títulos e citações, sans-serif para navegação e
monoespaçada para IDs, hashes e evidências. A homepage apresenta a cadeia
fonte → normalização → auditoria → grafo → release como narrativa visual.

O movimento é deliberadamente discreto: revela conteúdo e reforça estados, mas
nunca é necessário para compreender uma norma. A política
`prefers-reduced-motion` remove animações decorativas e mantém a navegação
completa por teclado.

Os vetores em `site_docs/assets` são locais e não carregam fontes, imagens ou
rastreadores externos. A origem versionada, as dependências e as lacunas de
licenciamento estão registradas em [`docs/ASSET_INVENTORY.md`](ASSET_INVENTORY.md).
O `logo-lockup.svg` atende fundos claros e o
`logo-lockup-dark.svg` atende fundos escuros; o `brand-mark.svg` é reservado
para favicon e navegação compacta. Registrar autoria e licença de cada asset
antes de redistribuir materiais promocionais.

## Direção de marca para o rebranding

### Princípio de diferenciação

A marca deve representar a passagem de texto normativo a estrutura, evidência e acesso. O livro e o código são símbolos comuns; a distinção deve vir da rastreabilidade e da legibilidade, não de imitar órgão público, editora jurídica ou dashboard SaaS. Não usar brasão, selo, balança ou elementos que sugiram chancela estatal. O grafo do hero agora é um recorte real gerado de `bases/derived/relacoes/normative-graph.jsonl`: nós abrem os diplomas, setas preservam a direção registrada e a lista expansível expõe tipo e extremos da relação. A visualização declara ser apenas um recorte e oferece rotas para as fichas completas.

A promessa pública é: “Encontrar um diploma, verificar sua proveniência e reutilizar uma referência que identifica release e corte temporal.” Evitar autoelogios como premium, elite, revolucionário, impecável ou top tier. Não alegar cobertura universal, vigência garantida, aconselhamento ou ausência de alucinação.

### Tokens e contraste

Esta paleta é a fonte de verdade para README, SVG, CSS, Pages e capas. Não misturar a paleta Obsidian/Gold/Emerald dos planos antigos sem decisão registrada.

| Token | Valor atual | Regra de uso |
| --- | --- | --- |
| Ink | #13243A | Texto principal e navegação; definir par compatível em tema escuro |
| Ivory | #FBF8F0 | Fundo de leitura |
| Paper | #FFFDF8 | Superfície elevada |
| Gold | #B48A3C | Acento, filete ou ícone; contraste aproximado 2.98:1 sobre ivory, portanto evitar texto pequeno |
| Green | #2D7659 | Links/estado em fundo claro validado; não presumir contraste no escuro |
| Amber | #A96D19 | Cautela; contraste aproximado 4.05:1 sobre ivory, criar variante mais escura para texto normal |
| Red | #A23B3B | Erro/conflito; validar por tema |
| Slate | #38516D | Texto secundário claro; criar variante para tema escuro |
| Gold-soft | #E7D7AC | Superfície/acento, não texto sobre fundo claro |
| Dark ink | #0D1828 | Fundo base do tema escuro |
| Dark paper | #14253A | Superfície elevada no tema escuro |
| Dark text | #F5F0E6 | Texto principal do tema escuro e texto sobre navegação escura |
| Dark gold | #D7B96F | Acento no tema escuro |
| Dark green | #83CFA8 | Link/estado no tema escuro |
| Dark slate | #BAC6D2 | Texto secundário no tema escuro |
| Dark amber | #F3BD63 | Atualização pendente no tema escuro |
| Dark red | #FF9696 | Erro/conflito no tema escuro |

Os pares de texto e superfície abaixo são calculados em sRGB a partir dos tokens atuais e passam 4,5:1 para texto normal. Isso é uma verificação dos pares sólidos listados; não certifica combinações com opacidade, gradiente, imagem, borda, SVG, foco ou outro estado. Links não dependem apenas da cor. A inspeção dos componentes reais, estados, tema e tecnologia assistiva continua necessária. [WCAG 2.2, W3C](https://www.w3.org/TR/WCAG22/).

| Tema | Texto | Superfície | Contraste calculado | Uso |
| --- | --- | --- | ---: | --- |
| Claro | Ink `#13243A` | Ivory `#FBF8F0` | 14,75:1 | Texto principal |
| Claro | Ink `#13243A` | Paper `#FFFDF8` | 15,40:1 | Texto em superfície elevada |
| Claro | Slate `#38516D` | Ivory `#FBF8F0` | 7,71:1 | Texto secundário |
| Claro | Green `#2D7659` | Ivory `#FBF8F0` | 5,14:1 | Links e estados |
| Claro | Gold text `#8A641E` | Ivory `#FBF8F0` | 5,04:1 | Texto dourado |
| Claro | Amber text `#805915` | Ivory `#FBF8F0` | 5,89:1 | Cautela |
| Claro | Red `#A23B3B` | Ivory `#FBF8F0` | 6,14:1 | Erro ou conflito |
| Escuro | Dark text `#F5F0E6` | Dark ink `#0D1828` | 15,69:1 | Texto principal |
| Escuro | Dark text `#F5F0E6` | Dark paper `#14253A` | 13,64:1 | Texto em superfície elevada |
| Escuro | Dark slate `#BAC6D2` | Dark ink `#0D1828` | 10,26:1 | Texto secundário |
| Escuro | Dark green `#83CFA8` | Dark ink `#0D1828` | 9,72:1 | Links e estados |
| Escuro | Dark gold text `#E7D7AC` | Dark ink `#0D1828` | 12,49:1 | Texto dourado |
| Escuro | Dark amber `#F3BD63` | Dark ink `#0D1828` | 10,41:1 | Cautela |
| Escuro | Dark red `#FF9696` | Dark ink `#0D1828` | 8,53:1 | Erro ou conflito |

### Tipografia, leitura e assets

- Serif de sistema para texto normativo; sans-serif para interface; mono para IDs, hashes e datas técnicas.
- Declarar apenas fontes realmente carregadas ou como fallback. O CSS usa pilhas de fontes do sistema para texto, interface e dados técnicos; conferir a legibilidade nos ambientes-alvo.
- Referência de coluna: 65–78 caracteres; revisar zoom de 200% e reflow a 320 CSS px.
- Testar ordinais, romanos, pontuação, listas, nomes longos e hashes.
- O lockup SVG contém texto que pode mudar conforme fontes instaladas. Depois da escolha de direção, transformar o lettering aprovado em paths ou compor o nome em HTML/CSS com fallback consistente.
- Criar lockup horizontal, marca compacta, versões monocromáticas e para fundos claros/escuros; validar favicon em 16, 32 e 64 px.
- SVGs sem scripts, chamadas externas, IDs duplicados ou elementos remotos; alt conciso e sem redundância.
- README, favicon, homepage, Open Graph e capa de release devem usar a mesma identidade.

### Direção escolhida para a candidata

Em 2026-10-22, a direção **Índice normativo** foi escolhida como sistema principal da candidata por privilegiar localizar, ler e citar diplomas, que são as tarefas centrais do produto. **Registro de evidência** define a hierarquia de fonte, corte, hash e relações nos metadados. **Atlas de relações** fica como recurso funcional alimentado pelo grafo real, sem transformar o grafo na assinatura da marca nem sugerir interpretação jurídica. Os três estudos e a comparação estão em [`BRAND_DIRECTIONS.md`](BRAND_DIRECTIONS.md).

A candidata aplica essa hierarquia no README (índice Markdown e atalhos primeiro), na homepage (busca e catálogo em destaque), nas fichas (texto normativo como foco e proveniência como camada contextual), e nos ativos (símbolo editorial, paleta única e variações clara/escura). A seleção é uma decisão de produto para orientar a implementação, não evidência de preferência de usuários. Avaliação com advogados, pesquisadores e profissionais de tecnologia continua aberta; feedback pode ajustar a direção antes de seu anúncio como identidade final.

### Voz e gate de marca pronta

- Português brasileiro natural, preciso e direto; headings orientados a tarefas.
- Hash prova correspondência com conteúdo identificado segundo um processo, não correção jurídica.
- Preferir “Copiar texto e referência” a “Copiar para petição” se a saída não garantir adequação processual.
- Mensagens de erro informam falha e alternativa.

O rebranding só está pronto quando nome, recorte e natureza não oficial são entendidos sem contexto; busca/leitura dominam visualmente; paleta passa contraste nos dois temas; favicon, zoom e fallback tipográfico foram conferidos; animação não esconde conteúdo; claims têm evidência; assets têm origem/licença; README, Pages e capas são consistentes.

## Direções criativas para prototipagem

Estas propostas são territórios de exploração, não logos aprovados. Prototipar cada uma nos mesmos contextos antes da escolha final.

| Direção | Ideia visual | Assinatura possível | Risco a controlar |
| --- | --- | --- | --- |
| **Índice normativo** — recomendada para prototipar primeiro | publicação editorial com margem, numeração de dispositivos, filetes e referências precisas | monograma/página com eixo de índice e marcações que remetem a identificadores | pode parecer editora tradicional se faltar a camada de dados |
| **Registro de evidência** | estrutura técnica que organiza fonte, corte, hash e estado como metadados verificáveis | moldura modular inspirada em ficha de proveniência e checksum | pode ficar com aparência de dashboard ou reduzir a leitura a métricas |
| **Atlas de relações** | relações normativas como mapa navegável com direção e contexto | linha editorial que conecta dispositivos identificados, sempre baseada em relações publicadas | pode insinuar interpretação jurídica ou fazer o grafo decorativo parecer dado real |

Decisão da candidata: adotar **Índice normativo** como plataforma, usar **Registro de evidência** nos metadados e manter **Atlas de relações** como visualização funcional do grafo real. A decisão final de identidade pública deve considerar feedback e evidência de uso, além da avaliação editorial documentada.

Os estudos existentes cobrem uma mesma amostra e tarefa em painéis comparáveis. Antes do lançamento, verificar a direção escolhida em escala real no README renderizado pelo GitHub, favicon, homepage, catálogo, leitor, tema escuro, mobile e cartões sociais; avaliar clareza de escopo, distinção, associação não estatal, leitura, acessibilidade e custo de manutenção. Registrar feedback e eventuais ajustes sem tratar a recomendação interna como teste com usuários.

## Governança da marca

Este documento é a fonte única da identidade. Mudanças em tokens, logo, promessa ou tom atualizam CSS, assets, README, Pages e exemplos no mesmo PR. Mudanças visuais preservam texto canônico, IDs, rotas e status. Manter rationale, vetores, licença e relatório de contraste versionados.
