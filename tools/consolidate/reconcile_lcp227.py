"""Promote the staged official snapshot for Lei Complementar 227/2026."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import sys

TOOLS = Path(__file__).parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from migrate_public_corpus import frontmatter, parse_frontmatter  # noqa: E402


TODAY = "2026-10-21"
DOC_ID = "br-federal-lei_complementar-227-2026"
DOC_PATH = ROOT / "bases/curated/legislacao/federal/leis-complementares/2026/lei-complementar-227-2026.md"
SOURCE_URL = "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp227.htm"


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    candidates = list(args.snapshot.rglob("lcp-227-2026-01-13.md"))
    if not candidates:
        raise SystemExit(f"Snapshot não localizado em: {args.snapshot}")
    source = candidates[0]
    if not args.apply:
        print("Dry-run: a LC 227/2026 seria promovida para consolidada_fonte_oficial.")
        return 0

    current, body = parse_frontmatter(DOC_PATH.read_text(encoding="utf-8"))
    raw, _ = parse_frontmatter(source.read_text(encoding="utf-8"))
    metadata = {
        "id": DOC_ID,
        "titulo": "Lei Complementar nº 227, de 13 de janeiro de 2026",
        "esfera": "federal", "jurisdicao": "BR", "tipo": "lei_complementar",
        "numero": "227", "ano": 2026, "dominio": "tributario_financeiro", "prioridade": "P1",
        "publicos": ["academia", "OAB", "concursos", "pratica"], "sensibilidade_atualizacao": "critica",
        "data_assinatura": "2026-01-13",
        "ementa": "Institui o Comitê Gestor do Imposto sobre Bens e Serviços (CGIBS); dispõe sobre o processo administrativo tributário do Imposto sobre Bens e Serviços (IBS) e sobre a distribuição do produto da arrecadação do IBS aos entes federativos; institui normas gerais relativas ao Imposto sobre Transmissão Causa mortis e Doação de Quaisquer Bens ou Direitos (ITCMD); altera a legislação tributária e revoga dispositivos legais.",
        "situacao": "em_vigor", "versao_texto": "consolidada",
        "consolidacao_status": "consolidada_fonte_oficial", "data_corte": TODAY,
        "fonte_oficial": [SOURCE_URL], "fonte_publicacao": [], "origem_formato": "markdown",
        "baixado_em": TODAY, "sha256_origem": hashlib.sha256(source.read_bytes()).hexdigest(),
        "alterada_por": [], "revogada_por": [], "regulamentada_por": [], "retificada_por": [],
        "relacionada_a": ["br-federal-lei_complementar-214-2025"],
        "observacoes_proveniencia": [
            "Texto oficial do Planalto preservado no snapshot local de 2026-10-15.",
            "A lei contém dispositivos com efeitos em datas futuras; as datas de efeito serão detalhadas no grafo normativo.",
        ],
        "camada": "cobertura_especializada",
    }
    DOC_PATH.write_text(frontmatter(metadata) + "\n\n" + body.rstrip() + "\n", encoding="utf-8", newline="\n")

    sources_path = ROOT / "manifests/sources-official.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    for entry in sources["documents"]:
        if entry.get("id") == DOC_ID:
            entry.update({"fontes": [SOURCE_URL], "data_consulta": TODAY, "data_corte": TODAY, "sha256_origem": metadata["sha256_origem"]})
    sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    matrix_path = ROOT / "manifests/corpus.csv"
    with matrix_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        rows, fields = list(reader), reader.fieldnames or []
    for row in rows:
        if row["tipo"] == "lei_complementar" and row["numero"] == "227" and row["ano"] == "2026":
            row["fonte_oficial"] = SOURCE_URL
            row["status_atualidade"] = "confirmada"
    with matrix_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

    subprocess.run([sys.executable, str(ROOT / "tools/build_public_indexes.py"), "--apply"], check=True)
    print(f"Reconciliada: {DOC_ID}; sha256={metadata['sha256_origem']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
