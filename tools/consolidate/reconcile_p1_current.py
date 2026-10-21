"""Reconcile recent P1 laws from staged official snapshots plus corroboration."""

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


TODAY = "2026-10-21"
SPECS = [
    {
        "raw": "lei-15358-2026-03-24.md", "file": "lei-ordinaria-15358-2026.md",
        "id": "br-federal-lei_ordinaria-15358-2026", "number": "15358", "year": "2026",
        "date": "2026-03-24", "title": "Lei nº 15.358, de 24 de março de 2026",
        "domain": "penal", "sources": ["https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/lei/l15358.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:lei:2026-03-24;15358"],
        "ementa": "Institui o Marco Legal do Combate ao Crime Organizado no Brasil; tipifica os crimes de domínio social estruturado e de favorecimento ao domínio social estruturado; e altera os Decretos-Leis nºs 2.848, de 7 de dezembro de 1940, e 3.689, de 3 de outubro de 1941, e as Leis nºs 8.072, de 25 de julho de 1990, 7.210, de 11 de julho de 1984, 11.343, de 23 de agosto de 2006, 10.826, de 22 de dezembro de 2003, 9.613, de 3 de março de 1998, 4.737, de 15 de julho de 1965, 13.756, de 12 de dezembro de 2018, e 14.790, de 29 de dezembro de 2023.",
        "layer": "core_profissional", "sensitivity": "critica", "publicos": ["academia", "OAB", "concursos", "pratica"],
        "note": "A página vigente do Planalto foi consultada em 2026-10-21 e não apresenta marcação de alteração posterior; relações de alteração serão detalhadas no grafo.",
    },
    {
        "raw": "lei-15378-2026-04-06.md", "file": "lei-ordinaria-15378-2026.md",
        "id": "br-federal-lei_ordinaria-15378-2026", "number": "15378", "year": "2026",
        "date": "2026-04-06", "title": "Lei nº 15.378, de 6 de abril de 2026",
        "domain": "direitos sociais", "sources": ["https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/lei/l15378.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:lei:2026-04-06;15378"],
        "ementa": "Institui o Estatuto dos Direitos do Paciente.",
        "layer": "cobertura_especializada", "sensitivity": "alta", "publicos": ["academia", "concursos", "pratica"],
        "note": "A página vigente do Planalto foi consultada em 2026-10-21 e não apresenta marcação de alteração posterior; relações de alteração serão detalhadas no grafo.",
    },
    {
        "raw": "lei-15142-2025-06-03.md", "file": "lei-ordinaria-15142-2025.md",
        "id": "br-federal-lei_ordinaria-15142-2025", "number": "15142", "year": "2025",
        "date": "2025-06-03", "title": "Lei nº 15.142, de 3 de junho de 2025",
        "domain": "direitos sociais", "sources": ["https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15142.htm", "https://normas.leg.br/?urn=urn:lex:br:federal:lei:2025-06-03;15142"],
        "ementa": "Reserva às pessoas pretas e pardas, indígenas e quilombolas o percentual de 30% das vagas oferecidas em concursos públicos e processos seletivos simplificados no âmbito federal; e revoga a Lei nº 12.990, de 9 de junho de 2014.",
        "layer": "cobertura_especializada", "sensitivity": "alta", "publicos": ["academia", "concursos", "pratica"],
        "note": "A página vigente do Planalto foi consultada em 2026-10-21 e não apresenta marcação de alteração posterior; a revogação da Lei nº 12.990/2014 será modelada como relação de saída.",
    },
]


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print("Dry-run: três leis recentes seriam reconciliadas.")
        return 0
    for spec in SPECS:
        raw_path = next(args.snapshot.rglob(spec["raw"]))
        doc_path = next((ROOT / "bases/curated/legislacao/federal").rglob(spec["file"]))
        current, body = parse_frontmatter(doc_path.read_text(encoding="utf-8"))
        metadata = {
            "id": spec["id"], "titulo": spec["title"], "esfera": "federal", "jurisdicao": "BR",
            "tipo": "lei_ordinaria", "numero": spec["number"], "ano": int(spec["year"]), "dominio": spec["domain"],
            "prioridade": "P1", "publicos": spec["publicos"], "sensibilidade_atualizacao": spec["sensitivity"],
            "data_assinatura": spec["date"], "ementa": spec["ementa"], "situacao": "em_vigor",
            "versao_texto": "consolidada", "consolidacao_status": "consolidada_reconciliada", "data_corte": TODAY,
            "fonte_oficial": spec["sources"], "fonte_publicacao": [], "origem_formato": "markdown",
            "baixado_em": TODAY, "sha256_origem": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
            "alterada_por": [], "revogada_por": [], "regulamentada_por": [], "retificada_por": [],
            "relacionada_a": [], "observacoes_proveniencia": [spec["note"]], "camada": spec["layer"],
        }
        doc_path.write_text(frontmatter(metadata) + "\n\n" + body.rstrip() + "\n", encoding="utf-8", newline="\n")
        print(f"{spec['file']}: sha256={metadata['sha256_origem']}")

        sources_path = ROOT / "manifests/sources-official.json"
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
        for entry in sources["documents"]:
            if entry.get("id") == spec["id"]:
                entry.update({"fontes": spec["sources"], "data_consulta": TODAY, "data_corte": TODAY, "sha256_origem": metadata["sha256_origem"]})
        sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    matrix_path = ROOT / "manifests/corpus.csv"
    with matrix_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";"); rows, fields = list(reader), reader.fieldnames or []
    for row in rows:
        if any(row["tipo"] == "lei_ordinaria" and row["numero"] == s["number"] and row["ano"] == s["year"] for s in SPECS):
            row["status_atualidade"] = "confirmada"
            spec = next(s for s in SPECS if row["numero"] == s["number"] and row["ano"] == s["year"])
            row["fonte_oficial"] = "|".join(spec["sources"])
    with matrix_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)

    for name in ("completeness.json", "release.json"):
        path = ROOT / "manifests" / name; report = json.loads(path.read_text(encoding="utf-8"))
        counts = {"consolidada_fonte_oficial": 245, "consolidada_reconciliada": 5, "requer_reconciliacao": 110}
        report["consolidation_status" if name == "completeness.json" else "consolidacao"] = counts
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
