# O projeto como infraestrutura de leitura jurídica

## O problema

Publicações normativas são acessíveis em sites oficiais, mas podem ser difíceis
de consultar, comparar e consumir de forma reproduzível. Agentes de IA também
precisam de identidade documental, fonte, data de corte e dispositivos citáveis
para não transformar texto incompleto ou contexto em resposta normativa.

## A proposta

O VadeMecum MD organiza legislação federal curada em documentos Markdown com
identidade estável, fontes oficiais, metadados, hashes e relações normativas.
O repositório é o artefato público versionado; o site estático é uma edição para
leitura humana; as skills descrevem como um agente deve consultar e citar o
material que realmente estiver disponível na sessão.

```text
fonte oficial → normalização e auditoria → Markdown canônico
                                      ├→ histórico e grafo com evidência
                                      ├→ leitor estático e catálogo
                                      └→ release, manifestos e skills
```

O texto do corpus é a referência das páginas derivadas. Grafo, histórico,
skills e índices são contexto ou instruções; não substituem o texto normativo.

## Decisões de engenharia

- **Identidade antes de inferência:** cada diploma mantém ID estável, fonte,
  hashes e data de corte.
- **Camadas separadas:** corpo normativo, metadados curatoriais, histórico e
  relações não são misturados.
- **Build estático:** MkDocs e GitHub Pages publicam o leitor sem backend.
- **Distribuição fixada:** ZIP, manifesto e checksums permitem identificar e
  verificar uma release.
- **Consulta de agente delimitada:** a skill exige acesso verificável ao
  documento, citação e respeito aos estados; ela não fornece busca automática,
  cobertura integral nem garantia de vigência posterior ao corte.
- **Proposta sob gates:** mudanças públicas passam pelo fluxo de PR e pelos
  validadores antes de qualquer incorporação.

## O que não é prometido

O projeto não é publicação oficial, aconselhamento jurídico, sistema de gestão
de processos ou declaração de cobertura de todo o Direito brasileiro. O corpus
não contém RAG como fonte normativa; respostas de agentes dependem dos arquivos
ou ferramentas de leitura disponíveis e da evidência que esses materiais
oferecem.

## Evidência pública

O estado de cada release deve ser lido nos manifests e no pacote publicado.
Métricas da página inicial são geradas a partir dos dados versionados. Relações
externas classificadas e arestas do grafo são contagens diferentes e não devem
ser apresentadas como sinônimos.
