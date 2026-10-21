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
PROMOTIONS = ROOT / "manifests/editorial-promotions.json"
ALLOWED_HOSTS = {"planalto.gov.br", "normas.leg.br", "senado.leg.br", "camara.leg.br"}
REQUIRED = {
    "id", "tipo", "numero", "ano", "dominio", "prioridade", "instrumento",
    "motivo_inclusao", "fonte_oficial", "status_cobertura", "status_integridade",
    "status_atualidade",
    "status_aquisicao", "data_aquisicao", "sha256_origem", "sha256_corpo", "fonte_oficial_count",
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
        coverage_status = row.get("status_cobertura")
        acquisition_status = row.get("status_aquisicao")
        if coverage_status not in {"candidato_gap", "promovido_corpus"}:
            errors.append(f"status de cobertura inválido: {row.get('id')}")
        if acquisition_status not in {"adquirido_pendente_reconciliacao", "promovido_corpus"}:
            errors.append(f"aquisição não materializada: {row.get('id')}")
        if coverage_status == "promovido_corpus" and acquisition_status != "promovido_corpus":
            errors.append(f"promoção sem aquisição promovida: {row.get('id')}")
        for field in ("sha256_origem", "sha256_corpo"):
            if not re.fullmatch(r"[0-9a-f]{64}", row.get(field, "")):
                errors.append(f"hash inválido em {field}: {row.get('id')}")
        if row.get("prioridade") not in {"P0", "P1", "P2"}:
            errors.append(f"prioridade inválida: {row.get('id')}")
        if not official(row.get("fonte_oficial", "")):
            errors.append(f"fonte não oficial: {row.get('id')}")
    matrix_rows, _ = read_rows(MATRIX)
    matrix_identities = {normalized_identity(row) for row in matrix_rows}
    overlaps = sorted(identity for identity in identities if identity in matrix_identities)
    for identity in overlaps:
        candidate = next(row for row in rows if normalized_identity(row) == identity)
        if candidate.get("status_cobertura") != "promovido_corpus":
            errors.append(f"candidato já presente na matriz sem promoção registrada: {identity}")
    if not PROMOTIONS.is_file():
        errors.append("manifesto de decisões editoriais ausente")
    else:
        try:
            import json
            decisions_payload = json.loads(PROMOTIONS.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            decisions_payload = {}
            errors.append(f"manifesto de decisões editoriais inválido: {error}")
        if decisions_payload.get("schema") != "editorial-promotion-decision/v2":
            errors.append("schema do manifesto de decisões editoriais inválido")
        decisions = decisions_payload.get("decisions", {})
        for row in rows:
            decision = decisions.get(row.get("id"))
            if not isinstance(decision, dict):
                errors.append(f"candidato sem decisão editorial: {row.get('id')}")
                continue
            if decision.get("decision") not in {"promote", "history", "out_of_scope", "reconcile"}:
                errors.append(f"decisão editorial inválida: {row.get('id')}")
            if decision.get("decision") == "promote":
                if decision.get("situacao") not in {"em_vigor", "desconhecida", "revogada", "parcialmente_revogada", "transitoria", "historica"}:
                    errors.append(f"situação jurídica ausente ou inválida: {row.get('id')}")
                if not isinstance(decision.get("evidencias"), list) or not decision.get("evidencias"):
                    errors.append(f"evidências ausentes: {row.get('id')}")
                if not decision.get("revisor") or not decision.get("revisado_em"):
                    errors.append(f"revisão não identificada: {row.get('id')}")
    print(f"Expansão editorial: {len(rows)} candidatos; sobreposição: {len(overlaps)}; erros: {len(errors)}")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
