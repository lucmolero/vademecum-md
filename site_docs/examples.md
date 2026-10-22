# Exemplos de consumo

## Localizar um diploma

```python
import csv
from pathlib import Path

with Path("manifests/corpus.csv").open(encoding="utf-8", newline="") as stream:
    for row in csv.DictReader(stream, delimiter=";"):
        if row["document_id"] == "br-federal-lei_ordinaria-10406-2002":
            print(row["document_path"])
```

## Ler metadados e corpo

```python
from pathlib import Path
from tools.migrate_public_corpus import parse_frontmatter

path = Path("bases/curated/legislacao/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002.md")
metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
print(metadata["situacao"], metadata["data_corte"])
print(body[:200])
```

Agentes devem citar o `id`, a fonte oficial, a data de corte e o dispositivo
consultado. Índices derivados servem à navegação; não devem ser tratados como
texto normativo.
