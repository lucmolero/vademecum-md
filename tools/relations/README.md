# Relações normativas

`build_review_queue.py` agrupa referências não resolvidas e aplica uma decisão
autônoma do agente. Atos alteradores, revogadores e regulamentadores ficam no
histórico; referências diretas ou ambíguas sem identidade oficial única ficam
no grafo.

A fila não é um conjunto de documentos pendentes e não exige ação do usuário.
Todos os alvos recebem `review_status: approved`, justificativa, evidências e
`decision_scope: autonomous_agent_legal_curation`.

Os validadores determinísticos continuam obrigatórios: IDs, tipos, duplicidade,
inversos, fontes, hashes e dispositivos não são inferidos pela LLM.
