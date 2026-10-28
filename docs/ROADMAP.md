# Roadmap de evolução

## Estado público — v1.1.3

A release v1.1.3 é a referência pública do produto e do pacote de consulta. O
corpus mantém o corte jurídico de 2026-10-21; o monitor de 2026-10-28 confirmou
375 documentos dentro das respectivas políticas de frescor, sem fonte ausente.

- 375 documentos canônicos, integrais, com fonte oficial e hash;
- 372 documentos consolidados diretamente por fonte oficial e 3 reconciliados;
- 33/33 documentos da prioridade P0 consolidados;
- 1.841 relações normativas materializadas;
- 15/15 decisões da expansão editorial registradas e promovidas;
- baseline e completude com estado `pass`, sem divergências estruturais.

Os números descrevem o snapshot, não a legislação em tempo real. Confira a data
de corte no documento e a publicação oficial antes de citar ou aplicar uma
norma.

## Entregas concluídas nesta versão

- Home, catálogo e leitor redesenhados para consulta compacta em desktop e
  celular, preservando a linguagem Markdown e a leitura e-ink.
- README, contratos, escopo jurídico e documentação de manutenção alinhados.
- Release identificada em código, manifests e metadados de citação, com pacote,
  checksums e SBOM reproduzíveis.
- Main protegida, gate de qualidade obrigatório, política de merge automático
  limitada ao proprietário e ao Dependabot, Actions fixadas por SHA e alertas
  automatizados de dependência.
- Builds estritos, validação HTML e suíte automatizada executados nos fluxos de
  qualidade, completude e release.

## Próximo ciclo — v1.2

Priorizar melhorias que reforcem a consulta e a confiança sem aumentar o escopo
do corpus:

1. executar verificação de teclado, reflow e leitor de tela sobre as rotas
   principais e uma lei extensa;
2. medir desempenho em condições reais e manter o orçamento de bytes das páginas;
3. ensaiar recuperação de uma publicação com falha e confirmar o rollback dos
   artefatos estáticos;
4. manter monitoramento diário, análise semanal de completude e coleta oficial
   conforme as políticas P0, P1 e P2;
5. avaliar recursos adicionais do grafo apenas quando melhorarem descoberta sem
   tornar o leitor ou o acesso ao Markdown mais complexos.

## Fora do escopo publicado

Regulamentos, tratados, jurisprudência, RAG, chunks e embeddings não integram a
release v1.1.3. Uma ampliação futura requer fontes allowlisted, contratos
próprios, evidência, testes e critérios de publicação. A cobertura atual não é
exaustiva e não substitui fonte oficial nem orientação jurídica.
