// Gera o documento descritivo da entrega de Compliance, QA & Tests (GS 2026/2).
// Uso: node gerar_documento.js <pasta_imagens> <saida.docx>
// <pasta_imagens> deve ter: visao-00.png ... visao-04.png (exportadas do Archi)
// ou preview-0.png ... preview-4.png (preview do gerador).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, ImageRun, PageBreak, PageOrientation, Footer, Header,
  PageNumber, LevelFormat, TableOfContents, ExternalHyperlink,
} = require("docx");

const IMG_DIR = process.argv[2] || "../build/archi";
const OUT = process.argv[3] || "../build/entrega/GranaAmiga-Documento-Descritivo.docx";

// ---------- página ----------
const A4 = { width: 11906, height: 16838 };
const MARGIN = 1134; // 2 cm
const W_PORT = A4.width - 2 * MARGIN;   // 9638
const W_LAND = A4.height - 2 * MARGIN;  // 14570
const NAVY = "1F3864", TEAL = "0E7C86", GRAY = "595959", LIGHT = "EAF1F8";

// ---------- helpers de texto ----------
function runs(text, base = {}) {
  // **negrito** dentro do texto
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((part) =>
    part.startsWith("**") ? new TextRun({ ...base, text: part.slice(2, -2), bold: true })
                          : new TextRun({ ...base, text: part }));
}
const P = (text, opt = {}) => new Paragraph({
  children: runs(text, opt.run || {}), alignment: opt.align || AlignmentType.JUSTIFIED,
  spacing: { after: opt.after ?? 120, line: 300 }, ...(opt.para || {}),
});
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const B = (text, level = 0) => new Paragraph({
  numbering: { reference: "bullets", level }, children: runs(text),
  spacing: { after: 60, line: 288 }, alignment: AlignmentType.LEFT,
});
const N = (text, instance = 1) => new Paragraph({
  numbering: { reference: "numbers", level: 0, instance }, children: runs(text), spacing: { after: 60, line: 288 },
});
const breakPage = () => new Paragraph({ children: [new PageBreak()] });
const note = (text) => new Paragraph({
  children: runs(text, { italics: true, color: GRAY, size: 18 }), spacing: { after: 160 },
});

// ---------- tabelas ----------
const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, rows, widthsPct, total = W_PORT) {
  const widths = widthsPct.map((p) => Math.round((total * p) / 100));
  widths[widths.length - 1] = total - widths.slice(0, -1).reduce((a, b) => a + b, 0);
  const cell = (text, i, head) => new TableCell({
    borders, width: { size: widths[i], type: WidthType.DXA },
    shading: head ? { fill: NAVY, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: String(text).split("\n").map((ln) => new Paragraph({
      children: runs(ln, head ? { bold: true, color: "FFFFFF", size: 19 } : { size: 19 }),
      spacing: { after: 20 },
    })),
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r, ri) => new TableRow({
        children: r.map((c, i) => {
          const tc = cell(c, i, false);
          if (ri % 2 === 1) tc.options = tc.options; // zebra opcional abaixo
          return tc;
        }),
      }))],
  });
}
const space = (after = 120) => new Paragraph({ children: [], spacing: { after } });

// ---------- figuras ----------
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function findImg(i) {
  // aceita visao-0N.png, o nome padrão do Archi ("0N - <nome da visão>.png") ou o preview
  const archi = fs.readdirSync(IMG_DIR).find((n) => n.startsWith(`0${i} - `) && n.toLowerCase().endsWith(".png"));
  for (const name of [`visao-0${i}.png`, archi, `preview-${i}.png`].filter(Boolean)) {
    const f = path.join(IMG_DIR, name);
    if (fs.existsSync(f)) return f;
  }
  throw new Error(`imagem da visão ${i} não encontrada em ${IMG_DIR}`);
}
let figCount = 0;
function figure(i, caption, maxW, maxH) {
  const f = findImg(i);
  const { w, h } = pngSize(f);
  // dimensões em pixels a 96 dpi (docx-js usa px)
  const mw = maxW / 15, mh = maxH / 15; // DXA -> px (1 px = 15 DXA)
  const k = Math.min(mw / w, mh / h);
  figCount += 1;
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(f),
        transformation: { width: Math.round(w * k), height: Math.round(h * k) },
        altText: { title: caption, description: caption, name: `figura-${figCount}` } })],
    }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
      children: [new TextRun({ text: `Figura ${figCount} – ${caption}`, italics: true, size: 18, color: GRAY })] }),
  ];
}

// ---------- conteúdo ----------
const EQUIPE = [
  ["Cassio Ribeiro", "567295", "DevOps Tools & Cloud Computing"],
  ["Davi Isac Colin Pereira", "567265", "Mastering Relational and Non-Relational Database"],
  ["Hugo Souza de Jesus", "568542", "Mobile Application Development"],
  ["Matheus Peres Moraes de Jesus", "567300", "Advanced Business Development with .NET"],
  ["Pedro Gonçalves Rodrigues", "567651", "Java Advanced"],
];

const capa = [
  space(1200),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "FIAP · GLOBAL SOLUTION 2026/2 · CITIZENTECH", color: TEAL, bold: true, size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "Compliance, Quality Assurance & Tests", color: GRAY, size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Grana Amiga", bold: true, size: 72, color: NAVY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Arquitetura de Soluções com TOGAF e ArchiMate", size: 32, color: NAVY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 900 }, children: [new TextRun({ text: "Documento descritivo da solução", size: 26, color: GRAY })] }),
  table(["Integrante", "RM", "Disciplina principal na GS"], EQUIPE, [40, 15, 45]),
  space(200),
  P("**Turma:** 2TDSPR   ·   **Linha do desafio:** Serviços e direitos   ·   **Data:** novembro de 2026", { align: AlignmentType.CENTER }),
  space(600),
  P("Entregáveis do .zip: este documento (DOCX e PDF), o modelo GranaAmiga-Arquitetura.archimate e o diagrama exportado do Archi em PDF de alta definição.", { align: AlignmentType.CENTER, run: { size: 18, color: GRAY } }),
];

const sumario = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Sumário")], pageBreakBefore: true }),
  new TableOfContents("Sumário", { hyperlink: true, headingStyleRange: "1-2" }),
];

