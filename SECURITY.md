# Segurança operacional

## Relatar uma vulnerabilidade

Use o [canal privado de Security Advisories](https://github.com/lucmolero/vademecum-md/security/advisories/new)
para relatar vulnerabilidades. Não publique detalhes exploráveis em issues,
discussões ou pull requests. Para problemas de navegação ou divergências
editoriais sem risco de segurança, use os formulários de issue.

## Controles do repositório

- Não versionar credenciais, cookies, tokens ou dumps de bases privadas.
- Manter a área privada de aquisição, caches e bancos locais fora do Git.
- Executar aquisição e conversão em ambiente isolado e revisar dependências antes de instalá-las.
- Tratar Markdown baixado como dado, nunca como código executável.
- Validar URLs, hashes, tamanho de resposta e encoding antes de substituir um documento.
- Usar comparação e revisão de diff para toda alteração normativa.
- Não publicar texto como vigente quando sua fonte oficial ou consolidação estiver pendente.
- Fixar GitHub Actions por SHA completa e atualizar dependências por PR do Dependabot.
- Tratar alerta de segredo ou alteração suspeita do pipeline como incidente e usar o canal privado.
