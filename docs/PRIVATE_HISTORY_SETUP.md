# Configuração do histórico técnico privado

O repositório público contém apenas o corpus curado, hashes, fontes oficiais e
relatórios não sensíveis. Snapshots brutos, logs de aquisição e evidências de
execução devem permanecer em um repositório privado separado.

## Estado atual

O workflow `.github/workflows/sync-private-history.yml` usa a variável
`HISTORY_REPOSITORY` e a secret `HISTORY_REPO_SSH_KEY`. A chave é uma deploy key
Ed25519 com escrita limitada exclusivamente ao repositório privado de histórico.

O workflow não depende de aprovação humana de conteúdo. A chave não deve ser
armazenada no código nem em arquivos `.env` versionados.

## Ativação controlada

1. Criar, na mesma conta ou organização, um repositório privado dedicado, por
   exemplo `OWNER/vademecum-md-history`.
2. Gerar uma chave Ed25519 exclusiva para a automação e cadastrá-la como deploy
   key com escrita somente nesse repositório privado.
3. Cadastrar no repositório público a variável:

   ```text
   HISTORY_REPOSITORY=OWNER/vademecum-md-history
   ```

4. Cadastrar a chave privada como secret do repositório público com o nome
   `HISTORY_REPO_SSH_KEY`.
5. Executar primeiro `sync-private-history` manualmente como smoke test e conferir
   o commit criado no repositório privado.
6. Confirmar que o relatório público contém apenas metadados e hashes, nunca o
   conteúdo bruto dos snapshots.

Exemplo de comandos para o proprietário executar após criar o repositório:

```bash
gh variable set HISTORY_REPOSITORY \
  --repo OWNER/vademecum-md \
  --body OWNER/vademecum-md-history

gh secret set HISTORY_REPO_SSH_KEY \
  --repo OWNER/vademecum-md
```

O fluxo de lançamento usa uma chave dedicada e não reutiliza tokens pessoais.

## Verificação de segurança

- A área privada de aquisição e `reports/` permanecem fora do repositório público.
- O workflow público usa `persist-credentials: false` no checkout público.
- A sincronização falha de forma explícita se a deploy key não estiver disponível.
- O histórico privado recebe um ledger com hash de cada arquivo copiado.
- Nenhuma alteração do corpus curado é feita pelo workflow de histórico.
