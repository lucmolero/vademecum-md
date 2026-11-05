# Uso da skill

## Ativação

### Sem terminal: kit pronto para abrir no agente

Baixe o [kit completo para agentes](https://lucmolero.github.io/vademecum-md/downloads/vademecum-consulta-juridica-kit.zip), extraia e abra a pasta no Codex, Claude Code, Cursor ou OpenCode. Ele contém a skill e o corpus da mesma release, em pastas próprias. A skill é descoberta pelas pastas de projeto `.agents/skills/` (Codex, Cursor e OpenCode) ou `.claude/skills/` (Claude Code); o corpus fica em `corpus/`. Não precisa de Node.js, npm ou `npx`.

Para adicionar ao projeto que já está aberto, use na homepage **Copiar instrução para o agente**. O agente baixa o kit, confere o SHA-256, instala a skill na pasta de projeto do agente e coloca os dados em `.vademecum-md/releases/<versão>/`. Aponte `.vademecum-md/current.json` para a release instalada. O kit inclui `README.md` com o procedimento e o manifesto lista os hashes dos arquivos.

O ponteiro do projeto tem este formato, com a versão realmente instalada:

```json
{
  "schema": "vademecum-corpus-pointer/v1",
  "release": "1.2.1",
  "path": "releases/1.2.1"
}
```

Para uma instalação pessoal, use como pasta de dados `%LOCALAPPDATA%/VadeMecumMD` no Windows, `~/Library/Application Support/VadeMecumMD` no macOS ou `${XDG_DATA_HOME:-~/.local/share}/vademecum-md` no Linux. O ponteiro `current.json` fica nessa pasta. Para usar outro local, defina `VADEMECUM_MD_DATA` para uma pasta de dados que contenha esse ponteiro.

### Instalação por CLI

Se já usa Node.js 22.20 ou superior, o CLI `skills` instala apenas as instruções da skill:

```sh
npx skills add lucmolero/vademecum-md --skill vademecum-consulta-juridica --agent codex --global --yes
```

Troque `codex` pelo identificador do agente (`claude-code`, `cursor` ou
`opencode`). Remova `--global` para instalar somente no projeto atual. Esse
comando não baixa o corpus; para isso, baixe o kit completo ou abra o repositório
VadeMecum MD no workspace do agente. Para outros agentes compatíveis, consulte a
[lista oficial de agentes](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).

### Onde a skill procura os dados

A skill procura o repositório aberto no workspace, `corpus/` no kit extraído,
`.vademecum-md/current.json` no projeto ou o diretório pessoal de dados do
VadeMecum MD. Para personalizar o último caminho, defina
`VADEMECUM_MD_DATA`. Instalar só a skill não concede acesso ao corpus.

O formato `SKILL.md` é compartilhado por ecossistemas compatíveis com Agent
Skills, incluindo Codex e Claude. A skill não concede acesso ao repositório. Para
consultar o corpus, disponibilize os arquivos da release, o site ou uma
ferramenta de leitura já autorizada no ambiente.

## Exemplos de solicitação

**Consulta objetiva**

> No corpus disponível, qual é a redação do art. 5º da norma identificada por
> [ID ou tipo, número e ano]? Informe a release, a data de corte e a fonte
> oficial.

**Análise**

> Com base nos documentos disponíveis, analise a questão [descreva a questão].
> Use IRAC, cite os dispositivos e indique a release, o corte e as limitações.

**Referência acadêmica**

> Gere uma referência em ABNT para o diploma citado, usando apenas os dados
> verificáveis no corpus e mantendo o ID, a release, o corte e a fonte oficial.

**Sem acesso ao corpus**

> Verifique se você consegue acessar este repositório. Se não conseguir, diga
> quais dados ou arquivos preciso fornecer; não responda de memória como se
> tivesse consultado o corpus.

## Formato sugerido de citação em respostas

> **Fonte no corpus:** [título do diploma], [dispositivo], ID `[document_id]`,
> VadeMecum MD [release], corte em [data_corte]. **Fonte oficial:** [URL].

Esse modelo é informativo e não substitui a referência acadêmica exigida pelo
usuário ou pela instituição. Se algum campo estiver ausente, marque-o como não
verificado em vez de inventá-lo.

## Referências do projeto

- [Contrato machine-readable](https://github.com/lucmolero/vademecum-md/blob/main/manifests/consumer-contract.json).
- [Schema do corpus](https://github.com/lucmolero/vademecum-md/blob/main/docs/SCHEMA.md).
- [Política de proveniência](https://github.com/lucmolero/vademecum-md/blob/main/docs/SOURCES.md).
- [Guia de públicos e consumo](https://github.com/lucmolero/vademecum-md/blob/main/site_docs/audiences.md).
- Cenários de avaliação: [`evals.md`](evals.md).
