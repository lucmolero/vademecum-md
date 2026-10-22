# Uso da skill

## Ativação

Copie o diretório `vademecum-consulta-juridica` para o local de skills
reconhecido pelo seu agente, ou forneça `SKILL.md` como instrução contextual. O
suporte e o caminho de instalação dependem do ambiente e da versão da plataforma;
consulte a documentação atual do seu agente. Não há dependências ou scripts a
executar.

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

- Contrato machine-readable: `../../manifests/consumer-contract.json`.
- Schema do corpus: `../../docs/SCHEMA.md`.
- Política de proveniência: `../../docs/SOURCES.md`.
- Guia de públicos e consumo: `../../site_docs/audiences.md`.
- Cenários de avaliação: [`evals.md`](evals.md).
