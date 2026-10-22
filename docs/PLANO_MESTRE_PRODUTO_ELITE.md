# VadeMecum MD — Plano Diretor de Produto de Elite (v2)

> **Documento Estratégico de Arquitetura, Marca, UX e Governança**  
> **Status:** Especificação Aprofundada e Pronta para Execução  
> **Diretriz Mandatória:** Exclusão de RAG e MCP nesta fase. Foco absoluto na experiência de leitura de alto nível para juristas, consumo por IA via Skills puras, consolidação de marca de prestígio e excelência na apresentação e organização do repositório.

---

## 1. Visão de Produto: O Vade Mecum Aberto do Século XXI

O mercado jurídico brasileiro divide-se historicamente entre duas experiências insatisfatórias:
1. **Os portais estatais oficiais (ex: Planalto):** Confiáveis na autoridade textual, mas obsoletos na interface (HTML dos anos 1990, poluição de textos riscados, navegação truncada, ausência de busca rápida de artigos e zero padronização computável).
2. **Os portais comerciais privados (ex: Jusbrasil, QConcursos):** Interfaces mais modernas, porém cercadas de paywalls agressivos, exigência de cadastro, anúncios invasivos, rastreadores e falta de rastreabilidade de código aberto.

### A Tese de Produto do VadeMecum MD
O **VadeMecum MD** posiciona-se como a **terceira via definitiva**:
> **A integridade inquestionável do texto oficial com a elegância editorial das grandes publicações jurídicas e a transparência do código aberto.**

---

## 2. Marca, Identidade Visual e Tom de Voz (Branding de Elite)

Para que o projeto transmita autoridade incontestável no primeiro impacto visual (teste dos 5 segundos), a identidade visual deve superar o padrão genérico de documentação de código.

### 2.1 Paleta Cromática Institucional

| Cor | Hex | Aplicação | Significado Semântico |
| :--- | :--- | :--- | :--- |
| **Ink Profundo** | `#13243A` | Cor de base, títulos e navegação principal | Autoridade, estabilidade, precisão institucional |
| **Marfim Nobre** | `#FBF8F0` | Fundo principal da página e leitura | Redução de fadiga visual, tom de papel bíblia de luxo |
| **Dourado Códice** | `#B48A3C` | Acentos, bordas ativas, medalhões e foco | Prestígio editorial, linhagem dos clássicos do direito |
| **Verde Prova** | `#2D7659` | Status "Em Vigor", hashes conferidos e chips | Evidência empírica, fidelidade à fonte oficial |
| **Âmbar Transição**| `#A96D19` | Vacatio legis, regras transitórias, pendências| Cautela interpretativa, vigência diferida |
| **Slate Escuro** | `#0D1828` | Fundo do modo noturno de alta imersão | Contraste calmo para leitura forense em pouca luz |

### 2.2 Sistema Tipográfico
- **Títulos e Diplomas (Display):** Tipografia com serifa clássica de transição (*Newsreader*, *Playfair* ou *Georgia* com kerning calibrado).
- **Corpo Normativo (Leitura):** Tipografia serifa de proporções editoriais (*Charter*, *Spectral* ou *Lora*), com entrelinha relaxada (`line-height: 1.78`) e limite de leitura travado em `74ch`.
- **Metadados e Dispositivos Técnicos:** Monospaçada com números tabulares alinhados (*JetBrains Mono* ou *Geist Mono*).

---

## 3. Apresentação Pública: O Novo README Institucional de Alta Conversão

O `README.md` principal no GitHub (`workspace/README.md`) é a vitrine de entrada. Ele deve causar impacto imediato em investidores, juízes, advogados, acadêmicos e desenvolvedores.

### Elementos Principais do README:
1. **Header com Logotipo Centralizado e Badges de Excelência:** Logotipo `logo-lockup.svg` e badges de release, diplomas, testes e licença.
2. **Vitrine dos Grandes Códigos:** Acesso com 1 clique para CF/88, Código Civil, CPC, CP, CPP, CLT, CDC, Licitações, OAB e CTN.
3. **Guias Dedicados por Público:** Seções claras para juristas, desenvolvedores e agentes de IA.

---

## 4. UX Forense do Leitor Web

1. **Barra de Ferramentas de Leitura Forense (*Reader Toolbar*):**
   - Indicador dinâmico do diploma e artigo ativo;
   - Salto rápido de artigo via `Ctrl + K`;
   - Modo de Leitura Foco (sem distrações laterais).
2. **Botão Forense "Copiar para Petição":** Cópia formatada no padrão dos tribunais e ABNT em 1 clique.
3. **Popovers de Remissão Normativa (*Hover Preview*):** Prévia flutuante de normas referenciadas sem sair da página.

---

## 5. UX para Agentes de IA via Skills Puras

1. **Ancoragem Exclusiva em Dispositivos Presentes:** Sem paráfrase de memória não verificada.
2. **Separação Obrigatória entre Texto Legal e Análise Hermenêutica (IRAC).**
3. **Mecanismo Transparente de Recusa para Leis Fora do Recorte das 375 Curadas.**

---

## 6. Organização do Repositório

1. **Autocontenção Total em `workspace/`:** Eliminação de artefatos avulsos temporários.
2. **Nomes Populares nos Catálogos:** Mapeamento explícito de títulos como "Lei Anticorrupção", "Marco Legal do Saneamento", etc.
