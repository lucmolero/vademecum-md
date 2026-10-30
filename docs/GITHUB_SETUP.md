# Configuração operacional do GitHub

O `origin` esta configurado para o repositorio autoral. A `main` esta protegida contra push direto, force-push e delecoes; o check `quality` e obrigatorio. Acuradoria e atualizacao de conteudo nao dependem de aprovacao humana.

## Repositorio publico

- branch padrao: `main`;
- Pull Request e check `quality` obrigatorios; o workflow enfileira o merge automatico com `--auto` para aguardar todos os checks concorrentes, sem depender de revisao manual de conteudo;
- historico linear, force-push e delecao da `main` bloqueados;
- permissoes padrao do Actions como somente leitura;
- workflows de completude e release executados por agenda ou manualmente, com gates proprios.

## Repositório privado de histórico

O repositório privado de histórico é configurado pela variável
`HISTORY_REPOSITORY`. A sincronização usa uma deploy key Ed25519 exclusiva desse
repositório, sem token pessoal amplo. O workflow só é executado quando `HISTORY_REPOSITORY` e
`HISTORY_REPO_SSH_KEY` estão disponíveis.

O conteúdo esperado é o ledger produzido por
`tools/history/build_private_ledger.py`, incluindo snapshots, logs, hashes e
evidências de execução. A chave privada nunca é gravada no repositório público.

## Ambientes

- `update-proposal`: workflow autônomo, sem bloqueio de aprovação de ambiente;
- `production`: não é exigido para publicação; os gates determinísticos são a barreira de release;
- `private-history`: sincronização condicionada apenas à existência da deploy key de menor privilégio;
- nenhum ambiente deve permitir credenciais em Pull Requests nao confiaveis.

O workflow de proposta continua gerando apenas evidencia nao sensivel; snapshots brutos nao sao publicados no repositorio autoral. A publicacao de release ocorre automaticamente apos todos os gates passarem e nao escreve diretamente na branch padrao.
