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
        if "gh pr create --draft" in text:
            errors.append(f"{path.name}: PRs de atualização não podem depender de ação humana para sair de rascunho")
        if path.name == "prepare-update-pr.yml" and "gh pr merge" not in text:
            errors.append(f"{path.name}: merge autônomo da proposta ausente")
        if path.name in {"quality.yml", "release.yml", "weekly-completeness.yml"}:
            if "sync_editorial_matrix.py" not in text:
                errors.append(f"{path.name}: gate da matriz editorial ausente")
            if "audit_editorial_expansion.py" not in text:
                errors.append(f"{path.name}: inventário de expansão editorial ausente")
            if "audit_normative_graph.py --strict" not in text:
                errors.append(f"{path.name}: auditoria estrita do grafo normativo ausente")
        if "contents: read" not in text:
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
        ):
            errors.append(f"{path.name}: escrita permitida somente para release protegida")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Workflows validados: {len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
