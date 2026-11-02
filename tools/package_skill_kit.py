"""Build a self-contained, agent-ready skill and corpus kit for the homepage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "vademecum-consulta-juridica"
SKILL_ROOT = ROOT / "skills" / SKILL_NAME
CORPUS_ROOT = ROOT / "bases" / "curated" / "legislacao" / "federal"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _kit_readme(version: str, cutoff: str, count: int) -> str:
    return f"""# VadeMecum MD · kit para agentes

Este pacote reúne a skill de consulta jurídica e o corpus oficial da mesma release.

- Release do corpus: **{version}**
- Data de corte: **{cutoff}**
- Documentos: **{count}**
- Não exige Node.js, npm ou `npx`.

## Começar sem terminal

1. Extraia este ZIP para uma pasta de trabalho.
2. Abra essa pasta no Codex, Claude Code, Cursor ou OpenCode.
3. A skill fica disponível no projeto e lê os documentos em `corpus/`.

O pacote inclui `.agents/skills/` para Codex, Cursor e OpenCode e
`.claude/skills/` para Claude Code. Para instalar em um projeto já aberto,
copie a pasta `vademecum-consulta-juridica/` correspondente para o destino de
projeto do agente e mantenha `corpus/` na raiz do workspace. As instruções
completas acompanham cada cópia da skill em `README.md`.

## Integridade e atualização

`KIT-MANIFEST.json` lista release, data de corte, quantidade de normas e SHA-256
de cada arquivo de conteúdo do pacote. A homepage também publica o SHA-256 do
ZIP. Compare-o antes de instalar. Para atualizar, baixe o kit novo e preserve o
pacote anterior até confirmar a nova release.

O corpus é dado curado e versionado; não substitui a publicação oficial. Confira
a fonte oficial citada em cada documento para confirmar o texto aplicável.
"""


def build(output_dir: Path, metadata_path: Path) -> dict[str, object]:
    release = json.loads((ROOT / "manifests/release.json").read_text(encoding="utf-8"))
    version = str(release["version"])
    expected_count = int(release["corpus_count"])
    with (ROOT / "manifests/corpus.csv").open(encoding="utf-8", newline="") as stream:
        cutoffs = sorted({str(row["data_corte"]) for row in csv.DictReader(stream, delimiter=";") if row.get("data_corte")})
    if len(cutoffs) != 1:
        raise ValueError(f"Esperada uma única data de corte na release; encontradas {cutoffs}")
    cutoff = cutoffs[0]
    markdown_files = sorted(CORPUS_ROOT.rglob("*.md"))
    if len(markdown_files) != expected_count:
        raise ValueError(f"Esperados {expected_count} documentos Markdown; encontrados {len(markdown_files)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / "vademecum-consulta-juridica-kit.zip"
    temporary_archive = archive.with_suffix(".zip.tmp")
    entries: list[tuple[Path, str]] = []

    kit_readme = output_dir / "KIT-README.md"
    kit_readme.write_text(_kit_readme(version, cutoff, expected_count), encoding="utf-8", newline="\n")
    entries.append((kit_readme, "README.md"))

    for agent_prefix in (".agents/skills", ".claude/skills"):
        for name in ("SKILL.md", "README.md", "evals.md"):
            source = SKILL_ROOT / name
            if not source.is_file():
                raise FileNotFoundError(f"Arquivo da skill ausente: {source}")
            entries.append((source, f"{agent_prefix}/{SKILL_NAME}/{name}"))

    for source in markdown_files:
        entries.append((source, f"corpus/bases/curated/legislacao/federal/{source.relative_to(CORPUS_ROOT).as_posix()}"))
    for name in ("release.json", "consumer-contract.json", "corpus.csv"):
        entries.append((ROOT / "manifests" / name, f"corpus/manifests/{name}"))
    for name in ("SCHEMA.md", "SOURCES.md"):
        entries.append((ROOT / "docs" / name, f"corpus/docs/{name}"))

    file_hashes = {archive_path: _sha256(source) for source, archive_path in entries}
    kit_manifest = {
        "schema": "vademecum-agent-kit/v1",
        "product": "vademecum-md",
        "skill": SKILL_NAME,
        "release": version,
        "data_cutoff": cutoff,
        "document_count": expected_count,
        "file_count": len(entries) + 1,
        "files": file_hashes,
    }
    manifest_temp = output_dir / "KIT-MANIFEST.json"
    manifest_temp.write_text(json.dumps(kit_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    with zipfile.ZipFile(temporary_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for source, archive_path in entries:
            bundle.write(source, archive_path)
        bundle.write(manifest_temp, "KIT-MANIFEST.json")
    temporary_archive.replace(archive)

    digest = _sha256(archive)
    checksum_path = output_dir / f"{archive.name}.sha256"
    checksum_path.write_text(f"{digest}  {archive.name}\n", encoding="ascii", newline="\n")
    metadata = {
        "schema": "vademecum-skill-kit-download/v1",
        "version": version,
        "cutoff": cutoff,
        "documentCount": expected_count,
        "fileCount": len(entries) + 1,
        "download": f"./downloads/{archive.name}",
        "checksum": f"./downloads/{checksum_path.name}",
        "sha256": digest,
        "sizeBytes": archive.stat().st_size,
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    kit_readme.unlink(missing_ok=True)
    manifest_temp.unlink(missing_ok=True)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "homepage/public/downloads")
    parser.add_argument("--metadata", type=Path, default=ROOT / "homepage/public/skill-kit.json")
    args = parser.parse_args()
    metadata = build(args.output.resolve(), args.metadata.resolve())
    print(json.dumps(metadata, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
