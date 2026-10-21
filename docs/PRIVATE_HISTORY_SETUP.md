# Configuração do histórico técnico privado

O repositório público contém apenas o corpus curado, hashes, fontes oficiais e
relatórios não sensíveis. Snapshots brutos, logs de aquisição e evidências de
execução devem permanecer em um repositório privado separado.

## Estado atual

O workflow `.github/workflows/sync-private-history.yml` já está preparado, mas
permanece desativado enquanto a variável `HISTORY_REPOSITORY` não existir. Isso
evita que uma execução publique ou descarte snapshots por configuração
incompleta.

O workflow não depende de aprovação humana de conteúdo. O token usado deve ter
permissão mínima e não deve ser armazenado no código nem em arquivos `.env`
versionados.

## Ativação controlada

1. Criar, na mesma conta ou organização, um repositório privado dedicado, por
   exemplo `OWNER/vademecum-md-history`.
2. Conceder ao token uma permissão fine-grained mínima: `Contents: Read and
   write` somente nesse repositório privado; `Metadata: Read` é implícita.
3. Cadastrar no repositório público a variável:

   ```text
   HISTORY_REPOSITORY=OWNER/vademecum-md-history
   ```

4. Cadastrar o token como secret do repositório público com o nome
   `HISTORY_REPO_TOKEN`.
5. Executar primeiro `sync-private-history` manualmente como smoke test e conferir
   o commit criado no repositório privado.
6. Confirmar que o relatório público contém apenas metadados e hashes, nunca o
   conteúdo bruto dos snapshots.

Exemplo de comandos para o proprietário executar após criar o repositório:

```bash
gh variable set HISTORY_REPOSITORY \
  --repo OWNER/vademecum-md \
  --body OWNER/vademecum-md-history

gh secret set HISTORY_REPO_TOKEN \
  --repo OWNER/vademecum-md
```

Os comandos não devem ser executados neste workspace sem a decisão explícita de
qual repositório privado será usado e sem o token fornecido pelo proprietário.

## Verificação de segurança

- A área privada de aquisição, `reports/` e `bases/derived/` permanecem ignorados pelo Git.
- O workflow público usa `persist-credentials: false` no checkout público.
- A sincronização exige o ambiente `private-history` e falha sem o secret.
- O histórico privado recebe um ledger com hash de cada arquivo copiado.
- Nenhuma alteração do corpus curado é feita pelo workflow de histórico.
