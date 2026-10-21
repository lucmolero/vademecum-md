"""Promote explicitly approved editorial candidates into the canonical corpus.

Discovery candidates are never promoted implicitly.  This command requires a
decision manifest, an official collection report, explicit candidate IDs, and
``--apply`` before it writes anything.  The private snapshot is used only as
evidence; public output contains the official URL and hashes, never its local
path.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "normalize"))

from migrate_public_corpus import frontmatter, parse_frontmatter  # noqa: E402
from official_html_to_markdown import convert  # noqa: E402


EXPANSION = ROOT / "manifests/editorial-expansion.csv"
MATRIX = ROOT / "manifests/corpus.csv"
ALLOWED_LAYERS = {
    "core_constitucional",
    "core_codigos",
    "core_profissional",
    "cobertura_especializada",
    "auditoria_especialista",
}
ALLOWED_HOSTS = {"planalto.gov.br", "normas.leg.br", "senado.leg.br", "camara.leg.br"}
TYPE_DIR = {
    "lei_ordinaria": "leis-ordinarias",
    "lei_complementar": "leis-complementares",
    "lei_delegada": "leis-delegadas",
    "decreto_lei": "decretos-lei",
    "decreto": "decretos",
}
ALLOWED_SITUATIONS = {
    "em_vigor",
    "desconhecida",
    "revogada",
    "parcialmente_revogada",
    "transitoria",
    "historica",
}
ALLOWED_DECISIONS = {"promote", "history", "out_of_scope", "reconcile"}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        return list(reader), list(reader.fieldnames or [])


def official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return any(host == allowed or host.endswith("." + allowed) for allowed in ALLOWED_HOSTS)


def load_attempt(report: dict[str, object], candidate_id: str, expected_raw: str) -> dict[str, object]:
    result = next((item for item in report.get("results", []) if item.get("matrix_id") == candidate_id), None)
    if not isinstance(result, dict):
        raise ValueError(f"{candidate_id}: resultado de coleta ausente")
    if result.get("status") != "changed_candidate":
        raise ValueError(f"{candidate_id}: status de coleta não aprovável: {result.get('status')}")
    attempts = [item for item in result.get("attempts", []) if item.get("status") == "fetched"]
    attempt = next((item for item in attempts if item.get("sha256_raw") == expected_raw), None)
    if not attempt:
        raise ValueError(f"{candidate_id}: snapshot não coincide com o hash da matriz de expansão")
    snapshot_name = str(attempt.get("snapshot_file") or "")
    snapshot = ROOT / snapshot_name
    if not snapshot.is_file():
        raise ValueError(f"{candidate_id}: snapshot local ausente")
    actual_raw = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    if actual_raw != expected_raw:
        raise ValueError(f"{candidate_id}: hash bruto do snapshot não confere")
    source = str(attempt.get("url") or result.get("primary_url") or "")
    if not official(source):
        raise ValueError(f"{candidate_id}: fonte fora da allowlist oficial: {source}")
    return {"result": result, "attempt": attempt, "snapshot": snapshot, "source": source}


def canonical_path(document_type: str, number: str, year: str) -> Path:
    directory = TYPE_DIR.get(document_type)
    if not directory or not number or not year:
        raise ValueError(f"tipo/número/ano não suportado: {document_type}/{number}/{year}")
    return ROOT / "bases/curated/legislacao/federal" / directory / year / f"{document_type.replace('_', '-')}-{number}-{year}.md"


def canonical_id(document_type: str, number: str, year: str) -> str:
    return f"br-federal-{document_type}-{number}-{year}"


def build_metadata(row: dict[str, str], decision: dict[str, object], attempt: dict[str, object], as_of: str, document_id: str) -> dict[str, object]:
    source = str(attempt["source"])
    status = str(decision.get("consolidacao_status") or "")
    if status not in {"consolidada_fonte_oficial", "consolidada_reconciliada"}:
        raise ValueError(f"{row['id']}: promoção exige status de consolidação válido")
    layer = str(decision.get("camada") or "")
    if layer not in ALLOWED_LAYERS:
        raise ValueError(f"{row['id']}: camada editorial inválida: {layer}")
    situation = str(decision.get("situacao") or "")
    if situation not in ALLOWED_SITUATIONS:
        raise ValueError(f"{row['id']}: situação jurídica inválida ou ausente: {situation}")
    evidence = decision.get("evidencias")
    if not isinstance(evidence, list) or not evidence or not all(str(item).strip() for item in evidence):
        raise ValueError(f"{row['id']}: evidências jurídicas ausentes")
    if not str(decision.get("revisor") or "").strip():
        raise ValueError(f"{row['id']}: revisor ausente")
    if not str(decision.get("revisado_em") or "").strip():
        raise ValueError(f"{row['id']}: data de revisão ausente")
    number = str(row.get("numero") or "")
    year = str(row.get("ano") or "")
    return {
        "id": document_id,
        "titulo": str(decision["titulo"]),
        "esfera": "federal",
        "jurisdicao": "BR",
        "tipo": str(row["tipo"]),
        "numero": number,
        "ano": int(year),
        "dominio": str(row["dominio"]),
        "prioridade": str(row["prioridade"]),
        "publicos": list(decision.get("publicos") or ["academia", "OAB", "concursos", "pratica"]),
        "sensibilidade_atualizacao": str(decision.get("sensibilidade_atualizacao") or "alta"),
        "data_assinatura": str(decision["data_assinatura"]),
        "ementa": str(decision["ementa"]),
        "situacao": situation,
        "versao_texto": "consolidada",
        "consolidacao_status": status,
        "data_corte": as_of,
        "fonte_oficial": [source],
        "fonte_publicacao": [],
        "origem_formato": "html",
        "baixado_em": as_of,
        "sha256_origem": str(attempt["sha256_raw"]),
        "sha256_normalizado": str(attempt.get("sha256_normalized") or ""),
        "sha256_corpo": str(attempt.get("sha256_body") or ""),
        "alterada_por": [],
        "revogada_por": [],
        "regulamentada_por": [],
        "retificada_por": [],
        "relacionada_a": [],
        "observacoes_proveniencia": [
            "Texto incluído após decisão editorial explícita e verificação de fonte oficial.",
            str(decision.get("motivo") or decision.get("nota_curatorial") or ""),
            *[str(item) for item in evidence],
        ],
        "camada": layer,
    }


def matrix_row(row: dict[str, str], decision: dict[str, object], metadata: dict[str, object], path: Path, matrix_id: str) -> dict[str, str]:
    sources = metadata["fonte_oficial"]
    return {
        "id": matrix_id,
        "camada": str(metadata["camada"]),
        "dominio": row["dominio"],
        "instrumento": str(decision["instrumento"]),
        "tipo": row["tipo"],
        "numero": row["numero"],
        "ano": row["ano"],
        "prioridade": row["prioridade"],
        "publicos": "|".join(metadata["publicos"]),
        "motivo_inclusao": str(decision["motivo_inclusao"]),
        "fonte_oficial": "|".join(sources),
        "status_cobertura": "incluido",
        "status_integridade": "integral",
        "status_atualidade": "confirmada",
        "sensibilidade_atualizacao": str(metadata["sensibilidade_atualizacao"]),
        "document_id": str(metadata["id"]),
        "document_path": path.relative_to(ROOT).as_posix(),
        "status_consolidacao": str(metadata["consolidacao_status"]),
        "status_situacao": str(metadata["situacao"]),
        "data_corte": str(metadata["data_corte"]),
        "sha256_origem": str(metadata["sha256_origem"]),
        "fonte_oficial_count": str(len(sources)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-file", type=Path, required=True)
    parser.add_argument("--collection-report", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", required=True, help="candidate IDs; never inferred")
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    decisions = json.loads(args.decision_file.read_text(encoding="utf-8"))
    if decisions.get("schema") != "editorial-promotion-decision/v2":
        raise SystemExit("manifesto de decisão inválido")
    report = json.loads(args.collection_report.read_text(encoding="utf-8"))
    expansion_rows, expansion_fields = read_csv(EXPANSION)
    matrix_rows, matrix_fields = read_csv(MATRIX)
    by_candidate = {row["id"]: row for row in expansion_rows}
    by_matrix_id = {row["id"]: row for row in matrix_rows}
    entries: list[dict[str, object]] = []
    selected = list(dict.fromkeys(args.ids))
    for candidate_id in selected:
        row = by_candidate.get(candidate_id)
        decision = decisions.get("decisions", {}).get(candidate_id)
        if not row or not isinstance(decision, dict):
            raise SystemExit(f"{candidate_id}: candidato ou decisão ausente")
        if decision.get("decision") not in ALLOWED_DECISIONS:
            raise SystemExit(f"{candidate_id}: decisão inválida")
        if decision.get("decision") != "promote":
            raise SystemExit(f"{candidate_id}: decisão não é promote; use a fila editorial para essa disposição")
        if row.get("status_cobertura") == "promovido_corpus":
            raise SystemExit(f"{candidate_id}: já promovido; operação não é idempotente")
        matrix_id = str(decision.get("matrix_id") or "")
        if not re.fullmatch(r"VM-\d+", matrix_id):
            raise SystemExit(f"{candidate_id}: matrix_id inválido: {matrix_id}")
        if row.get("status_aquisicao") != "adquirido_pendente_reconciliacao":
            raise SystemExit(f"{candidate_id}: candidato não está adquirido para reconciliação")
        attempt_info = load_attempt(report, candidate_id, str(row.get("sha256_origem") or ""))
        number = str(row["numero"])
        year = str(row["ano"])
        document_id = canonical_id(row["tipo"], number, year)
        path = canonical_path(row["tipo"], number, year)
        existing_document = path.is_file()
        if existing_document:
            existing_metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
            if str(existing_metadata.get("id")) != document_id or str(existing_metadata.get("sha256_origem")) != str(row.get("sha256_origem")):
                raise SystemExit(f"{candidate_id}: documento existente não corresponde ao snapshot aprovado")
        existing_matrix = by_matrix_id.get(matrix_id)
        if existing_matrix and str(existing_matrix.get("document_id")) != document_id:
            raise SystemExit(f"{candidate_id}: matrix_id já aponta para outro documento")
        body = convert(attempt_info["snapshot"], "auto")
        if not body.strip() or len(body) < 500 or any(ord(char) == 0xFFFD for char in body):
            raise SystemExit(f"{candidate_id}: corpo vazio, truncado ou com caractere de substituição")
        if not re.search(r"(?:\*\*)?Art\.\s+\d+", body):
            raise SystemExit(f"{candidate_id}: corpo sem artigos detectáveis")
        selected_attempt = dict(attempt_info["attempt"])
        selected_attempt["source"] = attempt_info["source"]
        metadata = build_metadata(row, decision, selected_attempt, args.as_of, document_id)
        text = frontmatter(metadata) + "\n\n# " + str(metadata["titulo"]) + "\n\n" + body
        entries.append({
            "candidate_id": candidate_id,
            "matrix_id": matrix_id,
            "document_id": document_id,
            "document_path": path.relative_to(ROOT).as_posix(),
            "source": attempt_info["source"],
            "sha256_origem": metadata["sha256_origem"],
            "sha256_corpo": metadata["sha256_corpo"],
            "body_characters": len(body),
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "already_present": existing_document and bool(existing_matrix),
            "text": text,
            "matrix_row": matrix_row(row, decision, metadata, path, matrix_id),
        })

    result_entries = [{key: value for key, value in entry.items() if key not in {"text", "matrix_row"}} for entry in entries]
    result = {
        "schema": "editorial-promotion-application/v1",
        "mode": "apply" if args.apply else "dry_run",
        "as_of": args.as_of,
        "candidate_ids": selected,
        "promoted_count": len(entries),
        "entries": result_entries,
        "policy": "autonomous_agent_decision_required; discovery_never_auto_promotes; official_source_only",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.apply:
        output_fields = list(matrix_fields)
        for entry in entries:
            if not entry["already_present"]:
                matrix_rows.append(entry["matrix_row"])
                target = ROOT / str(entry["document_path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(str(entry["text"]), encoding="utf-8", newline="\n")
        with MATRIX.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=output_fields, delimiter=";", lineterminator="\n")
            writer.writeheader()
            writer.writerows(matrix_rows)
        by_id = {row["id"]: row for row in expansion_rows}
        for entry in entries:
            candidate_id = str(entry["candidate_id"])
            by_id[candidate_id].update({
                "status_cobertura": "promovido_corpus",
                "status_integridade": "texto_oficial_promovido",
                "status_atualidade": "confirmada",
                "status_aquisicao": "promovido_corpus",
            })
        with EXPANSION.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=expansion_fields, delimiter=";", lineterminator="\n")
            writer.writeheader()
            writer.writerows([by_id[row["id"]] for row in expansion_rows])
    print(json.dumps({"mode": result["mode"], "promoted_count": len(entries), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
