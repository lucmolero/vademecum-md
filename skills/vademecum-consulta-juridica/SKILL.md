---
name: vademecum-consulta-juridica
description: Consulte o corpus brasileiro do VadeMecum MD para localizar, citar ou analisar normas com atenção à release, data de corte, situação, consolidação, fonte oficial e evidências. Use quando a pergunta exigir consultar ou fundamentar uma resposta em documentos deste repositório. Não presume que o agente tenha acesso ao repositório.
---

# Consulta jurídica fundamentada no VadeMecum MD

Use esta skill quando a resposta depender de localizar ou interpretar um diploma
do VadeMecum MD. Ela orienta o uso cuidadoso do corpus; não é fonte normativa,
ferramenta de busca ou parecer jurídico.

## 1. Localize o corpus e confirme a versão

1. Procure primeiro no workspace por `manifests/release.json` e
   `bases/curated/legislacao/federal/`. No kit baixado da homepage, os mesmos
   dados ficam em `corpus/manifests/` e `corpus/bases/curated/legislacao/federal/`.
2. Para uma instalação no projeto, consulte `.vademecum-md/current.json`. Leia o
   campo `path` relativo a `.vademecum-md/` e confirme que ele contém
   `manifests/release.json` e `bases/curated/legislacao/federal/`.
3. Para uma instalação pessoal, procure o mesmo arquivo `current.json` em:
   `%LOCALAPPDATA%/VadeMecumMD/` no Windows,
   `~/Library/Application Support/VadeMecumMD/` no macOS ou
   `${XDG_DATA_HOME:-~/.local/share}/vademecum-md/` no Linux. A variável
   `VADEMECUM_MD_DATA` pode apontar para uma pasta de dados personalizada.
4. Confirme que `current.json`, `manifests/release.json` e o diretório de
   documentos apontam para a mesma release. Não alegue ter consultado o corpus
   quando só encontrou a skill, um link ou metadados sem os documentos.
5. Identifique a release e a data de corte em `manifests/release.json` e
   `manifests/corpus.csv` ou nos metadados do documento. Se só houver um arquivo
   avulso, registre a versão e o corte que ele próprio declara; se não declarar,
   diga que não foi possível confirmá-los.
6. Use o ID estável do documento para identificar o diploma. O caminho do
   arquivo, título aproximado ou resultado de busca isolado não substituem o ID.
7. Se o corpus não estiver acessível, informe essa limitação e peça o documento,
   trecho ou acesso necessário. Não invente conteúdo, status, citação ou URL.

## 2. Recupere e confira a evidência

Localize a norma por ID, tipo/número/ano, título ou dispositivo. Leia o texto do
dispositivo no Markdown canônico e confira o frontmatter. Para qualquer
afirmação sobre vigência ou atualidade, confira `situacao`,
`consolidacao_status`, `data_corte` e a evidência da fonte oficial.

Os estados `requer_reconciliacao`, `historica` e `desconhecida` não sustentam
afirmação de vigência atual. `consolidada_reconciliada` informa uma condição de
curadoria, não equivalência automática a consolidação oficial. Estados como
`revogada`, `parcialmente_revogada` e `transitoria` devem ser descritos conforme
constam nos metadados, sem generalizar para todos os dispositivos quando o
corpus não delimitar o alcance.

Se houver conflito, ausência de dado, texto parcial ou incerteza sobre a
vigência, apresente a limitação e não a resolva por inferência. Para conclusão
jurídica atual, recomende conferir a publicação oficial indicada no documento.

Quando houver uma skill instalada sem os dados, informe isso claramente. Se o
agente tiver acesso à rede e ao sistema de arquivos, ofereça obter o kit completo
na URL oficial
`https://lucmolero.github.io/vademecum-md/downloads/vademecum-consulta-juridica-kit.zip`;
confirme o SHA-256 no arquivo `.zip.sha256` correspondente antes de extrair. Não execute
scripts do ZIP para instalar os dados: leia `README.md` e coloque os arquivos no
diretório de dados configurado pelo usuário. Se não houver permissão ou
conectividade, pare e ofereça o download manual.

## 3. Preserve as camadas de informação

Distinga claramente:

- **Texto normativo:** redação do dispositivo publicado no documento canônico.
- **Metadados curatoriais:** identidade, situação, consolidação, datas, hashes,
  proveniência e observações do documento.
- **Histórico:** versões anteriores, atos alteradores, revogações ou diffs; não
  confunda redação histórica com a redação vigente na data consultada.
- **Grafo:** relações entre diplomas. Uma relação é dado contextual, não texto
  legal, prova conclusiva de vigência ou substituto da leitura do dispositivo.
- **Análise do agente:** inferência jurídica produzida a partir das fontes; deve
  ser identificada como análise e apoiada em dispositivos citados.

Ao usar uma relação do grafo, verifique origem, destino, tipo e, se disponíveis,
dispositivo, evidência, confiança e estado de revisão. Respeite as direções
recíprocas (`altera`/`alterada_por`, `revoga`/`revogada_por` etc.). Se a relação
for ambígua ou não estiver ligada a dispositivo, não a atribua a um artigo
específico nem a converta em afirmação normativa.

## 4. Responda e cite proporcionalmente

Toda resposta baseada no corpus deve trazer uma citação rastreável, incluindo,
quando disponíveis:

- diploma e dispositivo;
- ID estável (`document_id`);
- release;
- data de corte (`data_corte`);
- URL da fonte oficial (`fonte_oficial`).

Não preencha campo ausente por suposição. Indique explicitamente quando release,
corte, dispositivo ou fonte não puderem ser verificados. Para perguntas simples,
responda diretamente e acrescente a referência. Para análise jurídica, use
IRAC quando solicitado ou quando ajudar a organizar a resposta:

1. **Questão** — questão apresentada;
2. **Regra** — dispositivos e regras relevantes, com citações;
3. **Aplicação** — aplicação ao contexto fornecido, separando fatos de
   pressupostos;
4. **Conclusão** — conclusão calibrada à evidência e às limitações.

IRAC é estrutura de apresentação, não garantia de correção. Não exponha cadeia
de pensamento privada; forneça fundamentos, fontes e uma justificativa concisa.

Quando o usuário pedir referências acadêmicas em ABNT, formate os dados
bibliográficos verificáveis nesse estilo. Preserve também os identificadores do
corpus e a URL oficial; não invente autor, edição, local, data ou paginação para
completar uma referência.

## 5. Saiba quando parar

Não complete trechos ausentes, não atribua texto a uma norma sem evidência e não
afirme vigência atual além do corte consultado. Se a fonte ou evidência for
insuficiente, explique o que falta, ofereça somente o que pode ser sustentado e
recuse a conclusão específica que dependa da informação ausente. Não apresente o
VadeMecum MD como publicação oficial, cobertura exaustiva do direito ou
aconselhamento jurídico.

## Exemplos e avaliação

Consulte `README.md` para exemplos de ativação e consulta e `evals.md` para
cenários de avaliação e critérios observáveis de aprovação.
