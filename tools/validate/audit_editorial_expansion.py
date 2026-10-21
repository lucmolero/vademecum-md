"""Validate the controlled editorial expansion inventory.

Expansion candidates are not curated documents. They are reviewed proposals
with official discovery sources and cannot silently enter the public corpus.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parents[2]
EXPANSION = ROOT / "manifests/editorial-expansion.csv"
MATRIX = ROOT / "manifests/corpus.csv"
ALLOWED_HOSTS = {"planalto.gov.br", "normas.leg.br", "senado.leg.br", "camara.leg.br"}
REQUIRED = {
    "id", "tipo", "numero", "ano", "dominio", "prioridade", "instrumento",
    "motivo_inclusao", "fonte_oficial", "status_cobertura", "status_integridade",
    "status_atualidade",
}


def normalized_identity(row: dict[str, str]) -> tuple[str, str, str]:
    return (row.get("tipo", ""), re.sub(r"\D", "", row.get("numero", "")), row.get("ano", ""))


def official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return any(host == allowed or host.endswith("." + allowed) for allowed in ALLOWED_HOSTS)


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        return list(reader), list(reader.fieldnames or [])


def main() -> int:
    rows, fields = read_rows(EXPANSION)
    errors: list[str] = []
    if REQUIRED - set(fields):
        errors.append(f"colunas ausentes: {sorted(REQUIRED - set(fields))}")
    ids: set[str] = set()
    identities: set[tuple[str, str, str]] = set()
    for row in rows:
        if row.get("id") in ids:
            errors.append(f"ID duplicado: {row.get('id')}")
        ids.add(row.get("id", ""))
        identity = normalized_identity(row)
        if identity in identities:
            errors.append(f"identidade duplicada: {identity}")
        identities.add(identity)
        if row.get("status_cobertura") != "candidato_gap":
            errors.append(f"status de cobertura inválido: {row.get('id')}")
        if row.get("prioridade") not in {"P0", "P1", "P2"}:
            errors.append(f"prioridade inválida: {row.get('id')}")
        if not official(row.get("fonte_oficial", "")):
            errors.append(f"fonte não oficial: {row.get('id')}")
    matrix_rows, _ = read_rows(MATRIX)
    matrix_identities = {normalized_identity(row) for row in matrix_rows}
    overlaps = sorted(identity for identity in identities if identity in matrix_identities)
    if overlaps:
        errors.append(f"candidatos já presentes na matriz: {overlaps}")
    print(f"Expansão editorial: {len(rows)} candidatos; sobreposição: {len(overlaps)}; erros: {len(errors)}")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
