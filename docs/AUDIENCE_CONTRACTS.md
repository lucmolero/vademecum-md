# Contratos de consumo

O VadeMecum MD é um corpus federal curado em Markdown para três públicos:
profissionais do Direito, cientistas de dados e desenvolvedores de agentes de
IA. Este documento define o contrato mínimo comum. O guia completo, com
exemplos, está em [Públicos e consumo](https://lucmolero.github.io/vademecum-md/audiences/).

O contrato machine-readable está em
[`manifests/consumer-contract.json`](../manifests/consumer-contract.json).

## Contrato comum

Todo consumidor deve:

1. fixar uma release e uma data de corte;
2. identificar o diploma por `id`, nunca apenas pelo caminho do arquivo;
3. ler `situacao` e `consolidacao_status` antes de usar o texto;
4. preservar a distinção entre corpo normativo, metadados, histórico e grafo;
5. registrar fonte oficial e dispositivo utilizado;
6. tratar estados `requer_reconciliacao`, `historica` e `desconhecida` como
   insuficientes para afirmar vigência;
7. consultar a fonte oficial antes de uma decisão jurídica ou publicação de
   resultado.

## Perfis e artefatos

| Perfil | Interface primária | Resultado esperado |
| --- | --- | --- |
| jurídico | Markdown canônico + site derivado | leitura e citação contextualizadas |
| dados | `manifests/corpus.csv` + frontmatter + JSONL | pipeline determinístico e reproduzível |
| agentes | documentos, IDs, hashes e relações | recuperação com evidência e limites |

## Separação de autoridade

O agente jurídico pode classificar e propor decisões curatoriais com base em
evidências oficiais. Validadores determinísticos verificam identidade,
integridade, hashes, relações, links e políticas de segurança. Nenhuma dessas
camadas substitui a autoridade da publicação oficial.

## Regras para agentes

Uma resposta gerada sobre o corpus deve carregar, quando aplicável:

```json
{
  "document_id": "...",
  "dispositivo": "art. ...",
  "release": "v1.1.0",
  "data_corte": "YYYY-MM-DD",
  "fonte_oficial": "https://...",
  "limitações": []
}
```

O agente não deve completar texto ausente, promover inferência a norma, ocultar
conflito entre fontes ou chamar o site derivado de publicação oficial.

## Evolução

RAG, embeddings e índices semânticos estão adiados até a estabilização do
corpus. Quando forem implementados, serão artefatos derivados com versão,
avaliação de recuperação e citações verificáveis; jamais serão a fonte
normativa principal.
