"""Enforce the no-direct-main-mutation policy for GitHub workflows."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[2]
WORKFLOWS = ROOT / ".github/workflows"
REQUIRED = {
    "quality.yml",
    "monitor-legislation.yml",
    "collect-legislation.yml",
    "prepare-update-pr.yml",
    "release.yml",
    "weekly-completeness.yml",
    "discover-legislation.yml",
    "sync-private-history.yml",
    "pr-policy.yml",
}


def main() -> int:
    actual = {path.name for path in WORKFLOWS.glob("*.yml")}
    missing = REQUIRED - actual
    if missing:
        print("Workflows ausentes: " + ", ".join(sorted(missing)))
        return 1
    errors: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        trusted_merge_policy = (
            path.name == "pr-policy.yml"
            and "contents: write" in text
            and "pull-requests: write" in text
            and "workflows: [quality]" in text
            and "QUALITY_RESULT" in text
            and 'head_sha" != "$CHECKED_SHA"' in text
            and 'gh pr merge "$PR_NUMBER" --repo "$GH_REPOSITORY" --squash' in text
            and "actions/checkout" not in text
            and "actions/download-artifact" not in text
        )
        if "gh pr create --draft" in text:
            errors.append(f"{path.name}: PRs de atualização não podem depender de ação humana para sair de rascunho")
        if path.name == "prepare-update-pr.yml" and "gh pr merge" in text:
            errors.append(f"{path.name}: PR de atualização não pode ser mesclado automaticamente")
        if path.name in {"quality.yml", "release.yml", "weekly-completeness.yml"}:
            if "sync_editorial_matrix.py" not in text:
                errors.append(f"{path.name}: gate da matriz editorial ausente")
            if "audit_editorial_expansion.py" not in text:
                errors.append(f"{path.name}: inventário de expansão editorial ausente")
            if "audit_normative_graph.py --strict" not in text:
                errors.append(f"{path.name}: auditoria estrita do grafo normativo ausente")
        if "contents: read" not in text and not trusted_merge_policy:
            errors.append(f"{path.name}: permissao de conteudo nao e somente leitura")
        if "pull_request_target" in text:
            errors.append(f"{path.name}: marcador proibido pull_request_target")
        if re.search(r"\bgit(?:\s+-C\s+[^\n]+)?\s+push\b", text) and not (
            path.name == "prepare-update-pr.yml"
            and 'git push origin "$branch"' in text
            and "gh pr create" in text
            and "automation/update-" in text
            and "github.event.repository.default_branch" in text
            and 'git checkout -B "$base_branch" "origin/$base_branch"' in text
            and "Refusing to write to the default branch" in text
        ) and not (
            path.name == "sync-private-history.yml"
            and "HISTORY_REPO_SSH_KEY" in text
            and "ssh-key:" in text
            and "git -C history-repository push origin HEAD:main" in text
        ):
            errors.append(f"{path.name}: push permitido somente para branch de proposta")
        if "contents: write" in text and not (
            (
                path.name == "release.yml"
                and "gh release create" in text
            )
            or (
                path.name == "prepare-update-pr.yml"
                and "pull-requests: write" in text
                and "gh pr create" in text
            )
            or trusted_merge_policy
        ):
            errors.append(f"{path.name}: escrita permitida somente para release protegida")
        if "pull-requests: write" in text and path.name not in {"prepare-update-pr.yml", "pr-policy.yml"}:
            errors.append(f"{path.name}: escrita de PR permitida somente para proposta validada ou política confiável")
        if path.name == "pr-policy.yml":
            if "workflow_run:" not in text or "workflows: [quality]" not in text:
                errors.append("pr-policy.yml: política deve ser acionada somente após o workflow quality")
            if "actions/checkout" in text or "actions/download-artifact" in text:
                errors.append("pr-policy.yml: workflow privilegiado não pode baixar nem executar conteúdo do PR")
            for trusted_author in ("lucmolero", "dependabot[bot]", "app/dependabot"):
                if trusted_author not in text:
                    errors.append(f"pr-policy.yml: allowlist de autores ausente: {trusted_author}")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Workflows validados: {len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
