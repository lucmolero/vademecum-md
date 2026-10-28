# Roadmap de evolução

## Baseline publicado: v1.1.2

A release v1.1.2 é o estado público de referência do projeto. O baseline
reproduzível foi gerado em 2026-10-21 e os manifests da release em 2026-10-22:

- 375 documentos canônicos, integrais, com fonte oficial e hash;
- 372 documentos consolidados diretamente por fonte oficial e 3 reconciliados;
- 33/33 documentos da prioridade P0 consolidados;
- 1.841 relações normativas materializadas;
- 15/15 decisões da expansão editorial registradas e promovidas;
- baseline e completude com estado `pass`, sem divergências estruturais.

Esses números descrevem o snapshot da release, não a legislação em tempo real.
O estado atual deve ser lido nos manifests e relatórios gerados, não inferido
deste resumo histórico.

## Ciclo atual: auditoria de produto e arquitetura

A prioridade é tornar o produto mais fácil de entender e usar sem comprometer a
proveniência jurídica ou a simplicidade de publicação:

1. **Apresentação:** hierarquia editorial compacta na home, tipografia legível
   em desktop e celular, navegação clara e leitor jurídico sem distrações.
2. **Produto:** dar acesso rápido ao catálogo, às normas centrais, à fonte
   oficial e às instruções de consulta para agentes.
3. **Repositório:** manter diretórios apenas para camadas implementadas; explicar
   em especificações quais domínios permanecem fora do escopo.
4. **Documentação:** alinhar README, site, contratos, estado da release e
   instruções de manutenção, evitando planos duplicados ou desatualizados.
5. **Ferramentas:** declarar que os comandos operacionais precisam de um
   checkout local e falhar com diagnóstico claro quando executados fora dele.

Critérios de conclusão: build estrito aprovado, testes de contrato aprovados,
renderização conferida em viewport desktop e móvel, texto legal inalterado e
ausência de diferenças entre os manifests e o corpus.

## Próximo ciclo: v1.2

Priorizar manutenção verificável do snapshot e da experiência de consulta:

- repetir as auditorias de fonte, fidelidade e completude antes de publicar um
  novo corte;
- aprimorar busca, filtros e navegação por dispositivo sem introduzir
  dependência do site para acessar o texto canônico;
- manter as instruções de consumo para humanos, pipelines e agentes alinhadas ao
  contrato dos manifests;
- decidir a distribuição futura do CLI antes de prometer comandos operacionais
  fora de um checkout.

Cada entrega depende dos gates editoriais, jurídicos e técnicos já definidos.
Relações pendentes, cobertura ampliada ou automação adicional nunca substituem
fonte oficial nem evidência de fidelidade.

## Fora do escopo atual

Regulamentos, tratados, jurisprudência, RAG, chunks e embeddings não integram a
release v1.1.2. Só devem entrar em um ciclo futuro com fontes allowlisted,
contratos próprios, evidência, testes e critérios de publicação. Não há
diretórios vazios dessas camadas no produto atual.
