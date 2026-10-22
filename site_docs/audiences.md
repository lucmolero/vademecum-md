# Três públicos, um corpus

O VadeMecum MD é um produto editorial em Markdown com três superfícies de
consumo. O texto normativo é único; o modo de trabalhar com ele muda conforme
o objetivo.

O corpus não é uma publicação oficial, não substitui a consulta à fonte
governamental e não oferece aconselhamento jurídico. Em qualquer uso, a fonte
oficial indicada no diploma e a data de corte são parte da resposta.

## Para advogados e pesquisadores jurídicos

### O que o produto entrega

- leitura integral em Markdown, com hierarquia preservada;
- identificação estável do diploma e navegação por artigo;
- ementa, situação, consolidação e data de corte visíveis;
- fonte oficial destacada e acesso direto à publicação pública;
- relações normativas e histórico em camadas separadas;
- citação reproduzível por `id`, artigo, release e fonte.

### Protocolo de leitura

1. Abra o diploma pelo [catálogo](generated/catalog.md) ou pela busca.
2. Confirme `situacao`, `consolidacao_status` e `data_corte`.
3. Leia o dispositivo no corpo canônico ou na página derivada.
4. Verifique a fonte oficial antes de tomar uma decisão profissional.
5. Cite o identificador, o dispositivo, a release e a URL oficial.

Exemplo de citação operacional:

```text
br-federal-lei_ordinaria-10406-2002, art. 1º
VadeMecum MD v1.1.0, data de corte 2026-10-21.
Fonte oficial: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm
```

O site melhora a leitura, mas não é a autoridade normativa: ele é regenerado a
partir de `bases/curated` e pode ser comparado com o Markdown publicado.

## Para cientistas de dados

### Contrato de dados

O consumo deve começar pelos manifestos, e não por scraping do HTML do site.

| Necessidade | Artefato canônico | Garantia operacional |
| --- | --- | --- |
| catálogo e caminhos | `manifests/corpus.csv` | um registro por diploma |
| metadados e fontes | frontmatter Markdown | schema versionado |
| relações | `bases/derived/relacoes/normative-graph.jsonl` | uma relação por linha |
| qualidade | `manifests/completeness.json` e relatórios | gates reproduzíveis |
| release | `manifests/release.json` | versão e data de corte |

Cada documento tem `id` estável. Hashes possuem escopo explícito: origem bruta,
fonte normalizada, corpo normativo e corpo publicado não são intercambiáveis.
Uma alteração de texto deve gerar nova evidência; nunca deve ser absorvida por
uma atualização silenciosa.

### Exemplo de inventário determinístico

```python
import csv
from pathlib import Path

with Path("manifests/corpus.csv").open(encoding="utf-8", newline="") as stream:
    corpus = list(csv.DictReader(stream, delimiter=";"))

vigentes = [row for row in corpus if row["status_situacao"] == "em_vigor"]
print({"total": len(corpus), "em_vigor": len(vigentes)})
```

Para análises comparáveis, fixe a release, preserve o arquivo de manifestos e
registre a versão do schema. Não derive métricas de títulos renderizados nem
misture histórico com o corpus curado.

### Princípios de engenharia de dados

- **idempotência:** a mesma entrada oficial produz a mesma saída;
- **proveniência:** cada transformação aponta para sua origem e seu hash;
- **separação de camadas:** corpus, histórico, grafo e site têm papéis distintos;
- **falha segura:** conflito ou fonte indisponível preserva a versão anterior;
- **reprodutibilidade:** uma release pode ser reconstruída e verificada;
- **validade temporal:** a data de corte é um atributo do conjunto, não um detalhe.

## Para desenvolvedores de agentes de IA

### O que o agente pode assumir

O agente pode usar o corpus como base documental versionada quando respeitar o
contrato abaixo:

1. buscar por `id`, título, número, domínio ou artigo;
2. recuperar o Markdown canônico ou um artefato derivado identificável;
3. verificar a data de corte e o status de consolidação;
4. citar o dispositivo e a fonte oficial;
5. separar texto normativo de inferência, resumo e relação derivada;
6. declarar insuficiência quando a evidência não sustentar uma conclusão.

### Resposta mínima com evidência

Uma skill ou ferramenta consumidora deve produzir uma estrutura equivalente a:

```json
{
  "answer": "resposta fundamentada no dispositivo recuperado",
  "citations": [
    {
      "document_id": "br-federal-lei_ordinaria-10406-2002",
      "dispositivo": "art. 1º",
      "release": "v1.1.0",
      "data_corte": "2026-10-21",
      "fonte_oficial": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm"
    }
  ],
  "limitations": ["confirmar a redação vigente na fonte oficial"]
}
```

O agente não deve afirmar vigência atual quando o documento estiver marcado
como `requer_reconciliacao`, `desconhecida` ou `historica`. Também não deve
transformar uma relação do grafo em texto legal nem inventar um dispositivo
ausente.

### Preparação para agentes sem RAG prematuro

O corpus foi desenhado para futura recuperação híbrida, mas RAG e índices
semânticos não são fontes normativas e não fazem parte desta release. Antes de
criar embeddings, estabilize:

- chunking por unidade jurídica, preservando artigo e parágrafo;
- referências ao `document_id` e ao hash do documento;
- filtros por data de corte, situação e release;
- avaliação de recuperação com citações verificáveis;
- testes de recusa para fonte ausente, conflito e texto histórico.

## O que é comum aos três públicos

```text
fonte oficial
      ↓
Markdown canônico
      ↓
metadados + hashes
      ↓
histórico e grafo
      ↓
site e artefatos de release
```

O site é uma camada de apresentação. O Markdown e os manifestos são as
interfaces públicas primárias; relatórios e catálogos são derivados. Essa
separação mantém a leitura confortável sem sacrificar auditabilidade ou
consumo por máquinas.

## Critérios de pronto por público

| Público | Consegue fazer | Evidência |
| --- | --- | --- |
| jurídico | localizar, ler e citar um diploma | página do diploma + fonte oficial |
| dados | enumerar, filtrar e comparar releases | CSV, JSONL, hashes e manifestos |
| agentes | recuperar com identidade e citar com limites | contrato de evidência e exemplos |

Se um fluxo não consegue apontar para a fonte, a release e a data de corte,
ele não está pronto para produção.
