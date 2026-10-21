"""Validate the public corpus contract and release blockers."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from migrate_public_corpus import ALLOWED_STATUS, CURATED, ROOT, parse_frontmatter


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


def public_files() -> list[Path]:
    paths: list[Path] = []
    for directory in (ROOT / "bases/curated", ROOT / "docs", ROOT / "manifests", ROOT / "tools", ROOT / ".github"):
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="falha também se houver P0 não consolidado")
    args = parser.parse_args()
    errors: list[str] = []
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

    if len(docs) != 360:
        errors.append(f"corpus esperado: 360; encontrado: {len(docs)}")
    matrix = ROOT / "manifests/corpus.csv"
    if not matrix.is_file():
        errors.append("manifests/corpus.csv ausente")
    else:
        with matrix.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=";"))
        if len(rows) != len(docs):
            errors.append("matriz e corpus têm quantidades diferentes")
        required_matrix_columns = {"document_id", "document_path", "status_consolidacao", "status_situacao", "data_corte", "sha256_origem", "fonte_oficial_count"}
        if rows and not required_matrix_columns <= set(rows[0]):
            errors.append("matriz editorial sem colunas canonicas completas")
        elif rows:
            matrix_ids = {str(row.get("document_id")) for row in rows}
            if matrix_ids != ids:
                errors.append("matriz editorial e corpus possuem IDs canonicos diferentes")
            for row in rows:
                if row.get("status_consolidacao") not in ALLOWED_STATUS:
                    errors.append(f"matriz: status de consolidacao invalido {row.get('id')}")
                if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256_origem") or "")):
                    errors.append(f"matriz: hash invalido {row.get('id')}")
                if not row.get("document_path") or not (ROOT / str(row.get("document_path"))).is_file():
                    errors.append(f"matriz: caminho canonico ausente {row.get('id')}")
        if {row["camada"] for row in rows} - {"core_constitucional", "core_codigos", "core_profissional", "cobertura_especializada", "auditoria_especialista"}:
            errors.append("camada editorial não neutra")

    corpus_ids = ids
    graph = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    if graph.is_file():
        for line_no, line in enumerate(graph.read_text(encoding="utf-8").splitlines(), 1):
            relation = json.loads(line)
            if relation["source_id"] not in corpus_ids or relation["target_id"] not in corpus_ids:
                errors.append(f"relação {line_no}: ID inexistente")
            if not relation.get("fonte"):
                errors.append(f"relação {line_no}: fonte ausente")

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
