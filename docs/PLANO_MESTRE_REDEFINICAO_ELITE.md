# Plano mestre de rebranding e refinamento — VadeMecum MD

> **Versão:** 10 · **Atualizado:** 2026-10-22
>
>
> **Estado:** plano de execução e auditoria de lançamento. O painel abaixo resume a candidata no workspace; a aprovação final exige fechar os gates externos listados.

## Painel de prontidão para lançamento

**Decisão atual: NO-GO para publicação.** A candidata local está tecnicamente consistente nos gates automatizados, mas a versão hospedada ainda não contém as mudanças e faltam evidências humanas e operacionais que não podem ser inferidas do build.

| Frente | Situação verificada | Evidência de saída |
| --- | --- | --- |
| Corpus e proveniência | Candidato passa: 375 documentos; auditoria estrita de fidelidade `pass: 375`; release com 33/33 gates P0 em revalidações anteriores | `tools/audit_fidelity.py --strict`; `tools/validate_release.py --stabilization`; revalidar no commit candidato |
| README e descoberta | README local foi simplificado como índice sem emojis; homepage local prioriza busca, catálogo e seis leis | Testes de contrato na suíte; revisar render real do GitHub após integração |
| Site e grafo | Build estrito aprovado; 396 páginas e zero erros; grafo gerado de relações canônicas e nós abrem diplomas | `mkdocs build --strict`; `tools/validate/validate_site.py`; teste visual atual ainda pendente |
| Leitor e acessibilidade | Fonte padrão do leitor 14 px, faixa 13–16 px e sidebars mantidas; contratos automatizados passam | Testes de leitor e navegação; inspeção de teclado, leitor de tela, zoom, foco e contraste em browser ainda pendente |
| Identidade e ativos | Direção “Índice normativo” aplicada; escolha do usuário documentada como MIT para código e marca | Revisão de titularidade/proveniência, aplicação final em favicon e avaliação com públicos ainda pendentes |
| Desempenho e dispositivos | Site estático e índices sob demanda; não há medição atual de bytes transferidos/Core Web Vitals na produção após o redesign | Definir orçamento após baseline em desktop e celular com cache/rede registrados |
| Rotas e recuperação | Links internos do candidato validados; não há prova de rollback do deploy candidato | Comparar mapa de URLs publicado/candidato, testar navegação direta e ensaiar rollback antes da publicação |
| Produção e integração | Em 2026-10-22 a homepage e `/graph/` respondiam HTTP 200, mas não continham o hero novo nem `data-graph-explorer`; seis PRs do Dependabot seguem abertos | PR candidato, checks obrigatórios verdes, decisão explícita sobre PRs de dependência e smoke test pós-deploy |

### Sequência bloqueante de lançamento

1. Abrir revisão do candidato e aguardar os checks obrigatórios no GitHub.
2. Revisar o README renderizado e o Pages em desktop/celular, temas claro/escuro, zoom e estados de interação; executar teste moderado com pelo menos um advogado, um pesquisador e uma pessoa de tecnologia, registrando tarefas, falhas e decisões sem inventar feedback.
3. Resolver titularidade/licenças de cada asset e validar a amostra jurídica e seus metadados contra a fonte e o corte que serão publicados.
4. Medir desempenho e acessibilidade no preview; definir e cumprir os budgets antes da aprovação.
5. Conferir compatibilidade de URLs e artefatos, ensaiar rollback e publicar somente o artefato aprovado pelo fluxo protegido.
6. Após deploy, repetir smoke test público de homepage, grafo, busca, documento, arquivos Markdown e release; guardar evidência datada e registrar decisão GO/NO-GO.

### Protocolo mínimo de avaliação formativa

Executar cinco sessões individuais de 20–30 minutos: ao menos duas com advogados, uma com pesquisador(a) jurídico(a) e uma com profissional de tecnologia; a quinta amplia o perfil que revelar maior dificuldade. Usar build de preview, desktop e celular, com cenário e roteiro iguais. Não pedir parecer jurídico nem coletar casos reais, dados de clientes ou informação sensível.

1. No README, localizar e abrir o Markdown canônico da Lei 13.964/2019.
2. No site, localizar o art. 121 do Código Penal; apontar o ID, o corte temporal e a fonte oficial exibidos.
3. No grafo, seguir uma relação para outro diploma e explicar com as próprias palavras o que a visualização permite concluir e o que não permite.
4. No leitor, ajustar a fonte, navegar para um artigo usando teclado e copiar a referência completa.
5. Repetir uma tarefa em tela estreita e informar onde esperava encontrar a ação principal.

Registrar por tarefa: conclusão sem ajuda/ com ajuda/ falha, tempo, caminho tomado, erro observado, literal comentário consentido e prioridade. Não guardar nomes ou áudio por padrão. Critério formativo para avançar: ao menos 80% de conclusão sem ajuda nas tarefas; 100% dos participantes identificam a fonte/corte sem confundir a interface com publicação oficial; nenhuma barreira crítica de teclado, foco ou reflow; falhas restantes têm correção, responsável e decisão documentados. A amostra é qualitativa e não prova representatividade nem conformidade WCAG.

**Regra:** checks automatizados verdes autorizam revisão do candidato, mas não substituem as avaliações humanas, a comprovação de direitos, o teste operacional nem a verificação pós-deploy. Até que todos os itens bloqueantes tenham evidência, manter NO-GO.

## 1. Direção executiva

O diferencial do produto é a cadeia verificável entre **texto normativo, identidade estável, fonte, situação, corte temporal, hash e relações**. Marca e interface devem tornar essa cadeia fácil de entender e usar.

**Posicionamento:** VadeMecum MD — legislação federal brasileira estruturada para leitura, auditoria e uso por máquinas.

**Promessa:** encontrar um diploma, conferir sua proveniência e obter uma referência reproduzível sabendo qual release e corte temporal está sendo consultado.

Princípios:

1. Evidência antes de efeito visual: todo total, estado de validação ou alegação de cobertura tem fonte e data.
2. A interface não é autoridade legal: mostrar fonte oficial, proveniência local e corte junto ao texto.
3. Uma fonte canônica: README, site e badges derivam de manifests/artefatos ou são identificados como exemplos.
4. Interação progressiva: README orienta; o leitor web oferece busca e ferramentas. Não prometer no README comportamento que ele não executa.
5. Acessível sem movimento ou mouse: teclado, foco, contraste, redução de movimento e telas estreitas.
6. Priorizar confiabilidade, navegação e atualização antes de animações.

## 2. Auditoria do README atual

O README contém logo clicável, seis badges, quatro CTAs, tabela comparativa, cinco acordeões `<details>`, blocos de citação, links para leitor e Markdown canônico, Skill, tabela de dez diplomas, sete âncoras de ramos e links de governança.

| Elemento | Comportamento atual | Recomendação |
| --- | --- | --- |
| Logo e 4 CTAs | Navegam para site, release, Skill e catálogo | Manter 2–3 ações principais; confirmar rotas e release |
| 6 badges | Imagens clicáveis com texto/status embutidos na URL | Gerar de fonte versionada ou remover números/status frágeis |
| Tabela comparativa | Faz afirmações sobre portais públicos, paywalls e produto | Trocar por capacidades verificáveis; remover juízos sem evidência |
| 5 acordeões de diplomas | Expande amostras, citações e links | Rotular como trechos demonstrativos; validar texto e corte contra fonte canônica |
| Blocos `text` | Texto selecionável/copiar via recursos do navegador/GitHub | Chamar “modelo para copiar”, não botão de cópia do projeto |
| Links “Abrir diploma” | Levam ao leitor web | Verificar alvos e disponibilizar Markdown canônico quando útil |
| Prompt da Skill | Requer seleção manual e duplica instrução | Evitar cópia de instrução volátil; linkar artefato versionado |
| Tabela dos 10 códigos | Contém páginas web e arquivos locais | Gerar do catálogo/manifests; incluir fonte oficial quando disponível |
| 7 ramos | Links para âncoras do catálogo | Confirmar âncoras e derivar totais; chamar de classificação editorial |
| Governança | Links locais para contribuição, segurança e changelog | Manter numa área final breve |
| TOC automática do GitHub | Criada pelos headings | Manter hierarquia concisa; evitar duplicação sem necessidade |

### Limites da interação

- `<details><summary>` expande/recolhe conteúdo; é adequado para amostras.
- O README hospedado no GitHub não executa JavaScript próprio. Pesquisa dinâmica, `Ctrl/Cmd+K`, controles de fonte, modo foco e botão personalizado de cópia pertencem ao site.
- Selecionar/copiar um bloco usando recursos do cliente GitHub não equivale a um botão fornecido pelo projeto.
- Não depender de CSS/scripts embutidos para conteúdo essencial.
- O README deve orientar e demonstrar; texto integral e consulta em escala ficam no leitor e nos arquivos canônicos.

### Referência fornecida

