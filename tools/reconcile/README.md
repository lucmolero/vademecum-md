# Reconciliação autônoma

`apply_reviewed_updates.py` promove snapshots oficiais somente depois da análise
jurídica do agente e dos gates determinísticos. O fluxo não depende de aprovação
ou ação do usuário.

Fluxo:

```text
collect_legislation.py --fetch
build_candidate_diffs.py --source-resolution manifests/source-resolution.json
apply_reviewed_updates.py --apply
build_public_indexes.py --apply
validate_release.py --strict
```

Conflitos entre fontes são resolvidos pelo agente no manifesto
`manifests/source-resolution.json`, com fonte selecionada, hash bruto esperado,
justificativa e escopo da análise. Hash divergente impede a aplicação.

Fonte indisponível preserva o texto curado e gera diagnóstico; não há promoção
presumida. Revogação ou alteração estrutural exige evidência oficial e nunca
remove automaticamente a versão anterior do histórico.

O comando não faz push, merge ou escrita direta na branch padrão. A automação
gera uma proposta reproduzível e os gates determinísticos impedem publicação
inconsistente.