// 1. Apresentação
const cap1 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun("1. Apresentação do projeto")] }),
  H2("1.1 Nome do projeto e equipe"),
  P("**Grana Amiga** é uma CitizenTech de educação e organização financeira para famílias brasileiras de baixa renda. O nome foi escolhido por ser simples de falar (inclusive por comando de voz) e por transmitir acolhimento: a proposta não é julgar quem está endividado, e sim caminhar junto até a família sair da faixa de risco."),
  P("A equipe é formada por cinco integrantes da turma 2TDSPR. Cada um é responsável por uma disciplina técnica da Global Solution, e todos participam desta entrega de Compliance e da parte de IoT. A mesma solução é a base das sete disciplinas, o que garante coerência entre a arquitetura descrita aqui e o que foi de fato implementado."),
  table(["Integrante", "RM", "Responsabilidade principal na solução"], [
    ["Cassio Ribeiro", "567295", "Infraestrutura: VM Azure por Azure CLI, Docker e Docker Compose (API Java + PostgreSQL)"],
    ["Davi Isac Colin Pereira", "567265", "Banco de dados: regras do Termômetro e plano de quitação em PL/SQL"],
    ["Hugo Souza de Jesus", "568542", "App mobile em Flutter (7 telas)"],
    ["Matheus Peres Moraes de Jesus", "567300", "API de Conteúdo em ASP.NET Core (trilhas e desafios)"],
    ["Pedro Gonçalves Rodrigues", "567651", "API Principal em Java/Spring Boot e vídeo pitch"],
  ], [32, 12, 56]),
  space(),
  H2("1.2 Desafio escolhido"),
  P("O tema da GS é **CitizenTech – tecnologia com o cidadão no centro da inovação**. Escolhemos a linha **Serviços e direitos**, porque o acesso à informação financeira e a capacidade de organizar o próprio orçamento são condições para que a família exerça outros direitos: moradia, alimentação, energia e crédito justo."),
  P("O problema é concreto e mensurável. Em julho de 2026, **82% das famílias brasileiras tinham dívidas**, o maior patamar da série histórica da Pesquisa de Endividamento e Inadimplência do Consumidor (Peic) da CNC e o sexto recorde seguido. Entre as famílias com renda de até três salários mínimos, o índice chega a **84,9%**, e foi a única faixa em que a inadimplência subiu no mês. O cartão de crédito aparece em **85,3%** dos casos de endividamento."),
  P("Somam-se a isso duas causas que a solução ataca diretamente:"),
  B("**Falta de educação financeira acessível:** os aplicativos de finanças pressupõem conta em banco digital, leitura fluente e internet boa. Quem mais precisa é justamente quem tem menos acesso a esse tipo de ferramenta."),
  B("**Consumo invisível:** a conta de luz é um dos maiores gastos fixos da família, mas o consumo só aparece quando a fatura chega, e aí já não há o que fazer naquele mês."),
  space(),
  H2("1.3 Como a solução funciona"),
  P("A Grana Amiga combina três frentes, que se reforçam:"),
  N("**Aprender:** na área aberta, sem cadastro, qualquer pessoa joga simuladores curtos (\"Desafio do Supermercado\" e \"Fugindo dos Juros\", este último sobre rotativo e parcelamento do cartão), com áudio, ícones grandes e linguagem simples."),
  N("**Organizar:** ao criar a conta (telefone e senha no primeiro acesso, biometria do aparelho nos seguintes), a família ganha um painel com o **Termômetro do Dinheiro**, que classifica a situação em Verde, Amarelo ou Vermelho conforme o comprometimento da renda, e um **plano visual de quitação** com alertas de vencimento. Os gastos podem ser registrados por ícones, por voz ou pelo WhatsApp."),
  N("**Medir:** um medidor de energia de baixo custo (ESP32 com sensor de alicate SCT-013) mostra em reais quanto a casa está gastando de luz e avisa antes da conta estourar a meta, transformando um consumo invisível em decisão financeira."),
  P("A solução é **gratuita para as famílias** e sustentada por parcerias com prefeituras (CRAS), cooperativas de crédito, ONGs, distribuidoras de energia e a operadora Claro (acesso sem consumo do pacote de dados). Ela contribui com os ODS 4 (educação de qualidade), 10 (redução das desigualdades) e 13 (ação contra a mudança do clima)."),
];

