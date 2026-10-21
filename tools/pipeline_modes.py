"""Shared operating-mode contract for acquisition, application and release."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES_PATH = ROOT / "manifests/operating-modes.json"
MODES = ("dry_run", "proposal", "apply_reviewed", "release")


def load_modes() -> dict[str, object]:
    payload = json.loads(MODES_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != "pipeline-operating-modes/v1":
        raise ValueError("invalid operating modes schema")
    if payload.get("decision_authority") != "autonomous_legal_agent":
        raise ValueError("operating modes must use the autonomous legal agent")
    missing = set(MODES) - set(payload.get("modes", {}))
    if missing:
        raise ValueError(f"missing operating modes: {sorted(missing)}")
    return payload


def resolve_mode(mode: str | None, *, legacy_mutation: bool = False, legacy_fetch: bool = False) -> str:
    if mode:
        if mode not in MODES:
            raise ValueError(f"invalid operating mode: {mode}")
        return mode
    if legacy_mutation:
        return "apply_reviewed"
    if legacy_fetch:
        return "proposal"
    return "dry_run"
