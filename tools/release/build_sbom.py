"""Generate a small, dependency-free CycloneDX SBOM for the release build."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import tomllib
from datetime import date
from pathlib import Path


ROOT = Path(__file__).parents[2]
PACKAGE_RE = re.compile(r"^([A-Za-z0-9_.-]+)")


def normalized_purl(name: str, version: str) -> str:
    return f"pkg:pypi/{name.lower().replace('_', '-')}@{version}"


def build_document() -> dict:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    docs_requirements = pyproject.get("project", {}).get("optional-dependencies", {}).get("docs", [])
    dependencies = list(project.get("dependencies", [])) + list(docs_requirements)
    components = [{
        "type": "application",
        "bom-ref": f"pkg:pypi/{project['name']}@{project['version']}",
        "name": project["name"],
        "version": project["version"],
        "scope": "required",
        "purl": f"pkg:pypi/{project['name']}@{project['version']}",
    }]
    for requirement in dependencies:
        match = PACKAGE_RE.match(requirement)
        if not match:
            continue
        name = match.group(1)
        try:
            version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            version = "unspecified"
        component = {
            "type": "library",
            "bom-ref": normalized_purl(name, version),
            "name": name,
            "version": version,
            "scope": "optional" if requirement in docs_requirements else "required",
            "properties": [{"name": "vademecum:requirement", "value": requirement}],
        }
        if version != "unspecified":
            component["purl"] = normalized_purl(name, version)
        components.append(component)
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:vademecum-md-{project['version']}",
        "version": 1,
        "metadata": {
            "timestamp": date.today().isoformat() + "T00:00:00Z",
            "component": components[0],
            "properties": [{"name": "vademecum:source", "value": "pyproject.toml"}],
        },
        "components": components[1:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = build_document()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output.as_posix(), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
