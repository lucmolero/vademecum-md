# Metodologia

O corpus separa quatro camadas: texto curado, histórico, grafo e artefatos
derivados. A inclusão de um diploma, a integridade de seu texto e sua atualidade
são dimensões independentes.

## Fluxo de uma alteração

```text
fonte oficial → snapshot → normalização → comparação estrutural
→ curadoria jurídica autônoma → gates determinísticos → Pull Request → release
```

O sistema preserva a versão pública anterior quando a evidência é insuficiente.
Casos ambíguos são registrados como pendências autônomas e não como redação
vigente.
