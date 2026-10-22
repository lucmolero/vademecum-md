# Contrato de consulta e consumo

O VadeMecum MD publica um corpus jurídico para leitura e análise humanas e para
consulta fundamentada por agentes de IA. Dados estruturados são a interface de
integração que distribui o mesmo conteúdo; não constituem uma camada normativa
independente.

O contrato machine-readable está em
[`manifests/consumer-contract.json`](../manifests/consumer-contract.json).

## Contrato comum

Todo leitor, agente ou pipeline deve:

1. Fixar uma release e registrar sua data de corte.
2. Identificar o diploma por `id`, não apenas pelo caminho do arquivo.
3. Verificar `situacao` e `consolidacao_status` antes de caracterizar o texto.
4. Preservar a distinção entre corpo normativo, metadados, histórico e grafo.
5. Citar o dispositivo, a release, o corte e a fonte oficial.
6. Não afirmar vigência atual quando o estado for `requer_reconciliacao`,
   `historica` ou `desconhecida`.
7. Consultar a publicação oficial antes de decisão jurídica ou publicação de
   resultado.

## Interfaces públicas

| Uso | Interface primária | Resultado esperado |
| --- | --- | --- |
| Leitura e análise humana | Markdown canônico e leitor derivado | localizar, ler, contextualizar e citar |
| Consulta por agentes | Markdown, IDs, manifestos e instruções de skill | recuperar conteúdo acessível e responder com limites e evidência |
| Integração de dados | CSV, frontmatter, JSONL e pacotes de release | enumerar, filtrar e reproduzir uma versão do corpus |

## Contrato mínimo de citação

Uma resposta sobre o corpus registra, quando aplicável:

```json
{
  "document_id": "...",
  "dispositivo": "art. ...",
  "release": "v...",
  "data_corte": "YYYY-MM-DD",
  "fonte_oficial": "https://...",
  "limitacoes": []
}
```

A formatação ABNT é uma opção de apresentação para referências acadêmicas
solicitadas. Ela não substitui o contrato de rastreabilidade acima.

## Regras para agentes

- Usar somente arquivos ou ferramentas que estejam realmente acessíveis na
  sessão; a skill não concede acesso automático ao GitHub.
- Responder diretamente com citação para pedidos de localização ou extração.
- Usar estrutura Questão, Regra, Aplicação e Conclusão para análises jurídicas
  quando solicitada ou útil.
- Não completar texto ausente, converter relação em norma ou ocultar conflito
  entre fontes.
- Declarar insuficiência quando a evidência ou o acesso forem inadequados.

## Autoridade e limites

A publicação oficial indicada no diploma é a autoridade textual. Metadados são
curados com evidência oficial; site, skills, grafo, índices e relatórios são
artefatos derivados. O projeto não declara cobertura integral do direito
brasileiro, não oferece aconselhamento e não transforma a data de corte em
garantia de atualização em tempo real.