// 2. Público-alvo
const cap2 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun("2. Público-alvo e impacto esperado")] }),
  H2("2.1 Quem usa e quem se beneficia"),
  table(["Público", "Perfil", "Como se beneficia"], [
    ["Principal: famílias de baixa renda", "Renda de até 3 salários mínimos; chefes de família muitas vezes com baixa escolaridade e pouca familiaridade digital; celular Android simples e pacote de dados limitado.", "Entende a própria situação (Termômetro), recebe um plano de quitação viável, aprende jogando e reduz a conta de luz."],
    ["Secundário: crianças e jovens da família", "Usam o celular da casa; aprendem com jogos.", "Educação financeira desde cedo, sem cadastro."],
    ["Institucional: CRAS e prefeituras", "Equipes de assistência social que acompanham famílias em programas sociais.", "Ferramenta gratuita para orientar as famílias e painel agregado e anonimizado do território."],
    ["Parceiros", "Cooperativas de crédito, ONGs, distribuidoras de energia e operadora de telefonia.", "Alcance social, renegociação com menor risco, eficiência energética e posicionamento de marca."],
  ], [22, 40, 38]),
  space(),
  H2("2.2 Dimensão do problema (dados de mercado)"),
  table(["Indicador", "Valor", "Fonte"], [
    ["Famílias com dívidas a vencer (jul/2026)", "82,0% – recorde da série, 6º recorde seguido (cerca de 60 milhões de lares)", "Peic/CNC, jul/2026"],
    ["Endividamento na faixa de até 3 salários mínimos", "84,9% (contra 72% acima de 10 salários mínimos)", "Peic/CNC, jul/2026"],
    ["Cartão de crédito entre as famílias endividadas", "85,3%", "Peic/CNC, jul/2026"],
    ["Famílias com contas em atraso", "29,8% (a faixa de menor renda foi a única com alta)", "Peic/CNC, jul/2026"],
    ["Comprometimento médio da renda com dívidas", "cerca de 30% – usado como limite do Verde no Termômetro", "Peic/CNC"],
    ["Efeito do feedback de consumo de energia", "redução de 4% a 12% no consumo residencial", "ACEEE, Report E105 (2010)"],
  ], [36, 40, 24]),
  note("Os números da Peic de julho de 2026 foram divulgados pela CNC em 06/08/2026 e reportados por diversos veículos (ver Referências)."),
  H2("2.3 Estimativa de impacto"),
  P("As metas abaixo aparecem no modelo como elementos **Outcome** da camada de Motivação. Elas são estimativas da equipe, construídas a partir dos dados acima, e servem para medir se a arquitetura está cumprindo seu propósito."),
  table(["Resultado esperado (Outcome)", "Meta", "Como será medido", "Justificativa"], [
    ["Famílias saindo da faixa Vermelha", "30% dos usuários ativos em 3 meses", "Classificação do Termômetro no cadastro x após 90 dias", "O plano de quitação ataca primeiro as dívidas de maior juros (método avalanche), o que reduz o comprometimento mais rápido."],
    ["Dívidas quitadas", "Crescimento mês a mês do valor total quitado", "Soma de saldo devedor zerado no período", "Indicador direto de efetividade do plano."],
    ["Engajamento educativo", "Trilhas concluídas e dias seguidos registrando gastos", "Eventos do app e da API de Conteúdo", "Hábito é o que sustenta a mudança depois do primeiro mês."],
    ["Conversão da área aberta", "20% dos visitantes criam conta", "Visitantes únicos x cadastros", "A área aberta reduz a barreira de entrada; a meta mede se ela leva ao uso completo."],
    ["Redução do consumo de energia", "10% nas casas com medidor", "kWh médio antes x depois da instalação", "Dentro da faixa de 4–12% da ACEEE; o medidor dá feedback em tempo real, tipo de programa que fica no topo da faixa."],
  ], [24, 18, 26, 32]),
  space(),
  P("**Exemplo de piloto:** um município médio que acompanhe 5.000 famílias pelo CRAS e alcance a meta de 30% teria **1.500 famílias saindo da faixa Vermelha em três meses**. No medidor, uma casa com conta de R$ 150 por mês que reduza 10% do consumo economiza cerca de **R$ 15 por mês (R$ 180 por ano)**, dinheiro que pode ir direto para o plano de quitação."),
  note("Premissas ilustrativas da equipe (tamanho do piloto e valor da conta), apresentadas apenas para dimensionar a ordem de grandeza do impacto."),
];

// 3. Metodologia
const cap3 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun("3. Metodologia: TOGAF ADM e ArchiMate")] }),
  P("A arquitetura foi desenvolvida com o **TOGAF ADM** (Architecture Development Method), percorrendo da Fase Preliminar até a Fase D, como visto em aula. Cada fase gerou uma camada do modelo ArchiMate, desenhado na ferramenta **Archi**."),
  table(["Fase do ADM", "Pergunta que responde", "Camada no modelo", "Capítulo"], [
    ["Preliminar", "Onde, o quê, por quê, quem e como a arquitetura será feita", "Definição do escopo, da equipe e das ferramentas (este capítulo)", "3"],
    ["A – Visão de Arquitetura", "Por que mudar e aonde queremos chegar?", "Motivação", "4"],
    ["B – Arquitetura de Negócio", "Quem participa, quais serviços e processos?", "Negócio", "5"],
    ["C – Arquitetura de Sistemas", "Quais aplicações e dados realizam o negócio?", "Aplicação", "6"],
    ["D – Arquitetura de Tecnologia", "Qual infraestrutura executa e conecta as aplicações?", "Tecnologia", "7"],
    ["E a H", "Oportunidades, migração, governança e mudança", "Fora do escopo desta entrega; ver capítulo 9", "9"],
  ], [24, 32, 30, 14]),
  space(),
  H2("3.1 Organização do modelo no Archi"),
  B("**Cinco visões:** \"00 – Arquitetura de Solução (visão completa)\", que mostra as quatro camadas integradas, e as visões 01 a 04, uma por camada, usadas nas figuras deste documento."),
  B("**Convenção de nomes:** cada elemento tem um prefixo com o seu tipo (DRIVER:, GOAL:, PROC:, COMP:, NODE: etc.), seguindo o padrão usado em aula. Isso facilita a leitura do PDF sem precisar conhecer todos os ícones."),
  B("**Documentação nos elementos:** detalhes técnicos (portas, versões, regras de cálculo, responsáveis) estão no campo Documentation de cada elemento, na aba Properties do Archi, para não poluir o desenho."),
  B("**Rastreabilidade:** além das relações desenhadas, o modelo guarda relações de rastreabilidade (por exemplo, função de aplicação → requisito e objeto de dados → objeto de negócio), consultáveis no Archi em Analysis → Model Relations."),
  B("**Validação:** o modelo passa no Validator do Archi sem erros. Os avisos restantes são do tipo \"Unused Relation\" e correspondem justamente a essas relações guardadas no modelo e mantidas fora dos desenhos de propósito."),
  H2("3.2 Relações ArchiMate utilizadas"),
  table(["Relação", "Significado no modelo", "Exemplo"], [
    ["Influência", "Um elemento de motivação afeta outro", "Avaliação \"82% das famílias têm dívidas\" influencia o objetivo \"Tirar famílias da faixa Vermelha\""],
    ["Realização", "Um elemento concretiza outro, mais abstrato", "Processo \"Consultar o Termômetro\" realiza o serviço \"Diagnóstico financeiro\""],
    ["Servir", "Um elemento fornece funcionalidade a outro", "Serviço de aplicação \"Transações e categorias\" serve o processo \"Registrar gastos\""],
    ["Designação", "Responsabilidade ou execução", "Ator \"Família\" designado ao papel \"Usuário cadastrado\""],
    ["Acesso", "Leitura ou escrita de um objeto passivo", "API Principal acessa os dados \"transacao\" e \"divida\""],
    ["Composição / Agregação", "Um elemento é formado por outros", "Trilha é composta de desafios (1:N)"],
    ["Disparo / Fluxo", "Sequência temporal ou transferência", "Medidor envia leituras por MQTT ao broker"],
    ["Associação", "Relação não direcionada", "Stakeholder associado ao seu direcionador"],
  ], [18, 34, 48]),
];

