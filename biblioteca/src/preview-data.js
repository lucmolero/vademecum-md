const law14133 = {
  id: 'br-federal-lei_ordinaria-14133-2021',
  title: 'Lei nº 14.133, de 1º de abril de 2021',
  author: 'Presidência da República',
  description: 'Lei de Licitações e Contratos Administrativos.',
  cardLabel: 'Lei ordinária · 2021',
  collection: 'vademecum',
  number: '14.133',
  year: '2021',
  language: 'pt-BR',
  legalStatus: 'Em vigor',
  sourceDate: '2021-04-01',
  cutoff: '2026-10-21',
  consolidationStatus: 'Texto consolidado',
  fidelityStatus: 'Conteúdo demonstrativo',
  officialSources: ['https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm'],
  file: 'preview/lei-14133.json',
  sections: [
    {
      label: 'Disposições preliminares',
      html: '<h2 id="art-1o">Art. 1º</h2><p>Esta Lei estabelece normas gerais de licitação e contratação para as Administrações Públicas diretas, autárquicas e fundacionais da União, dos Estados, do Distrito Federal e dos Municípios.</p>',
      size: 260,
    },
    {
      label: 'Licitações · princípios',
      html: '<h2 id="art-5o">Art. 5º · Princípios</h2><p>Na aplicação desta Lei, serão observados os princípios da legalidade, da impessoalidade, da moralidade, da publicidade, da eficiência, do interesse público, da probidade administrativa, da igualdade, do planejamento, da transparência, da eficácia, da segregação de funções, da motivação, da vinculação ao edital e do julgamento objetivo.</p><p>Também se observam os princípios da segurança jurídica, da razoabilidade, da competitividade, da proporcionalidade, da celeridade, da economicidade e do desenvolvimento nacional sustentável.</p>',
      size: 460,
    },
  ],
  toc: [
    { label: 'Disposições preliminares', section: 0, level: 1, id: 'art-1o' },
    { label: 'Art. 1º · Objeto e âmbito', section: 0, level: 2, id: 'art-1o' },
    { label: 'Licitações · princípios', section: 1, level: 1, id: 'art-5o' },
    { label: 'Art. 5º · Princípios', section: 1, level: 2, id: 'art-5o' },
  ],
  tags: ['Federal', 'Licitações', 'Contratos'],
  kind: 'static',
  progress: 0.18,
  lastReadAt: Date.parse('2026-11-01T09:00:00-03:00'),
};

const constitution = {
  ...law14133,
  id: 'br-federal-constituicao-1988',
  title: 'Constituição da República Federativa do Brasil',
  description: 'Constituição Federal de 1988.',
  cardLabel: 'Constituição · 1988',
  number: '',
  year: '1988',
  file: 'preview/constituicao.json',
  sourceDate: '1988-10-05',
  officialSources: ['https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm'],
  progress: 0,
  lastReadAt: 0,
  sections: [{ label: 'Administração pública', html: '<h2 id="art-37">Art. 37</h2><p>A administração pública direta e indireta de qualquer dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios obedecerá aos princípios de legalidade, impessoalidade, moralidade, publicidade e eficiência e, também, ao seguinte:</p>', size: 300 }],
  toc: [{ label: 'Administração pública · Art. 37', section: 0, level: 1, id: 'art-37' }],
  tags: ['Federal', 'Constituição', 'Direitos fundamentais'],
};

const civilCode = {
  ...law14133,
  id: 'br-federal-lei-10406-2002',
  title: 'Código Civil · Lei nº 10.406/2002',
  description: 'Código Civil brasileiro.',
  cardLabel: 'Lei ordinária · 2002',
  number: '10.406',
  year: '2002',
  file: 'preview/codigo-civil.json',
  sourceDate: '2002-01-10',
  officialSources: ['https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm'],
  progress: 0,
  lastReadAt: 0,
  sections: [{ label: 'Dos atos ilícitos', html: '<h2 id="art-186">Art. 186</h2><p>Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.</p><h2 id="art-927">Art. 927</h2><p>Aquele que, por ato ilícito, causar dano a outrem, fica obrigado a repará-lo.</p>', size: 280 }],
  toc: [{ label: 'Dos atos ilícitos', section: 0, level: 1, id: 'art-186' }, { label: 'Art. 186 · Ato ilícito', section: 0, level: 2, id: 'art-186' }, { label: 'Art. 927 · Dever de reparar', section: 0, level: 2, id: 'art-927' }],
  tags: ['Federal', 'Direito civil'],
};

export const PREVIEW_BOOKS = Object.fromEntries([law14133, constitution, civilCode].map(book => [book.id, book]));
export const PREVIEW_CATALOG = Object.values(PREVIEW_BOOKS).map(book => ({ ...book, sections: book.sections.length, importedAt: 0, lastReadAt: book.lastReadAt || 0 }));
