# Especificação do produto

## Visão

O VadeMecum MD é uma base federal curada em Markdown que transforma
publicações normativas públicas em unidades legíveis, identificáveis e
verificáveis. O produto serve simultaneamente a uma pessoa que precisa ler uma
lei, a um pipeline que precisa medir um corpus e a um agente que precisa
responder com evidência.

A unidade de valor não é apenas o texto: é o conjunto

```text
texto + identidade + situação + data de corte + fonte + hash + relações
```

## Jobs to be done

| Público | Tarefa principal | Critério de sucesso |
| --- | --- | --- |
| advogado ou pesquisador | localizar e citar um dispositivo | fonte, release e data de corte são visíveis |
| cientista de dados | construir uma análise reproduzível | mesma release produz os mesmos registros e hashes |
| desenvolvedor de agente | recuperar e fundamentar uma resposta | cada afirmação aponta para dispositivo e fonte |

## Arquitetura de produto

### Núcleo normativo

`bases/curated` contém o Markdown canônico. Ele preserva o texto adquirido e
seus metadados; não é reescrito pelo site, pelo grafo ou por um índice de busca.

### Evidência e contexto

`bases/history` guarda versões, alterações e diffs. `bases/derived` guarda
catálogos, relações e relatórios regeneráveis. Uma camada derivada pode ajudar
a encontrar ou explicar um documento, mas nunca substitui o texto canônico.

### Interfaces

- **humana:** site editorial, busca, índice, âncoras e painel de proveniência;
- **dados:** CSV, JSON, JSONL, frontmatter, hashes e releases;
- **agentes:** IDs estáveis, contrato de citação, relações com evidência e
  regras de recusa.

## Modelo de qualidade

Cada release é avaliada em seis dimensões independentes:

1. **fidelidade:** o corpo publicado corresponde à unidade oficial selecionada;
2. **completude:** o texto integral e os dispositivos esperados estão presentes;
3. **atualidade:** a data de corte e o status de consolidação são explícitos;
4. **proveniência:** fonte, seletor, transformação e hash são rastreáveis;
5. **usabilidade:** a leitura e a navegação funcionam para documentos extensos;
6. **interoperabilidade:** schemas, IDs e artefatos podem ser consumidos sem
   depender de HTML ou de comportamento do site.

Uma dimensão não compensa outra. Um documento com texto completo, mas sem fonte
ou status confiável, não pode ser apresentado como redação vigente.

## Governança de decisões

O fluxo usa duas autoridades complementares:

```text
agente jurídico + evidência oficial → análise curatorial
validadores determinísticos        → admissibilidade técnica
```

O agente pode interpretar relações, situação e relevância editorial. Os
validadores podem rejeitar ausência de fonte, hash inválido, ID duplicado,
truncamento, relação impossível ou alteração silenciosa. Os validadores não
inventam nem decidem significado jurídico.

Quando há conflito ou insuficiência, a política é falhar com segurança:
preservar a versão anterior, registrar a evidência e abrir uma proposta para a
próxima execução. Isso evita que automação transforme incerteza em texto
vigente.

## Contrato de atualização

```text
coleta oficial
→ snapshot privado
→ normalização determinística
→ diff estrutural
→ análise jurídica
→ proposta em Pull Request
→ gates técnicos
→ merge governado
→ release verificável
```

Nenhuma atualização escreve diretamente na branch padrão. O contrato completo
para consumidores está em
[`docs/AUDIENCE_CONTRACTS.md`](AUDIENCE_CONTRACTS.md) e no manifesto
[`manifests/consumer-contract.json`](../manifests/consumer-contract.json).

## Não objetivos

Na release `v1.1.3`, o produto não é:

- publicação oficial do Estado;
- aconselhamento ou parecer jurídico;
- cobertura declarada de toda a legislação federal existente;
- banco de jurisprudência, tratados ou regulamentos completos;
- RAG ou índice semântico tratado como fonte normativa.

Regulamentos, tratados e jurisprudência permanecem fora do escopo publicado.
Não se criam diretórios vazios para essas camadas; uma proposta futura deve
definir fonte, schema, contrato de evidência e gates antes de receber conteúdo.

## Evolução do produto

| Estágio | Entrega | Condição de avanço |
| --- | --- | --- |
| `v1.1.2` | corpus, site, contratos, release e auditoria | gates públicos verdes |
| `v1.1.3` | leitor compacto, site, documentação, segurança e release reproduzível | gates públicos verdes |
| `v1.2` | atualização proposta por PR e diffs mais ricos | evidência e rollback testados |
| `v2` | recuperação híbrida e ferramentas para agentes | avaliação de citações e recusa |

O roadmap é orientado por confiabilidade documental. Funcionalidades de IA só
entram depois que texto, identidade, proveniência e atualização forem estáveis.