const LAND = Symbol("land");   // marcador: o que vem em seguida vai para uma página paisagem
function capFig(num, title, intro, figIdx, figCaption, body) {
  return [
    new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun(title)] }),
    ...intro.map((t) => P(t)),
    P(`A Figura ${figCount + 1}, na página seguinte (em paisagem), mostra a visão completa desta camada.`,
      { run: { italics: true, color: GRAY } }),
    { [LAND]: figure(figIdx, figCaption, W_LAND, A4.width - 2 * MARGIN - 900) },
    ...body,
  ];
}

// 4. Motivação
const cap4 = capFig(4, "4. Visão de Arquitetura – Camada de Motivação (Fase A)", [
  "A Fase A define **por que** a solução existe e **aonde** ela quer chegar. A camada de Motivação é lida de cima para baixo: os **stakeholders** têm interesse em **direcionadores** (drivers), que são confirmados por **avaliações** baseadas em dados; as avaliações influenciam os **objetivos** (goals), medidos por **resultados** (outcomes); e os **requisitos** concretizam os resultados, respeitando **princípios** e **restrições**.",
  "**Escopo:** dentro do escopo estão a área aberta de jogos, o painel com Termômetro e plano de quitação, o registro de gastos, o medidor de energia e as APIs que os sustentam. O chatbot de WhatsApp com transcrição por IA e o painel B2G completo estão no modelo como **visão de produto**: fazem parte da arquitetura-alvo, mas não são implementados nesta GS (restrição explícita no modelo).",
], 1, "Visão 01 – Camada de Motivação (Fase A)", [
  H2("4.1 Stakeholders e direcionadores"),
  table(["Stakeholder", "Interesse principal", "Direcionador ligado"], [
    ["Famílias endividadas (renda até 3 SM)", "Sair das dívidas, entender o orçamento, pagar menos de luz", "Os três direcionadores"],
    ["Prefeituras e CRAS", "Orientar as famílias atendidas e medir resultados dos programas sociais", "Endividamento recorde (e educação financeira)"],
    ["Cooperativas de crédito e ONGs", "Educação financeira e renegociação justa com menor risco", "Endividamento recorde"],
    ["Claro e distribuidoras de energia", "Inclusão digital (zero-rating) e eficiência energética", "Conta de luz invisível"],
  ], [30, 46, 24]),
  space(),
  table(["Direcionador (Driver)", "Avaliações que o comprovam (Assessment)"], [
    ["Endividamento recorde das famílias brasileiras", "82% das famílias têm dívidas (Peic/CNC, jul/2026) · 84,9% entre quem ganha até 3 SM · cartão de crédito em 85,3% das famílias endividadas · comprometimento médio de ~30% da renda"],
    ["Baixa educação financeira e falta de ferramentas acessíveis", "Linguagem financeira difícil exclui quem tem baixa escolaridade · faltam ferramentas gratuitas, com áudio e que funcionem offline"],
    ["Conta de luz pesa no orçamento e o consumo é invisível", "O consumo só aparece quando a conta chega · feedback de consumo reduz de 4% a 12% o gasto de energia (ACEEE, 2010)"],
  ], [34, 66]),
  space(),
  H2("4.2 Objetivos e resultados"),
  table(["Objetivo (Goal)", "Resultados que o realizam (Outcome)"], [
    ["Tirar famílias da faixa Vermelha do Termômetro do Dinheiro", "Meta de 30% dos usuários ativos saindo do Vermelho em 3 meses · valor total de dívidas quitadas crescendo mês a mês"],
    ["Educar financeiramente de forma lúdica, inclusiva e gratuita", "Trilhas concluídas e dias seguidos registrando gastos · meta de 20% dos visitantes da área aberta criando conta"],
    ["Reduzir o desperdício de energia e o peso da conta de luz", "Meta de 10% a menos de consumo nas casas com medidor"],
  ], [38, 62]),
  space(),
  H2("4.3 Princípios"),
  table(["Princípio", "O que implica na arquitetura"], [
    ["Cidadão no centro – simples, inclusivo e acessível", "Área aberta sem cadastro, áudio, ícones grandes, linguagem simples, voz apenas para navegação"],
    ["Privacidade desde a concepção (LGPD)", "Login por telefone (não por CPF), senha com hash BCrypt, token JWT, dados agregados e anonimizados para parceiros"],
    ["Gratuito para as famílias", "Sustentação por B2G (prefeituras) e parcerias; nenhum recurso essencial é pago"],
    ["Funciona fora do cenário ideal (offline-first)", "App registra gastos offline e sincroniza depois; medidor mostra o custo no display mesmo sem internet"],
  ], [36, 64]),
  space(),
  H2("4.4 Requisitos e restrições"),
  table(["Requisito", "Realiza", "Restrição que o limita"], [
    ["Login por telefone + senha (JWT) e biometria do aparelho", "Princípio de privacidade", "LGPD: dados financeiros e de consumo são dados pessoais"],
    ["Painel agregado e anonimizado para CRAS e parceiros", "Meta de sair do Vermelho; privacidade; gratuidade", "–"],
    ["Termômetro: Verde ≤ 30%, Amarelo ≤ 50%, Vermelho > 50% da renda", "Meta de sair do Vermelho", "–"],
    ["Plano de quitação (maior juros primeiro) com alertas de vencimento", "Dívidas quitadas", "–"],
    ["Registrar gastos por ícones, voz ou WhatsApp", "Engajamento", "Escopo da GS: chatbot e IA de voz ficam como visão de produto"],
    ["Trilhas e desafios gerenciáveis sem novo deploy do app", "Engajamento; cidadão no centro", "–"],
    ["Área aberta com jogos sem cadastro, com áudio e ícones grandes", "Conversão; engajamento; cidadão no centro", "Baixa escolaridade e pouca familiaridade digital"],
    ["Medidor mostra a luz em R$ e alerta antes de estourar a meta", "Redução do consumo", "Medidor barato e não invasivo (sensor de alicate SCT-013)"],
    ["Registro offline com sincronização posterior", "Princípio offline-first", "Conectividade limitada e pacote de dados restrito"],
  ], [40, 30, 30]),
  space(),
  P("**Regra do Termômetro:** comprometimento = soma das parcelas das dívidas ativas ÷ renda mensal. Até 30% é Verde (próximo da média nacional da Peic), até 50% é Amarelo e acima disso é Vermelho. A mesma regra é usada no PL/SQL, na API e no app, o que garante que a família veja a mesma cor em qualquer canal."),
]);

