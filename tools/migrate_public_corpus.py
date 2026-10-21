"""Migrate the curated corpus to the public, authorial Markdown contract.

The migration is deterministic and deliberately conservative: it preserves the
normative body, removes acquisition/editorial metadata from public files, and
keeps technical provenance in an ignored local ledger.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).parents[1]
TODAY = date.today().isoformat()
MATRIX = ROOT / "manifests/corpus.csv"
CURATED = ROOT / "bases/curated/legislacao"
PRIVATE = ROOT / ".private"
SNAPSHOTS = ROOT / "bases/raw/snapshots"

TYPE_MAP = {
    "constituição": "constituicao",
    "constituicao": "constituicao",
    "ato constitucional": "ato_constitucional",
    "lei ordinaria": "lei_ordinaria",
    "lei complementar": "lei_complementar",
    "lei delegada": "lei_delegada",
    "decreto-lei": "decreto_lei",
    "decreto": "decreto",
}

ALLOWED_STATUS = {
    "consolidada_fonte_oficial",
    "consolidada_reconciliada",
    "requer_reconciliacao",
    "texto_original",
    "historica",
    "parcialmente_revogada",
    "revogada",
    "transitoria",
    "desconhecida",
}


def parse_frontmatter(text: str, *, strict: bool = False) -> tuple[dict[str, object], str]:
    opening = re.match(r"^---[ \t]*\r?\n", text)
    if not opening:
        if strict:
            raise ValueError("frontmatter opening delimiter missing")
        return {}, text
    remainder = text[opening.end():]
    closing = re.search(r"^---[ \t]*(?:\r?\n|$)", remainder, re.MULTILINE)
    if not closing:
        if strict:
            raise ValueError("frontmatter closing delimiter missing")
        return {}, text
    block = remainder[:closing.start()]
    try:
        parsed = yaml.safe_load(block) or {}
    except yaml.YAMLError as error:
        if strict:
            raise ValueError(f"frontmatter YAML invalid: {error}") from error
        return {}, text
    if not isinstance(parsed, dict):
        if strict:
            raise ValueError("frontmatter must be a YAML mapping")
        return {}, text
    body = remainder[closing.end():].lstrip("\r\n")
    return dict(parsed), body


def yaml_value(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def frontmatter(values: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in values.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.append("---")
    return "\n".join(lines)


def latest_snapshot() -> Path:
    candidates = [
        p for p in (ROOT / "bases/raw").rglob("*")
        if p.is_dir() and re.fullmatch(r"[0-9a-f]{40}", p.name)
    ]
    if not candidates:
        raise SystemExit("Nenhum snapshot local encontrado em bases/raw/snapshots.")
    return sorted(candidates, key=lambda p: p.name)[-1]


def list_rows() -> list[dict[str, str]]:
    with MATRIX.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def scalar(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value)


def source_url(raw_path: Path | None, current: dict[str, object], body: str) -> list[str]:
    candidates: list[str] = []
    if raw_path and raw_path.is_file():
        raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
        raw_front, _ = parse_frontmatter(raw_text)
        raw_source = scalar(raw_front.get("fonte"))
        if raw_source.startswith(("http://", "https://")):
            candidates.append(raw_source.split('"', 1)[0].split("<", 1)[0].rstrip(".,)"))
        for match in re.findall(r"https?://[^\s)\]>\"]+", raw_text):
            if any(host in match for host in ("planalto.gov.br", "normas.leg.br", "camara.leg.br", "senado.leg.br")):
                candidates.append(match.rstrip(".,"))
    current_source = scalar(current.get("fonte_oficial"))
    if current_source.startswith(("http://", "https://")) and not urlparse(current_source).netloc.endswith("githubusercontent.com"):
        candidates.append(current_source)
    for match in re.findall(r"https?://[^\s)\]>\"]+", body):
        if any(host in match for host in ("planalto.gov.br", "normas.leg.br", "camara.leg.br", "senado.leg.br")):
            candidates.append(match.rstrip(".,"))
    result: list[str] = []
    for url in candidates:
        parsed = urlparse(url)
        if not parsed.netloc or parsed.netloc.endswith("githubusercontent.com"):
            continue
        if url not in result:
            result.append(url)
    return result[:5]


def parse_date(current: dict[str, object], raw_path: Path | None, row: dict[str, str]) -> str | None:
    raw_date = scalar(current.get("data_assinatura")) or scalar(current.get("data"))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
        return raw_date
    if raw_path:
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", raw_path.name)
        if match:
            return "-".join(match.groups())
    if row["tipo"] in {"constituicao", "ato constitucional"}:
        return "1988-10-05"
    return None


def extract_ementa(current: dict[str, object], body: str) -> str | None:
    existing = scalar(current.get("ementa"))
    if existing:
        return existing
    for line in body.splitlines()[:18]:
        clean = re.sub(r"[*_`#]", "", line).strip()
        if not clean or clean.startswith(">"):
            continue
        if re.match(r"^(LEI|DECRETO|DECRETO-LEI|EMENDA|O PRESIDENTE|FAÇO|FA[ÇC]O|CONSIDERANDO|NÓS,)", clean, re.I):
            continue
        if len(clean) > 20 and not re.match(r"^(Art\.|ART\.|I\s+-|II\s+-|§)", clean):
            return clean
    return None


def neutral_layer(row: dict[str, str]) -> str:
    if row.get("camada") in {"core_constitucional", "core_codigos", "core_profissional", "cobertura_especializada", "auditoria_especialista"}:
        return row["camada"]
    if row["dominio"] == "constitucional":
        return "core_constitucional"
    if "codigo" in row["instrumento"].lower() or row["dominio"] in {
        "civil", "processo civil", "processo penal", "penal", "tributario", "consumidor",
        "eleitoral", "ambiental", "trabalhista",
    }:
        return "core_codigos"
    if row["prioridade"] == "P0":
        return "core_profissional"
    if row["camada"] == "specialist_gap_2026":
        return "auditoria_especialista"
    return "cobertura_especializada"


def canonical_status(current: dict[str, object], sources: list[str]) -> str:
    status = scalar(current.get("consolidacao_status"))
    if status not in ALLOWED_STATUS:
        status = "requer_reconciliacao"
    if not sources and status == "consolidada_fonte_oficial":
        status = "requer_reconciliacao"
    return status


def body_without_technical_preamble(body: str) -> str:
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


def build_record(row: dict[str, str], path: Path, snapshot: Path) -> tuple[dict[str, object], str, dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    current, body = parse_frontmatter(text)
    origin = scalar(current.get("origem_caminho"))
    raw_path = snapshot / origin if origin else None
    raw_bytes = raw_path.read_bytes() if raw_path and raw_path.is_file() else path.read_bytes()
    sources = source_url(raw_path, current, body)
    status = canonical_status(current, sources)
    norm_type = TYPE_MAP.get(row["tipo"].lower(), row["tipo"].lower().replace(" ", "_"))
    identifier = f"br-federal-{norm_type}-{row['numero'] or row['ano']}-{row['ano']}"
    if not row["numero"]:
        identifier = f"br-federal-{norm_type}-{row['ano']}"
    metadata: dict[str, object] = {
        "id": identifier,
        "titulo": row["instrumento"],
        "esfera": "federal",
        "jurisdicao": "BR",
        "tipo": norm_type,
        "numero": row["numero"] or None,
        "ano": int(row["ano"]) if row["ano"] else None,
        "dominio": row["dominio"],
        "prioridade": row["prioridade"],
        "publicos": row["publicos"].split("|") if row["publicos"] else [],
        "sensibilidade_atualizacao": row["sensibilidade_atualizacao"],
        "data_assinatura": parse_date(current, raw_path, row),
        "ementa": extract_ementa(current, body),
        "situacao": "em_vigor" if status in {"consolidada_fonte_oficial", "consolidada_reconciliada"} else "desconhecida",
        "versao_texto": "consolidada" if status in {"consolidada_fonte_oficial", "consolidada_reconciliada"} else "original",
        "consolidacao_status": status,
        "data_corte": TODAY,
        "fonte_oficial": sources,
        "fonte_publicacao": [],
        "origem_formato": scalar(current.get("origem_formato")) or "markdown",
        "baixado_em": TODAY,
        "sha256_origem": hashlib.sha256(raw_bytes).hexdigest(),
        "alterada_por": [],
        "revogada_por": [],
        "regulamentada_por": [],
        "retificada_por": [],
        "relacionada_a": [],
        "observacoes_proveniencia": ["Texto normalizado para o contrato público; trilha técnica mantida localmente."],
    }
    private = {
        "id": identifier,
        "matrix_id": row["id"],
        "path": path.relative_to(ROOT).as_posix(),
        "origin_path": origin,
        "snapshot": snapshot.name,
        "origin_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "migration_source": "curated-corpus",
        "transformation": "frontmatter-normalization-preserve-body",
    }
    return metadata, body_without_technical_preamble(body), private


def write_matrix(rows: list[dict[str, str]], records: dict[str, dict[str, object]]) -> None:
    target = ROOT / "manifests/corpus.csv"
    fields = [
        "id", "camada", "dominio", "instrumento", "tipo", "numero", "ano", "prioridade",
        "publicos", "motivo_inclusao", "fonte_oficial", "status_cobertura", "status_integridade",
        "status_atualidade", "sensibilidade_atualizacao",
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";")
        writer.writeheader()
        for row in rows:
            meta = records[row["id"]]
            writer.writerow({
                "id": meta["matrix_id"],
                "camada": meta["camada"],
                "dominio": row["dominio"],
                "instrumento": row["instrumento"],
                "tipo": meta["tipo"],
                "numero": row["numero"],
                "ano": row["ano"],
                "prioridade": row["prioridade"],
                "publicos": row["publicos"],
                "motivo_inclusao": row.get("nota_curatorial") or row.get("motivo_inclusao") or "Incluído por cobertura temática.",
                "fonte_oficial": "|".join(meta["fonte_oficial"]),
                "status_cobertura": "incluido",
                "status_integridade": "integral",
                "status_atualidade": "confirmada" if meta["situacao"] == "em_vigor" else "pendente",
                "sensibilidade_atualizacao": row["sensibilidade_atualizacao"],
            })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print(f"Dry-run: migraria {len(list_rows())} documentos para o contrato público.")
        return 0

    rows = list_rows()
    snapshot = latest_snapshot()
    by_matrix = {row["id"]: row for row in rows}
    old_files = sorted(CURATED.rglob("*.md"))
    private_records: list[dict[str, object]] = []
    records: dict[str, dict[str, object]] = {}
    missing = 0
    for path in old_files:
        current, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        matrix_id = scalar(current.get("id"))
        match = re.search(r"br-federal-(?:[^-]+-)?(?:\d+)-?\d{4}", matrix_id)
        row = None
        for candidate in rows:
            if candidate["instrumento"].lower() == scalar(current.get("titulo")).lower() and candidate["ano"] == scalar(current.get("ano")):
                row = candidate
                break
        if row is None and len(old_files) == len(rows):
            # The existing corpus is generated in matrix order; fallback keeps migration deterministic.
            row = rows[len(private_records)]
        if row is None:
            continue
        metadata, body, private = build_record(row, path, snapshot)
        metadata["id"] = f"br-federal-{metadata['tipo']}-{row['numero'] or row['ano']}-{row['ano']}" if row["numero"] else f"br-federal-{metadata['tipo']}-{row['ano']}"
        metadata["camada"] = neutral_layer(row)
        private["matrix_id"] = row["id"]
        private_records.append(private)
        records[row["id"]] = {**metadata, "matrix_id": row["id"], "camada": metadata["camada"]}
        if not metadata["fonte_oficial"]:
            missing += 1
        path.write_text(frontmatter(metadata) + "\n" + body, encoding="utf-8", newline="\n")

    write_matrix(rows, records)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    (PRIVATE / "provenance.json").write_text(
        json.dumps({"generated_at": TODAY, "records": private_records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Migrados: {len(records)}; fontes oficiais ausentes: {missing}; snapshot: {snapshot.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
