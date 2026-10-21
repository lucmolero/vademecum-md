# Segurança operacional

- Não versionar credenciais, cookies, tokens ou dumps de bases privadas.
- Manter `.private/`, `bases/raw/`, caches e bancos locais fora do Git.
- Executar aquisição e conversão em ambiente isolado e revisar dependências antes de instalá-las.
- Tratar Markdown baixado como dado, nunca como código executável.
- Validar URLs, hashes, tamanho de resposta e encoding antes de substituir um documento.
- Usar comparação e revisão de diff para toda alteração normativa.
- Não publicar texto como vigente quando sua fonte oficial ou consolidação estiver pendente.
- Abrir relato privado para qualquer exposição de segredo ou alteração suspeita do pipeline.