// 5. Negócio
const cap5 = capFig(5, "5. Arquitetura de Negócio (Fase B)", [
  "A Fase B descreve **quem participa** do ecossistema, **quais serviços** a solução oferece e **quais processos** os realizam. A visão é lida de cima para baixo: atores e canais, papéis, serviços de negócio, processos (agrupados em jornadas) e objetos de negócio.",
], 2, "Visão 02 – Camada de Negócio (Fase B)", [
  H2("5.1 Atores, papéis e canais"),
  table(["Ator", "Papel", "Canal (interface de negócio)"], [
    ["Família (chefe de família)", "Visitante da área aberta · Usuário cadastrado", "App Grana Amiga · WhatsApp · Display e LED do medidor"],
    ["Assistente social do CRAS", "Gestor do programa social", "Painel do parceiro"],
    ["Cooperativa de crédito / ONG", "Parceiro financeiro", "–"],
    ["Distribuidora de energia", "Parceiro de energia (distribui o medidor)", "–"],
    ["Claro (operadora)", "Parceiro de conectividade (zero-rating)", "Associado ao canal App"],
  ], [30, 38, 32]),
  space(),
  H2("5.2 Serviços de negócio"),
  table(["Serviço de negócio", "Consumido por", "Realizado pelo processo"], [
    ["Educação financeira gamificada", "Visitante da área aberta", "Jogar simuladores · Concluir trilha educativa"],
    ["Registro de gastos multicanal", "Usuário cadastrado", "Registrar gastos do dia a dia"],
    ["Diagnóstico financeiro (Termômetro)", "Usuário cadastrado", "Consultar o Termômetro do Dinheiro"],
    ["Plano de quitação e alertas", "Usuário cadastrado", "Seguir o plano de quitação · Receber alerta e pagar a parcela"],
    ["Monitoramento de energia em R$", "Usuário cadastrado (associado ao parceiro de energia)", "Acompanhar o custo da energia"],
    ["Painel social anonimizado", "Gestor do programa social", "Acompanhar indicadores do território"],
    ["Renegociação de dívidas", "Parceiro financeiro (serve o plano de quitação)", "Oferecer renegociação de dívidas"],
  ], [32, 32, 36]),
  space(),
  H2("5.3 Jornadas e processos"),
  P("Os processos estão agrupados em três jornadas da família e dois processos dos parceiros:"),
  B("**Aprender jogando (área aberta):** Jogar simuladores (sem cadastro) → Concluir trilha educativa. Não exige conta, para não afastar quem ainda desconfia de aplicativos financeiros."),
  B("**Jornada financeira da família:** Cadastrar renda e dívidas → Registrar gastos do dia a dia → Consultar o Termômetro → Seguir o plano de quitação → Receber alerta e pagar a parcela → evento \"Família sai da faixa Vermelha\". O evento final é exatamente o resultado medido na Fase A."),
  B("**Energia da casa:** Acompanhar o custo da energia → Ajustar o consumo após alerta. O ajuste no consumo dispara uma nova consulta ao Termômetro, ligando a economia de luz ao orçamento."),
  B("**Parceiros:** o CRAS acompanha indicadores do território (dados agregados, nunca individuais) e as cooperativas oferecem renegociação, que serve o processo de seguir o plano de quitação."),
  H2("5.4 Objetos de negócio"),
  P("Perfil da família (renda), Gasto, Dívida, Plano de quitação, Leitura de energia, Trilha e desafio e Indicadores anonimizados. Cada um é realizado por um objeto de dados na camada de Aplicação (por exemplo, \"Gasto\" é realizado pela tabela transacao), o que permite rastrear a informação do negócio até o banco."),
  H2("5.5 Modelo de negócio"),
  B("**Gratuito para as famílias.**"),
  B("**B2G:** prefeituras e CRAS adotam o app em programas sociais e recebem o painel agregado e anonimizado."),
  B("**Parcerias:** cooperativas e ONGs patrocinam trilhas e oferecem renegociação; distribuidoras de energia distribuem o medidor em programas de eficiência energética; a Claro oferece zero-rating."),
  H2("5.6 Análise de lacunas (AS-IS × TO-BE)"),
  table(["Situação atual (AS-IS)", "Arquitetura-alvo (TO-BE)", "Lacuna fechada por"], [
    ["Família não sabe quanto da renda está comprometida", "Termômetro em cores, com a mesma regra em todos os canais", "Serviço Diagnóstico financeiro"],
    ["Dívidas pagas sem estratégia, priorizando a mais \"urgente\"", "Plano de quitação pelo maior juros, com alertas", "Serviço Plano de quitação e alertas"],
    ["Educação financeira em linguagem técnica e paga", "Jogos curtos, gratuitos e com áudio, sem cadastro", "Serviço Educação financeira gamificada"],
    ["Consumo de luz percebido só na fatura", "Custo em R$ em tempo real e alerta antes de estourar a meta", "Serviço Monitoramento de energia"],
    ["CRAS sem dados para orientar e medir resultados", "Indicadores agregados e anonimizados do território", "Serviço Painel social anonimizado"],
  ], [34, 38, 28]),
]);

