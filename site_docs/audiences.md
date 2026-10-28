# Como usar o VadeMecum MD

Três percursos para consultar o mesmo corpus: **leitura jurídica**, **agentes de
IA** e **integrações de dados**. Em todos eles, identifique a versão consultada
e verifique a fonte oficial.

## Leitura jurídica

1. Localize a norma no [catálogo da legislação](generated/catalog.md) ou na
   busca do site.
2. Na página do diploma, confira o ID, a situação, o estado de consolidação e a
   data de corte.
3. Leia o dispositivo no texto e abra a fonte oficial indicada para conferir a
   redação antes de citar ou aplicar a norma.
4. Ao referenciar a consulta, registre diploma e dispositivo, ID, release, corte
   e fonte oficial.

Relações normativas ajudam a navegar pelo contexto; não substituem o texto da
norma.

## Agentes de IA

1. Disponibilize ao agente os arquivos da release, o documento Markdown ou uma
   ferramenta de leitura acessível na sessão.
2. Forneça a [skill de consulta jurídica](https://github.com/lucmolero/vademecum-md/blob/main/skills/vademecum-consulta-juridica/SKILL.md)
   como orientação de leitura e citação.
3. Exija referência verificável ao dispositivo, ID, release, corte e fonte
   oficial. Se o texto ou a evidência não estiver acessível, o agente deve
   declarar a limitação, sem completar lacunas de memória.

A skill não concede acesso automático ao GitHub. Estados `historica`,
`desconhecida` e `requer_reconciliacao` não sustentam uma afirmação de vigência
atual; relações do grafo também não são comandos normativos.

## Dados e integrações

1. Fixe uma versão baixando o [pacote de release](https://github.com/lucmolero/vademecum-md/releases).
2. Enumere os documentos em [`manifests/corpus.csv`](https://github.com/lucmolero/vademecum-md/blob/main/manifests/corpus.csv)
   e leia o texto e os metadados no Markdown canônico.
3. Use o [grafo normativo](https://github.com/lucmolero/vademecum-md/blob/main/bases/derived/relacoes/normative-graph.jsonl)
   como contexto com evidência, não como fonte normativa. Prefira os arquivos
   versionados ao HTML do site para pipelines.

Para as regras completas de citação, estados e limites, consulte o
[contrato público de consulta e consumo](https://github.com/lucmolero/vademecum-md/blob/main/docs/AUDIENCE_CONTRACTS.md)
e o [contrato em JSON](https://github.com/lucmolero/vademecum-md/blob/main/manifests/consumer-contract.json).
O [contrato dos documentos](contract.md) descreve os metadados e estados do
frontmatter.

## Limites comuns

O corpus é uma seleção curada de legislação federal; seu corte não significa
atualização em tempo real. O projeto não é publicação oficial nem
aconselhamento jurídico. A publicação oficial indicada em cada diploma é a
autoridade textual; consulte-a antes de tomar decisões ou publicar uma análise.
