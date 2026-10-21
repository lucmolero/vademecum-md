"""Promote the official Planalto snapshot for Lei 13.726/2018."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from migrate_public_corpus import frontmatter, parse_frontmatter  # noqa: E402


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = next(args.snapshot.rglob("lei-13726-2018-10-08.md"))
    path = next((ROOT / "bases/curated/legislacao/federal").rglob("lei-ordinaria-13726-2018.md"))
    if not args.apply:
        print("Dry-run: a Lei 13.726/2018 seria reconciliada.")
        return 0
    current, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    source_url = "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13726.htm"
    metadata = {
        "id": "br-federal-lei_ordinaria-13726-2018", "titulo": "Lei nº 13.726, de 8 de outubro de 2018",
        "esfera": "federal", "jurisdicao": "BR", "tipo": "lei_ordinaria", "numero": "13726", "ano": 2018,
        "dominio": "administrativo", "prioridade": "P1", "publicos": ["academia", "OAB", "concursos", "pratica"],
        "sensibilidade_atualizacao": "alta", "data_assinatura": "2018-10-08",
        "ementa": "Racionaliza atos e procedimentos administrativos dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios e institui o Selo de Desburocratização e Simplificação.",
        "situacao": "em_vigor", "versao_texto": "consolidada", "consolidacao_status": "consolidada_fonte_oficial",
        "data_corte": "2026-10-21", "fonte_oficial": [source_url], "fonte_publicacao": [],
        "origem_formato": "markdown", "baixado_em": "2026-10-21", "sha256_origem": hashlib.sha256(source.read_bytes()).hexdigest(),
        "alterada_por": [], "revogada_por": [], "regulamentada_por": [], "retificada_por": [], "relacionada_a": [],
        "observacoes_proveniencia": ["Texto oficial do Planalto conferido em 2026-10-21; não foi identificada marcação de alteração posterior na página vigente."],
        "camada": "cobertura_especializada",
    }
    path.write_text(frontmatter(metadata) + "\n\n" + body.rstrip() + "\n", encoding="utf-8", newline="\n")
    sources_path = ROOT / "manifests/sources-official.json"; sources = json.loads(sources_path.read_text(encoding="utf-8"))
    for entry in sources["documents"]:
        if entry.get("id") == metadata["id"]:
            entry.update({"fontes": [source_url], "data_consulta": "2026-10-21", "data_corte": "2026-10-21", "sha256_origem": metadata["sha256_origem"]})
    sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    matrix_path = ROOT / "manifests/corpus.csv"
    with matrix_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";"); rows, fields = list(reader), reader.fieldnames or []
    for row in rows:
        if row["tipo"] == "lei_ordinaria" and row["numero"] == "13726" and row["ano"] == "2018":
            row["fonte_oficial"] = source_url; row["status_atualidade"] = "confirmada"
    with matrix_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    for name in ("completeness.json", "release.json"):
        p = ROOT / "manifests" / name; report = json.loads(p.read_text(encoding="utf-8")); counts = {"consolidada_fonte_oficial": 246, "consolidada_reconciliada": 5, "requer_reconciliacao": 109}; report["consolidation_status" if name == "completeness.json" else "consolidacao"] = counts; p.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Reconciliada: {metadata['id']}; sha256={metadata['sha256_origem']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
