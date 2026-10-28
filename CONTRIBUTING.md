# Contribuir e manter

O VadeMecum MD publica um corpus curado para leitura humana e consulta por
agentes. As alterações aceitas vêm de `lucmolero` e do Dependabot. Pull requests
de outras contas são fechados automaticamente; use as issues públicas para
relatar problemas de texto ou navegação.

Pull requests desses autores para `main` são integrados por squash depois que o
workflow `quality` passa e a branch está atualizada. O fluxo mantém os checks
obrigatórios da branch, atualiza branches atrasadas por rebase e deixa rascunhos
sem merge. Um resultado de CI com falha não é integrado automaticamente.
Antes do merge, a política confirma que o check aprovado corresponde ao SHA atual
da proposta e que a autoria está na lista permitida.

## Relatar divergências e problemas de navegação

Use os formulários de issue para apontar uma divergência em relação à fonte
oficial ou um link quebrado. Inclua o ID do diploma, dispositivo afetado, URL
oficial e data de consulta. Não envie dados pessoais, documentos privados ou
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

## Licenças e citação

Scripts, schemas, manifests e documentação autoral são distribuídos sob MIT.
Os textos normativos e os materiais de terceiros seguem o regime aplicável às
respectivas fontes; a licença MIT do software não deve ser interpretada como
licença dos textos oficiais. Cite a release consultada e preserve a fonte
oficial do documento.
