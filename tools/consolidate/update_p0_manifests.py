"""Update public manifests after the explicit P0 reconciliation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[2]
TODAY = "2026-10-21"

P0 = {
    "br-federal-decreto_lei-3914-1941": {
        "tipo": "decreto_lei", "numero": "3914", "ano": "1941",
        "sources": ["https://www.planalto.gov.br/ccivil_03/decreto-lei/del3914.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:decreto.lei:1941-12-09;3914"],
        "hash": "1ad23964fc5308b467b38640f5d1ea749c579bff921c7082ad4d0561d97d081b",
    },
    "br-federal-decreto_lei-3931-1941": {
        "tipo": "decreto_lei", "numero": "3931", "ano": "1941",
        "sources": ["https://www.planalto.gov.br/ccivil_03/decreto-lei/1937-1946/del3931.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:decreto.lei:1941-12-11;3931"],
        "hash": "0df92db8d66a38b3f08125c0d6eb9ac98b2a840325e5814b29279f88cc4a0fa5",
    },
    "br-federal-lei_complementar-214-2025": {
        "tipo": "lei_complementar", "numero": "214", "ano": "2025",
        "sources": ["https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214compilado.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:lei.complementar:2025-01-16;214"],
        "hash": "eeb810c7ca20490a43ca468174fcd48a28653e328ceef731e87c7204a0d13589",
    },
    "br-federal-lei_complementar-225-2026": {
        "tipo": "lei_complementar", "numero": "225", "ano": "2026",
        "sources": ["https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp225.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:lei.complementar:2026-01-08;225"],
        "hash": "7139fb1afab9b2a4a34a6ce233cd0e4757ab2d7fffa3317fbf4f45a4036b9898",
    },
    "br-federal-lei_ordinaria-14133-2021": {
        "tipo": "lei_ordinaria", "numero": "14133", "ano": "2021",
        "sources": ["https://planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:lei:2021-04-01;14133"],
        "hash": "9b4e704411f3e488766fe1885b381326844afbba7b7921f7dbc70ece49de3728",
    },
}


def update_sources() -> None:
    path = ROOT / "manifests/sources-official.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for entry in data["documents"]:
        spec = P0.get(entry.get("id"))
        if spec:
            entry["fontes"] = spec["sources"]
            entry["data_consulta"] = TODAY
            entry["data_corte"] = TODAY
            entry["sha256_origem"] = spec["hash"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def update_matrix() -> None:
    path = ROOT / "manifests/corpus.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        rows = list(reader)
        fields = reader.fieldnames or []
    for row in rows:
        for spec in P0.values():
            if row["tipo"] == spec["tipo"] and row["numero"] == spec["numero"] and row["ano"] == spec["ano"]:
                row["fonte_oficial"] = "|".join(spec["sources"])
                row["status_atualidade"] = "confirmada"
                break
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def update_reports() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_public_indexes.py"), "--apply"], check=True)


if __name__ == "__main__":
    update_sources()
    update_matrix()
    update_reports()
    print("Manifestos P0 atualizados.")
