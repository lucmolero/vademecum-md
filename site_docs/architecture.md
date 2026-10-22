# Arquitetura

O produto separa a fonte normativa dos artefatos derivados:

```mermaid
flowchart LR
  A[Fontes oficiais] --> B[Snapshots privados]
  B --> C[Normalização]
  C --> D[Markdown canônico]
  D --> E[Índices e site]
  D --> F[Grafo normativo]
  D --> G[Auditorias]
  G --> H[Pull Request]
  H --> I[Release]
```

`bases/curated` é a camada normativa pública. `bases/history` preserva versões,
alterações e evidências. `bases/derived` é regenerável e nunca substitui o
texto canônico.

## Contratos

- cada diploma possui um ID estável e um Markdown próprio;
- o frontmatter descreve identidade, situação, corte, fonte e hashes;
- o grafo referencia somente IDs existentes;
- o site é gerado novamente a partir do corpus;
- uma proposta não altera a branch padrão diretamente.