// 6. Aplicação
const cap6 = capFig(6, "6. Arquitetura de Sistemas – Camada de Aplicação (Fase C)", [
  "A Fase C identifica as **aplicações e os dados** que realizam os processos de negócio. Na visão, os serviços de aplicação ficam no topo (e servem os processos da Fase B), os componentes no meio, com suas funções e interfaces desenhadas dentro deles, e os objetos de dados embaixo.",
], 3, "Visão 03 – Camada de Aplicação (Fase C)", [
  H2("6.1 Componentes de aplicação"),
  table(["Componente", "Tecnologia", "Funções principais", "Interface"], [
    ["App Mobile Grana Amiga", "Flutter (Hugo)", "Modo offline com sincronização · leitura em voz e ícones grandes · jogos e simuladores · biometria destrava o token JWT", "Telas do app (7 telas acessíveis)"],
    ["API Principal", "Java 21 · Spring Boot 3.5 (Pedro)", "Autenticação JWT + BCrypt (USER/ADMIN) · CRUD de transações, categorias e dívidas · resumo mensal com cache · receber leituras · HATEOAS, validação e erros padronizados · Actuator e Swagger", "REST API /api (JSON + JWT)"],
    ["API de Conteúdo", "ASP.NET Core 8 + EF Core (Matheus)", "CRUD de trilhas e desafios · respostas 400/404 em JSON", "REST API /api/trilhas"],
    ["Rotinas PL/SQL", "Oracle PL/SQL (Davi)", "PRC_REGISTRAR_TRANSACAO · PRC_TERMOMETRO_E_PLANO (IF/ELSIF do Termômetro, cursor por maior juros, LOOP de meses até quitar)", "–"],
    ["Integração IoT", "Node-RED", "Ponte MQTT → HTTP · dashboard de consumo", "Dashboard de energia"],
    ["Firmware do medidor", "ESP32 / Arduino (EmonLib)", "Calcular W, kWh e R$ · guardar leituras offline e publicar", "Tópico MQTT casa/{id}/energia"],
    ["Chatbot WhatsApp", "Visão de produto", "Extrair valor e categoria da mensagem e gravar a transação com origem = WHATSAPP", "Conversa no WhatsApp"],
  ], [18, 18, 44, 20]),
  space(),
  H2("6.2 Serviços de aplicação e ligação com o negócio"),
  table(["Serviço de aplicação", "Realizado por", "Serve o processo de negócio"], [
    ["Autenticação e conta", "API Principal", "Cadastrar renda e dívidas (e o acesso do app)"],
    ["Transações e categorias", "API Principal", "Registrar gastos do dia a dia"],
    ["Registro de gasto por mensagem", "Chatbot WhatsApp", "Registrar gastos do dia a dia"],
    ["Dívidas e plano de quitação", "API Principal", "Seguir o plano · Receber alerta e pagar a parcela"],
    ["Cálculo do Termômetro do Dinheiro", "Rotinas PL/SQL e API Principal", "Consultar o Termômetro"],
    ["Conteúdo educativo (trilhas e desafios)", "API de Conteúdo", "Concluir trilha educativa (e serve o app)"],
    ["Leituras e alertas de energia", "Integração IoT e API Principal", "Acompanhar o custo da energia"],
  ], [32, 30, 38]),
  space(),
  H2("6.3 Fluxos de integração"),
  B("**Energia:** o firmware calcula Irms × tensão = potência (W); potência × tempo = kWh; kWh × tarifa = custo em R$. Ele publica a leitura no tópico MQTT casa/{id}/energia; o Node-RED assina o tópico e faz POST /leituras na API Principal, que grava em leitura_energia e devolve os alertas ao app."),
  B("**Registro de gastos:** o app chama a API Principal com o token JWT; no WhatsApp (visão de produto), o chatbot transcreve o áudio (\"Gastei 15 reais com o ônibus\"), identifica valor e categoria e grava a transação com origem = WHATSAPP."),
  B("**Conteúdo:** o app consome as trilhas e desafios da API de Conteúdo, que podem ser atualizados por parceiros sem publicar uma nova versão do app."),
  H2("6.4 Dados"),
  table(["Objeto de dados", "Acessado por", "Observação"], [
    ["usuario", "API Principal", "Login por telefone; senha só como hash; papel USER/ADMIN; renda_mensal"],
    ["categoria", "API Principal (leitura)", "Ícone e tipo ENTRADA/SAIDA; cache"],
    ["transacao", "API Principal; PRC_REGISTRAR_TRANSACAO", "Campo origem (APP / WHATSAPP / IOT) amarra os canais"],
    ["divida", "API Principal; PRC_TERMOMETRO_E_PLANO", "Saldo, juros ao mês, parcela, vencimento e status"],
    ["dispositivo / leitura_energia", "API Principal", "Dispositivo 1:N leituras; tarifa e meta mensal em R$"],
    ["trilha / desafio", "API de Conteúdo", "Trilha 1:N desafio (composição no modelo)"],
  ], [26, 34, 40]),
  note("Os nomes de tabelas e colunas são iguais nos dois bancos (Oracle e PostgreSQL), em português e snake_case; só o DDL muda."),
  H2("6.5 Segurança e conformidade"),
  P("Autenticação com JWT e senha protegida por BCrypt; papéis USER (somente os próprios dados) e ADMIN (categorias). O login usa o telefone, e não o CPF, para reduzir a exposição de dado pessoal sensível sob a LGPD. A biometria do aparelho apenas destrava o token já salvo, e a voz é usada só para navegação, nunca como autenticação. Segredos (senhas e connection strings) ficam em variáveis de ambiente, nunca no código."),
]);

