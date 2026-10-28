"""Validate the deterministic source/fidelity gate ledger.

This gate verifies official evidence and makes its technical-only scope
explicit. It does not verify independent legal opinions or legal conclusions.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_DECISIONS = {"promote", "preserve_current", "history", "reconcile"}


def validate(path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return False, [f"consensus ledger invalid: {error}"]
    if payload.get("schema") != "legal-curation-consensus/v1":
        errors.append("invalid consensus schema")
    if payload.get("decision_authority") != "autonomous_legal_agent":
        errors.append("consensus lacks autonomous legal authority")
    if payload.get("analysis_method") != "deterministic_source_fidelity_gate":
        errors.append("ledger misstates its deterministic analysis method")
    if payload.get("independent_legal_opinion") is not False:
        errors.append("ledger must state that it is not an independent legal opinion")
    if payload.get("assessment_scope") != "source_identity_and_text_fidelity_only":
        errors.append("ledger must limit its scope to source identity and text fidelity")
    if payload.get("role_scope") != "legacy_technical_gate_label_not_legal_opinion":
        errors.append("ledger must disclose that legacy role names are not legal opinions")
    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        errors.append("consensus has no documents")
        return False, errors
    seen: set[str] = set()
    for item in documents:
        identifier = str(item.get("document_id") or "")
        if not identifier:
            errors.append("consensus item without document_id")
        if identifier in seen:
            errors.append(f"{identifier}: duplicate consensus item")
        seen.add(identifier)
        if item.get("decision") not in REQUIRED_DECISIONS:
            errors.append(f"{identifier}: invalid decision")
        if not item.get("official_evidence"):
            errors.append(f"{identifier}: consensus without official_evidence")
        for field in ("candidate_sha256_raw", "candidate_sha256_body"):
            if field in item and not re.fullmatch(r"[0-9a-f]{64}", str(item[field])):
                errors.append(f"{identifier}: invalid {field}")
        curator = item.get("legal_curator") or {}
        critic = item.get("legal_critic") or {}
        for role, pass_data in (("legal_curator", curator), ("legal_critic", critic)):
            if pass_data.get("status") != "complete":
                errors.append(f"{identifier}: {role} incomplete")
            if not pass_data.get("evidence"):
                errors.append(f"{identifier}: {role} without evidence")
            if pass_data.get("must_not_invent_text") is not True:
                errors.append(f"{identifier}: {role} does not prohibit invented text")
        if item.get("consensus") is not True or curator.get("decision") != critic.get("decision"):
            errors.append(f"{identifier}: curator/critic disagreement")
    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    valid, errors = validate(args.ledger)
    print(json.dumps({"valid": valid, "errors": errors}, ensure_ascii=False))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
