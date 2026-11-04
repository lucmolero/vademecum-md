# Operação e lançamento

## Fonte única

`main` é a branch de integração. Homepage, Biblioteca, Leitor, Grafo e kit de
consulta são compostos pelo mesmo workflow `site.yml`. O corpus canônico fica
em `bases/curated/legislacao/federal`; arquivos em `site/`, `dist/` e
`biblioteca/dist/` são gerados. Não editar esses artefatos para corrigir fontes.

Mudanças entram por PR, com `quality` obrigatório e branch atualizada. A política
de PR exige o SHA verificado, autoria permitida e branch do próprio repositório.
Propostas do bot usam `automation/update-*`. Após o merge automático, a política
dispara Pages explicitamente porque merges com o token do workflow não geram
novos eventos de push.

## Publicação

1. Sincronizar a versão em `pyproject.toml`, `src/vademecum_md/__init__.py`,
   `manifests/release.json`, `manifests/consumer-contract.json` e `CITATION.cff`.
   Atualizar changelog e links de download sem alterar o corte jurídico.
2. Passar `quality`, integrar o PR e aguardar `site` no commit integrado.
3. Executar `gh workflow run release.yml --ref main`. O fluxo regenera os
   índices, valida o corpus, executa os testes e publica ZIP, manifesto, SBOM
   e checksums. Releases existentes são imutáveis. Publicações são serializadas.
4. Conferir o commit e a versão em `vademecum-release.json`, a Biblioteca em
   `/biblioteca/`, o Grafo em `/graph/` e o kit em `/downloads/`.
5. Conferir os checksums dos arquivos da nova GitHub Release.

O corte do corpus e a data de lançamento têm significados diferentes. Relatórios
de monitoramento e coleta não certificam atualização jurídica posterior ao corte.

## Rotinas

| Workflow | Função | Acionamento |
| --- | --- | --- |
| `quality.yml` | Corpus, testes, builds, acessibilidade, Chromium e WebKit | PR, push em main, manual e trimestral |
| `browser-webkit.yml` | Jornadas no WebKit | Reutilizado por quality e site |
| `site.yml` | Composição e publicação conjunta no Pages | Main, dispatch e manual |
| `release.yml` | Pacote público imutável | Manual e trimestral |
| `monitor-legislation.yml` | Frescor e fontes | Diário e manual |
| `discover-legislation.yml` | Candidatos oficiais | Semanal e manual |
| `collect-legislation.yml` | Snapshots P0, P1 e P2 | Trimestral e manual |
| `prepare-update-pr.yml` | Coleta, diferenças e proposta protegida por gates | Manual ou repository dispatch |
| `weekly-completeness.yml` | Completude, grafo e testes | Semanal e manual |
| `sync-private-history.yml` | Histórico privado de aquisição | Manual ou repository dispatch |
| `pr-policy.yml` | Integração confiável após quality | Conclusão de quality |

O histórico privado requer a variável `HISTORY_REPOSITORY` e o segredo
`HISTORY_REPO_SSH_KEY`. Não registrar o valor do segredo em relatórios.
Coleta e propostas exigem conectividade com fontes oficiais; indisponibilidade,
conflito ou diferença textual devem ser relatados sem inventar conteúdo.

## Recuperação

Uma execução Pages que falha antes do deploy conserva a publicação anterior.
Para recuperar uma versão já publicada com defeito, prefira reverter a mudança
por PR e aguardar os mesmos gates. Não force a branch main nem sobrescreva uma
GitHub Release.

Em recuperação urgente, crie uma branch temporária apontando ao SHA de uma
execução `site` comprovadamente bem-sucedida e dispare `site.yml` nessa branch.
O workflow recompila e verifica aquele estado antes do deploy. Confirme
`vademecum-release.json` e as rotas após a recuperação. Corrija main por PR e
publique novamente; elimine a branch temporária quando a recuperação terminar.

## Higiene de branches

Remover branches de PRs integrados somente após conferir o commit do PR e sua
incorporação em main. Squash produz SHAs diferentes; divergência no grafo Git
não prova trabalho pendente. Candidatas encerradas devem ser comparadas com a
implementação atual e preservadas em arquivo recuperável antes da remoção.
Não apagar checkouts locais com alterações. O GitHub elimina automaticamente
branches de novos PRs integrados.
