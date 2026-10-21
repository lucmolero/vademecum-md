# Configuração operacional do GitHub

O `origin` já está configurado para o repositório autoral. Permanecem apenas as proteções administrativas descritas abaixo.

## Repositório público

- definir a branch padrão como `main`;
- exigir Pull Request e checks de `quality`, `weekly-completeness` e `release-gates`;
- bloquear push direto na `main`;
- manter permissões padrão do Actions como somente leitura;
- habilitar revisão obrigatória para alterações em `.github/workflows`, `manifests` e `bases/curated`.

## Repositório privado de histórico

O repositório separado `vademecum-md-history` já foi criado com acesso restrito. O conteúdo esperado é o ledger produzido por `tools/history/build_private_ledger.py`, incluindo snapshots, logs, hashes e evidências de execução.

O nome definitivo e o token de acesso não devem ser gravados no repositório público. Devem ser configurados como secret/environment protegido somente quando o destino privado existir.

## Ambientes

- `update-proposal`: aprovação obrigatória para o workflow que cria branches e PRs de proposta;
- `production`: aprovação obrigatória para o job que publica uma release GitHub;
- nenhum ambiente deve permitir credenciais em Pull Requests não confiáveis.

Até essa configuração externa, os workflows continuam seguros: geram relatórios e artefatos não sensíveis, mas não publicam snapshots brutos nem criam releases automaticamente.