// 7. Tecnologia
const cap7 = capFig(7, "7. Arquitetura de Tecnologia (Fase D)", [
  "A Fase D detalha a **infraestrutura** que executa as aplicações da Fase C e transporta os dados entre elas. Na visão, os serviços de tecnologia ficam no topo (e servem os componentes de aplicação), os nós e dispositivos no meio e as redes embaixo.",
], 4, "Visão 04 – Camada de Tecnologia (Fase D)", [
  H2("7.1 Nós, dispositivos e software"),
  table(["Elemento", "Composição", "Serviço que oferece / serve"], [
    ["VM Azure · Ubuntu 24.04 LTS (Standard_B2als_v2)", "Docker Engine + Compose v2 com dois containers: app (Java 21 JRE + granaamiga-api.jar) e db (PostgreSQL 16 + volume postgres-data); artefatos Dockerfile multi-stage, docker-compose.yml + .env, provision-vm.sh (Azure CLI); rede granaamiga-network", "Hospedagem de containers e Banco relacional PostgreSQL → API Principal"],
    ["Oracle FIAP", "Oracle Database; scripts PL/SQL; Migrations EF Core", "Banco relacional Oracle → API de Conteúdo e Rotinas PL/SQL"],
    ["Execução local (dotnet run)", "Runtime .NET 8 com o servidor Kestrel embutido, na máquina do desenvolvedor", "Runtime .NET → API de Conteúdo"],
    ["Broker MQTT HiveMQ (nuvem)", "Broker de mensagens", "Broker MQTT → Integração IoT e Firmware"],
    ["Servidor Node-RED", "Node-RED 4.1 (Node.js)", "Executa a Integração IoT"],
    ["Smartphone da família", "Android/iOS; grana_amiga.apk; biometria e leitor de tela do aparelho", "Realiza o App Mobile"],
    ["Medidor de energia ESP32", "Sensor SCT-013, LCD 16x2 I2C, LED RGB, buzzer, framework Arduino, firmware (.ino)", "Publica leituras via MQTT"],
    ["WhatsApp Business Platform (Meta)", "Visão de produto", "Mensageria WhatsApp → Chatbot"],
  ], [26, 46, 28]),
  space(),
  H2("7.2 Redes"),
  B("**Internet / rede móvel Claro (zero-rating):** acesso do smartphone ao app sem consumir o pacote de dados."),
  B("**Wi-Fi doméstico → Internet:** o medidor publica no broker; sem conexão, guarda as leituras e continua mostrando o custo no LCD."),
  B("**Azure VNet + NSG:** libera apenas as portas 22 (SSH) e 8080 (API). A porta 5432 do banco não é exposta: o container app fala com o db pela rede interna granaamiga-network, usando o nome do serviço (db) como host."),
  H2("7.3 Justificativas tecnológicas"),
  table(["Decisão", "Por quê"], [
    ["PostgreSQL em container (DevOps) e Oracle FIAP (.NET e PL/SQL)", "PostgreSQL é leve e reproduzível em container na VM; o Oracle da FIAP é exigido pelas disciplinas de .NET e Banco. Os nomes das tabelas são os mesmos nos dois."],
    ["Docker Compose com volume nomeado e healthcheck", "Infraestrutura reproduzível a partir do README; os dados sobrevivem à recriação dos containers; a API só sobe depois que o banco está saudável."],
    ["VM provisionada por Azure CLI", "Script versionado (provision-vm.sh) em vez de cliques no portal: qualquer pessoa recria o ambiente."],
    ["MQTT + Node-RED", "Protocolo leve, ideal para dispositivos de baixo custo e conexões instáveis; o Node-RED faz a ponte para HTTP sem acoplar o firmware à API."],
    ["ESP32 + SCT-013", "Wi-Fi embutido e baixo custo; o sensor de alicate mede a corrente sem mexer na fiação, sem risco elétrico para a família."],
    ["App com dados locais e sincronização", "Atende o princípio offline-first; o app continua útil com sinal fraco."],
  ], [34, 66]),
]);

// 8. Visão integrada
const cap8 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun("8. Visão integrada e validação da arquitetura")] }),
  P("A visão completa mostra as quatro camadas empilhadas e as relações entre elas: os serviços de aplicação **servem** os processos de negócio, e os serviços de tecnologia **servem** os componentes de aplicação. É ela que permite validar se cada necessidade da Fase A tem algo concreto que a sustente nas fases seguintes."),
  ...figure(0, "Visão 00 – Arquitetura de Solução completa (Fases A a D)", W_PORT, 11800),
  H2("8.1 Rastreabilidade: do requisito à tecnologia"),
  table(["Requisito (Fase A)", "Negócio (Fase B)", "Aplicação (Fase C)", "Tecnologia (Fase D)"], [
    ["Área aberta com jogos", "Educação financeira gamificada", "App Mobile (jogos) + API de Conteúdo", "Smartphone; execução local .NET; Oracle FIAP"],
    ["Login por telefone + senha e biometria", "Acesso do Usuário cadastrado", "Autenticação e conta (JWT + BCrypt); biometria no app", "Container app na VM Azure"],
    ["Termômetro do Dinheiro", "Diagnóstico financeiro", "Cálculo do Termômetro (PRC_TERMOMETRO_E_PLANO)", "Oracle FIAP; PostgreSQL"],
    ["Plano de quitação com alertas", "Plano de quitação e alertas", "Dívidas e plano de quitação", "VM Azure (app + db)"],
    ["Registrar gastos por ícones, voz ou WhatsApp", "Registro de gastos multicanal", "Transações e categorias; Chatbot (visão de produto)", "VM Azure; WhatsApp Platform"],
    ["Registro offline com sincronização", "Todos os serviços da família", "Modo offline do app; buffer do firmware", "Smartphone; ESP32"],
    ["Medidor em R$ com alerta", "Monitoramento de energia em R$", "Firmware; Integração IoT; Leituras e alertas", "ESP32 + SCT-013; HiveMQ; Node-RED; VM"],
    ["Trilhas sem novo deploy", "Educação financeira gamificada", "API de Conteúdo (CRUD de trilhas)", "Execução local .NET; Oracle FIAP"],
    ["Painel anonimizado para o CRAS", "Painel social anonimizado", "Relatórios agregados (evolução da API)", "VM Azure"],
  ], [24, 24, 28, 24]),
  space(),
  H2("8.2 Checagem dos princípios"),
  table(["Princípio", "Como a arquitetura cumpre", "Status"], [
    ["Cidadão no centro", "Área aberta sem cadastro, áudio, ícones grandes, canais de baixo consumo (WhatsApp, display do medidor)", "Atendido"],
    ["Privacidade (LGPD)", "Telefone no lugar de CPF, BCrypt, JWT, papéis, porta do banco fechada, dados anonimizados para parceiros", "Atendido"],
    ["Gratuito para as famílias", "Receita via B2G e parcerias; nenhum serviço essencial pago", "Atendido no modelo de negócio"],
    ["Offline-first", "Sincronização no app e buffer no medidor", "Atendido"],
  ], [24, 56, 20]),
];

