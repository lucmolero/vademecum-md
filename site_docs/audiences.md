# Como usar o VadeMecum MD

O VadeMecum MD é uma base pública de leitura e análise normativa. A página de
um diploma e os arquivos do repositório são interfaces de consulta; o projeto
não é um sistema de gestão jurídica, não presta aconselhamento e não promete
cobrir todo o Direito brasileiro.

Há duas formas principais de usar o mesmo corpus: leitura humana e consulta por
agentes de IA. Integrações de dados são uma forma de distribuir e preparar o
conteúdo para esses usos, não uma camada normativa separada.

## Para advogados e pesquisadores jurídicos

### Localizar, ler e citar

1. Encontre o diploma pelo [catálogo da legislação](generated/catalog.md) ou
   pela busca do site.
2. Confirme o ID, a situação, o estado de consolidação e a data de corte.
3. Leia o dispositivo no corpo do diploma e siga as relações como contexto
   editorial, não como substitutas do texto legal.
4. Abra a fonte oficial indicada antes de usar o texto em trabalho profissional
   ou acadêmico.
5. Registre diploma, dispositivo, release, data de corte e fonte oficial.

Exemplo de referência rastreável:

```text
br-federal-lei_ordinaria-10406-2002, art. 1º
VadeMecum MD, release v1.1.2, corte 2026-10-21.
Fonte oficial indicada no documento: https://normas.leg.br/?urn=urn:lex:br:federal:lei:2002-01-10;10406
```

O site é uma camada de leitura derivada. Para citação acadêmica, a referência
pode ser formatada no estilo solicitado, preservando os dados de identificação
e proveniência acima.

## Para agentes de IA

### Consultar com evidência

Um agente só pode usar o conteúdo que estiver acessível no contexto, nos arquivos
fornecidos ou por uma ferramenta de leitura disponível. A skill do projeto
instrui o agente a localizar a norma, verificar o corte e o estado, separar
texto legal de metadados e relações, e citar a fonte. Ela não concede acesso
automático ao GitHub nem transforma o corpus em conhecimento completo ou sempre
atual.

Uma resposta fundamentada identifica, quando aplicável:

```json
{
  "document_id": "br-federal-lei_ordinaria-10406-2002",
  "dispositivo": "art. 1º",
  "release": "v1.1.2",
  "data_corte": "2026-10-21",
  "fonte_oficial": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm",
  "limitacoes": []
}
```

O agente não deve completar texto ausente, afirmar vigência atual com base em
estado histórico ou desconhecido, ocultar conflito entre fontes nem converter
uma relação do grafo em comando normativo. Se não conseguir ler o documento,
deve declarar a limitação e pedir uma fonte acessível.

Use resposta direta e citada para perguntas de localização. Para análise
jurídica, organize a resposta em Questão, Regra, Aplicação e Conclusão quando
isso for apropriado. Referências ABNT podem ser produzidas quando solicitadas;
elas complementam, mas não substituem, os identificadores e a fonte oficial.

Consulte a [skill de consulta jurídica](https://github.com/lucmolero/vademecum-md/blob/main/skills/vademecum-consulta-juridica/SKILL.md) e o
[contrato de consumo](contract.md) para instruções e exemplos.

## Para integrações e pipelines

O repositório oferece artefatos versionados para montar uma experiência de
consulta ou indexação:

| Necessidade | Artefato | Uso |
| --- | --- | --- |
| Baixar o corpus de uma release | pacote ZIP e manifesto da release | fixa a versão e valida os checksums |
| Enumerar diplomas | `manifests/corpus.csv` | catálogo estruturado com IDs estáveis |
| Ler norma e metadados | Markdown canônico e frontmatter | preserva corpo, estado, corte e fontes |
| Consultar relações | `bases/derived/relacoes/normative-graph.jsonl` | grafo derivado com evidência e direção |
| Interpretar o contrato | `manifests/consumer-contract.json` | campos de citação, limites e perfis |

Fixe uma release para análises reproduzíveis. Não use o HTML do site como
interface de dados primária e não misture documentos, histórico e relações sem
preservar suas camadas e datas.

## Limites comuns

- O corpus é uma seleção curada, não uma declaração de cobertura integral da
  legislação brasileira.
- A data de corte pertence ao snapshot publicado; ela não é garantia de
  atualização em tempo real.
- Estados como `requer_reconciliacao`, `historica` e `desconhecida` não
  sustentam afirmação de vigência atual.
- O texto oficial indicado no documento prevalece para verificação normativa.
- Site, grafo, skills, índices e métricas são artefatos derivados e não fontes
  oficiais.
