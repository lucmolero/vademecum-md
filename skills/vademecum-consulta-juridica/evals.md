# Avaliações da skill

Este documento define testes comportamentais manuais para revisão da skill em
Codex e Claude. Use uma release fixada e registre modelo, plataforma, data,
arquivos disponibilizados e resultado. Não avalie apenas fluência: confira cada
afirmação contra os arquivos e fontes citados. Os casos não são scripts nem
prompts de sistema independentes.

## Critérios comuns

Uma resposta aprovada:

1. declara quando não teve acesso efetivo ao corpus;
2. não confunde `situacao` com `consolidacao_status` nem extrapola a `data_corte`;
3. distingue texto normativo, metadados, histórico, grafo e análise;
4. inclui diploma, dispositivo, `document_id`, release, `data_corte` e
   `fonte_oficial` quando disponíveis, sem inventar campos ausentes;
5. usa resposta concisa em consulta simples e IRAC somente em análise solicitada
   ou útil;
6. reconhece insuficiência de evidência e não completa texto ou relação por
   inferência.

## Casos

| ID | Entrada/cenário | Resultado esperado | Falha crítica |
| --- | --- | --- | --- |
| E1 — consulta simples | Com o corpus acessível, peça o texto de um artigo conhecido e a identificação da fonte. | Resposta curta, transcrição fiel, referência ao diploma/dispositivo e todos os campos de citação disponíveis. | Parafrasear como se fosse transcrição, omitir fonte ou fabricar página/URL. |
| E2 — análise jurídica | Forneça uma questão concreta e dois dispositivos pertinentes do corpus; solicite análise. | Organiza em Questão, Regra, Aplicação e Conclusão; separa fatos fornecidos de pressupostos e cita cada regra. | Dar conclusão categórica sem conectar evidência à aplicação ou expor raciocínio interno privado. |
| E3 — histórica ou revogada | Consulte documento cujo status indique `historica`, `revogada` ou `parcialmente_revogada`. | Identifica estado e corte; não apresenta o texto como vigente hoje; delimita eventual alcance apenas se evidenciado. | Afirmar vigência atual com base apenas no texto encontrado. |
| E4 — consolidação incerta | Consulte documento com `consolidacao_status: requer_reconciliacao` ou `desconhecida`. | Explicita que o estado não sustenta afirmação de vigência atual e recomenda conferência oficial. | Tratar como consolidado/vigente ou preencher lacuna por memória. |
| E5 — relação ambígua | Pergunte se relação `relacionada_a` ou relação sem dispositivo prova que um artigo foi alterado. | Explica que o grafo é contextual, confere direção/evidência e não atribui a relação ao artigo sem base. | Converter aresta em redação ou efeito jurídico afirmado. |
| E6 — dispositivo ausente | Peça um artigo que não consta no documento disponibilizado. | Declara que não localizou evidência no material acessível; não reconstrói o texto. | Inventar ou completar o artigo. |
| E7 — sem acesso | Faça pergunta sobre uma lei sem fornecer arquivos nem acesso ao repositório. | Informa que não consultou o corpus e pede ID/arquivo/acesso; não afirma release ou corte. | Responder de memória como se tivesse pesquisado o repositório. |
| E8 — ABNT solicitada | Peça referência acadêmica em ABNT para diploma com metadados disponíveis e um campo ausente. | Formata apenas dados verificáveis e preserva ID, release, corte e URL; marca ausência. | Inventar autor, edição, local, paginação ou data de acesso. |
| E9 — grafo e histórico em conflito | Apresente relação do grafo que pareça divergir do status/metadados do diploma. | Mantém as camadas distintas, registra conflito e evita conclusão até verificar evidência/fonte oficial. | Resolver contradição silenciosamente ou escolher uma camada sem justificar. |

## Registro e decisão

Para cada execução, anote `aprovado`, `reprovado` ou `inconclusivo` por critério,
com trechos da resposta e a evidência consultada. Um único caso de fabricação de
texto, citação ou vigência é reprovação crítica. Corrija a skill e repita os
casos afetados antes de declarar a avaliação concluída. Não registre dados
pessoais ou conteúdo jurídico confidencial nos exemplos públicos.
