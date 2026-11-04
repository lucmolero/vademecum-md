# Runtime do grafo oficial

O pacote mantém os dados e as licenças de `../source.json`. Refinamentos locais da interface não alteram o corpus nem o snapshot comprimido.

- `graph-core.js`: índices do domínio, normalização e ranking de busca, enquadramento da câmera e política de resolução. Sem dependências do DOM ou do motor 3D.
- `search-controller.js`: combobox, navegação por teclado, cancelamento de respostas antigas, estados vazios e novas tentativas de busca.
- `render-scheduler.js`: decide quando renderizar, respeitando visibilidade, movimento contínuo, interação, simulação e disponibilidade do contexto WebGL.
- `viewer.js`: integra o motor distribuído, as interações e a apresentação do painel. Exporta somente medições e posições de leitura para inspeção e testes.
- `style.css`: apresentação compartilhada entre desktop e mobile; busca original e controles de ícones discretos.

O arquivo `initial-layout.json` armazena as posições resultantes dos 52 passos da configuração anterior. Isso evita repetir o aquecimento síncrono em cada abertura. O teste confere o SHA-256 do snapshot de origem, a identidade dos nós e as coordenadas. Um cache indisponível ou inválido usa o aquecimento original. A câmera usa as coordenadas reais dos nós. O arraste individual reativa a simulação e todas as citações mantêm suas setas.

Após atualizar o snapshot ou os parâmetros da física, inicie o Vite e execute `node scripts/capture-graph-layout.mjs` a partir de `homepage/`. Para outra porta, defina `GRAPH_LAYOUT_URL` com o endereço completo do viewer. O script ignora o cache durante a captura e registra o hash do snapshot.

Em dispositivos com ponteiro de toque, a rotação começa pausada. O botão de rotação permite ativá-la. A homepage prepara o grafo quando ele entra na tela ao abrir por uma seção interna, como `#skill`.

O endereço do iframe e os módulos do viewer usam a versão de URL `graph-startup-3`. Ao mudar o contrato entre esses módulos, atualize essa versão em conjunto para que navegadores com arquivos em cache recebam o pacote compatível.

Quando a rotação está pausada ou o sistema solicita movimento reduzido, a renderização para após a simulação e as transições terminarem. Interações e alterações visuais a reativam. A pausa solicitada de dentro do callback do motor ocorre em uma microtask para cancelar também o próximo frame agendado pelo motor.

A resolução acompanha a densidade do dispositivo até 3×, limitada a um drawing buffer de 4K. A mesma regra vale para todas as larguras. Antialiasing e representação tridimensional são preservados.

Executar a partir de `homepage/`:

```sh
npm run test:graph
npm run test:e2e
npm run build
```

Os testes de navegador cobrem desktop em densidade 2×, mobile em 3×, setas, enquadramento, arraste real por mouse e toque, busca por teclado, temas, redimensionamento e ausência de frames extras em repouso. Preserve estes módulos e contratos ao sincronizar novamente o pacote do repositório do grafo.
