"""Build a deterministic public release package without private acquisition data."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).parents[2]
PUBLIC_ROOTS = (
    Path("bases/curated"),
    Path("bases/history/alteracoes"),
    Path("bases/history/versoes"),
    Path("docs"),
    Path("manifests"),
    Path("README.md"),
    Path("SECURITY.md"),
    Path("LICENSE.md"),
)


def public_files() -> list[Path]:
    files: set[Path] = set()
    for relative in PUBLIC_ROOTS:
        path = ROOT / relative
        if path.is_file():
            files.add(path)
        elif path.is_dir():
            files.update(item for item in path.rglob("*") if item.is_file() and "__pycache__" not in item.parts)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", default=None)
    args = parser.parse_args()
    release = json.loads((ROOT / "manifests/release.json").read_text(encoding="utf-8"))
    version = args.version or str(release["version"])
    generated_at = str(release.get("generated_at") or date.today().isoformat())
    files = public_files()
    args.output.mkdir(parents=True, exist_ok=True)
    archive_name = f"vademecum-md-{version}.zip"
    archive_path = args.output / archive_name
    prefix = f"vademecum-md-{version}/"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(prefix + relative, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    checksums = {path.relative_to(args.output).as_posix(): sha256(path) for path in [archive_path]}
    manifest = {
        "schema": "public-release-package/v1",
        "product": "vademecum-md",
        "version": version,
        "generated_at": generated_at,
        "corpus_count": release.get("corpus_count"),
        "files_count": len(files),
        "archive": archive_name,
        "sha256": checksums,
        "private_data_included": False,
    }
    (args.output / "release-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "CHANGELOG.md").write_text(
        f"# vademecum-md {version}\n\nRelease reproduzível gerada em {generated_at}.\n\n"
        f"- Documentos no corpus: {release.get('corpus_count')}\n"
        f"- Arquivos públicos empacotados: {len(files)}\n"
        "- Dados privados de aquisição: não incluídos\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
