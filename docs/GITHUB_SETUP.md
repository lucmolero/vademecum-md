# Configuração operacional do GitHub

O `origin` esta configurado para o repositorio autoral. A `main` esta protegida contra push direto, force-push e delecoes; o check `quality` e obrigatorio. Acuradoria e atualizacao de conteudo nao dependem de aprovacao humana.

## Repositorio publico

- branch padrao: `main`;
- Pull Request e check `quality` obrigatorios; a conclusao automatica depende dos checks, nao de revisao manual de conteudo;
- historico linear, force-push e delecao da `main` bloqueados;
- permissoes padrao do Actions como somente leitura;
- workflows de completude e release executados por agenda ou manualmente, com gates proprios.

## Repositório privado de histórico

O workflow está preparado, mas o repositório privado de histórico ainda não está
configurado no GitHub: `HISTORY_REPOSITORY` e `HISTORY_REPO_TOKEN` não estão
presentes. A sincronização permanece desativada até que o proprietário crie o
destino privado e configure credenciais de menor privilégio conforme
[PRIVATE_HISTORY_SETUP.md](PRIVATE_HISTORY_SETUP.md).

O conteúdo esperado é o ledger produzido por
`tools/history/build_private_ledger.py`, incluindo snapshots, logs, hashes e
evidências de execução. O nome definitivo e o token não devem ser gravados no
repositório público.

## Ambientes

- `update-proposal`: workflow autônomo, sem bloqueio de aprovação de ambiente;
- `production`: não é exigido para publicação; os gates determinísticos são a barreira de release;
- `private-history`: sincronização condicionada apenas à existência das credenciais de menor privilégio;
- nenhum ambiente deve permitir credenciais em Pull Requests nao confiaveis.

O workflow de proposta continua gerando apenas evidencia nao sensivel; snapshots brutos nao sao publicados no repositorio autoral. A publicacao de release ocorre automaticamente apos todos os gates passarem e nao escreve diretamente na branch padrao.
