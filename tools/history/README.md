# Histórico técnico privado

Snapshots brutos, logs, comandos, hashes e evidências de aquisição não devem ser publicados no repositório autoral. O coletor grava esses dados em `.private/acquisition`, e `build_private_ledger.py` exporta uma cópia verificável para um diretório ou repositório privado fornecido explicitamente pelo operador.

O destino privado ainda precisa ser configurado pelo proprietário do projeto. Até essa configuração, os workflows públicos não fazem upload dos snapshots brutos; somente relatórios não sensíveis são publicados como artefatos temporários.
