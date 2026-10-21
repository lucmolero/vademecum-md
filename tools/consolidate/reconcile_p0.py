"""Reconcile the five P0 documents using explicitly staged official HTML snapshots.

This is a deliberate, local, one-shot reconciliation command.  It does not
download sources and it does not implement the future update workflow.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

TOOLS = Path(__file__).parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from migrate_public_corpus import frontmatter, parse_frontmatter  # noqa: E402


TODAY = "2026-10-21"


SPECS = {
    "decreto-lei-3914-1941.md": {
        "path": "bases/curated/legislacao/federal/decretos-lei/1941/decreto-lei-3914-1941.md",
        "source_file": "del3914.html",
        "sources": [
            "https://www.planalto.gov.br/ccivil_03/decreto-lei/del3914.htm",
            "https://normas.leg.br/?urn=urn:lex:br:federal:decreto.lei:1941-12-09;3914",
        ],
        "title": "Lei de Introdução ao Código Penal e à Lei das Contravenções Penais",
        "ementa": "Lei de introdução ao Código Penal (Decreto-Lei nº 2.848, de 7 de dezembro de 1940) e à Lei das Contravenções Penais (Decreto-Lei nº 3.688, de 3 de outubro de 1941).",
        "notes": ["Texto oficial histórico conferido no portal do Planalto; alterações e revogações históricas serão detalhadas na etapa de histórico normativo."],
        "status": "consolidada_reconciliada", "tipo": "decreto_lei", "numero": "3914", "ano": 1941,
        "date": "1941-12-09", "domain": "penal", "layer": "core_codigos", "priority": "P0",
        "sensitivity": "media", "publicos": ["academia", "OAB", "concursos", "pratica"],
    },
    "decreto-lei-3931-1941.md": {
        "path": "bases/curated/legislacao/federal/decretos-lei/1941/decreto-lei-3931-1941.md",
        "source_file": "del3931.html",
        "sources": [
            "https://www.planalto.gov.br/ccivil_03/decreto-lei/1937-1946/del3931.htm",
            "https://normas.leg.br/?urn=urn:lex:br:federal:decreto.lei:1941-12-11;3931",
        ],
        "title": "Lei de Introdução ao Código de Processo Penal",
        "ementa": "Lei de introdução ao Código de Processo Penal (Decreto-Lei nº 3.689, de 3 de outubro de 1941).",
        "notes": ["Texto oficial histórico conferido no portal do Planalto; alterações e revogações históricas serão detalhadas na etapa de histórico normativo."],
        "status": "consolidada_reconciliada", "tipo": "decreto_lei", "numero": "3931", "ano": 1941,
        "date": "1941-12-11", "domain": "processo penal", "layer": "core_codigos", "priority": "P0",
        "sensitivity": "media", "publicos": ["academia", "OAB", "concursos", "pratica"],
    },
    "lei-complementar-214-2025.md": {
        "path": "bases/curated/legislacao/federal/leis-complementares/2025/lei-complementar-214-2025.md",
        "source_file": "lcp214.html", "body_file": "lcp214-cp1252.md",
        "sources": [
            "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214compilado.htm",
            "https://normas.leg.br/?urn=urn:lex:br:federal:lei.complementar:2025-01-16;214",
        ],
        "title": "Lei Complementar nº 214, de 16 de janeiro de 2025",
        "ementa": "Institui o Imposto sobre Bens e Serviços (IBS), a Contribuição Social sobre Bens e Serviços (CBS) e o Imposto Seletivo (IS); cria o Comitê Gestor do IBS e altera a legislação tributária.",
        "notes": ["Texto consolidado conforme página oficial compilada do Planalto, consultada em 2026-10-21.", "A Lei Complementar nº 227, de 2026, foi identificada como alteração relacionada e será detalhada no grafo normativo."],
        "status": "consolidada_fonte_oficial", "tipo": "lei_complementar", "numero": "214", "ano": 2025,
        "date": "2025-01-16", "domain": "tributario", "layer": "core_codigos", "priority": "P0",
        "sensitivity": "critica", "publicos": ["academia", "OAB", "concursos", "pratica"],
        "alterada_por": ["br-federal-lei_complementar-227-2026"],
    },
    "lei-complementar-225-2026.md": {
        "path": "bases/curated/legislacao/federal/leis-complementares/2026/lei-complementar-225-2026.md",
        "source_file": "lcp225.html", "body_file": "lcp225-cp1252.md",
        "sources": [
            "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp225.htm",
            "https://normas.leg.br/?urn=urn:lex:br:federal:lei.complementar:2026-01-08;225",
        ],
        "title": "Lei Complementar nº 225, de 8 de janeiro de 2026",
        "ementa": "Institui o Código de Defesa do Contribuinte.",
        "notes": ["Texto vigente conferido no portal do Planalto, com registro dos dispositivos vetados conforme a fonte oficial.", "A revogação promovida pelo art. 56 é uma relação de saída desta lei e não indica que a própria lei esteja revogada."],
        "status": "consolidada_fonte_oficial", "tipo": "lei_complementar", "numero": "225", "ano": 2026,
        "date": "2026-01-08", "domain": "tributario", "layer": "core_codigos", "priority": "P0",
        "sensitivity": "critica", "publicos": ["academia", "concursos", "pratica"],
    },
    "lei-ordinaria-14133-2021.md": {
        "path": "bases/curated/legislacao/federal/leis-ordinarias/2021/lei-ordinaria-14133-2021.md",
        "source_file": "l14133.html", "body_file": "l14133-cp1252.md",
        "sources": [
            "https://planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm",
            "https://normas.leg.br/?urn=urn:lex:br:federal:lei:2021-04-01;14133",
        ],
        "title": "Lei nº 14.133, de 1º de abril de 2021",
        "ementa": "Estabelece normas gerais de licitação e contratação para as Administrações Públicas diretas, autárquicas e fundacionais da União, dos Estados, do Distrito Federal e dos Municípios; altera as Leis nºs 13.105, de 16 de março de 2015, 8.987, de 13 de fevereiro de 1995, e 11.079, de 30 de dezembro de 2004, e o Decreto-Lei nº 2.848, de 7 de dezembro de 1940; revoga dispositivos da Lei nº 8.666, de 21 de junho de 1993, da Lei nº 10.520, de 17 de julho de 2002, e da Lei nº 12.462, de 4 de agosto de 2011; e dá outras providências.",
        "notes": ["Texto consolidado conforme página oficial do Planalto, consultada em 2026-10-21.", "O texto oficial registra alterações posteriores; a materialização individual das leis alteradoras será concluída na etapa de histórico e grafo normativo."],
        "status": "consolidada_fonte_oficial", "tipo": "lei_ordinaria", "numero": "14133", "ano": 2021,
        "date": "2021-04-01", "domain": "normas complementares", "layer": "core_profissional", "priority": "P0",
        "sensitivity": "alta", "publicos": ["academia", "concursos", "pratica"],
    },
}


def reconcile(source_dir: Path) -> None:
    for name, spec in SPECS.items():
        path = ROOT / spec["path"]
        old, old_body = parse_frontmatter(path.read_text(encoding="utf-8"))
        body_path = source_dir / spec.get("body_file", "")
        body = body_path.read_text(encoding="utf-8") if spec.get("body_file") else old_body
        source_bytes = (source_dir / spec["source_file"]).read_bytes()
        metadata = {
            "id": old["id"], "titulo": spec["title"], "esfera": "federal", "jurisdicao": "BR",
            "tipo": spec["tipo"], "numero": spec["numero"], "ano": spec["ano"], "dominio": spec["domain"],
            "prioridade": spec["priority"], "publicos": spec["publicos"], "sensibilidade_atualizacao": spec["sensitivity"],
            "data_assinatura": spec["date"], "ementa": spec["ementa"], "situacao": "em_vigor",
            "versao_texto": "consolidada", "consolidacao_status": spec["status"], "data_corte": TODAY,
            "fonte_oficial": spec["sources"], "fonte_publicacao": [], "origem_formato": "html",
            "baixado_em": TODAY, "sha256_origem": hashlib.sha256(source_bytes).hexdigest(),
            "alterada_por": spec.get("alterada_por", []), "revogada_por": [], "regulamentada_por": [],
            "retificada_por": [], "relacionada_a": [], "observacoes_proveniencia": spec["notes"],
            "camada": spec["layer"],
        }
        path.write_text(frontmatter(metadata) + "\n\n" + body.rstrip() + "\n", encoding="utf-8", newline="\n")
        print(f"{name}: {len(body):,} caracteres; sha256={metadata['sha256_origem']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print("Dry-run: cinco documentos P0 seriam reconciliados.")
        return 0
    reconcile(args.source_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
