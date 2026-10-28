"""Record only exact, snapshot-verified autonomous legal text updates."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from validate_release import ROOT, official_url, registry_hosts


LEDGER = ROOT / "manifests/automatic-update-ledger.json"
HASH = re.compile(r"^[a-f0-9]{64}$")


def build_entries(application_path: Path, audit_path: Path) -> list[dict[str, str]]:
    application = json.loads(application_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if application.get("schema") != "reviewed-update-application/v1":
        raise ValueError("schema de aplicação de atualização inválido")
    if audit.get("schema") != "normative-fidelity-audit/v1":
        raise ValueError("schema de auditoria de fidelidade inválido")
    if application.get("mode") != "apply_reviewed":
        raise ValueError("aplicação não está no modo apply_reviewed")

    audited = [item for item in audit.get("documents", []) if isinstance(item, dict)]
    by_id: dict[str, list[dict[str, object]]] = {}
    for item in audited:
        by_id.setdefault(str(item.get("document_id") or ""), []).append(item)
    allowed_hosts = registry_hosts()
    entries = []
    applied = application.get("applied")
    if not isinstance(applied, list) or len(applied) != application.get("applied_count"):
        raise ValueError("lista de documentos aplicados inconsistente")
    seen: set[str] = set()
    for update in applied:
        if not isinstance(update, dict):
            raise ValueError("entrada aplicada inválida")
        identifier = str(update.get("document_id") or "")
        if not identifier or identifier in seen:
            raise ValueError(f"ID de documento ausente ou duplicado: {identifier}")
        seen.add(identifier)
        matches = by_id.get(identifier, [])
        if len(matches) != 1:
            raise ValueError(f"auditoria ausente ou ambígua para {identifier}")
        evidence = matches[0]
        if evidence.get("evidence_status") != "snapshot_verified":
            raise ValueError(f"snapshot oficial não verificado: {identifier}")
        if evidence.get("equivalence_status") != "pass" or evidence.get("equivalence_basis") != "normalized_exact_match":
            raise ValueError(f"texto atualizado não é correspondência exata: {identifier}")
        if evidence.get("source_published_hash_match") is not True:
            raise ValueError(f"hash da fonte não corresponde ao texto publicado: {identifier}")
        source_hash = str(evidence.get("sha256_source_body") or "")
        published_hash = str(evidence.get("sha256_published_body") or "")
        if not HASH.fullmatch(source_hash) or source_hash != published_hash:
            raise ValueError(f"hashes normativos inválidos ou diferentes: {identifier}")
        source_url = str(update.get("source") or "")
        if urlparse(source_url).scheme != "https" or not official_url(source_url, allowed_hosts):
            raise ValueError(f"fonte da atualização não consta no registro oficial: {identifier}")
        if str(update.get("path") or "") != str(evidence.get("path") or ""):
            raise ValueError(f"caminho auditado não corresponde à aplicação: {identifier}")
        entries.append({
            "document_id": identifier,
            "path": str(evidence["path"]),
            "source_url": source_url,
            "source_id": str(update.get("source_id") or ""),
            "approved_source_body_sha256": source_hash,
            "approved_published_body_sha256": published_hash,
            "evidence_status": "snapshot_verified",
            "equivalence_basis": "normalized_exact_match",
        })
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--application", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="write the durable provenance ledger")
    args = parser.parse_args()
    try:
        new_entries = build_entries(args.application, args.audit)
        existing = {"schema": "automatic-update-ledger/v1", "documents": []}
        if LEDGER.exists():
            existing = json.loads(LEDGER.read_text(encoding="utf-8"))
            if existing.get("schema") != "automatic-update-ledger/v1":
                raise ValueError("schema do ledger de atualizações inválido")
        by_id = {str(item.get("document_id")): item for item in existing.get("documents", [])}
        for item in new_entries:
            by_id[item["document_id"]] = item
        result = {"schema": "automatic-update-ledger/v1", "documents": [by_id[key] for key in sorted(by_id)]}
        if args.apply and new_entries:
            LEDGER.parent.mkdir(parents=True, exist_ok=True)
            LEDGER.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"validated_updates": len(new_entries), "ledger_entries": len(result["documents"]), "written": bool(args.apply and new_entries)}))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
