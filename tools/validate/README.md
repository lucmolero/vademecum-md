# Validação

Os gates verificam schema, texto, hashes, fontes, IDs, relações, nomenclatura neutra e ausência de artefatos técnicos no produto público.

`python tools/validate/validate_site_budget.py` mede o HTML e os recursos iniciais da homepage, o índice de busca carregado sob demanda e o maior HTML legal, todos em gzip-9, e aplica budgets para impedir regressões de transferência.
