# Contribuindo

O VadeMecum MD é um corpus federal curado, não uma cópia de publicação
governamental. Toda alteração normativa deve ter fonte oficial, data de corte,
unidade de extração, hashes e uma decisão registrada no fluxo autônomo.

## Desenvolvimento

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[docs]"
python tools/site/build_site.py
python tools/validate_release.py
python -m unittest discover -s tests -v
```

Não inclua snapshots brutos, segredos ou caminhos locais. O texto publicado não
deve ser corrigido silenciosamente: anomalias da fonte são evidenciadas e
preservadas.
