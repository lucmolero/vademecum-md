"""Validate the public corpus contract and release blockers."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from migrate_public_corpus import ALLOWED_STATUS, CURATED, ROOT, parse_frontmatter
from pipeline_modes import load_modes


REQUIRED = {
    "id", "titulo", "esfera", "jurisdicao", "tipo", "ano", "data_assinatura",
    "ementa", "situacao", "versao_texto", "consolidacao_status", "data_corte",
    "fonte_oficial", "fonte_publicacao", "origem_formato", "baixado_em", "sha256_origem",
    "alterada_por", "revogada_por", "regulamentada_por", "retificada_por", "relacionada_a",
    "observacoes_proveniencia",
}
FORBIDDEN_PUBLIC_MARKERS = (
    "ct" + "resb",
    "raw" + ".githubusercontent.com",
    "up" + "stream",
    "editorial" + "_benchmark",
    "senado" + "_4ed",
    "vade_mecum_" + "senado",
    "vade_mecum_" + "profissional_2026",
)
AUTONOMOUS_AGENT = "autonomous_legal_agent"


def validate_analysis_policy(errors: list[str]) -> None:
    path = ROOT / "manifests/analysis-policy.json"
    if not path.is_file():
        errors.append("analysis authority policy missing")
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"analysis authority policy invalid: {error}")
        return
    if payload.get("schema") != "analysis-authority-policy/v1":
        errors.append("analysis authority policy schema invalid")
    if payload.get("decision_authority") != AUTONOMOUS_AGENT:
        errors.append("legal analysis authority is not autonomous")
    if payload.get("deterministic_gate_authority") != "release_validators":
        errors.append("deterministic gate authority is not release_validators")
    legal = payload.get("legal_analysis") or {}
    deterministic = payload.get("deterministic_analysis") or {}
    if legal.get("executor") != AUTONOMOUS_AGENT or legal.get("method") != "llm_legal_analysis_plus_official_evidence":
        errors.append("legal analysis method is not the declared LLM-plus-official-evidence method")
    if legal.get("must_not_invent_text") is not True or legal.get("must_record_evidence") is not True:
        errors.append("legal analysis policy does not prohibit invented text or require evidence")
    if deterministic.get("executor") != "release_validators" or deterministic.get("method") != "deterministic_validation":
        errors.append("deterministic validation method is not declared correctly")
    if deterministic.get("must_not_decide_legal_meaning") is not True:
        errors.append("deterministic validators are incorrectly authorized to decide legal meaning")
    if payload.get("user_action_required") is not False:
        errors.append("analysis policy still requires user action")


def validate_operating_modes(errors: list[str]) -> None:
    try:
        payload = load_modes()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"operating modes invalid: {error}")
        return
    policy = payload.get("policy", {})
    if policy.get("no_direct_main_mutation") is not True:
        errors.append("operating modes allow direct main mutation")
    if policy.get("no_human_content_decision_required") is not True:
        errors.append("operating modes require human content decision")
    if policy.get("official_sources_only") is not True:
        errors.append("operating modes do not enforce official sources")


def public_files() -> list[Path]:
    paths: list[Path] = []
    for directory in (
        ROOT / "bases/curated",
        ROOT / "bases/derived",
        ROOT / "bases/history/alteracoes",
        ROOT / "bases/history/versoes",
        ROOT / "docs",
        ROOT / "manifests",
        ROOT / "tools",
        ROOT / ".github",
    ):
        if directory.exists():
            paths.extend(
                p for p in directory.rglob("*")
                if p.is_file() and ".private" not in p.parts and "__pycache__" not in p.parts
                and p.suffix.lower() in {".md", ".json", ".csv", ".py", ".yml", ".yaml", ".toml"}
            )
    paths.append(ROOT / "README.md")
    paths.append(ROOT / "SECURITY.md")
    return sorted(set(paths))


def registry_hosts() -> set[str]:
    registry_path = ROOT / "manifests/sources-registry.json"
    if not registry_path.is_file():
        return set()
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    return {
        str(host).lower().lstrip(".")
        for source in payload.get("sources", [])
        for host in source.get("hosts", [])
    }


def official_url(url: str, allowed_hosts: set[str]) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return any(host == allowed or host.endswith("." + allowed) for allowed in allowed_hosts)


def validate_source_registry(errors: list[str]) -> set[str]:
    path = ROOT / "manifests/sources-registry.json"
    if not path.is_file():
        errors.append("registry de fontes ausente")
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"registry de fontes inválido: {error}")
        return set()
    if payload.get("schema") != "official-source-registry/v1":
        errors.append("schema do registry de fontes inválido")
    if payload.get("policy", {}).get("official_only") is not True:
        errors.append("registry não exige fontes oficiais")
    seen: set[str] = set()
    ranks: set[int] = set()
    hosts: set[str] = set()
    for source in payload.get("sources", []):
        required = {"id", "authority", "rank", "adapter", "adapter_version", "hosts", "formats", "rate_limit_seconds", "max_bytes"}
        missing = required - set(source)
        if missing:
            errors.append(f"registry {source.get('id')}: campos ausentes {sorted(missing)}")
        identifier = str(source.get("id"))
        if identifier in seen:
            errors.append(f"registry: ID duplicado {identifier}")
        seen.add(identifier)
        try:
            rank = int(source.get("rank"))
        except (TypeError, ValueError):
            rank = -1
        if rank in ranks:
            errors.append(f"registry: precedência duplicada {rank}")
        ranks.add(rank)
        hosts.update(str(host).lower().lstrip(".") for host in source.get("hosts", []))
        if float(source.get("rate_limit_seconds", 0)) < 0 or int(source.get("max_bytes", 0)) <= 0:
            errors.append(f"registry {identifier}: limites inválidos")
    return hosts


def validate_discovery_registry(errors: list[str], allowed_hosts: set[str]) -> None:
    path = ROOT / "manifests/discovery-registry.json"
    if not path.is_file():
        errors.append("registry de descoberta ausente")
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "official-discovery-registry/v1":
        errors.append("schema do registry de descoberta inválido")
    for catalog in payload.get("catalogs", []):
        url = str(catalog.get("url", ""))
        if not official_url(url, allowed_hosts):
            errors.append(f"catálogo de descoberta não oficial: {url}")
        if not catalog.get("adapter") or int(catalog.get("max_bytes", 0)) <= 0:
            errors.append(f"catálogo de descoberta incompleto: {catalog.get('id')}")


def validate_editorial_legal_audit(errors: list[str], corpus_ids: set[str]) -> None:
    path = ROOT / "bases/derived/relatorios/editorial-legal-audit.json"
    if not path.is_file():
        errors.append("auditoria juridica editorial ausente")
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"auditoria juridica editorial invalida: {error}")
        return
    if payload.get("schema") != "editorial-legal-audit/v1":
        errors.append("schema da auditoria juridica editorial invalido")
    if payload.get("status") != "pass":
        errors.append("auditoria juridica editorial nao passou")
    documents = payload.get("documents") or []
    seen: set[str] = set()
    for item in documents:
        identifier = str(item.get("document_id") or "")
        if identifier in seen:
            errors.append(f"auditoria juridica duplicada: {identifier}")
        seen.add(identifier)
        if identifier not in corpus_ids:
            errors.append(f"auditoria juridica aponta para ID inexistente: {identifier}")
        if item.get("decision") != "approved_for_curated_corpus":
            errors.append(f"auditoria juridica sem aprovacao: {identifier}")
        if item.get("source_status") not in {"unchanged", "changed_candidate"} or item.get("hash_match") is not True:
            errors.append(f"auditoria juridica sem confirmacao de fonte/hash: {identifier}")
        if ".private" in str(item.get("path") or "") or "raw" in str(item.get("path") or "").lower():
            errors.append(f"auditoria juridica expoe caminho privado/bruto: {identifier}")
    p0_path = ROOT / "bases/derived/relatorios/editorial-legal-audit-p0.json"
    if not p0_path.is_file():
        errors.append("auditoria juridica do P0 ausente")
        return
    try:
        p0_payload = json.loads(p0_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"auditoria juridica do P0 invalida: {error}")
        return
    p0_documents = p0_payload.get("documents") or []
    expected_p0 = sum(
        1
        for path in CURATED.rglob("*.md")
        for metadata, _ in [parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)]
        if metadata.get("prioridade") == "P0"
    )
    if p0_payload.get("schema") != "editorial-legal-audit/v1" or p0_payload.get("status") != "pass":
        errors.append("auditoria juridica do P0 nao passou")
    if len(p0_documents) != expected_p0 or p0_payload.get("approved_count") != expected_p0:
        errors.append("auditoria juridica do P0 incompleta")
    if any(item.get("decision") != "approved_for_curated_corpus" or item.get("hash_match") is not True for item in p0_documents):
        errors.append("auditoria juridica do P0 possui documento sem aprovação/hash")

    for priority, filename in (("P1", "editorial-legal-audit-p1.json"), ("P2", "editorial-legal-audit-p2.json")):
        audit_path = ROOT / "bases/derived/relatorios" / filename
        if not audit_path.is_file():
            errors.append(f"auditoria juridica do {priority} ausente")
            continue
        try:
            audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"auditoria juridica do {priority} invalida: {error}")
            continue
        expected = sum(
            1
            for path in CURATED.rglob("*.md")
            for metadata, _ in [parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)]
            if metadata.get("prioridade") == priority
        )
        audit_documents = audit_payload.get("documents") or []
        if audit_payload.get("schema") != "editorial-legal-audit/v1" or audit_payload.get("status") != "pass":
            errors.append(f"auditoria juridica do {priority} nao passou")
        if len(audit_documents) != expected or audit_payload.get("approved_count") != expected:
            errors.append(f"auditoria juridica do {priority} incompleta")
        if any(item.get("decision") != "approved_for_curated_corpus" or item.get("hash_match") is not True for item in audit_documents):
            errors.append(f"auditoria juridica do {priority} possui documento sem aprovacao/hash")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="falha também se houver P0 não consolidado")
    args = parser.parse_args()
    errors: list[str] = []
    validate_analysis_policy(errors)
    validate_operating_modes(errors)
    allowed_registry_hosts = validate_source_registry(errors)
    validate_discovery_registry(errors, allowed_registry_hosts)
    docs = []
    ids: set[str] = set()
    triples: set[tuple[str, str, str]] = set()
    for path in sorted(CURATED.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            metadata, body = parse_frontmatter(text, strict=True)
        except ValueError as error:
            errors.append(f"{path}: frontmatter invÃ¡lido: {error}")
            continue
        docs.append((path, metadata, body))
        missing = REQUIRED - set(metadata)
        if missing:
            errors.append(f"{path}: campos ausentes {sorted(missing)}")
        identifier = str(metadata.get("id"))
        if identifier in ids:
            errors.append(f"ID duplicado: {identifier}")
        ids.add(identifier)
        triple = (str(metadata.get("tipo")), str(metadata.get("numero")), str(metadata.get("ano")))
        if metadata.get("numero") is not None and triple in triples:
            errors.append(f"tipo/numero/ano duplicado: {triple}")
        triples.add(triple)
        status = metadata.get("consolidacao_status")
        if status not in ALLOWED_STATUS:
            errors.append(f"{path}: status inválido {status}")
        if not body.strip():
            errors.append(f"{path}: corpo vazio")
        sources = metadata.get("fonte_oficial")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{path}: fonte oficial ausente")
        elif not all(official_url(str(url), allowed_registry_hosts) for url in sources):
            errors.append(f"{path}: fonte não oficial")
        digest = str(metadata.get("sha256_origem") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"{path}: hash inválido")
        if metadata.get("situacao") == "em_vigor" and status not in {"consolidada_fonte_oficial", "consolidada_reconciliada"}:
            errors.append(f"{path}: vigente sem consolidação confirmada")

    matrix = ROOT / "manifests/corpus.csv"
    matrix_rows: list[dict[str, str]] = []
    if not matrix.is_file():
        errors.append("manifests/corpus.csv ausente")
    else:
        with matrix.open(encoding="utf-8", newline="") as stream:
            matrix_rows = list(csv.DictReader(stream, delimiter=";"))
        if len(matrix_rows) != len(docs):
            errors.append("matriz e corpus têm quantidades diferentes")
        required_matrix_columns = {"document_id", "document_path", "status_consolidacao", "status_situacao", "data_corte", "sha256_origem", "fonte_oficial_count"}
        if matrix_rows and not required_matrix_columns <= set(matrix_rows[0]):
            errors.append("matriz editorial sem colunas canonicas completas")
        elif matrix_rows:
            matrix_ids = {str(row.get("document_id")) for row in matrix_rows}
            if matrix_ids != ids:
                errors.append("matriz editorial e corpus possuem IDs canonicos diferentes")
            for row in matrix_rows:
                if row.get("status_consolidacao") not in ALLOWED_STATUS:
                    errors.append(f"matriz: status de consolidacao invalido {row.get('id')}")
                if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256_origem") or "")):
                    errors.append(f"matriz: hash invalido {row.get('id')}")
                if not row.get("document_path") or not (ROOT / str(row.get("document_path"))).is_file():
                    errors.append(f"matriz: caminho canonico ausente {row.get('id')}")
        if {row["camada"] for row in matrix_rows} - {"core_constitucional", "core_codigos", "core_profissional", "cobertura_especializada", "auditoria_especialista"}:
            errors.append("camada editorial não neutra")

    if matrix_rows and len(docs) != len(matrix_rows):
        errors.append(f"corpus esperado pela matriz: {len(matrix_rows)}; encontrado: {len(docs)}")

    baseline = ROOT / "manifests/baseline.json"
    if not baseline.is_file():
        errors.append("manifesto de baseline ausente")
    else:
        try:
            baseline_payload = json.loads(baseline.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            baseline_payload = {}
            errors.append(f"manifesto de baseline inválido: {error}")
        if baseline_payload.get("schema") != "vademecum-baseline/v1":
            errors.append("schema do baseline inválido")
        if baseline_payload.get("corpus_count") != len(docs) or baseline_payload.get("matrix_count") != len(matrix_rows):
            errors.append("baseline divergente do corpus ou da matriz")
        actual_p0_total = sum(meta.get("prioridade") == "P0" for _, meta, _ in docs)
        actual_p0_ready = sum(
            meta.get("prioridade") == "P0"
            and meta.get("consolidacao_status") in {"consolidada_fonte_oficial", "consolidada_reconciliada"}
            for _, meta, _ in docs
        )
        if baseline_payload.get("p0", {}).get("ready") != actual_p0_ready or baseline_payload.get("p0", {}).get("total") != actual_p0_total:
            errors.append("baseline divergente do P0")

    promotion_manifest = ROOT / "manifests/editorial-promotions.json"
    if not promotion_manifest.is_file():
        errors.append("manifesto de promoções editoriais ausente")
    else:
        try:
            promotion_payload = json.loads(promotion_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"manifesto de promoções inválido: {error}")
            promotion_payload = {}
        if promotion_payload.get("schema") != "editorial-promotion-decision/v2":
            errors.append("schema do manifesto de promoções inválido")
        if promotion_payload.get("reviewed_by") != AUTONOMOUS_AGENT or promotion_payload.get("analysis_executor") != AUTONOMOUS_AGENT:
            errors.append("manifesto de promoções sem executor jurídico autônomo")
        expansion = ROOT / "manifests/editorial-expansion.csv"
        expansion_rows: list[dict[str, str]] = []
        if expansion.is_file():
            with expansion.open(encoding="utf-8-sig", newline="") as stream:
                expansion_rows = list(csv.DictReader(stream, delimiter=";"))
        expansion_by_id = {row.get("id"): row for row in expansion_rows}
        matrix_by_id = {row.get("id"): row for row in matrix_rows}
        for candidate_id, decision in (promotion_payload.get("decisions") or {}).items():
            if not isinstance(decision, dict) or decision.get("decision") != "promote":
                errors.append(f"promoção sem decisão promote: {candidate_id}")
                continue
            if decision.get("situacao") not in {"em_vigor", "desconhecida", "revogada", "parcialmente_revogada", "transitoria", "historica"}:
                errors.append(f"promoção sem situação jurídica válida: {candidate_id}")
            if not isinstance(decision.get("evidencias"), list) or not decision.get("evidencias"):
                errors.append(f"promoção sem evidências: {candidate_id}")
            if not decision.get("revisor") or not decision.get("revisado_em"):
                errors.append(f"promoção sem revisão identificada: {candidate_id}")
            if decision.get("revisor") != AUTONOMOUS_AGENT or decision.get("analysis_executor") != AUTONOMOUS_AGENT:
                errors.append(f"promoção sem análise jurídica autônoma: {candidate_id}")
            if decision.get("analysis_method") != "llm_legal_analysis_plus_official_evidence":
                errors.append(f"promoção sem método de análise jurídica LLM declarado: {candidate_id}")
            if decision.get("deterministic_gate_method") != "deterministic_validation":
                errors.append(f"promoção sem método determinístico declarado: {candidate_id}")
            if decision.get("user_action_required") is not False:
                errors.append(f"promoção ainda depende de ação do usuário: {candidate_id}")
            if decision.get("review_status") != "approved_autonomously":
                errors.append(f"promoção sem status autônomo aprovado: {candidate_id}")
            matrix_id = str(decision.get("matrix_id") or "")
            if matrix_id not in matrix_by_id:
                errors.append(f"promoção sem linha canônica: {candidate_id} -> {matrix_id}")
            candidate = expansion_by_id.get(candidate_id)
            if not candidate or candidate.get("status_cobertura") != "promovido_corpus":
                errors.append(f"promoção não refletida na fila editorial: {candidate_id}")

    corpus_ids = ids
    validate_editorial_legal_audit(errors, corpus_ids)
    graph = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    if graph.is_file():
        for line_no, line in enumerate(graph.read_text(encoding="utf-8").splitlines(), 1):
            relation = json.loads(line)
            if relation["source_id"] not in corpus_ids or relation["target_id"] not in corpus_ids:
                errors.append(f"relação {line_no}: ID inexistente")
            if not relation.get("fonte"):
                errors.append(f"relação {line_no}: fonte ausente")

    if graph.is_file():
        for line_no, line in enumerate(graph.read_text(encoding="utf-8").splitlines(), 1):
            relation = json.loads(line)
            if not relation.get("evidencia_textual") or not relation.get("evidencia_sha256"):
                errors.append(f"relation {line_no}: missing textual evidence")
            elif hashlib.sha256(str(relation["evidencia_textual"]).encode("utf-8")).hexdigest() != str(relation["evidencia_sha256"]):
                errors.append(f"relation {line_no}: evidence hash mismatch")
            if relation.get("confianca") not in {"alta", "media", "baixa"}:
                errors.append(f"relation {line_no}: invalid confidence")
            if relation.get("status_revisao") != "aprovado_autonomamente":
                errors.append(f"relation {line_no}: missing autonomous review status")

    queue_path = ROOT / "bases/derived/relacoes/review-queue.json"
    if not queue_path.is_file():
        errors.append("autonomous relation queue missing")
    else:
        try:
            queue_payload = json.loads(queue_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"autonomous relation queue invalid: {error}")
            queue_payload = {}
        for item in queue_payload.get("targets", []):
            if item.get("review_status") != "approved":
                errors.append(f"relation target lacks autonomous decision: {item.get('target_key')}")
            if item.get("requires_editorial_decision") is not False:
                errors.append(f"relation target requires manual decision: {item.get('target_key')}")
            if item.get("disposition") not in {"historico", "grafo"}:
                errors.append(f"relation target lacks safe disposition: {item.get('target_key')}")
            if item.get("decision_scope") != "autonomous_agent_legal_curation":
                errors.append(f"relation target lacks autonomous scope: {item.get('target_key')}")
            if item.get("analysis_method") != "llm_legal_analysis_plus_deterministic_gates":
                errors.append(f"relation target lacks dual analysis method: {item.get('target_key')}")

    forbidden_hits: list[str] = []
    for path in public_files():
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for marker in FORBIDDEN_PUBLIC_MARKERS:
            if marker in text:
                forbidden_hits.append(f"{path.relative_to(ROOT)}: {marker}")
    errors.extend(f"referência pública proibida: {hit}" for hit in forbidden_hits)

    p0_total = sum(meta.get("prioridade") == "P0" for _, meta, _ in docs)
    p0_ready = sum(meta.get("prioridade") == "P0" and meta.get("consolidacao_status") in {"consolidada_fonte_oficial", "consolidada_reconciliada"} for _, meta, _ in docs)
    if args.strict and p0_ready != p0_total:
        errors.append(f"P0 pendente: {p0_ready}/{p0_total}")
    print(f"Documentos: {len(docs)}; P0 consolidado: {p0_ready}/{p0_total}; erros: {len(errors)}")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