// 9. Limitações
const cap9 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun("9. Limitações, riscos e próximos passos")] }),
  H2("9.1 Limitações da versão atual"),
  B("**Chatbot de WhatsApp e IA de voz:** fazem parte da arquitetura-alvo, mas não são implementados nesta GS (restrição de escopo explícita no modelo). No app há uma tela simulada de conversa ou link wa.me."),
  B("**App com dados mockados:** a disciplina de Mobile aceita dados locais; o app foi estruturado para trocar a fonte pela API Java."),
  B("**Medidor:** se a demonstração for feita no simulador Wokwi, a corrente é simulada com um potenciômetro; a leitura é uma estimativa (não substitui o medidor da distribuidora)."),
  B("**Painel B2G:** previsto como evolução da API Principal (relatórios agregados)."),
  B("**API de Conteúdo (.NET):** nesta GS roda localmente (dotnet run), ligada ao Oracle da FIAP, porque a disciplina não exige deploy. Em produção, ela iria para a nuvem junto com a API Principal (por exemplo, como mais um container na VM Azure)."),
  H2("9.2 Riscos e mitigação"),
  table(["Risco", "Mitigação"], [
    ["Baixa adesão por desconfiança de apps financeiros", "Área aberta sem cadastro; entrada pelo CRAS, que já tem relação de confiança com a família"],
    ["Vazamento de dados pessoais", "Princípio de privacidade, dados anonimizados para parceiros, segredos fora do código, porta do banco fechada"],
    ["Conectividade ruim", "Offline-first no app e no medidor; zero-rating com a Claro"],
    ["Custo da infraestrutura", "VM pequena (2 vCPU, 4 GB), script de remoção do ambiente e crescimento financiado por parcerias"],
  ], [36, 64]),
  space(),
  H2("9.3 Próximos passos (Fases E a H do ADM)"),
  N("**E – Oportunidades e soluções:** piloto com um CRAS e uma cooperativa parceira.", 2),
  N("**F – Planejamento da migração:** integrar o app à API Principal (substituindo os dados mockados) e implementar o painel B2G.", 2),
  N("**G – Governança da implementação:** acompanhar as metas de impacto (Outcomes) e a conformidade com a LGPD.", 2),
  N("**H – Gestão de mudanças:** evoluir para o chatbot de WhatsApp e expandir as trilhas com parceiros.", 2),
];

// 10. Referências e IA
const link = (text, url) => new Paragraph({
  numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 },
  children: [new TextRun(text + " "), new ExternalHyperlink({ link: url, children: [new TextRun({ text: url, style: "Hyperlink", size: 18 })] })],
});
const cap10 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun("10. Referências")] }),
  link("CNC – Peic de julho de 2026 (via Sou Brasília):", "https://soubrasilia.com/endividamento-familias-82-por-cento-julho-2026-peic-cnc-recorde/"),
  link("CNC – Peic de julho de 2026 (via Paraíba Business):", "https://paraibabusiness.com.br/endividamento-de-familias-chega-a-82-em-julho-diz-cnc/"),
  link("Endividamento atinge 60 milhões de lares em julho (Gazeta SP):", "https://www.gazetasp.com.br/economia/endividamento-familiar-atinge-60-milhoes-de-lares-em-julho-e-bate-6o-recorde-seguido-no-pais-aponta-cnc/"),
  link("CNC: endividamento sobe para 82%, mas inadimplência cai (Mercado & Consumo):", "https://mercadoeconsumo.com.br/06/08/2026/noticias/cnc-endividamento-das-familias-sobe-para-82-mas-inadimplencia-cai/"),
  link("DIEESE – Síntese Especial 23 (2026):", "https://www.dieese.org.br/sinteseespecial/2026/sinteseEspecial23.pdf"),
  link("Ehrhardt-Martinez, Donnelly e Laitner – Advanced Metering Initiatives and Residential Feedback Programs, ACEEE Report E105 (2010):", "https://www.aceee.org/research-report/e105"),
  link("The Open Group – TOGAF Standard:", "https://pubs.opengroup.org/togaf-standard/index.html"),
  link("The Open Group – ArchiMate 3.1, relacionamentos entre camadas:", "https://pubs.opengroup.org/architecture/archimate3-doc/"),
  link("Archi – ferramenta de modelagem ArchiMate:", "https://www.archimatetool.com/"),
  link("FIAP – Global Solution CitizenTech:", "https://experience.fiap.com.br/global-solution-citizen-tech"),
  B("Material de aula: \"Intro à Arquitetura de solução com TOGAF\" e \"TOGAF no Archi\" (Compliance & Quality Assurance, FIAP)."),
  H2("Declaração de uso de IA generativa"),
  P("A equipe usou o assistente Claude (Anthropic) para apoiar a estruturação do documento, a geração do arquivo do modelo ArchiMate por script e a revisão de texto e de consistência entre as camadas. Todo o conteúdo – problema, solução, decisões de arquitetura e metas – foi definido pela equipe, e o modelo foi aberto, conferido e validado no Archi pelos integrantes."),
];

// ---------- documento ----------
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
  new TextRun({ text: "Grana Amiga – Arquitetura de Soluções · GS 2026/2 · 2TDSPR    |    Página ", size: 16, color: GRAY }),
  new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GRAY }),
] })] });


function buildSections(items) {
  const margin = { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN };
  const port = { page: { size: A4, margin } };
  const land = { page: { size: { ...A4, orientation: PageOrientation.LANDSCAPE }, margin } };
  const out = [];
  let cur = [];
  for (const it of items) {
    if (it && it[LAND]) {
      out.push({ properties: port, footers: { default: footer }, children: cur });
      out.push({ properties: land, footers: { default: footer }, children: it[LAND] });
      cur = [];
    } else cur.push(it);
  }
  out.push({ properties: port, footers: { default: footer }, children: cur });
  return out;
}
const doc = new Document({
  creator: "Equipe Grana Amiga – 2TDSPR",
  title: "Grana Amiga – Documento descritivo da arquitetura",
  description: "GS 2026/2 – Compliance, Quality Assurance & Tests",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: "Arial", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Arial", size: 32, bold: true, color: NAVY },
        paragraph: { spacing: { before: 240, after: 160 }, keepNext: true, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: TEAL, space: 4 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Arial", size: 25, bold: true, color: TEAL },
        paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Arial", size: 22, bold: true, color: NAVY },
        paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] },
  ] },
  sections: buildSections([...capa, ...sumario, ...cap1, ...cap2, ...cap3, ...cap4, ...cap5, ...cap6, ...cap7, ...cap8, ...cap9, ...cap10]),
});

fs.mkdirSync(path.dirname(OUT), { recursive: true });
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("ok ->", OUT, figCount, "figuras"); });
