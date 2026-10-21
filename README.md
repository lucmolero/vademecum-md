# VadeMecum MD

Legislação federal brasileira estruturada para leitura humana, validação
auditável e uso por máquinas.

> Este é um corpus autoral e curado. Não é publicação oficial, não substitui a
> consulta às fontes governamentais e não oferece aconselhamento jurídico.

## O produto

Cada diploma principal vive em um Markdown canônico com identidade, situação,
data de corte, fonte oficial, unidade de extração e hashes. Histórico normativo,
relações e relatórios derivados ficam em camadas separadas.

O site de leitura é regenerado a partir do corpus:

```text
fonte oficial → snapshot privado → normalização → auditoria
→ curadoria jurídica autônoma → gates → release
```

## Estado atual

- escopo: legislação federal;
- corpus: 375 documentos;
- fidelidade normativa: 375/375 documentos aprovados pelo auditor estrutural;
- data de corte do snapshot: 2026-10-21;
- RAG: deliberadamente fora desta etapa;
- release `1.0.3`: snapshot histórico, sujeito à revalidação textual prevista.

O relatório atual de fidelidade está em
[`bases/derived/relatorios/fidelity-audit.json`](bases/derived/relatorios/fidelity-audit.json).
Ele registra divergências sem promover silenciosamente uma redação incerta.

## Comece

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[docs]"
python tools/site/build_site.py
mkdocs serve
```

CLI operacional:

```text
vademecum acquire
vademecum normalize
vademecum audit
vademecum graph
vademecum site
vademecum release
```

## Documentação

- [Metodologia](docs/LEGAL_AUDIT.md)
- [Contrato de fidelidade](manifests/fidelity-policy.json)
- [Qualidade](docs/QUALITY.md)
- [Governança de dados](docs/DATA_GOVERNANCE.md)
- [Contribuição](CONTRIBUTING.md)
- [Segurança](SECURITY.md)

As fontes textuais usadas pelo corpus são públicas e oficiais, com precedência e
allowlist definidas em [`manifests/sources-registry.json`](manifests/sources-registry.json).