A página [GitHub Topics: interactive-readme](https://github.com/topics/interactive-readme) é uma lista explorável de repositórios etiquetados. Na consulta de 2026-10-22 indicava sete resultados, muitos READMEs de perfil, cartões dinâmicos ou experimentos visuais. Serve como inspiração de formatos, não como benchmark validado de produtos jurídicos, acessibilidade ou confiabilidade. Não copiar contadores ou GIFs sem relação com as tarefas do produto.

## 3. Identidade

- **Nome:** VadeMecum MD.
- **Descritor:** Legislação federal brasileira estruturada para leitura, auditoria e uso por máquinas.
- **Tom:** preciso, editorial, sereno e transparente sobre limites.
- **Evitar:** “oficial”, “sem alucinações”, “100% vigente”, comparações depreciativas ou liderança sem medição.
- **Preferir:** texto canônico, fonte oficial, corte temporal, proveniência, release, validação e exemplo editorial.

Consolidar o sistema existente em `docs/BRANDING.md` (ink, marfim, dourado, verde, âmbar e erro). A proposta Obsidian/Gold/Emerald do plano anterior não deve criar uma paleta concorrente. Manter o símbolo de livro/estrutura sem sugerir chancela estatal. Usar serifas para leitura, sans-serif para navegação e mono para IDs/hashes. Comunicar estados por texto além da cor. Preferir SVG local e reduzir dependências remotas.

## 4. Arquitetura da experiência

### README — página de entrada

Ordem proposta:

1. Marca, frase de valor e release/corte atual.
2. Ações: **Abrir leitor**, **Explorar o corpus**, **Baixar release**.
3. O que é e para quem serve.
4. Fatos verificáveis e datados.
5. Como localizar diploma, abrir Markdown e baixar dados.
6. Até 3–5 amostras compactas em acordeões.
7. Consumo de dados e Skill, com exemplo curto/versionado.
8. Método, autoridade e limites.
9. Contribuição, segurança, licença, changelog e fontes.

### Leitor web

- Homepage orientada a tarefas: pesquisar, explorar catálogo e entender proveniência.
- Busca por diploma, número, ano e ID; declarar campos indexados e tratar erros/vazios claramente.
- Página do diploma com título, situação sustentada, fonte oficial, corte, release, hash e Markdown canônico.
- Leitura longa com âncoras estáveis, sumário, foco, tamanho de texto, cópia do dispositivo e retorno ao topo.
- Cópia inclui identificação, release, corte e fonte; feedback é anunciado por leitor de tela.
- Grafo mostra direção, tipo e evidência da relação; não inferir efeito jurídico automaticamente.
- Preservar acesso essencial quando JavaScript ou serviço de busca falhar.

## 5. Fases e critérios de aceite

### Fase 0 — Integridade editorial (P0)

- Conferir totais, relações, status, corte e release com manifests.
- Validar os cinco trechos legais contra os arquivos canônicos.
- Revisar todos os links, âncoras, badges, ZIP e rotas publicadas.
- Remover claims de oficialidade, vigência e comparação sem fonte.

**Aceite:** cada número/estado tem fonte e corte; trechos correspondem à fonte escolhida; ações levam ao destino prometido; limites são visíveis.

### Fase 1 — README confiável (P0)

- Reordenar pela jornada acima e eliminar texto repetido.
- Reduzir badges e acordeões; marcar trechos como demonstrativos.
- Não chamar bloco selecionável de botão de cópia.
- Garantir que release, site e Skill se referem à versão publicada.

**Aceite:** visitante entende em 10 segundos o que é, qual escopo/corte e onde começar; GitHub mobile/desktop renderizam bem; nenhuma promessa descreve função inexistente.

### Fase 2 — Fonte única e automação (P0/P1)

- Gerar catálogo e contagens de manifests.
- Gerar/validar badges no CI ou removê-los se a origem não for estável.
- Verificar links locais, âncoras e rotas publicadas.
- Sinalizar divergência entre README, release e catálogo antes da publicação.
- Manter revisão humana de texto e afirmações jurídicas: automação mede estrutura, não decide validade jurídica.

**Aceite:** números públicos não são mantidos manualmente em vários lugares; dados e links obsoletos falham de modo visível.

### Fase 3 — Leitor orientado a tarefas (P1)

- Mapear busca, leitor, cópia, atalhos, foco e grafo atuais antes do redesign.
- Priorizar catálogo e página do diploma; preservar URLs/IDs.
- Implementar apenas controles que resolvem tarefas observáveis.
- Mostrar fonte e corte perto do texto e na saída copiada.

**Aceite:** localizar, conferir e copiar funciona por teclado e toque; busca informa seu escopo; falha de índice não parece ausência de norma.

### Fase 4 — Dados e agentes (P1/P2)

- Versionar Skill e validar compatibilidade real; não listar modelos sem teste atual.
- Oferecer exemplos mínimos reproduzíveis para Markdown/JSON/CSV e IDs.
- Avaliar citação, recusa fora de escopo, status ambíguo e fonte conflitante.

**Aceite:** exemplos usam IDs reais; avaliações cobrem citação e recusa; formatos têm versão e documentação.

### Fase 5 — Refinamento visual e distribuição (P2)

- Aplicar o sistema de marca consolidado ao README e site.
- Criar diagramas locais leves somente quando explicarem fluxos.
- Atualizar tópicos e descrição do GitHub para descoberta relevante.
- Medir saúde de links, sucesso de tarefa, acessibilidade e consumo de artefatos.

**Aceite:** consistência visual não reduz legibilidade; dependências são conhecidas; melhorias atendem a tarefas observáveis.

## 6. Priorização

| Prioridade | Entregas |
| --- | --- |
| P0 — confiança | Fonte/corte/versão, transcrições, contagens, claims, links, autoridade e limites |
| P1 — uso | README direto, catálogo gerado, leitor e cópia acessíveis, busca com escopo |
| P2 — diferenciação | refinamento visual, movimento discreto, diagramas e descoberta avançada |
| Fora do escopo sem evidência | botão customizado dentro do README, garantia contra alucinações, cobertura universal, “luxo” como métrica |

## 7. Métricas

Criar baseline antes de fixar metas: cliques no leitor/catálogo/release/Skill sem rastreamento invasivo; sucesso e tempo para localizar/verificar/copiar; links válidos e divergências por release; navegação por teclado, foco, contraste, zoom e movimento reduzido; exemplos reproduzíveis; defeitos de texto, status e proveniência. Estrelas e visitas não medem, por si sós, qualidade documental.

## 8. Riscos e controles

| Risco | Controle |
| --- | --- |
| Amostra desatualizada | Comparar com fonte canônica versionada e mostrar corte/fonte |
| Badge obsoleto | Gerar de artefato verificável ou retirar o número |
| Aparência de publicação estatal | Identidade não estatal, aviso e link para fonte oficial |
| Cópia sem contexto | Incluir ID, release, corte e fonte; não chamar de peça pronta |
| Busca incompleta | Rotular campos indexados e oferecer catálogo/arquivos |
| Redesign quebra links | Preservar URLs/IDs ou criar redirecionamentos |
| Serviço externo indisponível | Manter arquivos canônicos e release acessíveis |

## 9. Checklist pré-publicação

- [ ] Nome, descritor e escopo são claros sem contexto.
- [ ] Release e corte correspondem ao artefato publicado.
- [ ] Números e badges têm fonte rastreável.
- [ ] Trechos e citações foram comparados com a fonte escolhida.
- [ ] README separa demonstração de diploma integral.
- [ ] Links, âncoras, downloads, imagens e Skill funcionam.
- [ ] Teclado, leitor de tela, zoom, mobile e redução de movimento foram considerados.
- [ ] Autoridade da fonte oficial e limites estão visíveis.
- [ ] Site indisponível não elimina acesso aos arquivos/release.
- [ ] Markdown renderizado no GitHub foi revisado.

## 10. Referências e decisões

- Auditoria local: `README.md`, `docs/BRANDING.md`, `docs/PRODUCT_SPEC.md`, `docs/ROADMAP.md`, `docs/ACCESSIBILITY.md`, `mkdocs.yml` (2026-10-22).
- GitHub Docs: [seções recolhíveis](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections) descreve `<details>`/`<summary>`.
- GitHub Docs: [sintaxe de escrita e formatação](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
- Inspiração exploratória: [tópico interactive-readme](https://github.com/topics/interactive-readme), não evidência de qualidade.
- README é porta de entrada; site contém as interações de busca/leitura.
- Consolidar `docs/BRANDING.md` como base visual.
- Proveniência, acessibilidade e atualização governada são diferenciais centrais.
- Nenhum número ou promessa é permanente sem fonte, escopo e data.

---

## 11. Plano integral de reconstrução do GitHub Pages

Esta seção amplia o plano para a experiência web completa. A implementação atual usa MkDocs Material, geração customizada em `tools/site/build_site.py`, conteúdo editorial em `site_docs/`, JavaScript em `site_docs/javascripts/` e estilos em `site_docs/stylesheets/`. A reconstrução deve começar pelo inventário e pelos contratos existentes, preservando o pipeline de conteúdo canônico; não implica trocar de framework por padrão.

### 11.1 Visão do produto web

O GitHub Pages será uma aplicação editorial estática para **localizar, ler, verificar e reutilizar** diplomas do corpus. Deve servir leitores ocasionais, profissionais jurídicos, pesquisadores, desenvolvedores de dados e construtores de agentes, sem misturar as necessidades desses públicos numa única interface.

**Resultado principal da experiência:** a pessoa consegue chegar de uma pergunta ou identificador ao texto relevante, entender a proveniência e sair com uma referência reproduzível.

**Não objetivos da interface:** determinar vigência sem evidência, interpretar caso concreto, substituir a publicação oficial, declarar cobertura universal, transformar busca textual em aconselhamento ou exigir conta/login.

### 11.2 Públicos, tarefas e jornadas

| Público | Jornada prioritária | Evidência de sucesso |
| --- | --- | --- |
| Leitor ocasional | buscar nome/número → abrir diploma → ler artigo | chega ao texto correto e percebe o escopo/corte |
| Advogado/pesquisador | localizar dispositivo → conferir fonte/status → copiar referência | citação inclui diploma, dispositivo, release/corte e links de origem |
| Pesquisador de corpus | filtrar/baixar catálogo → inspecionar metadados e cobertura | consegue reproduzir o conjunto e distinguir lacunas/estados |
| Desenvolvedor | entender schema → obter Markdown/JSON/CSV → consumir ID/hash | exemplo executável e contrato versionado |
| Construtor de agentes | ler Skill/contrato → testar recuperação e recusa | resposta rastreia IDs e sabe recusar fora do escopo |
| Contribuidor | entender padrão e fluxo → preparar alteração | encontra processo, revisão necessária e comandos corretos |

As jornadas devem ser testadas como tarefas curtas em protótipos. Não usar “usuário premium” ou persona genérica como substituto de tarefa observável.

### 11.3 Arquitetura de informação e mapa do site

Proposta de navegação principal, com rótulos orientados ao destino:

```text
Início
Explorar
  Catálogo de diplomas
  Ramos editoriais
  Busca
Método e confiança
  Como o corpus é montado
  Fontes e proveniência
  Qualidade e auditorias
  Grafo de relações
Dados e integração
  Formatos e schema
  Exemplos
  Skills para agentes
Projeto
  Atualizações
  Contribuir
  Segurança
  Limites jurídicos
```

O item **Explorar** deve ser o caminho dominante para o conteúdo. A navegação global fica curta; detalhes de metodologia e governança vivem em páginas secundárias. Páginas de diploma permanecem endereçáveis diretamente e não dependem de passar pela homepage.

#### Modelos de página

1. **Início:** proposta de valor, busca principal, caminhos por tarefa, um exemplo de diploma, indicadores de escopo com corte, atalhos para método/dados e aviso de autoridade.
2. **Explorador/catálogo:** busca, filtros explícitos, contagem resultante, estado de filtro na URL, ordenação previsível, paginação ou carregamento progressivo com acessibilidade.
3. **Página de diploma:** cabeçalho factual, metadados essenciais, fonte oficial, controles de leitura, sumário de dispositivos, texto, relações documentadas, histórico se disponível, arquivos alternativos e limites.
4. **Busca:** resultados com título, número, ano, status editorial, trecho contextual, ID e indicação do campo que correspondeu; estado vazio com consultas alternativas.
5. **Ramo editorial:** escopo do agrupamento, critério de classificação, diplomas que o compõem e data do catálogo; sem apresentá-lo como taxonomia jurídica oficial.
6. **Grafo:** explicação de semântica, filtros e representação acessível das mesmas relações em lista/tabela.
7. **Qualidade/proveniência:** métricas, método, manifestos de origem e distinção entre validação estrutural e revisão jurídica.
8. **Dados e Skill:** formatos, schema, versões, exemplos e contratos de consumo.
9. **Atualizações:** releases/cortes e mudanças em comparação, sem sugerir monitoramento em tempo real quando não existir.
10. **Erro/ausência:** página 404 útil, busca, catálogo e retorno à última rota válida.

### 11.4 Requisitos funcionais do leitor

#### Busca global

- P0: nome/título, número do diploma, ano, tipo, ID canônico e termos presentes em título/metadados.
- P1: texto integral dos diplomas, número de artigo e frases exatas; declarar escopo do índice e data em que foi gerado.
- P2: operadores avançados, combinações, filtros salvos pela URL e sugestões mais ricas, somente com índice confiável.
- Normalizar espaços, caixa, acentos e pontuação sem alterar o dado mostrado; suportar algarismos romanos e ordinais como consultas comuns.
- Usar debounce e limite de resultados. Não atrasar a interação com animações ou carregar grande índice na homepage.
- Não tratar erro de carregamento, diploma não indexado ou filtro incompatível como resultado “sem norma”. Diferenciar estados.
- Cada resultado deve abrir uma rota estável e, se conhecido, um fragmento do dispositivo.

#### Catálogo e filtros

- Filtros visíveis e combináveis: categoria/tipo, período, estado editorial/publicação e agrupamento disponível no dado.
- Não oferecer filtro “em vigor” como verdade se esse dado não tiver política de atualização comprovada.
- Mostrar número total de correspondências, critérios ativos e botão claro para limpar filtros.
- Guardar estado em query parameters quando a combinação puder ser compartilhada.
- Garantir que navegação por paginação preserve filtros e posição lógica.

#### Leitura de diploma

- Hierarquia legível para livros, títulos, capítulos, seções, artigos, parágrafos e incisos conforme o conteúdo canônico; não inventar estrutura ausente.
- Sumário local de navegação com recolhimento em telas pequenas; indicar dispositivo corrente sem depender só de cor.
- IDs de âncora estáveis; links para artigo devem funcionar ao carregar direto, atualizar histórico do navegador e sobreviver à regeneração do site.
- Ações: copiar link do artigo, copiar texto do dispositivo, aumentar/diminuir texto dentro de limites e alternar foco. Cada ação deve ter estado acessível e alternativa quando clipboard/localStorage falhar.
- Cópia inclui o conteúdo de exatamente um dispositivo e a referência do diploma. Não converter automaticamente em parecer, petição ou citação “oficial”. Permitir prévia do que será copiado e não truncar incisos/parágrafos.
- Fonte oficial e metadados de corte/release são encontrados sem rolar ao final do diploma; informação técnica detalhada pode ficar recolhida.
- Relações normativas aparecem separadas do texto legal, com tipo, direção, trecho de evidência e destino. Se não houver evidência ou destino, informar isso.
- Navegação entre ocorrência anterior/próxima em resultados de busca, caso a busca no texto integral entre no escopo.

#### Histórico e comparação

- Só ativar comparação entre versões quando houver snapshots identificados e alinhamento confiável de dispositivos.
- Exibir data da versão, release e origem de cada lado; marcar adição, remoção e alteração também textualmente.
- Disponibilizar texto linear alternativo ao diff colorido.
- Não chamar comparação de “alteração legislativa” sem evidência de que os dois snapshots são comparáveis e completos.

### 11.5 Contratos de dados e geração estática

1. **Entradas:** manifests, Markdown canônico, dados derivados e metadados públicos. A interface não altera o conteúdo normativo.
2. **Transformação:** gerador determinístico lê as entradas, valida schema/ID, gera catálogo, páginas, rotas, busca e relatório de build.
3. **Saídas:** HTML estático, CSS/JS locais, índices otimizados e artefatos para download com nomes/versionamento claros.
4. **Rastreabilidade:** guardar metadados da geração: release/corte, commit ou identificação da fonte, contagem de documentos e versão do schema/gerador.
5. **Reprodutibilidade:** a mesma entrada e versão das ferramentas devem produzir os mesmos artefatos relevantes, exceto metadados explicitamente voláteis.
6. **Falha segura:** documento inválido, ID duplicado, rota colisiva ou referência sem destino impede publicação ou fica em relatório bloqueante; não deve gerar página enganosa.
7. **URLs estáveis:** preservar rotas publicadas atuais, usar redirects quando houver mudança inevitável e manter fragmentos de artigo compatíveis.
8. **Peso do índice:** separar índices por escopo ou carregá-los sob demanda; definir orçamento medido em bytes comprimidos e tempo em rede móvel antes de ampliar busca integral.

O estado do build deve ser exibido como **data da geração do site**, sem insinuar data de atualização jurídica se forem conceitos distintos.

### 11.6 Direção visual e sistema de componentes

#### Linguagem visual

- Consolidar tokens existentes em `docs/BRANDING.md` e `site_docs/stylesheets/extra.css`; remover divergências entre versões claro/escuro.
- A interface principal deve ser clara, editorial e de alto conforto; modo escuro é uma preferência persistida que respeita preferência do sistema na primeira visita.
- O conteúdo jurídico usa largura controlada e entrelinha ampla; navegação, metadados e tabelas podem usar família sem serifa/mono.
- Grade editorial consistente, espaçamento escalável, bordas discretas e superfícies com profundidade mínima.
- O hero usa um recorte navegável das relações normativas publicadas. Se uma versão futura usar desenho decorativo, deve identificá-lo como ilustração e não como dado; o recorte real precisa declarar escopo, direção e acesso por teclado.
- Evitar estética de “dashboard SaaS” quando não houver ação/indicador útil; cada card responde a uma tarefa concreta.

#### Componentes a especificar

- Header institucional, navegação desktop/mobile e trilha de navegação.
- Campo de busca, sugestões, resultados, filtros, chips de filtro e estados vazio/erro/carregando.
- Cartão de diploma, badge de estado, linha de metadados e aviso de limite/autoridade.
- Sumário de diploma, cabeçalho de livro/título, dispositivo e margem de relações.
- Toolbar de leitura, botões de copiar, confirmação/erro e modal de salto.
- Tabela de dados, diff, bloco de código e aviso editorial.
- Paginação, links anterior/próximo, rodapé e página 404.

Para cada componente documentar: finalidade, variantes, semântica HTML, teclado, foco, mobile, estados, tokens, conteúdo longo e fallback sem JavaScript.

### 11.7 Acessibilidade e localização

- Definir WCAG 2.2 AA como alvo de projeto e verificar critérios aplicáveis em conteúdo, componentes e publicação.
- Idioma `pt-BR` consistente, com datas exibidas em formato legível e ISO quando usadas como identificadores de corte.
- Títulos e landmarks semânticos; um H1 por página; rótulos associados a campos; botões com nomes claros.
- Dialog de salto: foco inicial no campo, foco contido, Escape fecha, foco retorna ao gatilho, resultados navegáveis por setas/Tab e anúncios de atualização/resultados.
- Busca e cópia anunciam status em região apropriada; estado “copiado” não é comunicado somente por cor ou ícone.
- Zoom/reflow, foco não encoberto por header fixo, alvos de toque adequados e tabelas que não exigem rolagem horizontal sempre que possível.
- Testar tema claro/escuro, contraste de links e badges, alto contraste, teclado, leitor de tela e `prefers-reduced-motion`.
- Manter headings e links compreensíveis com movimento desativado e sem CSS avançado.
- Acessibilidade automatizada é uma triagem, não substitui revisão manual.

### 11.8 Desempenho, privacidade e segurança

- Páginas de diploma devem ser HTML estático e legíveis antes de scripts não essenciais.
- Usar assets locais, reduzir dependências, dividir JavaScript por tarefa e evitar baixar o índice completo em todas as páginas.
- Definir orçamento de desempenho a partir de baseline real em celular intermediário/rede lenta; observar LCP, INP e CLS, sem prometer nota específica antes de medir.
- Não adicionar analytics invasivo, fingerprinting, cookies não essenciais ou chamadas externas ocultas. Qualquer medição precisa de justificativa e minimização de dados.
- Busca e leitura devem funcionar sem autenticação. Não enviar texto pesquisado a serviços de terceiros sem explicação e consentimento adequado.
- Validar conteúdo gerado/HTML e escapar metadados antes de inseri-los em markup. Nunca tratar Markdown normativo como HTML confiável por padrão.
- Dependências e ações de CI têm versões controladas; artefatos de release devem ser consistentes com o commit publicado.
- Falhas de rede externa (badges, fontes, analytics) não devem remover o conteúdo ou bloquear o leitor.

### 11.9 Migração e compatibilidade

Antes de redesenhar, levantar URLs de páginas, IDs, links externos, acessos internos, canonical URLs e páginas geradas. Manter URLs existentes quando possível; quando não, produzir mapa explícito `rota antiga → rota nova` e redirect funcional no contexto de GitHub Pages. Preservar URLs dos diplomas e fragmentos de dispositivos, links para Markdown e contratos de dados.

Planejar publicação em incrementos verificáveis: gerar site de prévia em branch/artefato, comparar URLs e conteúdo, revisar visualmente em celular/desktop, executar gates e só então trocar a publicação. Manter a release anterior disponível para rollback. O plano não presume que GitHub Pages permita recursos de servidor ou redirects com configuração típica de plataformas dinâmicas; escolher solução compatível com hospedagem estática.

### 11.10 Estados e microinterações

Especificar cada estado explicitamente:

- busca não iniciada, buscando, resultados, sem resultados, erro de índice e resultado fora do escopo;
- carregamento/erro de conteúdo e link de fallback para arquivo canônico;
- clipboard disponível/negado/indisponível, sucesso e texto pronto para seleção manual;
- preferências de tema/fonte/foco salvas, bloqueadas ou restauradas;
- modal aberto, vazio, selecionado, sem correspondência e fechado;
- relações sem registros, incompletas, filtradas ou com destino ausente.

Movimentos devem comunicar mudança de estado, não decorar cada rolagem. Manter animações curtas, não essenciais e desativáveis; evitar scroll suave forçado que prejudique navegação assistiva.

### 11.11 Plano de entrega do Pages

| Etapa | Entrega revisável | Portão para avançar |
| --- | --- | --- |
| A. Descoberta | inventário de templates, URLs, dados, JS/CSS, build e problemas atuais | escopo e compatibilidade das rotas conhecidos |
| B. Produto | jornadas, sitemap, requisitos e critérios de aceite priorizados | público e sucesso das tarefas definidos |
| C. Protótipo | wireframes homepage, catálogo, busca, diploma e mobile | tarefas principais compreendidas sem explicação |
| D. Sistema visual | tokens, componentes e estados em claro/escuro | contraste, legibilidade e coerência aprovados |
| E. Dados/build | contratos e geração de páginas/índice/rotas | contagens e IDs batem com fonte; build determinístico |
| F. Fundação | navegação, layout responsivo, 404, SEO básico e fallback | rotas e navegação sem JS operantes |
| G. Leitor MVP | catálogo, página do diploma, sumário, âncoras e metadados | jornada localizar → verificar → ler concluída |
| H. Busca MVP | índice inicial, filtros e estados | escopo declarado, URL compartilhável e erros claros |
| I. Interações | cópia, foco, fonte, salto, grafo e histórico por prioridade | teclado/leitor de tela/fallback revisados |
| J. Migração | mapa de URLs e preview de publicação | links antigos e rotas novas resolvidos |
| K. Qualidade | revisão funcional, conteúdo, acessibilidade, desempenho e segurança | todos gates bloqueantes verdes |
| L. Lançamento | notas, versão, monitoramento de erros e plano de retorno | release e Pages representam o mesmo corte |

### 11.12 Plano de validação antes do lançamento

Validar com pelo menos estes cenários ponta a ponta, em desktop e mobile:

1. abrir URL direta de diploma e de artigo;
2. pesquisar por título, número, ID, artigo e termo não encontrado;
3. aplicar/remover filtros e compartilhar URL;
4. navegar o diploma só por teclado e abrir/fechar salto rápido;
5. copiar texto e link com clipboard permitido e negado;
6. alternar tamanho, foco, tema, atualizar a página e verificar persistência;
7. desligar JavaScript e carregar arquivo canônico/rota essencial;
8. simular índice indisponível e destino oficial inacessível;
9. verificar texto longo, incisos, tabelas e um diploma com metadados/relacionamentos incompletos;
10. validar leitor de tela e zoom elevado sem perda de conteúdo/controles;
11. verificar links legados e redirects de artigos compartilhados;
12. comparar contagens e amostras renderizadas com os artefatos da release.

Critérios quantitativos (orçamento de peso, tempos, taxa de sucesso, cobertura de links) devem ser definidos após baseline e protótipo, registrados antes do gate de lançamento e medidos no ambiente publicado.

### 11.13 Operação pós-lançamento

- Cada release publica junto a versão do corpus, corte, data de geração e commit/fonte reproduzível.
- Gerar changelog do site separado de alterações jurídicas; destacar mudanças que afetem rotas, schema ou busca.
- Manter canal de relato para erro textual, proveniência, acessibilidade, segurança e interface, com modelo que peça ID/URL e release.
- Classificar incidentes: texto/proveniência (crítico), integridade de busca/rotas (alto), visual/acessibilidade (alto conforme bloqueio), melhoria (normal).
- Corrigir falhas de conteúdo preservando rastreabilidade e processo governado; não editar o HTML publicado à mão.
- Revisar rotas, dependências e amostras em cada release; executar revisão periódica de acessibilidade e desempenho.
- Observar métricas agregadas e minimizadas; evitar coletar consultas jurídicas identificáveis.

### 11.14 Riscos específicos do redesign

| Risco | Mitigação/decisão |
| --- | --- |
| Refazer tudo quebra URLs citadas em artigos | inventário, mapa de redirects e teste de links antigos antes de publicar |
| Framework ou busca novos aumentam manutenção | manter MkDocs/build atual até protótipo provar lacuna concreta; justificar cada dependência |
| Índice integral deixa páginas lentas | medir payload, particionar e carregar sob demanda; manter busca por metadado disponível |
| Dados de status parecem parecer jurídico | definir semântica e fonte para cada status; expor incerteza e corte |
| Ações de cópia omitem parte do artigo | extrair unidade estrutural do gerador/corpus, não inferir limites pelo DOM; testar artigos com subitens |
| Atalho/modais falham com leitores de tela | requisitos de foco, teclado e anúncios antes da implementação |
| Cores de marca falham em dark mode/contraste | tokens semânticos por tema e medição de contraste dos pares reais |
| Métricas expõem consultas sensíveis | sem captura de consulta por padrão; telemetria mínima e transparente |
| Geração insere markup inseguro | escapar conteúdo e validar HTML; conteúdo normativo permanece dado, nunca código executável |
| Animação oculta conteúdo até script rodar | conteúdo visível por padrão; JS só adiciona efeitos progressivos |

## 12. Inventário técnico a fechar antes do redesign

O repositório já contém homepage customizada, cartões de diplomas, métricas, navegação de leitores, controles de foco/tamanho, botão de cópia de ID, salto rápido por `Ctrl/Cmd+K`, relações recolhíveis e animações de revelação. Portanto, o projeto não parte de uma página em branco: a etapa inicial deve revisar implementação e adequar o produto planejado ao comportamento real.

Itens para auditoria de implementação:

- origem e atualização de cada número apresentado na homepage e no README;
- se a busca atual é global ou somente salto por artigo da página aberta;
- consistência entre corte do corpus, release, badge, site e data de build;
- qualidade da extração de artigo usada na cópia (incisos, listas, próximos headings);
- gestão de foco e navegação por teclado no modal do leitor;
- fallback e comportamento quando Clipboard API/localStorage não estão disponíveis;
- preservação de âncoras antigas após mudança de gerador/títulos;
- diferença entre relações direcionadas e registros inversos apresentados no total;
- carga, tamanho e cobertura do índice de busca;
- comportamento no modo escuro e movimento reduzido em cada componente;
- se conteúdo essencial continua visível sem o JavaScript de revelação.

Este inventário é uma pauta de revisão, não uma declaração de que cada item esteja defeituoso.

## 13. Decisões em aberto e padrão de decisão

Registrar decisão em ADR curto quando afetar dependências, URLs ou contratos:

1. **Manter MkDocs Material ou substituir?** Decidir após mapear requisitos não atendidos, custo de migração e protótipo; preferência inicial é manter o gerador e customizar com parcimônia.
2. **Busca por texto integral no navegador?** Decidir após medir corpus/index, qualidade linguística, requisitos de privacidade e cenários sem JS.
3. **Qual status pode ser exposto como atualidade?** Exigir definição, campo de origem, política de corte e responsável pela semântica.
4. **Qual estrutura de artigo a cópia usa?** Preferir dados de build estruturados; documentar tratamento de dispositivos sem hierarquia confiável.
5. **Como comparar versões?** Só depois de existirem snapshots alinháveis e política para texto alterado/revogado.
6. **Quais sinais de uso medir?** Adotar privacidade por padrão; cada métrica deve responder a uma decisão concreta.

Para cada ADR: contexto, opções, decisão, consequências, dados/links afetados e critério de revisão. Não converter preferência estética em decisão irreversível de arquitetura.

## 14. Critério de conclusão do projeto

O redesign está pronto quando a experiência publicada e versionada permite:

- entender escopo, corte e limites sem abrir documentação separada;
- chegar ao diploma por navegação, catálogo, busca ou link direto;
- ler e saltar a dispositivos com URLs estáveis;
- confirmar fonte, metadados e release ao lado do texto;
- obter conteúdo/citação com contexto sem truncamento silencioso;
- usar as tarefas centrais por teclado, toque, zoom e leitor de tela;
- continuar com links e Markdown quando um recurso dinâmico falhar;
- reproduzir os números e artefatos públicos a partir do build;
- publicar e reverter versões sem perder links compartilhados;
- demonstrar que privacidade, manutenção e qualidade operacional foram consideradas.

Satisfação visual é necessária para consistência de marca, mas não substitui nenhum desses critérios.

## 15. Especificação de produto para execução

### 15.1 Limites de versão

Evitar tentar entregar todas as ideias no mesmo lançamento. Separar a reconstrução em versões que preservem uma experiência utilizável:

| Versão de produto web | Conteúdo do marco | Condição para iniciar a etapa seguinte |
| --- | --- | --- |
| **W0 — Baseline** | auditoria de rotas, dados, páginas, JS/CSS, métricas, acessibilidade e desempenho atuais | inventário reproduzível revisado |
| **W1 — Fundação** | arquitetura de informação, tokens, shell, navegação, mobile, SEO e páginas institucionais | navegação e design system aprovados nos templates principais |
| **W2 — Leitor confiável** | catálogo, página do diploma, metadados, fontes, sumário e âncoras estáveis | jornada buscar por catálogo → verificar → ler aceita |
| **W3 — Busca** | índice de metadados e, se viável, texto integral, filtros e URL compartilhável | cobertura, peso e semântica do índice documentados |
| **W4 — Ferramentas de leitura** | copiar, foco, salto, tipografia, relações e comparação priorizada | ações corretas com teclado, leitor de tela e falha de API |
| **W5 — Convergência** | README, Pages, releases, contratos e publicação sincronizados | checklist de migração e gates pós-build aprovados |

Cada versão deve ter feature flags ou uma forma simples de manter a experiência antiga acessível durante a prévia. Não publicar uma interface parcial que esconda os arquivos e caminhos que já funcionam.

### 15.2 Entregáveis obrigatórios de descoberta

Antes de alterar o visual, produzir e revisar estes artefatos:

1. **Mapa de rotas:** rota atual, destino, links internos, fragmentos, indexação e decisão de preservar/redirecionar.
2. **Inventário de dados exibidos:** valor, arquivo/campo de origem, regra de transformação, corte, responsável e páginas que o consomem.
3. **Mapa de templates:** homepage, catálogo, diploma por tipo, método, dados, auditoria, grafo, FAQ, atualização, erro e mobile.
4. **Matriz de capacidades reais:** o que funciona hoje, dependências JavaScript, limites, fallback e comportamento esperado.
5. **Baseline de qualidade:** tamanho dos artefatos, tempo de build, links, cobertura estrutural, acessibilidade manual/automática e métricas web disponíveis.
6. **Registro de problemas:** gravidade, tarefa afetada, frequência, evidência, correção proposta e risco de regressão.
7. **Protótipo testável:** pelo menos homepage, busca, catálogo, diploma e menu mobile, incluindo estados sem resultado/erro.

Não começar pela reescrita de CSS: sem estes artefatos, o redesign corre o risco de reproduzir as mesmas ambiguidades com uma estética nova.

### 15.3 Priorização com fórmula explícita

Pontuar cada item de backlog de 1 a 5 em **impacto na tarefa**, **frequência**, **risco de confiança/acessibilidade** e **custo**. Calcular prioridade inicial como:

```text
prioridade = (impacto × frequência + risco de confiança/acessibilidade) ÷ custo
```

Esta pontuação serve para ordenar conversa e não substitui P0 de integridade, privacidade, segurança ou compatibilidade. Toda iniciativa deve citar a tarefa e a evidência que a justifica. Não pontuar “parece moderno” como impacto sem hipótese mensurável.

### 15.4 Matriz de rastreabilidade dado → interface

Para cada dado exibido, manter linha equivalente no inventário:

| Campo exibido | Origem normativa/de produto | Transformação permitida | Exibição mínima | Fallback/recusa |
| --- | --- | --- | --- | --- |
| título/identificador | manifesto do diploma | formatação de leitura sem alterar identidade | página, resultado, catálogo | usar ID técnico e sinalizar metadado ausente |
| texto normativo | Markdown canônico da release | renderização segura que preserva estrutura | leitor e arquivo bruto | link ao Markdown; não fabricar texto |
| fonte oficial | metadado/proveniência | normalização de URL sem trocar autoridade | página do diploma e cópia | “fonte não identificada” e link ao registro de proveniência |
| corte/release | manifestos e configuração de release | apresentação em formato legível | cabeçalho e citação copiada | não inferir pela data do navegador/build |
| status editorial | campo definido por contrato | rótulo legível com descrição | resultado e metadados | mostrar valor original/indefinido, não deduzir vigência |
| hash | artefato de integridade | abreviar visualmente, copiar valor integral | detalhe técnico e download | reportar ausente/inválido sem selo positivo |
| total de documentos/relações | relatório derivado versionado | agrupar conforme definição explícita | homepage, catálogo, release | ocultar valor em erro ou falta de relatório |

Critério obrigatório: toda afirmação variável tem rastreio até artefato e versão. Se não houver rastreio, retirar a afirmação ou apresentá-la como descrição não quantitativa.

### 15.5 Contrato de UX para funções críticas

**Busca:** aceitar consulta em linguagem simples, preservar a consulta na URL, permitir limpar/voltar, indicar o campo correspondente e separar “não encontrado” de “índice indisponível”. Para cada resultado, mostrar nome, identificador, tipo, correspondência e link direto. Evitar resultados sem contexto ou ranking opaco.

**Leitura:** manter o texto como foco visual principal. Metadados complementares não deslocam o conteúdo; controles não interceptam seleção normal. O artigo visível recebe URL compartilhável e o estado de foco não impede voltar à navegação geral.

**Cópia:** antes de prometer “copiar citação”, definir a regra de seleção estrutural, tratamento de caput/incisos/anexos e limite de conteúdo. A saída leva texto e referência bibliográfica separáveis, inclui release/corte e fonte, preserva quebras úteis e nunca adiciona reticências silenciosas. Em falha de clipboard, selecionar/preparar texto para cópia manual.

**Grafo:** cada aresta tem direção, tipo, dispositivo ou evidência e origem; aresta não comprovada não se torna fato por visualização. A lista acessível é fonte equivalente ao desenho.

**Preferências:** tema, foco e tamanho de texto usam persistência local opcional, respeitam bloqueios do navegador e têm valores padrão úteis; nenhum conteúdo depende dessas preferências para aparecer.

## 16. Plano de arquitetura e qualidade do build

### 16.1 Fluxo de build alvo

```text
commit + manifests + corpus canônico
→ validar schema, IDs, fontes e integridade
→ gerar catálogo, métricas, páginas e índice
→ validar conteúdo derivado, rotas e links
→ build estático em modo estrito
→ validar HTML/acessibilidade/artefatos
→ publicar preview de Pull Request ou artefato
→ revisão visual e gates de release
→ deploy do mesmo artefato validado
```

O workflow Pages atual instala dependências, roda `tools/site/build_site.py`, executa `mkdocs build --strict` e publica o diretório gerado em push à `main`. O plano é evoluir os gates sobre esse fluxo e promover o mesmo artefato; não reconstruir bytes diferentes depois da validação.

### 16.2 Gates bloqueantes propostos

1. **Dados:** schema válido, IDs únicos, referências internas resolvidas, totais coerentes com manifestos e nenhum documento fora do contrato publicado.
2. **Geração:** execução limpa, saída determinística, links relativos e rotas previstas; página criada para todo documento publicável.
3. **HTML:** build estrito, idioma, títulos, landmarks, imagens com alt, botões nomeados e ausência de erro de console bloqueante.
4. **Navegação:** links internos, anchors, download de release e rotas de artigo validados; allowlist explícita para destinos externos não verificáveis.
5. **Acessibilidade:** validador automatizado, teclado manual, foco, reflow/zoom, movimento reduzido e pelo menos uma revisão com tecnologia assistiva por marco funcional.
6. **Conteúdo:** amostras e dados variáveis batem com suas fontes; ausência/ambiguidade é comunicada.
7. **Tamanho/desempenho:** medir bytes comprimidos de JS/CSS/índices e Web Vitals; bloqueio conforme budgets fixados no W0, não chute inicial.
8. **Segurança/privacidade:** nenhum segredo no bundle, nenhuma chamada de terceiros inesperada, conteúdo renderizado escapado e dependências críticas analisadas.
9. **Publicação:** tag/corte/manifesto e artefato correspondem; URL-base e rotas de GitHub Pages funcionam.

Classificar falhas como bloqueantes, advertências ou não aplicáveis; cada exceção tem justificativa registrada e prazo de revisão. Não transformar aviso cosmético em bypass geral de gate.

### 16.3 Orçamentos após baseline

No W0, coletar pelo menos três builds representativos e medir homepage, catálogo, diploma curto, diploma longo e rota com muitas relações. Registrar mediana e pior caso para:

- bytes comprimidos de CSS, JS inicial, índice e assets;
- tempo do gerador e tempo até artefato Pages;
- LCP, INP e CLS no perfil móvel acordado;
- HTML por página e número de rotas;
- percentual de rotas/links resolvidos;
- falhas por categoria de validação.

Definir budgets relativos à baseline e ao caso de uso, revisar quando corpus crescer e aprovar exceção documentada. Não estabelecer metas numéricas sem medições do repositório e ambiente real.

### 16.4 SEO e compartilhamento

- Títulos e descrições únicos por homepage, catálogo e diploma; canonical URL sob domínio GitHub Pages correto.
- Metadados Open Graph locais, sem expor status/corte enganoso em cartão social.
- `sitemap.xml` e `robots.txt` coerentes com páginas públicas, se suportados pelo build e necessários.
- Links compartilháveis ao dispositivo mantêm âncora estável e não dependem de sessão.
- Conteúdo acessível ao crawler como HTML estático; evitar esconder texto essencial atrás de busca client-side.
- 404 com caminho útil e links para repositório, catálogo e download.

## 17. Backlog mestre por épicos

Os épicos abaixo são unidades de planejamento; cada item só entra em implementação após definir dado de origem, estado de erro, risco e critério de aceite.

### E0 — Verdade e proveniência

- Inventariar claims quantitativos e estados em README e site.
- Exibir corte, release, hash e fonte de forma coerente.
- Reconciliar definição de total de arestas e registros inversos.
- Separar data do corpus, data da release e data da geração Pages.

### E1 — Exploração

- Definir catálogo e vocabulário dos filtros.
- Derivar cartões, grupos e totais de dado de origem.
- Persistir filtros compartilháveis na URL.
- Criar estados vazio, erro, sem índice e nenhum documento elegível.

### E2 — Leitor

- Definir semântica/estrutura HTML para diploma e artigo.
- Alinhar cópia com unidade estrutural canônica.
- Definir barra de ferramentas e painel de metadados em desktop/mobile.
- Garantir âncoras, seleção e cópia, foco e fallback.

### E3 — Busca

- Decidir cobertura/normalização e ranking por tipo de campo.
- Medir índice e escolher segmentação/carregamento.
- Criar teclado, anúncio de resultado, histórico e URL.
- Cobrir ausência, erro, indexação parcial e query longa.

### E4 — Confiança e metodologia

- Demonstrar coleta → normalização → comparação → validação → release sem alegar automatização de juízo jurídico.
- Distinguir evidência textual, revisão técnica, status editorial e inferência.
- Conectar qualidade e proveniência aos documentos/relatórios subjacentes.

### E5 — Dados e integrações

- Contratos de Markdown, JSON, CSV, schema e IDs.
- Exemplos reproduzíveis e erros comuns.
- Skill versionada e avaliação de saídas/citações.
- Download em nível de release com checksums publicados.

### E6 — Navegação, design e conteúdo

- Sistema de tokens e componentes claro/escuro.
- Header, navegação móvel, breadcrumbs, rodapé e 404.
- Conteúdo editorial conciso, linguagem jurídica precisa e mensagens de limite.
- Revisão das artes e metadados de compartilhamento.

### E7 — Confiabilidade e operação

- Gates de build e links, relatórios de falhas legíveis.
- Preview e promoção do artefato validado.
- Mapa de redirects e rollback.
- Processo de incidente e manutenção de dependências.

## 18. Gestão de trabalho e comunicação do projeto

### Modelo de issue para cada funcionalidade

```text
Problema/tarefa do usuário:
Público e contexto:
Evidência atual:
Resultado esperado:
Dados e contrato envolvidos:
Estados normais e de falha:
Acessibilidade/teclado/mobile:
Critérios de aceite verificáveis:
Rotas/compatibilidade afetadas:
Privacidade/segurança:
Métricas e budget:
Plano de rollback:
```

### Definition of Ready

- tarefa e público nomeados;
- origem dos dados definida;
- estados de erro/vazio definidos;
- requisito de acessibilidade e mobile incluído;
- critério de aceite reproduzível;
- dependências e compatibilidade de URLs conhecidas;
- prioridade justificada por impacto/evidência.

### Definition of Done

- implementado sem alterar texto canônico por efeito visual;
- gates automatizados pertinentes passam;
- teclado, zoom/mobile e estados alternativos revisados;
- links/âncoras e fallback conferidos;
- documentação/contrato/changelog atualizado quando necessário;
- preview publicado/revisado e release/corte coerentes;
- limitações conhecidas registradas sem ocultar falha.

### Decisões e comunicação

- ADR para mudanças de framework, schema, busca, URL, status, analytics ou dependências relevantes.
- Changelog do site separado do changelog jurídico/corpus.
- Pull Request descreve motivo da tarefa, capturas desktop/mobile, rotas afetadas, evidência de validação e rollback.
- Não encerrar item por estar visualmente completo se a jornada, acessibilidade ou fonte não passaram.

## 19. Matriz de risco e resposta operacional

| Severidade | Exemplo | Resposta mínima |
| --- | --- | --- |
| S0 — integridade | conteúdo diferente do canônico, citação truncada sem aviso, release/corte falso | suspender atualização da página afetada ou voltar ao artefato conhecido; preservar evidência e corrigir com nova publicação rastreável |
| S1 — confiança/uso | busca aponta ID errado, rota de artigo quebra, fonte de diploma errada | restaurar caminho anterior, corrigir dados/gerador e verificar páginas correlatas |
| S2 — acessibilidade | controle crítico inacessível ou conteúdo encoberto | fornecer caminho alternativo imediato e corrigir antes de promover a interface afetada |
| S3 — degradação | layout menor, ilustração quebrada ou falha não essencial | abrir issue priorizada sem ocultar dados/limites |

Não apagar histórico de uma página com erro relevante; registrar release, rota, reprodução, impacto e correção. A resposta a erro jurídico/dado não pode depender apenas de uma atualização de estilo.

## 20. Checklist de governança para decisões de produto

Antes de aprovar qualquer funcionalidade avançada, responder:

- Qual tarefa concreta melhora e para qual público?
- Qual dado alimenta a função e qual a semântica desse dado?
- Como se comporta em ausência, conflito, erro e conteúdo parcial?
- A função continua útil com teclado, leitor de tela, zoom e JS indisponível?
- Que novo custo de build, bytes, dependência e manutenção introduz?
- Que URL, exportação ou integração existente pode quebrar?
- A interface pode ser confundida com fonte oficial, estado vigente ou aconselhamento?
- Que evidência decidirá se a funcionalidade funciona?
- Qual rollback reduz dano sem esconder histórico?

Se uma resposta crítica estiver indefinida, a funcionalidade não está pronta para passar da concepção ao backlog comprometido.

## 21. Gate de qualidade do rebranding

“Top tier” é uma ambição, não um critério auditável. O rebranding só deve ser considerado pronto quando cumprir os gates abaixo e houver evidência registrada para cada um:

### Estratégia e distintividade

- Briefing identifica públicos, tarefa central, promessa, limites e concorrentes de referência sem copiar sua identidade.
- Há pelo menos três direções de marca aplicadas em contextos reais, avaliadas com critérios comuns.
- A direção escolhida é reconhecível em favicon, README, homepage, leitor, imagem social e tema escuro.
- Feedback de leitores jurídicos, pesquisa e tecnologia foi incorporado e a decisão registrada.
- A comunicação descreve o produto e não promete autoridade, cobertura, atualização ou resultado jurídico sem prova.

### Sistema visual

- `docs/BRANDING.md` é a fonte dos tokens; removidas as paletas conflitantes dos planos antigos e dos badges.
- Logo, favicon, cores, tipografia, ícones, capas e Open Graph pertencem à mesma família e têm arquivos fonte/licenças.
- Contraste é calculado para combinações concretas, todos os estados e temas; nenhuma cor de acento é usada em texto pequeno sem passar o critério.
- Componentes têm regras documentadas para semântica, foco, uso móvel, zoom, tema e movimento reduzido.
- Marca e ilustração nunca competem com busca, proveniência ou texto normativo.

### Qualidade de produto

- As jornadas localizar → verificar → ler → compartilhar/citar foram observadas com usuários e critérios de sucesso definidos.
- Cada dado variável na interface aponta para fonte de build e versão; números estáticos sem rastreio foram removidos.
- Rotas e âncoras existentes têm mapa de compatibilidade; o rollback foi demonstrado.
- Conteúdo essencial permanece visível sem JavaScript; busca/cópia têm estados de erro e alternativas.
- Acessibilidade é revisada com automação e inspeção manual; WCAG 2.2 AA é o alvo de projeto, conforme critérios aplicáveis [da W3C](https://www.w3.org/TR/WCAG22/).
- Desempenho tem baseline e budgets medidos em dispositivo/rede acordados; não é aceito “rápido” como claim sem medição.
- Build, conteúdo, links, segurança, privacidade e publicação passam gates definidos; exceções têm escopo, justificativa e prazo.

### Evidências que acompanham a decisão de lançamento

O Pull Request de rebranding deve incluir: briefing; comparação das direções; protótipos desktop/mobile; mapa de tokens e contraste; inventário de assets/licenças; capturas das páginas-chave nos dois temas; mapa de rotas; resultados de qualidade; problemas conhecidos; e plano de rollback. A aprovação visual isolada não libera o lançamento.

## 22. Aderência e pontos remanescentes da identidade

A base visual agora usa a paleta Ink/Ivory/Gold/Green em README, CSS e lockups. O plano antigo que pedia Obsidian/Gold/Emerald foi substituído por um aviso em `docs/PLANO_MESTRE_PRODUTO_ELITE.md`, e a tipografia do site declara pilhas de fontes de sistema em vez de prometer fontes remotas. A capa estática foi alinhada aos tons canônicos. As três direções de marca ainda precisam de protótipo/avaliação; o inventário `docs/ASSET_INVENTORY.md` rastreia os arquivos no histórico, mas não comprova titularidade pessoal, e o escopo do `LICENSE.md` sobre vetores ainda precisa de declaração explícita antes da redistribuição promocional independente. O lettering final também aguarda direção aprovada.

Os pares de cores foram revisados no build e o contrato do tema escuro agora calcula contraste mínimo de 4,5:1 para texto da navegação. Isso não certifica o restante dos componentes: links, foco, estados, gráficos, combinações semitransparentes e ambos os temas precisam ser auditados nas telas e estados reais. Os cálculos anotados continuam sendo aproximações sRGB, não certificação global.


## 23. Registro de execução e prontidão

**Atualização:** 2026-10-22. Esta seção registra o trabalho aplicado no workspace; não substitui revisão do preview publicado nem aprovação de lançamento.

### Implementado nesta etapa

- README reorganizado como entrada do produto, com release e corte identificados, caminhos de leitura/dados/integração e limites explícitos. Removidas comparações sem fonte, instruções de IA com promessa de resposta “sem alucinações”, status manuais de “em vigor” e a alegação de leitor interativo dentro do GitHub Markdown.
- README agora esclarece que os blocos `<details>` são exemplos estáticos. O logo alterna entre versões clara e escura com `<picture>`, recurso documentado para READMEs pelo [GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github).
- Homepage passou a derivar a contagem do link de catálogo dos manifests, deixou de exibir estados de vigência hard-coded nos destaques e recebeu lockups distintos para os dois temas. A cor de foco usa variante de texto com contraste superior ao dourado decorativo.
- Leitor gera referências com ID, corte, fonte disponível e release; cópia reporta indisponibilidade honestamente. A busca rápida cobre títulos, números, IDs e rótulos de artigos, enquanto a busca por corpo textual ocorre dentro de um diploma aberto.
- Páginas integrais dos diplomas saíram do índice genérico do MkDocs para evitar duplicar dezenas de megabytes; um índice compacto de metadados/rótulos de artigos é gerado separadamente. O índice genérico medido no build caiu de 31,561,957 bytes para 60,647 bytes; o índice customizado tem 749,339 bytes para 375 diplomas e 27,121 rótulos.
- Fontes externas da página de diploma são aceitas somente em HTTPS, sem credenciais, em host cadastrado no registro de fontes. O botão tem rótulo neutro “Fonte oficial” e deixa de rotular todo link como Planalto.
- O build de CI gera cartões sociais PNG de 1200 × 630 para 11 páginas-chave; metadados Open Graph/Twitter apontam para arquivos locais. `CI=true` ativa a geração no workflow; o build local no Windows não exige Cairo.
- A inspeção visual local ajustou os agrupamentos da release/diploma no mobile e impede que os rótulos da barra de leitura quebrem no meio; a indicação de atalho é ocultada em telas estreitas, mantendo o comando acessível no desktop.
- O tema escuro separa fundo e texto da navegação; títulos passam a usar o token de texto do tema. Um teste calcula a razão de contraste da navegação escura (mínimo 4,5:1) para evitar a regressão encontrada na primeira captura.
- A capa de release estática foi alinhada à paleta canônica; o README/HTML do GitHub continua sendo estático e não promete controles personalizados.
- As dependências da documentação declaram o intervalo de MkDocs 1.x e a linha de Material que contém o plugin social testado; uma futura migração do gerador requer avaliação própria, não atualização automática para uma versão major incompatível.
- O diretório publicado medido contém 46,13 MiB em 466 arquivos (396 HTML), mas esse total descreve o conjunto hospedado, não o download de cada visita. A homepage tem 39.595 bytes de HTML; os diplomas são páginas separadas; e o índice de busca sob demanda tem 749.339 bytes sem compressão (estimativa local gzip: 67.015 bytes), baixado somente quando a pessoa começa a buscar. Portanto, o peso inicial é baixo e o índice comprimido é pequeno; o maior custo potencial é abrir uma página de diploma extenso. Confirmar bytes transferidos, compressão, cache e tempo de interação no preview publicado, em rede móvel, antes de fixar budgets de performance.

### Validação executada

- `tools/site/build_site.py` gerou as páginas para 375 diplomas, 35 domínios e 1,841 relações.
- A suíte integral passou: 61 testes (`python -m unittest discover -s tests -v`). A validação focal de site também está coberta nela.
- `mkdocs build --strict` passou localmente; o build de CI com `CI=true` também passou em Ubuntu/WSL e gerou os 11 cartões sociais. O comando exibiu aviso do Material for MkDocs sobre mudanças anunciadas para MkDocs 2.0; rever compatibilidade antes de atualizar dependências.
- O projeto declara `mkdocs>=1.6.1,<2` e `mkdocs-material[imaging]>=9.7.7,<10`; `pip install -e '.[docs]'` resolveu e manteve as versões efetivamente exercitadas (MkDocs 1.6.1, Material 9.7.7). A restrição evita aceitar silenciosamente a linha 2.0 que ainda não é compatível com esta configuração.
- Sintaxe dos dois scripts JavaScript aprovada com `node --check` após os ajustes.
- `tools/check_markdown.py`, `validate_workflows.py`, `validate_site.py` (396 páginas HTML, 0 erros, cartões obrigatórios) e `tools/validate_release.py --stabilization` passaram; release validator encontrou 0 erros e 33/33 itens P0 consolidados.

### Ainda não é gate de lançamento

- A prévia local foi inspecionada com Microsoft Edge headless/CDP, em 390 e 320 CSS px, desktop e reflow equivalente a 200% (720 CSS px a DPR 2), nos temas claro e escuro. `document.documentElement.scrollWidth` igualou a largura do viewport em todos os tamanhos medidos. As capturas estão em `reports/rebranding-preview/`; a captura escura confirmou cabeçalho e títulos legíveis após correção. Isso não substitui revisão com navegador visível, testes completos de teclado/leitor de tela ou avaliação humana.
- Três direções conceituais foram prototipadas lado a lado em `docs/BRAND_DIRECTIONS.md`; ainda não foram avaliadas com usuários nem aplicadas a favicon, README renderizado, mobile, leitor completo e tema escuro, portanto a escolha de identidade segue preliminar. Confirmar origem/licença de todos os SVGs e cartões e registrar os ativos de origem.
- A taxonomia exibida no site parte de 35 domínios técnicos. Não foi demonstrado o mapeamento do corpus para os sete ramos e totais editoriais citados em versões antigas do README; removidos esses números do README, mas qualquer retorno deles requer taxonomia explícita validada.
- O trecho demonstrativo do art. 186 foi comparado literalmente com o Markdown canônico e confere. A URL pública atual do Pages respondeu HTTP 200; falta comparar o candidato desta revisão com a versão publicada e checar README nos dois temas, links locais, destino da release/artefatos e rotas em preview.
- Fazer revisão visual e medição real de rede no preview publicado (incluindo cache, compressão, fontes e interação da busca); os bytes estáticos locais não substituem Web Vitals/Lighthouse em desktop e dispositivo móvel. Definir budgets e metas explícitas antes de lançamento.
- Rever periodicamente o ciclo de suporte do gerador e executar uma prova de migração em branch antes de remover a restrição de MkDocs 2.x; validar Material, plugin social, navegação, hooks e contrato de publicação na ferramenta candidata.
- A documentação atual do [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) indica máximo publicado de 1 GB e limite flexível de 100 GB/mês; os 46,13 MiB atuais estão abaixo desses limites, mas medir tráfego real e rever se a audiência crescer.

**Decisão de estado:** o rebranding de base e a experiência web tiveram melhorias implementadas, mas o produto ainda não pode ser declarado top tier ou pronto para lançamento até fechar os itens acima com evidência verificável.


## 24. Navegação Markdown e grafo do hero — execução em 2026-10-22

### Implementado

- O README agora coloca **Encontre uma lei** no primeiro nível: 10 atalhos Markdown para Constituição, códigos e leis de uso frequente; link para `docs/INDICE_LEGISLACAO.md`, com todos os 375 documentos; link para navegação por pasta; e link separado para pesquisa web. O caminho recomendado para qualquer diploma no GitHub é nome/número ou Ctrl+F no índice, depois clique no Markdown canônico.
- `tools/site/build_site.py` gera o índice em grupos de tipo e ano, preserva os 375 links canônicos, oferece atalho para os 10 códigos e permite alternar para o leitor pesquisável. `bases/curated/README.md` aponta para esse índice e explica a estrutura tipo/ano/arquivo.
- O catálogo do Pages também oferece ligações a cada diploma. Removidos estados `Em vigor` e prioridades `P0` que estavam codificados manualmente; as colunas editoriais agora identificam tipo, número e ano.
- O grafo decorativo do hero foi removido. Agora o gerador usa `bases/derived/relacoes/normative-graph.jsonl`, escolhe o nó mais conectado do corpus e até seis vizinhos reais, resume relações repetidas por par e desenha setas na direção dos registros. Cada nó SVG é um link de teclado/touch para a página correspondente; uma lista HTML dá acesso equivalente aos diplomas, e um painel expansível lista tipo, origem e destino de cada relação mostrada. `site_docs/graph.md` explica o recorte e leva às fichas completas por diploma.
- `docs/ASSET_INVENTORY.md` registra a proveniência Git dos vetores, o uso atual, a chamada de Google Fonts que o plugin social pode fazer no build e as pendências de titularidade/licença; nenhuma fonte externa é carregada pelo navegador do site.

### Evidência e validação

- A geração reportou 375 documentos, 35 domínios e 1.841 registros relacionais.
- Auditoria de destino: 385 links no índice contando atalhos repetidos, 375 leis únicas e zero arquivo Markdown ausente; todos os 10 atalhos do README estão no corpus.
- No HTML gerado, o hero contém sete nós SVG com rotas de diploma existentes e oito arestas dirigidas com nome acessível; nenhuma aresta ou nó é decorativa.
- `mkdocs build --strict` em Ubuntu/WSL com `CI=true` passou após a atualização e gerou os 11 cartões sociais; a suíte completa passou com 61 testes; `validate_site.py` passou para 396 arquivos HTML com cartões sociais obrigatórios; `check_markdown.py` (754 arquivos), `validate_workflows.py` (nove workflows), `validate_release.py --stabilization` (33/33 P0, zero erros) e `git diff --check` também passaram.
- A inspeção visual manual do browser ficou pendente: a integração Computer Use retornou `Computer Use native pipe is unavailable: failed to connect native pipe` após a tentativa de reconexão; a tentativa separada de iniciar uma captura headless do Edge foi bloqueada pela revisão automática (`blocked by policy`). O comportamento dos links e a estrutura HTML foram verificados estaticamente; isso não substitui revisão visual, teclado físico e leitor de tela.


## 25. Correção de direção do grafo e estudos de identidade — 2026-10-22

### Correção de fidelidade

Na revisão das setas, foi encontrado que o gerador escolhia um registro relacional verdadeiro, mas a geometria usava o par de IDs ordenado alfabeticamente. Isso podia inverter visualmente uma relação dirigida. O gerador agora deriva origem e destino do próprio registro (`source_id` e `target_id`) tanto para SVG quanto para a lista expansível. A regressão é coberta por comparação dos metadados de cada aresta/list item com o grafo JSONL e por uma relação conhecida dirigida da Lei 13.964/2019 para o Código Penal. A interface continua descrevendo metadados do corpus; a seta não representa aconselhamento nem conclusão jurídica.

### Estudos de marca

`docs/BRAND_DIRECTIONS.md` apresenta três painéis vetoriais com a mesma tarefa, conteúdo e escala: Índice normativo, Registro de evidência e Atlas de relações. Isso permite discutir hierarquia e linguagem visual com referências comparáveis. São estudos iniciais em tamanho desktop; faltam versões de favicon, README renderizado pelo GitHub, mobile, leitor completo e tema escuro. A recomendação pelo Índice normativo é apenas ponto de partida e não foi validada com usuários.

### Validação desta atualização

- `python -m unittest discover -s tests -v`: 61 testes aprovados, incluindo a comparação das setas e da lista do hero com os registros canônicos.
- `python tools/site/build_site.py`: gerados 375 documentos, 35 domínios e 1.841 relações.
- `python tools/check_markdown.py docs` e `... bases`: 22 e 754 arquivos Markdown UTF-8 válidos; `validate_workflows.py`: nove workflows válidos; `validate_release.py --stabilization`: zero erros e 33/33 gates P0 consolidados.
- Os três estudos SVG passaram pela leitura XML; `git diff --check` sem erro.
- `CI=true mkdocs build --strict` passou no ambiente Linux/WSL recriado com MkDocs 1.6.1 e Material 9.7.7, em 78,15 s; `validate_site.py` passou sobre o site gerado, com 396 páginas HTML e zero erros, exigindo cartões sociais. Inspeção estrutural do HTML final confirmou sete links SVG de diploma, oito arestas e oito itens de detalhe; as triplas fonte/tipo/destino coincidem com o JSONL canônico, inclusive Lei 13.964/2019 → Código Penal.


## 26. Auditoria de links e diferença entre candidata e produção — 2026-10-22

### Navegação corrigida e protegida por validação

Uma auditoria de ponta a ponta do HTML gerado percorreu 53.610 destinos de link nas 396 páginas do site. Ela encontrou uma âncora inexistente no cartão “Conhecimento para agentes”: o destino apontava a “Para desenvolvedores de agentes de IA”, enquanto a seção real se chama “Para agentes de IA”. O gerador agora usa `audiences/#para-agentes-de-ia`; os cartões de advogados e agentes têm contrato de teste próprio. O novo `validate_internal_links()` verifica rotas locais e fragmentos HTML em todos os arquivos no build de qualidade.

### Candidata local

- Build `CI=true mkdocs build --strict` aprovado em Linux/WSL com MkDocs 1.6.1 e Material 9.7.7, em 43,66 s; 11 cartões sociais renderizados.
- `validate_site.py` aprovado sobre as 396 páginas com `VMD_REQUIRE_SOCIAL_CARDS=1`, cobrindo semântica básica, imagens sociais e links/fragmentos locais; zero erros após a correção.
- Suíte completa: 63 testes aprovados; scripts JavaScript passaram por `node --check`; Markdown (22 docs e 754 bases), nove workflows, 33/33 P0 do validador de release e `git diff --check` passaram.

### Produção ainda não corresponde à candidata

A verificação HTTP de 2026-10-22 recebeu status 200 na homepage (37.495 bytes), catálogo (116.774 bytes) e ficha da Lei 13.964/2019 (175.080 bytes). A inspeção do HTML da homepage publicada mostra o fragmento antigo `#para-desenvolvedores-de-agentes-de-ia` e não encontra `hero-graph-node` nem `hero-graph-relation-list`; portanto, o site hospedado ainda não contém esta candidata e retém a âncora inválida. A construção local não foi publicada.

Antes de declarar lançamento, comparar a revisão candidata com a produção após o fluxo autorizado de publicação, repetir a checagem de rotas e âncoras no endereço público e revisar o funcionamento visual com navegador real. O acesso Computer Use desta sessão informou lista vazia de browsers/apps; a alternativa anterior de captura headless foi bloqueada pela revisão automática. Não usar status HTTP nem validação HTML estática como substitutos para inspeção visual, teclado e leitor de tela.

**Estado:** a candidata local melhora e valida a descoberta de leis e o grafo real, mas a produção pública permanece desatualizada e a revisão visual/acessível continua aberta; prontidão de lançamento não demonstrada.

## 27. Âncoras únicas e nomes de controles — 2026-10-22

Uma auditoria dos 396 documentos HTML encontrou 35 IDs duplicados no catálogo, todos produzidos por um `div` vazio seguido do título Markdown que já recebia a mesma âncora automática. Removi o `div`: os fragmentos permanecem nos títulos e agora têm um único destino. Uma varredura heurística das âncoras e botões do site também não encontrou controles sem texto, `aria-label` ou `title`.

O validador de links internos agora registra contagem de IDs e rejeita duplicatas, além de destinos e fragmentos inexistentes. A suíte comprova os três casos negativos e o caso válido. O `mkdocs build --strict` recriado com `CI=true` passou em 47,43 s; em seguida, `validate_site.py` exigindo cartões sociais validou 396 páginas com zero erros. A suíte completa passou com 63 testes; Markdown (22 docs, 754 bases), nove workflows, JavaScript e release (33/33 P0, zero erros) também passaram.

A página pública ainda serve a versão anterior; esta correção e as demais melhorias permanecem apenas na candidata local até serem integradas e publicadas pelo fluxo apropriado. A inspeção visual e a avaliação com teclado/leitor de tela seguem pendentes, portanto não declarar prontidão de lançamento.

## 28. Nomes acessíveis nos controles — 2026-10-22

A auditoria heurística da candidata não encontrou âncoras nem botões sem nome. Para tornar a verificação reproduzível no CI, o coletor HTML do `validate_internal_links()` agora reconhece texto descendente, texto alternativo de imagens internas, `aria-label` e `title` em `<a>` e `<button>` e falha quando nenhum nome é encontrado. Testes de regressão cobrem controles nomeados e sem nome; o validador das 396 páginas construídas segue sem erros após esta regra.

A suíte completa passou novamente com 63 testes; Markdown (22 documentos de produto e 754 arquivos de base), nove workflows, JavaScript e validação de release (33/33 P0) passaram. O build estrito integral da candidata permanece o já registrado na seção 27 (47,43 s); a única alteração posterior foi ao validador e aos testes, não ao HTML gerado. Essa regra é uma triagem semântica automatizada, não substitui leitor de tela nem avaliação WCAG manual.

## 29. Compactação do conteúdo central — 2026-10-22

Após revisão do pedido de refinamento visual, a tipografia e o ritmo vertical do conteúdo central foram reduzidos sem alterar as regras das barras laterais. Na home, o título hero passou de `clamp(3.3rem, 7.2vw, 7.4rem)` para `clamp(2.45rem, 5.3vw, 5.2rem)`; a descrição e os espaços do hero também foram reduzidos. A altura mínima do hero caiu de 610 para 500 px, e o grafo de 420 para 360 px. Métricas, cartões e seções agora usam intervalos verticais menores.

No leitor de leis, o cabeçalho e o resumo ocupam menos espaço, a coluna passou de 74ch para 70ch, os artigos começam com menos espaço e o corpo padrão usa `0.96rem` com entrelinha 1.62. Os controles de tamanho permanecem disponíveis em quatro níveis crescentes (0.88, 0.96, 1.10 e 1.24 rem), permitindo que cada pessoa amplie a leitura.

Validação da candidata após a alteração: suíte completa com 63 testes aprovados; `CI=true mkdocs build --strict` concluído em 45,55 s; validador de HTML e links percorreu 396 páginas com zero erros; `git diff --check` limpo. O diff do refinamento não altera seletores de navegação ou barras laterais. Captura visual após a mudança e verificação manual em dispositivos continuam pendentes; os resultados de build não substituem essa inspeção.

## 30. Índice Markdown sem metadados nulos — 2026-10-22

A auditoria do índice completo encontrou rótulos pouco profissionais em grupos singulares (“1 diplomas”) e um risco de publicar `None` quando campos opcionais de número/ano chegam vazios. A geração agora normaliza valores nulos antes de construir os registros do site, omite identificadores de número/ano que não existam e flexiona “diploma”/“diplomas” no total e nos grupos. O índice foi regenerado sem `nº None` ou `None/ano`; seus 375 links continuam apontando para documentos canônicos existentes. Foi acrescentado um caso de regressão para a forma singular e campos ausentes.

Verificações desta etapa: 65 testes via `python -m unittest discover -s tests -v`; `CI=true mkdocs build --strict` em 47,87 s; validador de links/HTML em 396 páginas, zero erros; `validate_release.py --stabilization` com 375 documentos, 33/33 P0 e zero erros; Markdown (754 arquivos), nove workflows, compilação Python e `git diff --check` aprovados. Uma auditoria do README encontrou 41 referências locais (links e assets), todas existentes; um teste protege essa propriedade. A saída do índice foi conferida estruturalmente; revisão no renderizador real do GitHub e inspeção visual interativa ainda não foram executadas.

**Estado de lançamento:** a candidata local segue não publicada. Em nova leitura HTTP do Pages em 2026-10-22, a homepage retornou 200, manteve a âncora de audiência antiga e ainda não contém `hero-graph-node` nem `hero-graph-relation-list`; produção e candidata continuam divergentes. Permanecem gates materiais: revisão visual real em desktop/mobile e teclado/leitor de tela; avaliação das direções de marca e confirmação de titularidade/escopo dos assets; validação de trechos e alegações contra as fontes escolhidas; confirmação de release/corte e distribuição; e publicação/checagem pública da revisão candidata. Os checks automatizados não substituem esses passos nem constituem aprovação jurídica/editorial.

## 31. Navegação por grafo no site e no README — 2026-10-22

### Explorador interativo no GitHub Pages

A página `site_docs/graph.md` agora contém um explorador interativo alimentado por `site_docs/generated/graph-index.json`, gerado diretamente de `bases/derived/relacoes/normative-graph.jsonl`. O índice preserva os 375 diplomas e as 1.841 relações direcionais do corpus, incluindo origem, destino e tipo. Na página, a pessoa pode pesquisar por nome, número ou identificador; filtrar por tipo de relação e direção; selecionar um diploma para navegar pelos vizinhos; abrir a ficha Markdown canônica; e percorrer a lista completa de relações filtradas em grupos com paginação. A visualização SVG limita a 18 vizinhos por vez para manter legibilidade; a lista textual conserva as relações filtradas. O JavaScript é incluído somente em `graph.md`, e cada nó oferece controles acessíveis por teclado e nomeados para leitor de tela.

### Navegação de grafo no README

O build gera uma prévia SVG estática em `site_docs/assets/normative-graph-preview.svg`, vinculada à página interativa do Pages. A seção gerada do README também lista relações reais de uma amostra determinística derivada do mesmo índice; origem e destino são links diretos para os respectivos Markdown canônicos. O README explica que a prévia é estática e aponta para filtros e navegação completos no Pages. Essa escolha respeita o renderizador do GitHub: SVG não executa scripts inline ali, então a interação completa não é prometida dentro do README.

### Evidência e validação

- `python tools/site/build_site.py`: 375 documentos, 35 domínios e 1.841 relações.
- Suíte completa: 68 testes aprovados, incluindo paridade integral de direção e triplas com o JSONL de origem, links do README e carregamento do script apenas na página de grafo.
- `CI=true mkdocs build --strict`: aprovado; saída HTML verificada estruturalmente para presença do explorador e do índice JSON e ausência do script na home.
- `VMD_REQUIRE_SOCIAL_CARDS=1 python tools/validate/validate_site.py --site site`: 396 páginas HTML, zero erros.
- Compilação Python, `node --check` e `git diff --check` aprovados; validação de release: 375 documentos, 33/33 P0, zero erros.
- A interação ainda não foi exercitada em navegador visual, com teclado físico ou leitor de tela nesta sessão. A validação estrutural e automatizada não substitui essa revisão.

**Estado:** a navegação por grafo está implementada na candidata local e coberta pelos checks automatizados. Não foi publicada; a produção continua na versão anterior até o fluxo de release autorizado. O teste visual e acessível em navegador permanece pendente.

## 32. Links compartilháveis no grafo e reconciliação com produção — 2026-10-22

### Histórico e deep links do explorador

Selecionar um diploma no explorador agora grava seu ID no parâmetro `?node=` sem recarregar a página. Abrir ou compartilhar essa URL restaura o mesmo nó; os botões Voltar/Avançar do navegador percorrem a sequência de diplomas selecionados. Seleções feitas por busca e por teclado/toque/mouse no SVG usam a mesma navegação. A página explica esse comportamento. A escolha de tipo/direção e a paginação das relações continua local à sessão; apenas o diploma focado entra na URL.

### Verificações da candidata

- `node --check site_docs/javascripts/graph-explorer.js` passou.
- O contrato do explorador verifica leitura/gravação do parâmetro `node`, `history.pushState`, tratamento de `popstate` e instrução visível de compartilhamento/histórico.
- Suíte integral: 68 testes aprovados.
- `CI=true mkdocs build --strict`: aprovado em 82,14 s; o HTML foi emitido para 396 páginas.
- `validate_site.py` com cartões sociais obrigatórios: 396 páginas, zero erros.
- Markdown UTF-8 (754 arquivos), nove workflows, release (375 documentos, 33/33 P0, zero erros) e `git diff --check` passaram.

### Produção e evidência visual

A inspeção de estado externo confirma que `origin/main` ainda aponta para o commit-base local `dfcb453`; as mudanças desta candidata seguem no working tree sem commit. A página pública do site e a rota `/graph/` respondem HTTP 200, mas a resposta atual não contém a interface `data-graph-explorer` nem o script do histórico por `node`. O README servido pelo GitHub também é anterior à seção atual do grafo. A release pública marcada como Latest é `v1.1.2`, criada a partir do commit `6819b37`, sem incluir esta candidata. Esses dados confirmam que o site e README públicos ainda não foram atualizados.

Os PNGs arquivados em `reports/rebranding-preview/` não podem servir como evidência visual da candidata atual: uma captura de 320 px mostra o antigo desenho com rótulos genéricos “FONTE”/“ART. 186”, enquanto o HTML atual constrói o subgrafo com diplomas reais. O navegador conectado não está disponível nesta sessão; Computer Use retornou falha de pipe nativo e a lista de navegadores/apps está vazia. Não tentei iniciar outro navegador headless. Portanto, capturas atuais e interação visual/teclada/leitor de tela seguem pendentes.

**Estado:** deep links e navegação de histórico estão implementados e cobertos por checks automatizados. A produção continua na release anterior; publicação, inspeção visual atual e validação manual de acessibilidade não estão concluídas.

## 33. Direção de marca aplicada e contraste dos tokens de texto — 2026-10-22

### Decisão para esta candidata

Para manter a execução avançando sem declarar uma preferência de usuários que não foi pesquisada, a direção **Índice normativo** foi adotada como base da candidata. O **Registro de evidência** organiza proveniência e corte nos metadados; o **Atlas de relações** permanece como ferramenta do grafo real. O racional é priorizar localizar, ler e citar diplomas, e usar estrutura de dados para sustentar a confiança sem fazer a interface parecer órgão oficial ou dashboard. `docs/BRANDING.md` e `docs/BRAND_DIRECTIONS.md` agora registram essa decisão e suas aplicações no README, homepage, leitor e ativos. A identidade ainda é candidata até avaliação de advogados, pesquisadores e profissionais de tecnologia; nenhum feedback foi inventado ou presumido.

### Auditoria reproduzível dos pares sólidos de texto

Os tokens atuais foram calculados em sRGB sobre superfícies sólidas claras e escuras. Ink, Slate, Green, Gold text, Amber text e Red no tema claro; Dark text, Slate, Green, Gold text, Amber e Red no tema escuro superam 4,5:1 nos pares descritos em `docs/BRANDING.md`. O teste `test_brand_text_tokens_meet_wcag_aa_on_declared_flat_surfaces` lê os valores diretamente de `extra.css` e falha se qualquer par cair abaixo do limiar. Os valores exatos calculados e os tokens correspondentes estão documentados junto ao sistema visual.

O resultado é limitado a cores sólidas declaradas. Não certifica gradientes, transparências, estados de foco, bordas e ícones, artefatos sociais, contraste de gráficos ou combinações que dependam do renderizador. A revisão visual e a avaliação manual com teclado/leitor de tela seguem pendentes.

### Validação

- Pares do tema claro: 7/7 aprovados; pares do tema escuro: 7/7 aprovados, todos com no mínimo 5,04:1 nos pares avaliados.
- Suíte integral reexecutada: 69 testes aprovados, incluindo o contrato de contraste.
- `python tools/check_markdown.py docs`: 22 arquivos UTF-8 válidos; `git diff --check` sem erros.
- As duas cópias do plano mestre continuam sincronizadas por hash.

**Estado:** decisão interna de design e baseline de contraste são reproduzíveis na candidata. Pesquisa com usuários, inspeção de estados reais nos dois temas, direitos dos assets e publicação continuam em aberto.


## 34. Coerência das imagens sociais — 2026-10-22

A inspeção dos PNGs do build mostrou que a homepage exibia o símbolo da marca, enquanto a imagem da página “Grafo normativo” não. Configurei o caminho do lockup compacto local em `cards_layout_options.logo` no plugin social, para que todas as páginas-chave incluam a mesma assinatura visual. A opção segue a documentação oficial do [plugin social do Material for MkDocs](https://squidfunk.github.io/mkdocs-material/plugins/social/); o SVG do símbolo já é resolvido pelo tema e o build passou sem depender de um serviço de runtime.

As imagens PNG recém-geradas para home, grafo e catálogo foram abertas e inspecionadas: as três exibem wordmark, símbolo, paleta Ink/Ivory e tipografia editorial na proporção 1200 × 630. Essa revisão é visual dos artefatos de compartilhamento, não revisão interativa da página nem teste em cada rede social.

- `CI=true mkdocs build --strict`: aprovado em 81,11 s.
- Validador do site com cartões obrigatórios: 396 páginas HTML, zero erros.
- Suíte completa: 69 testes aprovados; nela, 14 pares de contraste dos tokens mantêm pelo menos 4,5:1.
- Markdown de docs: 22 arquivos válidos; workflows: nove aprovados; release: 375 documentos, 33/33 P0, zero erros; `git diff --check` limpo.

**Estado:** cartões sociais da candidata têm assinatura consistente e foram inspecionados como PNGs. README real no GitHub, screenshots atuais de páginas, validação com usuários, licença dos ativos e publicação seguem pendentes.

## 35. Continuidade do foco no explorador — 2026-10-22

A interação do grafo agora preserva o foco previsível do teclado. Ao selecionar um vizinho no SVG, o desenho é atualizado e o foco vai para o nó recém-centralizado, permitindo continuar a exploração sem recomeçar pela navegação da página. Ao selecionar uma sugestão de busca, o foco volta ao campo de busca; a consulta `aria-expanded` acompanha a abertura/fechamento das sugestões, inclusive quando não há resultados e ao pressionar Escape. O grupo de sugestões recebe um rótulo acessível. Um clique no nó já selecionado não redesenha a visualização nem perde o foco.

A página explica a interação com mouse, toque ou teclado. `test_graph_explorer_has_search_filters_accessible_edges_and_page_scoped_script` protege a semântica de estado da busca e os dois destinos de foco. Essa cobertura verifica os contratos no código/markup; não substitui teste prático com leitor de tela.

- `node --check` e o teste focal passaram.
- `CI=true mkdocs build --strict`: aprovado em 81,54 s.
- Suíte completa: 69 testes aprovados.
- Validador de links, cartões, semântica e 396 páginas HTML: zero erros.
- Docs (22 Markdown UTF-8), nove workflows, release (375 documentos, 33/33 P0, zero erros) e `git diff --check` passaram.

**Estado:** continuidade do foco e semântica dinâmica da busca estão implementadas e protegidas por regressão. Interação visual manual, leitores de tela reais e publicação permanecem pendentes.

## 36. Auditoria integral de fidelidade no corte da candidata — 2026-10-22

Reexecutei `tools/audit_fidelity.py --strict` sobre os snapshots oficiais completos já coletados (collection full v5 e expansão editorial) para verificar o estado corrente do corpus. A auditoria comparou unidades normativas dos 375 documentos e retornou `pass: 375`, sem revisão pendente. O novo JSON foi comparado ao relatório versionado: todo o conteúdo e as contagens eram idênticos; atualizei somente `generated_at` para 2026-10-22, mantendo os hashes e evidências existentes. O relatório canônico agora registra a data da verificação de lançamento.

Este resultado demonstra equivalência determinística do texto publicado às unidades dos snapshots oficiais registrados. Não comprova atualização posterior dos snapshots, vigência jurídica na data atual, interpretação ou completude semântica fora das unidades definidas.

- `python tools/audit_fidelity.py --strict --output <temp>`: 375/375 `pass`.
- `python tools/validate_release.py --stabilization`: 375 documentos, 33/33 P0, zero erros.
- Testes de contrato de fidelidade: 3 aprovados; `git diff --check` limpo.

**Estado:** fidelidade textual ao conjunto de snapshots disponíveis revalidada e registrada. A revisão jurídica por conteúdo, atualidade posterior ao snapshot, experiência visual/manual, licença de marca e publicação continuam como gates separados.

## 37. Contrato de segurança e acessibilidade dos vetores — 2026-10-22

Os seis SVGs ativos em `site_docs/assets/` foram auditados e agora têm contrato de regressão: XML válido; raiz SVG; `<title>` e `<desc>`; nenhum script ou `foreignObject`; IDs únicos; referências `href` apenas locais; nenhuma chamada HTTP em `@import` ou `url()`. O teste `test_brand_svg_assets_are_accessible_self_contained_and_have_unique_ids` percorre automaticamente todo o diretório, incluindo o lockup escuro e a prévia do grafo. A auditoria corrente encontrou seis arquivos e zero violações.

O contrato reduz risco técnico de scripts, recursos remotos e nomes acessíveis ausentes nos ativos vetoriais. Ele não comprova autoria, direitos sobre o símbolo/logotipo, licenças de tipografia nem legibilidade real em cada tamanho.

- Teste focal: aprovado para os seis SVGs.
- Suíte integral: 70 testes aprovados.
- `py_compile`, `git diff --check` e validação UTF-8 dos 22 documentos de `docs/` passaram.

**Estado:** higiene e metadados dos vetores estão protegidos no CI. A licença e titularidade continuam pendentes de declaração do responsável pela marca; a reprodução final do favicon e a revisão manual de marca permanecem gates distintos.


## 38. Escopo da licença de código e marca — 2026-10-22

A pedido do responsável pelo projeto, a licença foi explicitada como MIT para o código e a marca. `LICENSE.md` agora traz o texto integral da licença, identifica Luciano Molero (autor registrado no commit de origem dos vetores, `aefec1c`, de 2026-10-21) e inclui documentação autoral e ativos de marca/design, como logos, favicon, vetores, capas e imagens sociais autorais. O README aponta para essa licença. O inventário visual registra o escopo e a proveniência sem tratar o histórico Git como prova independente de titularidade.

Atos normativos federais, reproduções de publicações oficiais e materiais de terceiros permanecem expressamente fora da concessão e sujeitos ao regime aplicável a cada fonte. Source Serif 4, utilizada pelo plugin somente na geração de cartões sociais, continua como dependência externa com licença própria; nenhuma fonte foi incorporada nos vetores autorais.

- Histórico de origem dos lockups e marca: commit `aefec1c`, atribuído a Luciano Molero em 2026-10-21.
- Escopo MIT registrado em `LICENSE.md`, README, `docs/BRANDING.md` e `docs/ASSET_INVENTORY.md`.
- Revisão final do titular para o uso pretendido, revisão humana da identidade, pesquisa com usuários e publicação continuam gates separados.

**Estado:** escolha da licença aplicada e documentada; isso não encerra a revisão de marca nem autoriza alegações de atualização jurídica do corpus.

## 39. README como índice de leitura — 2026-10-22

O README foi reorganizado para servir primeiro à tarefa principal de encontrar e abrir uma lei. A entrada oferece o índice completo dos 375 documentos, rotas por coleção/tipo, atalhos Markdown para diplomas de uso frequente e um link separado para a pesquisa no GitHub Pages. O grafo real permanece navegável por uma prévia estática com relações e extremos ligados aos documentos canônicos; o README esclarece que interações completas estão no Pages. Removidos badges da Agent Skill e licença e listas de funcionalidades repetidas para reduzir ruído e manter a orientação de leitura em primeiro plano. Não há caracteres emoji no README.

Mantidos na página o corte do snapshot, limites de uso, proveniência, rota para a release e contribuições. A contagem do corpus é explicitamente vinculada ao corte informado e não sugere cobertura universal ou atualização em tempo real.

- Testes focais de links relativos/assets, afirmações estáticas no GitHub e links canônicos do grafo: 3 aprovados.
- Varredura de caracteres emoji e adornos pictográficos: zero ocorrências.
- `git diff --check`: aprovado.

**Estado:** README local funciona como índice compacto e sem emojis; renderização atual no GitHub e avaliação visual com leitores continuam pendentes até publicação e revisão em navegador.

## 40. Revalidação da candidata e divergência em produção — 2026-10-22

Revalidei a candidata completa após o refinamento do README. O build foi feito em checkout temporário no filesystem Linux para reproduzir o ambiente de CI: a tentativa nativa Windows abortou em modo estrito porque o plugin de cartões sociais não encontrou a biblioteca Cairo. No Linux, `CI=true python tools/site/build_site.py` derivou 375 documentos, 35 domínios e 1.841 relações; `CI=true mkdocs build --strict` concluiu em 47,76 s. `VMD_REQUIRE_SOCIAL_CARDS=1 python tools/validate/validate_site.py --site site` percorreu 396 páginas e encontrou zero erros. A cópia temporária continha apenas as pastas e fontes necessárias ao build, sem `.private` ou `reports`.

A suíte completa local passou com 70 testes; `tools/check_markdown.py docs` validou 22 documentos UTF-8; `tools/validate_release.py --stabilization` encontrou 375 documentos, 33/33 P0 e zero erros; `git diff --check` passou. O plano local e a cópia Antigravity foram sincronizados pelo mesmo SHA-256.

### Evidência atual da produção

- API do GitHub: `main` permanece em `dfcb4537609ef67d6e2085fb2b24357893643a3c`; o check `quality` e o workflow `site` desse commit concluíram com sucesso. A branch está protegida e exige o check `quality`.
- A release pública Latest continua `v1.1.2`, no commit `6819b37ade18ffe8391bf9772dfeef8c543bf291`.
- A homepage e `/graph/` respondem HTTP 200, mas nenhuma contém `data-graph-explorer`; a homepage também não contém `hero-graph-node`. A candidata com explorador real continua apenas local.
- O README renderizado do repositório ainda é a versão institucional anterior, com emojis, alegações comparativas sem evidência e afirmações de situação jurídica que a revisão local removeu.
- Há seis PRs abertos do Dependabot para GitHub Actions. Eles não foram mesclados nesta revisão.
- O navegador conectado não está disponível (`apps=[]`, `browsers=[]`). A skill `computer-use` foi procurada nos diretórios de skill declarados e não foi encontrada. Logo, não há inspeção visual interativa, teclado físico ou leitor de tela real nesta rodada.

**Estado:** gates automatizados da candidata foram reexecutados em ambiente Linux e passaram. A produção permanece defasada; a prontidão final segue não demonstrada até revisão visual/acessível em browser, avaliação humana de conteúdo e marca, e integração/publicação pelo fluxo protegido com verificação pós-deploy. A falha de dependência Cairo no Windows permanece uma limitação do ambiente de build local, não do build Linux de Pages.

## 41. Refatoração compacta da homepage e do leitor — 2026-10-22

A homepage foi reestruturada para começar pela busca e pela leitura. O hero agora apresenta uma chamada curta, uma busca sem sobreposição e um painel compacto do grafo real com cinco nós canônicos selecionados do índice de relações. Cada nó abre o documento correspondente; as linhas terminam antes dos nós para preservar as setas, os rótulos mostram tipo e identificação curta, e detalhes da relação ficam recolhidos por padrão. Seis leis frequentes oferecem acesso direto. A home deixa de repetir blocos extensos de audiência, domínios e argumentos institucionais.

O centro da página foi limitado a uma coluna mais estreita, preservando as sidebars. A tipografia geral foi reduzida e o texto normativo passa a usar 14 px no padrão, com opções de 13, 15 e 16 px, largura de leitura de 72ch e entrelinha de 1,62. A barra de controles do leitor é compacta e não permanece fixa durante a rolagem. A configuração antiga de fonte não força tamanhos grandes: a chave de preferência foi migrada e os controles indicam os limites disponíveis.

- Suíte completa: 71 testes aprovados.
- `node --check site_docs/javascripts/reader.js` e `git diff --check`: aprovados.
- Build de Pages em Linux com `CI=true mkdocs build --strict`: aprovado.
- Validador de site: 396 páginas HTML, zero erros.
- Testes focais de homepage e leitor: 24 aprovados.

**Estado:** a candidata local tem estrutura, navegação, tipografia e contratos automatizados atualizados. A publicação ainda mostra a versão anterior. Esta rodada não teve inspeção visual interativa em navegador conectado; conferir o render em desktop e celular após a integração/deploy continua necessário.

## 42. Auditoria de prontidão e gates remanescentes — 2026-10-22

Reauditei a candidata e o estado remoto para distinguir evidência de implementação de evidência de lançamento. A versão do plano foi elevada para 10; o painel de prontidão no início deste arquivo agora é o resumo autoritativo, com decisão NO-GO e sequência bloqueante. Incluí um protocolo formativo de cinco sessões e tarefas reproduzíveis para README, busca, proveniência, grafo e leitor, sem tratar uma amostra pequena como certificação de acessibilidade ou pesquisa representativa.

### Evidência local revalidada

- Suíte `pytest`: 71 aprovados; suíte de CI `python -m unittest discover -s tests -v`: 71 aprovados.
- Build Linux `CI=true mkdocs build --strict`: aprovado; `validate_site.py` percorreu 396 páginas HTML, zero erros.
- Fidelidade estrita: 375/375 documentos `pass`; release: 375 documentos, 33/33 gates P0 e zero erros.
- Matriz editorial: 375/375, zero drift; grafo: 1.841 relações, zero duplicatas e zero conflitos de tipo inverso.
- Markdown: 754 arquivos UTF-8; nove workflows validados; expansão editorial com 15 candidatos, zero erros.
- Três scripts JavaScript passaram em `node --check`; `git diff --check` passou.
- A integração de navegador segue indisponível (`apps=[]`, `browsers=[]`), então não há capturas atuais nem inspeção manual visual, de teclado ou leitor de tela.

### Evidência remota revalidada

- `main` continua em `dfcb4537609ef67d6e2085fb2b24357893643a3c`; `quality` é o status obrigatório e a branch exige checks estritos.
- O workflow Pages mais recente observado para `main` concluiu com sucesso em 2026-10-22 05:06 UTC; isso só valida o conteúdo já em `main`, não esta candidata local.
- A release `v1.1.2` continua como Latest. A página e `/graph/` respondem HTTP 200, mas a homepage não contém o novo título nem `hero-graph-node` e `/graph/` não contém `data-graph-explorer`.
- Há seis PRs abertos do Dependabot para majors de GitHub Actions; todos mostram check `quality` concluído com sucesso, mas nenhum tem decisão de revisão. Não foram mesclados nesta mudança.

**Decisão:** manter NO-GO. O candidato local passou os gates automatizados reexecutados; não está integrado nem publicado. Faltam revisão visual/acessível em navegador real, avaliação formativa com pessoas, validação final de titularidade e amostras, orçamento de desempenho medido, mapa de compatibilidade/rollback demonstrado e smoke test pós-deploy. A automação não pode provar esses itens.