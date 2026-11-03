# Contribuir e manter

O VadeMecum MD publica um corpus curado para leitura humana e consulta por
agentes. As alterações aceitas vêm de `lucmolero` e do Dependabot. A rotina
interna de atualização legislativa também publica propostas por
`github-actions[bot]`, após validação de proveniência e fidelidade. Pull requests
de outras contas são fechados automaticamente; use as issues públicas para
relatar problemas de texto, navegação ou funcionamento das interfaces.

Pull requests desses autores para `main` são integrados por squash depois que o
workflow `quality` passa e a branch está atualizada. O fluxo mantém os checks
obrigatórios da branch, atualiza branches atrasadas por rebase e deixa rascunhos
sem merge. Um resultado de CI com falha não é integrado automaticamente.
Antes do merge, a política confirma que o check aprovado corresponde ao SHA atual
da proposta e que a autoria está na lista permitida.

## Relatar divergências e problemas de navegação

Use os formulários de issue para apontar uma divergência em relação à fonte
oficial, um link quebrado ou um problema na homepage, na Biblioteca ou no grafo.
Em relatos de conteúdo, inclua o ID do diploma, dispositivo afetado, URL
oficial e data de consulta. Em problemas de interface, descreva os passos,
o navegador e o tamanho de tela. Não envie dados pessoais, documentos privados ou
pedidos de orientação jurídica. Issues fora desses escopos podem ser fechadas
com indicação do canal apropriado.

## Propor uma alteração

Toda proposta que afete o corpus deve indicar a fonte oficial, a unidade de
extração, a data de corte, a evidência e os hashes pertinentes. Não corrija o
texto normativo silenciosamente. Não inclua snapshots brutos, credenciais,
caminhos locais ou dados privados.

As mudanças passam pelos validadores do projeto. Mantenha o escopo do PR pequeno
e descreva claramente se ele altera corpus, grafo, manifestos, ferramentas,
documentação ou apresentação.

## Ambiente de manutenção

O site público é estático e derivado. Para reconstruí-lo e validar a versão de
desenvolvimento, use Python 3.12 ou superior:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[docs]"
python tools/site/build_site.py
mkdocs serve
```

Para uma validação local completa antes de abrir ou revisar um PR:

```powershell
python tools/check_markdown.py
python tools/validate/validate_workflows.py
python tools/build_public_indexes.py --apply
python tools/site/build_site.py
mkdocs build --strict
python tools/validate/validate_site.py
python tools/validate_release.py --stabilization
python -m unittest discover -s tests -v
```

O CI é a validação final. Não publique manualmente arquivos gerados sem
regenerá-los a partir dos artefatos canônicos.

O workflow de Pages também executa os testes do grafo e as jornadas de navegador
antes de disponibilizar o artefato para publicação. O Dependabot acompanha
GitHub Actions, Python e os dois módulos JavaScript.

## Licenças e citação

O software e os materiais autorais seguem o texto MIT em [`LICENSE`](LICENSE),
com escopo e exceções descritos em [`LICENSE.md`](LICENSE.md). A licença não se
estende aos textos normativos nem a materiais de terceiros. Cite a release
consultada e preserve a fonte oficial do documento.
