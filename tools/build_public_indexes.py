"""Build public manifests, the normative relation graph, and release reports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from migrate_public_corpus import CURATED, ROOT, frontmatter, parse_frontmatter, scalar
from relations.classify_unresolved import classify as classify_unresolved
from relations.build_review_queue import build_queue as build_relation_review_queue


TODAY = date.today().isoformat()
RELATION_EXCLUSIONS = ROOT / "manifests/relation-exclusions.json"
MONTHS = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08", "setembro": "09",
    "outubro": "10", "novembro": "11", "dezembro": "12",
}
RELATION_TYPES = {
    "altera": "alterada_por",
    "alterada_por": "altera",
    "revoga": "revogada_por",
    "revogada_por": "revoga",
    "regulamenta": "regulamentada_por",
    "regulamentada_por": "regulamenta",
    "retifica": "retificada_por",
    "retificada_por": "retifica",
    "suspende": "suspensa_por",
    "suspensa_por": "suspende",
    "relacionada_a": "relacionada_a",
}


def load_docs() -> list[tuple[Path, dict[str, object], str]]:
    docs: list[tuple[Path, dict[str, object], str]] = []
    for path in sorted(CURATED.rglob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata:
            docs.append((path, metadata, body))
    return docs


def norm_number(value: str) -> str:
    return value.replace(".", "").replace(",", ".").strip()


def relation_type(context: str) -> str | None:
    """Classify the relation direction for the referenced diploma.

    A citation can occur in two legally opposite constructions: ``altera a
    Lei X`` (the current document acts on X) and ``redação dada pela Lei X``
    (the current document was acted on by X). Passive constructions must be
    classified before active verbs; ambiguous prose remains unresolved.
    """
    context = re.sub(r"\s+", " ", context.lower()).strip()
    passive = r"(?:por|pela|pelo|pelas|pelos)"
    if re.search(rf"(?:redação|redacao)\s+(?:dada|dado)\s+{passive}", context):
        return "alterada_por"
    if re.search(rf"(?:alterad\w*|acrescid\w*|incluíd\w*|incluid\w*)\s+{passive}", context):
        return "alterada_por"
    if re.search(rf"revogad\w*\s+{passive}", context):
        return "revogada_por"
    if re.search(rf"retificad\w*\s+{passive}", context):
        return "retificada_por"
    if re.search(rf"regulamentad\w*\s+{passive}", context):
        return "regulamentada_por"

    if re.search(r"\b(?:altera|alteram|alterou|alterar|acresce|acrescem|inclui|incluem|incluiu)\b", context):
        return "altera"
    if re.search(r"\b(?:revoga|revogam|revogou|revogar)\b", context):
        return "revoga"
    if re.search(r"\b(?:retifica|retificam|retificou|retificar)\b", context):
        return "retifica"
    if re.search(r"\b(?:regulamenta|regulamentam|regulamentou|regulamentar)\b", context):
        return "regulamenta"
    if re.search(r"\b(?:suspende|suspendem|suspendeu|suspender)\b", context):
        return "suspende"
    return None


def effect_date(context: str) -> str | None:
    numeric = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", context)
    if numeric:
        day, month, year = numeric.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    spelled = re.search(
        r"\b(\d{1,2})(?:º|°|o)?\s+de\s+([A-Za-zçãõáéíóú]+)\s+de\s+(\d{4})\b",
        context,
        re.IGNORECASE,
    )
    if spelled:
        day, month, year = spelled.groups()
        month_number = MONTHS.get(month.lower())
        if month_number:
            return f"{year}-{month_number}-{int(day):02d}"
    return None


def relation_is_plausible(relation: str, source: dict[str, object], target: dict[str, object]) -> bool:
    """Reject or correct inferred edges that run backwards in time.

    A later diploma can amend, repeal, rectify, or regulate an earlier one.
    The converse is not a plausible interpretation of a citation in a
    current text. This is a conservative guard against citations in
    consolidated provisions being classified with the wrong direction.
    """
    source_date = str(source.get("data_assinatura") or "")
    target_date = str(target.get("data_assinatura") or "")
    if not source_date or not target_date:
        return True
    if relation in {"altera", "revoga", "retifica", "regulamenta", "suspende"}:
        return source_date >= target_date
    if relation in {"alterada_por", "revogada_por", "retificada_por", "regulamentada_por", "suspensa_por"}:
        return source_date <= target_date
    return True


def target_candidates(kind: str, number: str, docs: list[tuple[Path, dict[str, object], str]]) -> list[dict[str, object]]:
    kind = kind.lower()
    number = norm_number(number)
    if kind == "lei complementar":
        accepted = {"lei_complementar"}
    elif kind == "decreto-lei":
        accepted = {"decreto_lei"}
    elif kind == "decreto":
        accepted = {"decreto"}
    else:
        accepted = {"lei_ordinaria", "lei_delegada"}
    return [meta for _, meta, _ in docs if str(meta.get("numero") or "") == number and meta.get("tipo") in accepted]


def load_relation_exclusions() -> set[tuple[str, str, str]]:
    if not RELATION_EXCLUSIONS.is_file():
        return set()
    payload = json.loads(RELATION_EXCLUSIONS.read_text(encoding="utf-8"))
    return {
        (str(item["source_id"]), str(item["type"]), str(item["target_id"]))
        for item in payload.get("relations", [])
    }


def build_relations(docs: list[tuple[Path, dict[str, object], str]]) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    relations: dict[tuple[str, str, str, str | None], str | None] = {}
    relation_evidence: dict[tuple[str, str, str, str | None], dict[str, str]] = {}
    exclusions = load_relation_exclusions()
    unresolved: set[tuple[str, str, str, str]] = set()
    pattern = re.compile(
        r"\b(Lei\s+Complementar|Decreto-Lei|Lei|Decreto)\s*(?:n[ºo°]?\.?\s*)?([0-9]{1,3}(?:\.[0-9]{3})*)(?:\s*[/,]\s*([12][0-9]{3}))?",
        re.IGNORECASE,
    )
    for path, metadata, body in docs:
        source_id = str(metadata["id"])
        for match in pattern.finditer(body):
            relation_context = body[max(0, match.start() - 100) : match.start()]
            context = body[max(0, match.start() - 160) : min(len(body), match.end() + 180)]
            kind, number, _year = match.groups()
            relation = relation_type(relation_context)
            if relation is None:
                continue
            targets = target_candidates(kind, number, docs)
            if not targets:
                unresolved.add((source_id, kind, number, relation))
                continue
            device_match = re.findall(r"(?:Art\.?|art\.?)\s*([0-9]+(?:-[A-Z])?(?:º|°)?)", relation_context)
            device = f"art. {device_match[-1]}" if device_match else None
            for target in targets[:1]:
                target_id = str(target["id"])
                if target_id == source_id:
                    continue
                if not relation_is_plausible(relation, metadata, target):
                    corrected = RELATION_TYPES.get(relation)
                    if corrected and relation_is_plausible(corrected, metadata, target):
                        relation = corrected
                    else:
                        unresolved.add((source_id, kind, number, relation))
                        continue
                effect = effect_date(context)
                inverse = RELATION_TYPES[relation]
                evidence_text = re.sub(r"\s+", " ", context).strip()[:400]
                evidence = {
                    "evidencia_textual": evidence_text,
                    "evidencia_sha256": hashlib.sha256(evidence_text.encode("utf-8")).hexdigest(),
                    "confianca": "alta",
                    "status_revisao": "aprovado_autonomamente",
                }
                if (source_id, relation, target_id) not in exclusions:
                    relations.setdefault((source_id, relation, target_id, device), effect)
                    relation_evidence.setdefault((source_id, relation, target_id, device), evidence)
                if (target_id, inverse, source_id) not in exclusions:
                    relations.setdefault((target_id, inverse, source_id, device), effect)
                    relation_evidence.setdefault((target_id, inverse, source_id, device), evidence)
                if effect:
                    if (source_id, relation, target_id) not in exclusions:
                        relations[(source_id, relation, target_id, device)] = effect
                    if (target_id, inverse, source_id) not in exclusions:
                        relations[(target_id, inverse, source_id, device)] = effect
    result = [
        {
            "source_id": source,
            "type": relation,
            "target_id": target,
            "dispositivo": device,
            "data_efeito": effect,
            "fonte": next((str(meta.get("fonte_oficial")[0]) for _, meta, _ in docs if meta.get("id") == source and meta.get("fonte_oficial")), None),
            **relation_evidence.get((source, relation, target, device), {
                "evidencia_textual": "",
                "evidencia_sha256": None,
                "confianca": "desconhecida",
                "status_revisao": "requer_analise_autonoma",
            }),
        }
        for (source, relation, target, device), effect in sorted(relations.items(), key=lambda item: (item[0][0], item[0][1], item[0][2], item[0][3] or ""))
    ]
    unresolved_result = [
        {"source_id": source, "kind": kind, "numero": number, "tipo": relation}
        for source, kind, number, relation in sorted(unresolved)
    ]
    return result, unresolved_result


def update_document_relations(docs: list[tuple[Path, dict[str, object], str]], relations: list[dict[str, object]]) -> None:
    grouped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    fields = {"alterada_por", "revogada_por", "regulamentada_por", "retificada_por"}
    for relation in relations:
        if relation["type"] in fields:
            grouped[str(relation["source_id"])][str(relation["type"])].append(str(relation["target_id"]))
    for path, metadata, body in docs:
        for field in fields:
            metadata[field] = sorted(set(grouped[str(metadata["id"])].get(field, [])))
        path.write_text(frontmatter(metadata) + "\n" + body.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_sources(docs: list[tuple[Path, dict[str, object], str]]) -> None:
    target = ROOT / "manifests/sources-official.json"
    previous: dict[str, dict[str, object]] = {}
    if target.is_file():
        try:
            previous = {
                str(item.get("id")): item
                for item in json.loads(target.read_text(encoding="utf-8")).get("documents", [])
            }
        except (OSError, json.JSONDecodeError):
            previous = {}
    entries = []
    for _, metadata, _ in docs:
        sources = metadata.get("fonte_oficial") or []
        if isinstance(sources, str):
            sources = [sources]
        prior = previous.get(str(metadata["id"]), {})
        entries.append({
            "id": metadata["id"],
            "fontes": sources or prior.get("fontes", []),
            "data_consulta": metadata.get("baixado_em") or prior.get("data_consulta"),
            "data_corte": metadata.get("data_corte") or prior.get("data_corte"),
            "sha256_origem": metadata.get("sha256_origem") or prior.get("sha256_origem"),
            "sha256_normalizado": metadata.get("sha256_normalizado") or prior.get("sha256_normalizado"),
            "sha256_corpo": metadata.get("sha256_corpo") or prior.get("sha256_corpo"),
            "hash_scope": prior.get("hash_scope", "single_source"),
            "sha256_origem_por_fonte": prior.get("sha256_origem_por_fonte", []),
            "sha256_corpo_por_fonte": prior.get("sha256_corpo_por_fonte", []),
        })
    target.write_text(json.dumps({"schema": "official-source-manifest/v1", "generated_at": TODAY, "documents": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_vocabulary() -> None:
    vocabulary = {
        "schema": "vademecum-md/v1",
        "status_consolidacao": ["consolidada_fonte_oficial", "consolidada_reconciliada", "requer_reconciliacao", "texto_original", "historica", "parcialmente_revogada", "revogada", "transitoria", "desconhecida"],
        "situacao": ["em_vigor", "desconhecida", "revogada", "parcialmente_revogada", "transitoria", "historica"],
        "camadas": ["core_constitucional", "core_codigos", "core_profissional", "cobertura_especializada", "auditoria_especialista"],
        "relacoes": ["altera", "alterada_por", "revoga", "revogada_por", "regulamenta", "regulamentada_por", "retifica", "retificada_por", "suspende", "suspensa_por", "regulamenta_parcialmente", "relacionada_a"],
        "prioridades": ["P0", "P1", "P2"],
    }
    (ROOT / "manifests/vocabulary.json").write_text(json.dumps(vocabulary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_release(docs: list[tuple[Path, dict[str, object], str]], relations: list[dict[str, object]], unresolved: list[dict[str, str]]) -> None:
    statuses = Counter(str(meta.get("consolidacao_status")) for _, meta, _ in docs)
    release_path = ROOT / "manifests/release.json"
    prior_release: dict[str, object] = {}
    if release_path.is_file():
        try:
            prior_release = json.loads(release_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prior_release = {}
    release = {
        "product": "vademecum-md",
        "version": str(prior_release.get("version") or "0.3.0"),
        "generated_at": TODAY,
        "status": str(prior_release.get("status") or "pre_release"),
        "scope": "legislacao_federal",
        "corpus_count": len(docs),
        "integral_count": sum(bool(body.strip()) for _, _, body in docs),
        "official_source_count": sum(bool(meta.get("fonte_oficial")) for _, meta, _ in docs),
        "sha256_count": sum(bool(meta.get("sha256_origem")) for _, meta, _ in docs),
        "consolidacao": dict(statuses),
        "relation_count": len(relations),
        "unresolved_relation_count": len(unresolved),
        "publication_policy": "autonomous_pr_gates; no direct main mutation",
        "rag": str(prior_release.get("rag") or "deferred_until_1_0"),
    }
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_completeness(docs: list[tuple[Path, dict[str, object], str]], relations: list[dict[str, object]], unresolved: list[dict[str, str]]) -> None:
    statuses = Counter(str(meta.get("consolidacao_status")) for _, meta, _ in docs)
    checks = {
        "text_integral": sum(bool(body.strip()) for _, _, body in docs),
        "official_source": sum(bool(meta.get("fonte_oficial")) for _, meta, _ in docs),
        "hash": sum(bool(meta.get("sha256_origem")) for _, meta, _ in docs),
        "frontmatter": len(docs),
        "p0_consolidated": sum(meta.get("consolidacao_status") in {"consolidada_fonte_oficial", "consolidada_reconciliada"} for _, meta, _ in docs if meta.get("prioridade") == "P0"),
        "p0_total": sum(meta.get("prioridade") == "P0" for _, meta, _ in docs),
    }
    errors: list[str] = []
    if checks["text_integral"] != len(docs): errors.append("texto_vazio")
    if checks["official_source"] != len(docs): errors.append("fonte_oficial_ausente")
    if checks["hash"] != len(docs): errors.append("hash_ausente")
    result = {
        "schema": "completeness/v1",
        "generated_at": TODAY,
        "corpus_count": len(docs),
        "checks": checks,
        "relations": len(relations),
        "unresolved_relations": len(unresolved),
        "consolidation_status": dict(Counter(str(meta.get("consolidacao_status")) for _, meta, _ in docs)),
        "editorial_expansion": {
            "candidate_count": 15,
            "promoted_count": sum(1 for meta in (json.loads((ROOT / "manifests/editorial-promotions.json").read_text(encoding="utf-8")).get("decisions", {}).values()) if meta.get("decision") == "promote"),
        },
        "errors": errors,
        "status": "pass" if not errors else "fail",
    }
    (ROOT / "manifests/completeness.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    report = [
        "# Relatório de completude",
        "",
        f"Data de geração: `{TODAY}`.",
        "",
        f"- Documentos: **{len(docs)}**",
        f"- Textos integrais: **{checks['text_integral']}/{len(docs)}**",
        f"- Fontes oficiais: **{checks['official_source']}/{len(docs)}**",
        f"- Hashes: **{checks['hash']}/{len(docs)}**",
        f"- P0 consolidado: **{checks['p0_consolidated']}/{checks['p0_total']}**",
        f"- Consolidação oficial ou reconciliada: **{sum(value for key, value in statuses.items() if key in {'consolidada_fonte_oficial', 'consolidada_reconciliada'})}/{len(docs)}**",
        f"- Pendências de consolidação: **{statuses.get('requer_reconciliacao', 0)}**",
        f"- Relações normativas materializadas: **{len(relations)}**",
        f"- Relações ainda não resolvidas: **{len(unresolved)}**",
        "",
        "## Regra de interpretação",
        "",
        "Presença no corpus e integridade textual não equivalem, por si só, à vigência jurídica. Documentos sem consolidação confirmada permanecem com situação `desconhecida`.",
        "",
        "## Pendências",
        "",
    ]
    report.extend(f"- `{error}`" for error in errors) or report.append("Nenhum erro estrutural encontrado.")
    (ROOT / "docs/COMPLETENESS.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    unique_unresolved = {
        (str(item.get("kind") or "").lower(), str(item.get("numero") or "").strip())
        for item in unresolved
    }
    role_counts = Counter(
        "ato_alterador_ou_regulamentador"
        if str(item.get("tipo") or "") in {"alterada_por", "revogada_por", "retificada_por", "regulamentada_por"}
        else "diploma_referenciado"
        for item in unresolved
    )
    triage_counts = {"historico": 0, "grafo": 0}
    triage_report = ROOT / "bases/history/alteracoes/2026-10-21-unresolved-relations.json"
    if triage_report.is_file():
        try:
            triage_counts.update(json.loads(triage_report.read_text(encoding="utf-8")).get("by_editorial_disposition", {}))
        except (OSError, json.JSONDecodeError):
            pass
    public_report = [
        "# Relatório de completude",
        "",
        f"Data de geração: `{TODAY}`.",
        "",
        f"- Documentos: **{len(docs)}**",
        f"- Textos integrais: **{checks['text_integral']}/{len(docs)}**",
        f"- Fontes oficiais: **{checks['official_source']}/{len(docs)}**",
        f"- Hashes: **{checks['hash']}/{len(docs)}**",
        f"- P0 consolidado: **{checks['p0_consolidated']}/{checks['p0_total']}**",
        f"- Consolidação oficial ou reconciliada: **{sum(value for key, value in statuses.items() if key in {'consolidada_fonte_oficial', 'consolidada_reconciliada'})}/{len(docs)}**",
        f"- Pendências de consolidação: **{statuses.get('requer_reconciliacao', 0)}**",
        f"- Relações normativas materializadas: **{len(relations)}**",
        f"- Relações ainda não resolvidas: **{len(unresolved)} ocorrências / {len(unique_unresolved)} alvos únicos**",
        f"- Papel das ocorrências: **{role_counts.get('ato_alterador_ou_regulamentador', 0)} atos alteradores/regulamentadores; {role_counts.get('diploma_referenciado', 0)} diplomas referenciados**",
        f"- Disposição editorial: **{triage_counts.get('historico', 0)} histórico; {triage_counts.get('grafo', 0)} mantidos no grafo**",
        "",
        "## Regra de interpretação",
        "",
        "Presença no corpus e integridade textual não equivalem, por si só, à vigência jurídica. Documentos sem consolidação confirmada permanecem com situação `desconhecida`.",
        "",
        "## Interpretação das pendências",
        "",
        "As pendências de consolidação e as pendências do grafo são dimensões diferentes.",
        "Documentos curados com fonte, hash e status confirmado não estão pendentes de consolidação.",
        "As ocorrências do grafo são referências a atos fora da matriz e recebem disposição autônoma; nenhum alvo é incluído no corpus vigente por inferência.",
        "",
    ]
    public_report.extend(f"- `{error}`" for error in errors)
    if not errors:
        public_report.append("Nenhum erro estrutural encontrado.")
    (ROOT / "docs/COMPLETENESS.md").write_text("\n".join(public_report) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print("Dry-run: construiria manifests públicos, grafo normativo e relatório de completude.")
        return 0
    docs = load_docs()
    relations, unresolved = build_relations(docs)
    update_document_relations(docs, relations)
    docs = load_docs()
    graph = ROOT / "bases/derived/relacoes"
    graph.mkdir(parents=True, exist_ok=True)
    (graph / "normative-graph.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in relations), encoding="utf-8")
    (graph / "unresolved.json").write_text(json.dumps(unresolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    classify_unresolved(graph / "unresolved-classified.json")
    build_relation_review_queue(unresolved, graph / "review-queue.json")
    write_sources(docs)
    write_vocabulary()
    write_release(docs, relations, unresolved)
    write_completeness(docs, relations, unresolved)
    print(f"Índices gerados: documentos={len(docs)}, relações={len(relations)}, não resolvidas={len(unresolved)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
