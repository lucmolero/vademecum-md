# Ferramentas

Os scripts de raiz são orquestradores compatíveis com execução local e CI. As subpastas organizam a evolução do pipeline:

- `acquire/`: resolução e captura de fontes oficiais;
- `normalize/`: schema, encoding e caminhos canônicos;
- `consolidate/`: reconciliação de redações e diffs;
- `relations/`: grafo normativo;
- `validate/`: gates estruturais e jurídicos de publicação;
- `release/`: geração e empacotamento de releases.

Nenhuma ferramenta deve publicar um documento como vigente sem evidência oficial compatível.
