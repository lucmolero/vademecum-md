# Configuracao operacional do GitHub

O `origin` esta configurado para o repositorio autoral. A `main` esta protegida contra push direto, force-push e delecoes; o check `quality` e uma aprovacao de Pull Request sao obrigatorios.

## Repositorio publico

- branch padrao: `main`;
- Pull Request e check `quality` obrigatorios;
- historico linear, force-push e delecao da `main` bloqueados;
- permissoes padrao do Actions como somente leitura;
- workflows de completude e release executados por agenda ou manualmente, com gates proprios.

## Repositorio privado de historico

O repositorio separado `vademecum-md-history` foi criado com acesso restrito. O conteudo esperado e o ledger produzido por `tools/history/build_private_ledger.py`, incluindo snapshots, logs, hashes e evidencias de execucao.

O nome definitivo e o token de acesso nao devem ser gravados no repositorio publico. O destino privado existe, mas a sincronizacao de snapshots permanece deliberadamente desativada ate que um secret de menor privilegio seja configurado.

## Ambientes

- `update-proposal`: ambiente criado, com aprovador obrigatorio, sem autoaprovacao e sem bypass administrativo;
- `production`: ambiente criado, com aprovador obrigatorio, sem autoaprovacao e sem bypass administrativo;
- nenhum ambiente deve permitir credenciais em Pull Requests nao confiaveis.

O workflow de proposta continua gerando apenas evidencia nao sensivel; snapshots brutos nao sao publicados no repositorio autoral. A publicacao de release exige aprovacao do ambiente `production`.
