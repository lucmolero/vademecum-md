# Runtime do grafo oficial

O pacote mantém os dados e as licenças de `../source.json`. Refinamentos locais da interface não alteram o corpus nem o snapshot comprimido.

- `graph-core.js`: índices do domínio, normalização e ranking de busca, enquadramento da câmera e política de resolução. Sem dependências do DOM ou do motor 3D.
- `search-controller.js`: combobox, navegação por teclado, cancelamento de respostas antigas, estados vazios e novas tentativas de busca.
- `render-scheduler.js`: decide quando renderizar, respeitando visibilidade, movimento contínuo, interação, simulação e disponibilidade do contexto WebGL.
- `viewer.js`: integra o motor distribuído, as interações e a apresentação do painel. Exporta somente medições e posições de leitura para inspeção e testes.
- `style.css`: apresentação compartilhada entre desktop e mobile; busca original e controles de ícones discretos.

O layout inicial utiliza os mesmos 52 passos da configuração anterior (4 de aquecimento + 48 da simulação), calculados antes do enquadramento. A câmera usa as coordenadas reais dos nós para evitar limites de meshes ainda não atualizados. O arraste individual continua habilitado e reativa a simulação. Todas as relações de citação mantêm suas setas, inclusive no panorama.

Quando a rotação está pausada ou o sistema solicita movimento reduzido, a renderização para após a simulação e as transições terminarem. Interações e alterações visuais a reativam. A pausa solicitada de dentro do callback do motor ocorre em uma microtask para cancelar também o próximo frame agendado pelo motor.

A resolução acompanha a densidade do dispositivo até 3×, limitada a um drawing buffer de 4K. A mesma regra vale para todas as larguras. Antialiasing e representação tridimensional são preservados.

Executar a partir de `homepage/`:

```sh
npm run test:graph
npm run test:e2e
npm run build
```

Os testes de navegador cobrem desktop em densidade 2×, mobile em 3×, setas, enquadramento, arraste real por mouse e toque, busca por teclado, temas, redimensionamento e ausência de frames extras em repouso. Preserve estes módulos e contratos ao sincronizar novamente o pacote do repositório do grafo.
