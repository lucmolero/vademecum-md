# O projeto como engenharia

## O problema

Legislação federal é legível por pessoas, mas raramente é distribuída com uma
estrutura estável para validação, comparação e consumo por máquinas. O projeto
organiza cada diploma como uma unidade editorial e computável sem substituir a
fonte oficial.

## Um produto para três disciplinas

O mesmo corpus oferece três interfaces coordenadas:

- **Direito:** leitura integral, contexto de vigência e citação verificável;
- **dados:** schemas, hashes, manifestos e releases reproduzíveis;
- **agentes:** recuperação com identidade, evidência, data de corte e regras de recusa.

Essa separação evita dois erros comuns: criar uma experiência bonita sem contrato
de dados, ou criar um dataset técnico que não seja confortável para leitura jurídica.
Veja os [contratos de consumo](audiences.md) e a
[especificação do produto](https://github.com/lucmolero/vademecum-md/blob/main/docs/PRODUCT_SPEC.md).

## A solução

```text
fonte oficial → aquisição privada → normalização → auditoria
→ curadoria jurídica → histórico e grafo → site e release
```

O Markdown canônico é a fonte do produto. O site, os catálogos, os índices e os
relatórios são derivados e regeneráveis.

## Separação de responsabilidades

| Camada | Responsabilidade |
| --- | --- |
| Fonte oficial | autoridade textual pública |
| Agente jurídico | vigência, contexto, relações e decisão curatorial |
| Validadores | identidade, estrutura, hashes, links e segurança |
| Site | leitura, navegação e apresentação |
| Release | empacotamento e distribuição reproduzíveis |

O agente não inventa texto. Os validadores não decidem significado jurídico.
Conflitos preservam a versão pública anterior e são registrados na proposta.

## O que torna o projeto demonstrável

- corpus real e extenso;
- contrato documental explícito;
- hashes com escopo definido;
- histórico normativo separado;
- grafo com evidência textual;
- atualização proposta por Pull Request;
- site editorial derivado;
- acessibilidade e movimento reduzido;
- pacote reproduzível;
- limitações jurídicas documentadas.

## Decisões deliberadas

O projeto não implementa RAG nesta fase. Primeiro estabiliza texto, proveniência,
fidelidade, atualização e experiência de leitura. Índices semânticos, skills e
harnesses serão construídos somente sobre um corpus editorialmente estabilizado.

Também não há analytics comportamental. O produto privilegia privacidade,
reprodutibilidade e evidência pública.

## Limites

O VadeMecum MD é um corpus autoral curado. Não é uma publicação oficial, não
declara cobrir toda a legislação federal e não substitui a consulta à fonte
oficial ou a orientação profissional.
