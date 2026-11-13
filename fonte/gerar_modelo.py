"""Gera o modelo ArchiMate (.archimate) da Grana Amiga para a entrega de
Compliance, Quality Assurance & Tests (GS 2026/2).

Uso:  python gerar_modelo.py <pasta_saida>
Saída: <pasta_saida>/GranaAmiga-Arquitetura.archimate  +  modelo.json (para o preview)

O arquivo é aberto direto no Archi (archimatetool.com). Cada elemento recebe
prefixo no nome (DRIVER:, GOAL:, ...) seguindo o padrão usado em aula.
"""
import json
import sys
import uuid
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 170, 85          # tamanho padrão de um elemento
E = {}                  # key -> elemento
R = []                  # relacionamentos


def _id():
    return "id-" + uuid.uuid4().hex


def el(key, typ, name, x, y, w=W, h=H, parent=None, layer=None, doc="", fill=None, fixed=False):
    if key in E:
        raise ValueError(f"chave duplicada: {key}")
    if parent and layer is None:
        layer = E[parent]["layer"]
    E[key] = dict(key=key, id=_id(), type=typ, name=name, x=x, y=y, w=w, h=h,
                  parent=parent, layer=layer, doc=doc, fill=fill, fixed=fixed)
    return key


def rel(typ, src, tgt, show=True, name="", access=None, doc=""):
    R.append(dict(id=_id(), type=typ, src=src, tgt=tgt, show=show, name=name, access=access, doc=doc))


def row(y, items, x0=40, step=195, layer=None, w=W, h=H):
    """items: lista de (key, type, name, doc) colocados lado a lado."""
    for i, (k, t, n, d) in enumerate(items):
        el(k, t, n, x0 + i * step, y, w, h, layer=layer, doc=d)


# =============================================================================
# CAMADA DE MOTIVAÇÃO  (Fase A – Visão de Arquitetura)
# =============================================================================
L = "motivacao"
el("G_M", "Grouping", "CAMADA DE MOTIVAÇÃO  ·  Fase A – Visão de Arquitetura",
   20, 20, 2010, 850, layer=L, fill="#F3F0FF",
   doc="Por que a solução existe: interessados, direcionadores, avaliações (dados de mercado), "
       "objetivos, resultados esperados, princípios, requisitos e restrições.")

for k, n, x, d in [
    ("s_fam", "STAKEHOLDER: Famílias endividadas (renda até 3 salários mínimos)", 1015,
     "Público principal: chefes de família de baixa renda, muitas vezes com baixa escolaridade."),
    ("s_cras", "STAKEHOLDER: Prefeituras e CRAS", 430,
     "Assistência social municipal; usa a solução em programas sociais (modelo B2G)."),
    ("s_coop", "STAKEHOLDER: Cooperativas de crédito e ONGs", 625,
     "Patrocinam trilhas educativas e oferecem renegociação justa de dívidas."),
    ("s_ener", "STAKEHOLDER: Claro e distribuidoras de energia", 1405,
     "Claro (parceira da GS) com zero-rating; distribuidoras/programas de eficiência energética distribuem o medidor."),
]:
    el(k, "Stakeholder", n, x, 70, layer=L, doc=d)

for k, n, x, d in [
    ("d_divida", "DRIVER: Endividamento recorde das famílias brasileiras", 625,
     "Peic/CNC jul/2026: 82% das famílias com dívidas, recorde da série histórica."),
    ("d_educ", "DRIVER: Baixa educação financeira e falta de ferramentas acessíveis", 1015,
     "Apps financeiros pressupõem conta digital, leitura fluente e internet boa."),
    ("d_luz", "DRIVER: Conta de luz pesa no orçamento e o consumo é invisível", 1405,
     "A família só descobre quanto gastou de energia quando a conta chega."),
]:
    el(k, "Driver", n, x, 180, layer=L, doc=d)

for k, n, x, d in [
    ("a_82", "ASSESS: 82% das famílias têm dívidas (Peic/CNC, jul/2026)", 235, "Recorde da série histórica da CNC."),
    ("a_849", "ASSESS: 84,9% entre famílias com renda até 3 salários mínimos", 430, "Contra 72% acima de 10 salários mínimos."),
    ("a_cartao", "ASSESS: Cartão de crédito em 85,3% das famílias endividadas (Peic, jul/2026)", 625, "Rotativo e parcelamento são o principal vilão."),
    ("a_30", "ASSESS: Comprometimento médio de ~30% da renda com dívidas", 820, "Base do limite Verde do Termômetro do Dinheiro."),
    ("a_ling", "ASSESS: Linguagem financeira difícil exclui quem tem baixa escolaridade", 1015, ""),
    ("a_tools", "ASSESS: Faltam ferramentas gratuitas, com áudio e que funcionem offline", 1210, ""),
    ("a_invis", "ASSESS: Consumo de energia só aparece quando a conta chega", 1405, ""),
    ("a_feedback", "ASSESS: Feedback de consumo reduz de 4% a 12% o gasto de energia (ACEEE, 2010)", 1600,
     "Ehrhardt-Martinez, Donnelly e Laitner, ACEEE Report E105 (2010): meta-análise de programas de feedback residencial; feedback em tempo real fica no topo da faixa (~12%)."),
]:
    el(k, "Assessment", n, x, 290, layer=L, doc=d)

for k, n, x in [
    ("g_verm", "GOAL: Tirar famílias da faixa Vermelha do Termômetro do Dinheiro", 527),
    ("g_educ", "GOAL: Educar financeiramente de forma lúdica, inclusiva e gratuita", 1112),
    ("g_luz", "GOAL: Reduzir o desperdício de energia e o peso da conta de luz", 1502),
]:
    el(k, "Goal", n, x, 400, layer=L)

for k, n, x, d in [
    ("o_verm", "OUTCOME: Meta – 30% dos usuários ativos saem do Vermelho em 3 meses", 430, "Principal métrica de impacto."),
    ("o_quit", "OUTCOME: Valor total de dívidas quitadas cresce mês a mês", 625, ""),
    ("o_trilha", "OUTCOME: Trilhas concluídas e dias seguidos registrando gastos", 1015, ""),
    ("o_conta", "OUTCOME: Meta – 20% dos visitantes da área aberta criam conta", 1210, "Conversão da área aberta (jogos) em uso do painel."),
    ("o_kwh", "OUTCOME: Meta – 10% a menos de consumo nas casas com medidor", 1502, "Dentro da faixa de 4–12% da ACEEE; o medidor dá feedback em tempo real, tipo de programa no topo da faixa."),
]:
    el(k, "Outcome", n, x, 510, layer=L, doc=d)

# requisitos ordenados para ficar embaixo dos resultados que realizam
REQS = [
    ("r_login", "REQ: Login por telefone + senha (JWT) e biometria do aparelho", "Biometria só destrava o token salvo; voz apenas para navegação."),
    ("r_painel", "REQ: Painel agregado e anonimizado para CRAS e parceiros", "Modelo B2G que sustenta a gratuidade."),
    ("r_termo", "REQ: Termômetro – Verde ≤ 30%, Amarelo ≤ 50%, Vermelho > 50% da renda", "comprometimento = soma das parcelas ativas / renda mensal."),
    ("r_plano", "REQ: Plano de quitação (maior juros primeiro) com alertas de vencimento", "Método avalanche."),
    ("r_gastos", "REQ: Registrar gastos por ícones, voz ou WhatsApp", ""),
    ("r_trilhas", "REQ: Trilhas e desafios gerenciáveis sem novo deploy do app", ""),
    ("r_jogos", "REQ: Área aberta com jogos sem cadastro, com áudio e ícones grandes", ""),
    ("r_medidor", "REQ: Medidor mostra a luz em R$ e alerta antes de estourar a meta", "LED verde < 70%, amarelo 70–100%, vermelho > 100% + buzzer."),
    ("r_offline", "REQ: Registro offline com sincronização posterior", ""),
]
for i, (k, n, d) in enumerate(REQS):
    el(k, "Requirement", n, 40 + i * 195, 640, layer=L, doc=d)

# linha de baixo: restrições e princípios, cada um perto dos requisitos ligados a ele
for k, t, n, x, d in [
    ("c_lgpd", "Constraint", "CONST: LGPD – dados financeiros e de consumo são dados pessoais", 40, ""),
    ("p_priv", "Principle", "PRINCIPLE: Privacidade desde a concepção (LGPD)", 235,
     "Telefone no lugar de CPF; dados agregados e anonimizados para parceiros."),
    ("p_gratis", "Principle", "PRINCIPLE: Gratuito para as famílias", 430, "Sustentado por B2G e parcerias."),
    ("c_escopo", "Constraint", "CONST: Escopo da GS – chatbot e IA de voz ficam como visão de produto", 820,
     "Não são cobrados por nenhuma disciplina; no app há uma tela simulada / link wa.me."),
    ("p_cidadao", "Principle", "PRINCIPLE: Cidadão no centro – simples, inclusivo e acessível", 1015,
     "Áudio, ícones grandes, linguagem simples."),
    ("c_escol", "Constraint", "CONST: Baixa escolaridade e pouca familiaridade digital", 1210, ""),
    ("c_seg", "Constraint", "CONST: Medidor barato e não invasivo (sensor de alicate SCT-013)", 1405,
     "Segurança elétrica: nada em série com a rede 127/220 V."),
    ("c_conect", "Constraint", "CONST: Conectividade limitada e pacote de dados restrito", 1600, ""),
    ("p_offline", "Principle", "PRINCIPLE: Funciona fora do cenário ideal (offline-first)", 1795,
     "Conectividade ruim não pode impedir o uso."),
]:
    el(k, t, n, x, 760, layer=L, doc=d)

# relações da motivação
for s, ds in [("s_fam", ["d_divida", "d_educ", "d_luz"]), ("s_cras", ["d_divida"]),
              ("s_coop", ["d_divida"]), ("s_ener", ["d_luz"])]:
    for d in ds:
        rel("Association", s, d)
rel("Association", "s_cras", "d_educ", show=False)
for d, as_ in [("d_divida", ["a_82", "a_849", "a_cartao", "a_30"]), ("d_educ", ["a_ling", "a_tools"]),
               ("d_luz", ["a_invis", "a_feedback"])]:
    for a in as_:
        rel("Influence", d, a)
for a, g in [("a_849", "g_verm"), ("a_cartao", "g_verm"), ("a_30", "g_verm"), ("a_82", "g_verm"),
             ("a_ling", "g_educ"), ("a_tools", "g_educ"), ("a_invis", "g_luz"), ("a_feedback", "g_luz")]:
    rel("Influence", a, g)
for o, g in [("o_verm", "g_verm"), ("o_quit", "g_verm"), ("o_trilha", "g_educ"), ("o_conta", "g_educ"), ("o_kwh", "g_luz")]:
    rel("Realization", o, g)
for p, g in [("p_cidadao", "g_educ"), ("p_gratis", "g_verm")]:
    rel("Influence", p, g, show=False)
for r, t in [("r_jogos", "o_conta"), ("r_jogos", "o_trilha"), ("r_termo", "o_verm"), ("r_plano", "o_quit"),
             ("r_gastos", "o_trilha"), ("r_medidor", "o_kwh"), ("r_trilhas", "o_trilha"), ("r_painel", "o_verm"),
             ("r_jogos", "p_cidadao"), ("r_trilhas", "p_cidadao"), ("r_login", "p_priv"), ("r_painel", "p_priv"),
             ("r_painel", "p_gratis"), ("r_offline", "p_offline")]:
    rel("Realization", r, t)
for c, r in [("c_escol", "r_jogos"), ("c_lgpd", "r_login"), ("c_escopo", "r_gastos"), ("c_conect", "r_offline"),
             ("c_seg", "r_medidor")]:
    rel("Influence", c, r)

# =============================================================================
# CAMADA DE NEGÓCIO  (Fase B)
# =============================================================================
L = "negocio"
el("G_B", "Grouping", "CAMADA DE NEGÓCIO  ·  Fase B – Arquitetura de Negócio",
   20, 910, 2410, 670, layer=L, fill="#FFFDE8",
   doc="Quem participa do ecossistema, quais serviços de negócio a solução oferece, quais processos os realizam "
       "e quais informações de negócio são usadas.")

# linha 1: atores e canais (interfaces) da família
for k, t, n, x, d in [
    ("ac_fam", "BusinessActor", "ACTOR: Família (chefe de família)", 240, "Pessoa que usa o app, o WhatsApp e o medidor."),
    ("bi_lcd", "BusinessInterface", "INTERFACE: Display e LED do medidor", 440, "Funciona mesmo sem internet."),
    ("bi_wa", "BusinessInterface", "INTERFACE: WhatsApp", 630, "Canal de baixo consumo de dados."),
    ("bi_app", "BusinessInterface", "INTERFACE: App Grana Amiga", 820, "Canal principal."),
    ("ac_claro", "BusinessActor", "ACTOR: Claro (operadora)", 1015, "Parceira da GS; acesso ao app sem consumir o pacote de dados."),
    ("ac_dist", "BusinessActor", "ACTOR: Distribuidora de energia", 1655, "Ou programa de eficiência energética que distribui o medidor."),
    ("ac_cras", "BusinessActor", "ACTOR: Assistente social do CRAS", 2050, ""),
    ("ac_coop", "BusinessActor", "ACTOR: Cooperativa de crédito / ONG", 2245, ""),
]:
    el(k, t, n, x, 960, layer=L, doc=d)

# linha 2: papéis
for k, t, n, x, d in [
    ("rl_visit", "BusinessRole", "ROLE: Visitante da área aberta", 40, "Joga sem cadastro."),
    ("rl_user", "BusinessRole", "ROLE: Usuário cadastrado", 470, "Login por telefone + senha; biometria nos acessos seguintes."),
    ("rl_conect", "BusinessRole", "ROLE: Parceiro de conectividade (zero-rating)", 1015, ""),
    ("rl_ener", "BusinessRole", "ROLE: Parceiro de energia", 1655, ""),
    ("bi_painel", "BusinessInterface", "INTERFACE: Painel do parceiro", 1855, "Indicadores agregados e anonimizados."),
    ("rl_gestor", "BusinessRole", "ROLE: Gestor do programa social", 2050, ""),
    ("rl_fin", "BusinessRole", "ROLE: Parceiro financeiro", 2245, ""),
]:
    el(k, t, n, x, 1070, layer=L, doc=d)

# linha 3: serviços de negócio
for k, n, x, d in [
    ("bs_educ", "SERV: Educação financeira gamificada", 155, "Simuladores 'Desafio do Supermercado' e 'Fugindo dos Juros'."),
    ("bs_gasto", "SERV: Registro de gastos multicanal", 655, "Por ícones, voz ou WhatsApp."),
    ("bs_termo", "SERV: Diagnóstico financeiro (Termômetro)", 840, ""),
    ("bs_plano", "SERV: Plano de quitação e alertas", 1117, ""),
    ("bs_luz", "SERV: Monitoramento de energia em R$", 1720, ""),
    ("bs_painel", "SERV: Painel social anonimizado", 2050, "Modelo B2G."),
    ("bs_reneg", "SERV: Renegociação de dívidas", 2245, ""),
]:
    el(k, "BusinessService", n, x, 1190, layer=L, doc=d)

# linha 4: processos agrupados por jornada
el("G_apr", "Grouping", "Aprender jogando (área aberta)", 40, 1300, 400, 130, layer=L, fill="#FFF7C2")
el("pr_jogar", "BusinessProcess", "PROC: Jogar simuladores (sem cadastro)", 55, 1340, parent="G_apr")
el("pr_trilha", "BusinessProcess", "PROC: Concluir trilha educativa", 255, 1340, parent="G_apr")

el("G_jorn", "Grouping", "Jornada financeira da família", 460, 1300, 1125, 130, layer=L, fill="#FFF7C2")
jorn = [("jp_cad", "BusinessProcess", "PROC: Cadastrar renda e dívidas"),
        ("jp_gasto", "BusinessProcess", "PROC: Registrar gastos do dia a dia"),
        ("jp_termo", "BusinessProcess", "PROC: Consultar o Termômetro do Dinheiro"),
        ("jp_plano", "BusinessProcess", "PROC: Seguir o plano de quitação"),
        ("jp_pagar", "BusinessProcess", "PROC: Receber alerta e pagar a parcela"),
        ("ev_verde", "BusinessEvent", "EVENT: Família sai da faixa Vermelha")]
for i, (k, t, n) in enumerate(jorn):
    el(k, t, n, 470 + i * 185, 1340, parent="G_jorn")

el("G_ener", "Grouping", "Energia da casa", 1605, 1300, 400, 130, layer=L, fill="#FFF7C2")
el("pr_luz", "BusinessProcess", "PROC: Acompanhar o custo da energia", 1620, 1340, parent="G_ener")
el("pr_ajust", "BusinessProcess", "PROC: Ajustar o consumo após alerta", 1815, 1340, parent="G_ener")

el("pr_indic", "BusinessProcess", "PROC: Acompanhar indicadores do território", 2050, 1340, layer=L)
el("pr_reneg", "BusinessProcess", "PROC: Oferecer renegociação de dívidas", 2245, 1340, layer=L)

for g in ["G_apr", "G_jorn", "G_ener"]:
    for k, e in E.items():
        if e["parent"] == g:
            rel("Aggregation", g, k, show=False)
ks = [k for k, _, _ in jorn]
for a_, b_ in zip(ks, ks[1:]):
    rel("Triggering", a_, b_)
rel("Triggering", "pr_jogar", "pr_trilha")
rel("Triggering", "pr_luz", "pr_ajust")
rel("Triggering", "pr_ajust", "jp_termo", show=False)

# linha 5: objetos de negócio
for k, n, x in [
    ("bo_trilha", "OBJ: Trilha e desafio", 255),
    ("bo_perfil", "OBJ: Perfil da família (renda)", 470),
    ("bo_gasto", "OBJ: Gasto", 655),
    ("bo_divida", "OBJ: Dívida", 840),
    ("bo_plano", "OBJ: Plano de quitação", 1025),
    ("bo_leit", "OBJ: Leitura de energia", 1620),
    ("bo_indic", "OBJ: Indicadores anonimizados", 2050),
]:
    el(k, "BusinessObject", n, x, 1475, 120, 55, layer=L)

# relações de negócio
for a_, r_ in [("ac_fam", "rl_visit"), ("ac_fam", "rl_user"), ("ac_cras", "rl_gestor"), ("ac_coop", "rl_fin"),
               ("ac_dist", "rl_ener"), ("ac_claro", "rl_conect")]:
    rel("Assignment", a_, r_)
rel("Assignment", "rl_visit", "pr_jogar")
rel("Assignment", "rl_visit", "G_apr", show=False)
rel("Assignment", "rl_user", "jp_cad")
rel("Assignment", "rl_user", "G_jorn", show=False)
rel("Assignment", "rl_user", "G_ener", show=False)
rel("Assignment", "rl_gestor", "pr_indic", show=False)
rel("Assignment", "rl_fin", "pr_reneg", show=False)
for i_ in ["bi_lcd", "bi_wa", "bi_app"]:
    rel("Serving", i_, "rl_user")
rel("Serving", "bi_painel", "rl_gestor")
rel("Association", "rl_conect", "bi_app")
rel("Association", "rl_ener", "bs_luz")
for i_, s in [("bi_app", "bs_termo"), ("bi_wa", "bs_gasto"), ("bi_lcd", "bs_luz"), ("bi_painel", "bs_painel")]:
    rel("Assignment", i_, s, show=False)
for s, r_, show in [("bs_educ", "rl_visit", True), ("bs_gasto", "rl_user", True), ("bs_termo", "rl_user", True),
                    ("bs_plano", "rl_user", True), ("bs_luz", "rl_user", False), ("bs_painel", "rl_gestor", True),
                    ("bs_reneg", "rl_fin", True)]:
    rel("Serving", s, r_, show=show)
for p, s in [("pr_jogar", "bs_educ"), ("pr_trilha", "bs_educ"), ("jp_gasto", "bs_gasto"), ("jp_termo", "bs_termo"),
             ("jp_plano", "bs_plano"), ("jp_pagar", "bs_plano"), ("pr_luz", "bs_luz"), ("pr_reneg", "bs_reneg"),
             ("pr_indic", "bs_painel")]:
    rel("Realization", p, s)
for p, o, acc in [("pr_trilha", "bo_trilha", "read"), ("jp_cad", "bo_perfil", "write"), ("jp_cad", "bo_divida", "write"),
                  ("jp_gasto", "bo_gasto", "write"), ("jp_termo", "bo_divida", "read"), ("jp_plano", "bo_plano", "read"),
                  ("pr_luz", "bo_leit", "read"), ("pr_indic", "bo_indic", "read")]:
    rel("Access", p, o, access=acc)
rel("Serving", "bs_reneg", "jp_plano", show=False)

# =============================================================================
# CAMADA DE APLICAÇÃO  (Fase C – Sistemas de Informação: aplicação e dados)
# =============================================================================
L = "aplicacao"
el("G_A", "Grouping", "CAMADA DE APLICAÇÃO  ·  Fase C – Arquitetura de Sistemas (aplicações e dados)",
   20, 1740, 2010, 580, layer=L, fill="#EAFBFF",
   doc="Componentes de software, serviços de aplicação, interfaces e objetos de dados que realizam os serviços de negócio.")

# serviços de aplicação: cada um logo acima do componente que o realiza
for k, n, x, d in [
    ("as_bot", "SERV: Registro de gasto por mensagem", 420, "Transcreve o áudio e grava a transação com origem = WHATSAPP."),
    ("as_auth", "SERV: Autenticação e conta", 625, ""),
    ("as_tx", "SERV: Transações e categorias", 805, "Extrato do mês, filtro dinâmico, resumo por categoria."),
    ("as_div", "SERV: Dívidas e plano de quitação", 985, ""),
    ("as_cont", "SERV: Conteúdo educativo (trilhas e desafios)", 1190, ""),
    ("as_termo", "SERV: Cálculo do Termômetro do Dinheiro", 1400, ""),
    ("as_ener", "SERV: Leituras e alertas de energia", 1610, ""),
]:
    el(k, "ApplicationService", n, x, 1790, layer=L, doc=d)

# componentes com funções e interface aninhadas (composição implícita)
FW, FH = 160, 62
CY, CH = 1920, 271
def comp(key, name, x, w, items, doc=""):
    cols = max(1, (w - 10) // (FW + 10))
    el(key, "ApplicationComponent", name, x, CY, w, CH, layer=L, doc=doc)
    for i, it in enumerate(items):
        fk, fn = it[0], it[1]
        ft = it[2] if len(it) > 2 else "ApplicationFunction"
        fd = it[3] if len(it) > 3 else ""
        c, r_ = i % cols, i // cols
        fw = w - 20 if cols == 1 else FW
        el(fk, ft, fn, x + 10 + c * (FW + 10), CY + 48 + r_ * (FH + 10), fw, FH, parent=key, doc=fd)
        rel("Composition" if ft == "ApplicationInterface" else "Assignment", key, fk, show=False)

AI = "ApplicationInterface"
comp("c_app", "COMP: App Mobile Grana Amiga (Flutter)", 40, 360, [
    ("f_offline", "FUNC: Modo offline com sincronização"),
    ("f_voz", "FUNC: Leitura em voz e ícones grandes"),
    ("f_jogos", "FUNC: Jogos e simuladores"),
    ("f_biom", "FUNC: Biometria destrava o token JWT"),
    ("ai_telas", "INTERFACE: Telas do app (7 telas acessíveis)", AI,
     "Início, Jogo, Login/Cadastro, Painel, Adicionar gasto, Plano de quitação, Alertas e energia."),
], doc="Hugo – Mobile. Dados mockados nas classes Dart, estruturado para trocar a fonte pela API Java.")
comp("c_bot", "COMP: Chatbot WhatsApp (visão de produto)", 420, 180, [
    ("f_transc", "FUNC: Extrair valor e categoria da mensagem"),
    ("ai_wa", "INTERFACE: Conversa no WhatsApp", AI),
], doc="Fora do escopo das disciplinas; representado como evolução do produto.")
comp("c_api", "COMP: API Principal (Java 21 · Spring Boot 3.5)", 620, 540, [
    ("f_jwt", "FUNC: Autenticação JWT + BCrypt (USER/ADMIN)"),
    ("f_crud", "FUNC: CRUD de transações, categorias e dívidas"),
    ("f_resumo", "FUNC: Resumo mensal com cache"),
    ("f_leit", "FUNC: Receber leituras (POST /leituras)"),
    ("f_hateoas", "FUNC: HATEOAS, validação e erros padronizados"),
    ("f_actuator", "FUNC: Actuator e Swagger/OpenAPI"),
    ("ai_rest", "INTERFACE: REST API /api (JSON + JWT)", AI),
], doc="Pedro – Java Advanced. Spring Web, Data JPA, Bean Validation, Security + JWT, Cache, HATEOAS, Actuator, Swagger.")
comp("c_net", "COMP: API de Conteúdo (C# / EF Core)", 1190, 190, [
    ("f_trilhas", "FUNC: CRUD de trilhas e desafios (EF Core)"),
    ("f_valid", "FUNC: Respostas 400 / 404 em JSON"),
    ("ai_restnet", "INTERFACE: REST API /api/trilhas", AI),
], doc="Matheus – ASP.NET Core 8 Web API em C#, EF Core com Oracle. Trilha 1:N Desafio, Migrations versionadas.")
comp("c_plsql", "COMP: Rotinas PL/SQL (Oracle)", 1400, 230, [
    ("f_prc1", "PROC: PRC_REGISTRAR_TRANSACAO", "ApplicationProcess"),
    ("f_prc2", "PROC: PRC_TERMOMETRO_E_PLANO", "ApplicationProcess"),
], doc="Davi – Banco. IF/ELSIF do Termômetro, cursor por maior juros e LOOP de meses até quitar.")
comp("c_nr", "COMP: Integração IoT (Node-RED)", 1610, 190, [
    ("f_ponte", "FUNC: Ponte MQTT → HTTP"),
    ("f_dash", "FUNC: Dashboard de consumo"),
    ("ai_dash", "INTERFACE: Dashboard de energia", AI),
])
comp("c_fw", "COMP: Firmware do medidor (ESP32 / Arduino)", 1820, 190, [
    ("f_kwh", "FUNC: Calcular W, kWh e R$ (EmonLib)"),
    ("f_buffer", "FUNC: Guardar leituras offline e publicar"),
    ("ai_mqtt", "INTERFACE: Tópico MQTT casa/{id}/energia", AI),
], doc="Irms × tensão = W; W × tempo = kWh; kWh × tarifa = R$; LED/buzzer conforme a meta.")

# objetos de dados (coordenadas finais), deixando corredores livres embaixo dos componentes
for k, n, x in [
    ("do_usuario", "DATA: usuario", 750), ("do_categoria", "DATA: categoria", 910), ("do_transacao", "DATA: transacao", 1070),
    ("do_divida", "DATA: divida", 1300), ("do_trilha", "DATA: trilha", 1490), ("do_desafio", "DATA: desafio", 1700),
    ("do_leitura", "DATA: leitura_energia", 1960), ("do_dispositivo", "DATA: dispositivo", 2150),
]:
    el(k, "DataObject", n, x, 2240, 150, 55, layer=L, fixed=True)

for c, s, show in [("c_bot", "as_bot", True), ("c_api", "as_auth", True), ("c_api", "as_tx", True),
                   ("c_api", "as_div", True), ("c_net", "as_cont", True), ("c_plsql", "as_termo", True),
                   ("c_api", "as_termo", "layer"), ("c_api", "as_ener", "layer"), ("c_nr", "as_ener", True)]:
    rel("Realization", c, s, show=show)
for i_, s in [("ai_rest", "as_tx"), ("ai_restnet", "as_cont"), ("ai_wa", "as_bot"), ("ai_dash", "as_ener")]:
    rel("Assignment", i_, s, show=False)
for s, c, show in [("as_auth", "c_app", True), ("as_cont", "c_app", True), ("as_tx", "c_bot", False)]:
    rel("Serving", s, c, show=show)
rel("Flow", "c_fw", "c_nr", name="MQTT")
rel("Flow", "c_nr", "c_api", doc="POST /leituras (JSON com potência, kWh e custo estimado).")
for c, d, a in [("c_api", "do_usuario", "readwrite"), ("c_api", "do_transacao", "readwrite"), ("c_api", "do_divida", "readwrite"),
                ("c_api", "do_categoria", "read"), ("c_api", "do_leitura", "write"), ("c_api", "do_dispositivo", "read"),
                ("c_net", "do_trilha", "readwrite"), ("c_net", "do_desafio", "readwrite"),
                ("c_plsql", "do_divida", "read"), ("c_plsql", "do_transacao", "write")]:
    rel("Access", c, d, access=a,
        show="layer" if (c, d) in {("c_api", "do_dispositivo"), ("c_plsql", "do_transacao"), ("c_net", "do_desafio")} else True)
rel("Composition", "do_trilha", "do_desafio", doc="1:N – uma trilha tem vários desafios.")
rel("Composition", "do_dispositivo", "do_leitura", name="1:N", show=False)
for s, p in [("as_tx", "jp_gasto"), ("as_bot", "jp_gasto"), ("as_termo", "jp_termo"), ("as_div", "jp_plano"),
             ("as_div", "jp_pagar"), ("as_cont", "pr_trilha"), ("as_ener", "pr_luz"), ("as_auth", "jp_cad")]:
    rel("Serving", s, p)
for d, b in [("do_transacao", "bo_gasto"), ("do_divida", "bo_divida"), ("do_usuario", "bo_perfil"),
             ("do_leitura", "bo_leit"), ("do_trilha", "bo_trilha")]:
    rel("Realization", d, b, show=False)
for e_, r_ in [("f_offline", "r_offline"), ("f_jwt", "r_login"), ("f_prc2", "r_termo"), ("f_prc2", "r_plano"),
               ("f_kwh", "r_medidor"), ("f_trilhas", "r_trilhas"), ("f_jogos", "r_jogos")]:
    rel("Realization", e_, r_, show=False)

# =============================================================================
# CAMADA DE TECNOLOGIA  (Fase D)
# =============================================================================
L = "tecnologia"
el("G_T", "Grouping", "CAMADA DE TECNOLOGIA  ·  Fase D – Arquitetura de Tecnologia",
   20, 2430, 2010, 640, layer=L, fill="#EEF8E8",
   doc="Dispositivos, nós, software de sistema, redes e artefatos que executam e conectam as aplicações.")

el("ts_mqtt", "TechnologyService", "SERV: Broker de mensagens MQTT", 820, 2480, 150, 85, layer=L)
el("ts_docker", "TechnologyService", "SERV: Hospedagem de containers", 1060, 2480, layer=L)
el("ts_pg", "TechnologyService", "SERV: Banco relacional PostgreSQL", 1440, 2480, layer=L)

TY = 2600
el("dv_phone", "Device", "DEVICE: Smartphone da família (Android / iOS)", 40, TY, 360, 245, layer=L)
el("ar_apk", "Artifact", "ARTIFACT: grana_amiga.apk", 52, TY + 45, 160, 60, parent="dv_phone")
el("sw_os", "SystemSoftware", "SW: Android / iOS", 222, TY + 45, 160, 60, parent="dv_phone")
el("sw_bio", "SystemSoftware", "SW: Biometria e leitor de tela do aparelho", 52, TY + 118, 160, 60, parent="dv_phone")

el("dv_esp", "Device", "DEVICE: Medidor de energia ESP32", 420, TY, 380, 245, layer=L,
   doc="Componentes de baixo custo; se a demo for no Wokwi, a corrente é simulada com potenciômetro.")
for i, (k, t, n, d) in enumerate([
    ("ar_fw", "Artifact", "ARTIFACT: firmware do medidor", "Arquivo medidor_energia.ino (framework Arduino) com a lógica de medição."),
    ("sw_ard", "SystemSoftware", "SW: Framework Arduino", ""),
    ("dv_sct", "Device", "DEVICE: Sensor SCT-013", "Sensor de corrente de alicate com resistor de carga."),
    ("dv_lcd", "Device", "DEVICE: LCD 16x2 I2C", ""),
    ("dv_led", "Device", "DEVICE: LED RGB", ""),
    ("dv_buz", "Device", "DEVICE: Buzzer", ""),
]):
    c, r_ = i % 3, i // 3
    el(k, t, n, 432 + c * 120, TY + 45 + r_ * 75, 112, 68, parent="dv_esp", doc=d)

el("nd_mqtt", "Node", "NODE: Broker MQTT HiveMQ (nuvem)", 820, TY, 150, 75, layer=L)
el("nd_nr", "Node", "NODE: Servidor Node-RED", 820, TY + 100, 210, 90, layer=L)
el("sw_nr", "SystemSoftware", "SW: Node-RED 4.1 (Node.js)", 832, TY + 140, 172, 44, parent="nd_nr")

AX = 1050
el("nd_vm", "Node", "NODE: VM Azure · Ubuntu 24.04 LTS", AX, TY, 580, 328, layer=L,
   doc="Standard_B2als_v2 (2 vCPU, 4 GB). Provisionada por Azure CLI (scripts/provision-vm.sh). Entrega de DevOps (Cassio).")
el("sw_docker", "Node", "NODE: Docker Engine + Compose v2", AX + 10, TY + 48, 555, 184, parent="nd_vm",
   doc="Executa os dois containers integrados (app + db) em background (docker compose up -d).")
el("nd_capp", "Node", "NODE: Container app", AX + 20, TY + 93, 262, 126, parent="sw_docker",
   doc="Imagem multi-stage, usuário não-root, WORKDIR, variáveis de ambiente, porta 8080 exposta.")
el("sw_jre", "SystemSoftware", "SW: Java 21 JRE (Temurin)", AX + 30, TY + 137, 120, 70, parent="nd_capp")
el("ar_jar", "Artifact", "ARTIFACT: API Java (JAR)", AX + 156, TY + 137, 110, 70, parent="nd_capp",
   doc="granaamiga-api.jar, gerado no estágio de build do Dockerfile multi-stage.")
el("nd_cdb", "Node", "NODE: Container db", AX + 292, TY + 93, 262, 126, parent="sw_docker",
   doc="PostgreSQL com volume nomeado; porta 5432 só na rede interna granaamiga-network.")
el("ar_vol", "Artifact", "ARTIFACT: volume postgres-data", AX + 302, TY + 137, 120, 70, parent="nd_cdb")
el("sw_pg", "SystemSoftware", "SW: PostgreSQL 16", AX + 428, TY + 137, 110, 70, parent="nd_cdb")
for i, (k, t, n) in enumerate([
    ("ar_dockerfile", "Artifact", "ARTIFACT: Dockerfile (multi-stage)"),
    ("ar_compose", "Artifact", "ARTIFACT: Compose (YAML)"),
    ("ar_prov", "Artifact", "ARTIFACT: provision-vm.sh (Azure CLI)"),
    ("nt_docker", "CommunicationNetwork", "NET: granaamiga-network"),
]):
    el(k, t, n, AX + 10 + i * 139, TY + 242, 131, 74, parent="nd_vm")
E["ar_compose"]["doc"] = "docker-compose.yml com os serviços app e db, rede, volume nomeado e healthcheck; variáveis no .env (fora do Git, com .env.example versionado)."

el("ts_ora", "TechnologyService", "SERV: Banco relacional Oracle", 1980, 2480, 100, 85, layer=L, fixed=True)
el("ts_net", "TechnologyService", "SERV: .NET 8 Runtime", 2140, 2480, 130, 85, layer=L, fixed=True,
   doc="ASP.NET Core 8 com o servidor Kestrel embutido.")
el("ts_wa", "TechnologyService", "SERV: Mensageria WhatsApp (Cloud API)", 2290, 2480, 130, 85, layer=L, fixed=True,
   doc="Visão de produto.")
el("nd_ora", "Node", "NODE: Oracle FIAP", 1980, TY, 140, 250, layer=L, fixed=True,
   doc="Servidor Oracle da FIAP (oracle.fiap.com.br), usado pelo .NET e pelo PL/SQL.")
el("ar_sql", "Artifact", "ARTIFACT: Scripts PL/SQL", 1990, TY + 45, 110, 58, parent="nd_ora",
   doc="Arquivos .sql com DDL, carga de dados, bloco anônimo e as procedures PRC_REGISTRAR_TRANSACAO e PRC_TERMOMETRO_E_PLANO.")
el("ar_migr", "Artifact", "ARTIFACT: Migrations EF Core", 1990, TY + 111, 110, 58, parent="nd_ora")
el("sw_ora", "SystemSoftware", "SW: Oracle Database", 1990, TY + 177, 110, 58, parent="nd_ora")
el("nd_net", "Node", "NODE: Execução local (dotnet run)", 2140, TY, 130, 85, layer=L, fixed=True,
   doc="A API de Conteúdo roda localmente na máquina do desenvolvedor (dotnet run, servidor Kestrel embutido do ASP.NET Core 8), conectada ao Oracle da FIAP. A disciplina de .NET não exige deploy em nuvem.")
el("nd_wa", "Node", "NODE: WhatsApp Business Platform (Meta)", 2290, TY, 130, 85, layer=L, fixed=True,
   doc="Visão de produto.")

for k, n, x, w in [
    ("nt_inet", "NET: Internet / rede móvel Claro (zero-rating)", 40, 360),
    ("nt_wifi", "NET: Wi-Fi doméstico", 420, 380),
    ("nt_azure", "NET: Azure VNet + NSG (libera 22 e 8080)", 1050, 580),
]:
    el(k, "CommunicationNetwork", n, x, TY + 360, w, 60, layer=L)
el("nt_inet2", "CommunicationNetwork", "NET: Internet", 820, TY + 360, 210, 60, layer=L)
rel("Aggregation", "nt_inet", "nt_inet2", show=False)

for p in ["dv_phone", "dv_esp", "nd_nr", "nd_vm", "sw_docker", "nd_capp", "nd_cdb", "nd_ora"]:
    for k, e in E.items():
        if e["parent"] == p:
            t = {"Artifact": "Assignment", "CommunicationNetwork": "Association"}.get(e["type"], "Composition")
            rel(t, p, k, show=False)
for a, c, show in [("ar_apk", "c_app", True), ("ar_jar", "c_api", False), ("ar_fw", "c_fw", False),
                   ("ar_sql", "c_plsql", False)]:
    rel("Realization", a, c, show=show)
for n, s in [("nd_mqtt", "ts_mqtt"), ("sw_docker", "ts_docker"), ("sw_pg", "ts_pg"), ("nd_ora", "ts_ora"),
             ("nd_net", "ts_net"), ("nd_wa", "ts_wa")]:
    rel("Realization", n, s)
for s, c in [("ts_mqtt", "c_nr"), ("ts_mqtt", "c_fw"), ("ts_docker", "c_api"), ("ts_pg", "c_api"), ("ts_ora", "c_net"),
             ("ts_ora", "c_plsql"), ("ts_net", "c_net"), ("ts_wa", "c_bot")]:
    rel("Serving", s, c)
rel("Serving", "sw_nr", "c_nr", show=False)
rel("Realization", "ar_vol", "do_transacao", show=False)
rel("Association", "ar_dockerfile", "nd_capp", show=False)
rel("Association", "nt_inet2", "nd_mqtt", show=False)
for n, a in [("nt_wifi", "dv_esp"), ("nt_inet", "dv_phone"), ("nt_inet2", "nd_nr"),
             ("nt_azure", "nd_vm"), ("nt_wifi", "nt_inet2")]:
    rel("Association", n, a)
rel("Association", "nt_docker", "nd_capp", show=False)
rel("Association", "nt_docker", "nd_cdb", show=False)
rel("Flow", "nd_capp", "nd_cdb", doc="JDBC usando o nome do serviço como host (db:5432) na rede interna.")
rel("Flow", "dv_esp", "nd_mqtt", name="MQTT")
rel("Flow", "nd_mqtt", "nd_nr", doc="Node-RED assina o tópico casa/{id}/energia.")

# =============================================================================
# AJUSTE FINAL DE LAYOUT: camadas com 2410 px de largura e espaçamento horizontal
# maior em Motivação/Aplicação/Tecnologia; Aplicação e Tecnologia sobem 120 px.
# =============================================================================
def _desc(k):
    return [c for c, e in E.items() if e["parent"] == k] +         [d for c, e in E.items() if e["parent"] == k for d in _desc(c)]

for k in ["G_M", "G_B", "G_A", "G_T"]:
    E[k]["w"] = 2410
for k, e in list(E.items()):
    if e["parent"] or e["fixed"] or e["layer"] == "negocio" or k in ("G_M", "G_A", "G_T"):
        continue
    if e["w"] == W and e["type"] not in ("DataObject",):
        e["w"] = 200          # mais espaço para o texto na fonte do Archi
    dx = round(20 + (e["x"] - 20) * 1.2) - e["x"]
    for c in [k] + _desc(k):
        E[c]["x"] += dx
for k, e in E.items():
    if e["layer"] == "aplicacao":
        e["y"] += 15          # -120 (compacta) + 135 (motivação mais alta)
    elif e["layer"] == "tecnologia":
        e["y"] -= 55          # idem, e a Aplicação ficou 70 px mais baixa
    elif e["layer"] == "negocio":
        e["y"] += 135
for k, e in E.items():
    if e["layer"] == "motivacao" and k != "G_M":
        e["y"] = 20 + round((e["y"] - 20) * 1.18)
E["G_M"]["h"] += 135

# =============================================================================
# SERIALIZAÇÃO
# =============================================================================
FOLDER = {
    "Stakeholder": "motivation", "Driver": "motivation", "Assessment": "motivation", "Goal": "motivation",
    "Outcome": "motivation", "Principle": "motivation", "Requirement": "motivation", "Constraint": "motivation",
    "BusinessActor": "business", "BusinessRole": "business", "BusinessInterface": "business",
    "BusinessProcess": "business", "BusinessEvent": "business", "BusinessService": "business", "BusinessObject": "business",
    "ApplicationComponent": "application", "ApplicationInterface": "application", "ApplicationService": "application",
    "ApplicationFunction": "application", "ApplicationProcess": "application", "DataObject": "application",
    "Node": "technology", "Device": "technology", "SystemSoftware": "technology", "CommunicationNetwork": "technology",
    "TechnologyService": "technology", "Artifact": "technology",
    "Grouping": "other",
}
FOLDERS = [("Strategy", "strategy"), ("Business", "business"), ("Application", "application"),
           ("Technology &amp; Physical", "technology"), ("Motivation", "motivation"),
           ("Implementation &amp; Migration", "implementation_migration"), ("Other", "other")]
ACCESS = {"write": "0", "read": "1", "access": "2", "readwrite": "3"}

VIEWS = [
    ("00 - Arquitetura de Solução Grana Amiga (visão completa)", None),
    ("01 - Motivação (Fase A)", "motivacao"),
    ("02 - Negócio (Fase B)", "negocio"),
    ("03 - Aplicação (Fase C)", "aplicacao"),
    ("04 - Tecnologia (Fase D)", "tecnologia"),
]


def a(s):
    return escape(s, {'"': "&quot;"})


def doc_xml(d, ind):
    return f"\n{ind}  <documentation>{a(d)}</documentation>\n{ind}" if d else ""


def element_xml(e, ind="    "):
    d = doc_xml(e["doc"], ind)
    end = f">{d}</element>" if d else "/>"
    return f'{ind}<element xsi:type="archimate:{e["type"]}" name="{a(e["name"])}" id="{e["id"]}"{end}'


def rel_xml(r, ind="    "):
    extra = f' accessType="{ACCESS[r["access"]]}"' if r["type"] == "Access" and r["access"] else ""
    nm = f' name="{a(r["name"])}"' if r["name"] else ""
    d = doc_xml(r["doc"], ind)
    end = f">{d}</element>" if d else "/>"
    return (f'{ind}<element xsi:type="archimate:{r["type"]}Relationship" id="{r["id"]}"{nm} '
            f'source="{E[r["src"]]["id"]}" target="{E[r["tgt"]]["id"]}"{extra}{end}')


def ancestors(k):
    out = []
    while E[k]["parent"]:
        k = E[k]["parent"]
        out.append(k)
    return out


# =============================================================================
# ROTEAMENTO DAS CONEXÕES
# O Archi liga os elementos em linha reta (centro a centro). Quando essa reta
# atravessaria outra caixa, a conexão ganha dobras em ângulo reto (bendpoints):
# sobe/desce até um corredor livre, corre na horizontal e entra no alvo por uma
# coluna sem obstáculos. A camada de Motivação fica como está (já é limpa).
# =============================================================================
ROUTES = {}
LAYER_GROUP = {"motivacao": "G_M", "negocio": "G_B", "aplicacao": "G_A", "tecnologia": "G_T"}


def seg_hits(p0, p1, r, pad=2):
    """Liang–Barsky: o segmento p0-p1 cruza o retângulo r=(x,y,w,h) encolhido por pad?"""
    x0, y0 = p0
    x1, y1 = p1
    rx0, ry0, rx1, ry1 = r[0] + pad, r[1] + pad, r[0] + r[2] - pad, r[1] + r[3] - pad
    dx, dy_ = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - rx0), (dx, rx1 - x0), (-dy_, y0 - ry0), (dy_, ry1 - y0)):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                if t > t1:
                    return False
                t0 = max(t0, t)
            else:
                if t < t0:
                    return False
                t1 = min(t1, t)
    return t0 < t1


def plan_routes(keys, rels, dy):
    B = {k: (E[k]["x"], E[k]["y"] + dy, E[k]["w"], E[k]["h"]) for k in keys}
    cands = [k for k in keys if E[k]["type"] != "Grouping"]
    used = []          # colunas verticais já usadas: (x, y0, y1)
    hsegs = []         # trechos horizontais já usados: (y, x0, x1)
    routes = {}

    def lane(base, step, n, x0, x1):
        """Primeira faixa horizontal livre a partir de base (evita linhas sobrepostas)."""
        lo, hi = min(x0, x1), max(x0, x1)
        for i in range(n):
            y = base + i * step
            if not any(abs(y - hy) < 3 and not (hi < hx0 - 8 or lo > hx1 + 8) for hy, hx0, hx1 in hsegs):
                hsegs.append((y, lo, hi))
                return y
        hsegs.append((base, lo, hi))
        return base

    def center(k):
        x, y, w, h = B[k]
        return (x + w / 2, y + h / 2)

    # linhas retas verticais que não serão roteadas: reservar a coluna delas
    for r in rels:
        s, t = r["src"], r["tgt"]
        if E[s]["layer"] != E[t]["layer"]:
            continue
        cs, ct = center(s), center(t)
        if abs(cs[0] - ct[0]) < 2:
            excl = {s, t, *ancestors(s), *ancestors(t), *_desc(s), *_desc(t)}
            if not any(seg_hits(cs, ct, B[k]) for k in cands if k not in excl):
                used.append((cs[0], min(cs[1], ct[1]), max(cs[1], ct[1])))
    # conexões entre camadas primeiro (são as mais longas)
    rels = sorted(rels, key=lambda r: E[r["src"]]["layer"] == E[r["tgt"]]["layer"])
    for r in rels:
        s, t = r["src"], r["tgt"]
        if E[s]["layer"] == "motivacao" and E[t]["layer"] == "motivacao":
            continue
        excl = {s, t, *ancestors(s), *ancestors(t), *_desc(s), *_desc(t)}
        obst = [B[k] for k in cands if k not in excl]
        cs, ct = center(s), center(t)
        cross = E[s]["layer"] != E[t]["layer"]
        nested_up = (not cross and E[s]["parent"] and not E[t]["parent"]
                     and B[t][1] + B[t][3] < B[s][1])
        if nested_up:
            # sai pelo topo, numa coluna alinhada ao alvo, longe dos títulos centralizados
            S, T = B[s], B[t]
            tx = min(max(ct[0], S[0] + 12), S[0] + S[2] - 12)
            routes[r["id"]] = [(tx, S[1] - 4), (tx, T[1] + T[3] + 4)]
            used.append((tx, T[1] + T[3], S[1]))
            continue
        if not cross and not any(seg_hits(cs, ct, o) for o in obst):
            continue
        S, T = B[s], B[t]

        def clear(x, ya, yb):
            lo, hi = min(ya, yb), max(ya, yb)
            if any(seg_hits((x, lo), (x, hi), o, pad=-4) for o in obst):
                return False
            return not any(abs(x - ux) < 16 and not (hi < u0 or lo > u1) for ux, u0, u1 in used)

        def find_x(R_, ya, yb, pref):
            xs = sorted(range(int(R_[0]) + 10, int(R_[0] + R_[2]) - 9, 3), key=lambda x: abs(x - pref))
            return next((x for x in xs if clear(x, ya, yb)), None)

        S_bot, T_bot = S[1] + S[3], T[1] + T[3]
        pts = None
        if T_bot < S[1]:                                   # alvo acima da origem
            if E[s]["layer"] != E[t]["layer"]:             # corredor = faixa entre as duas camadas
                g = LAYER_GROUP[E[s]["layer"]]
                gtop = E[g]["y"] + dy
                sx = find_x(S, S[1], gtop - 36, cs[0])
                if sx is not None:
                    used.append((sx, gtop - 36, S[1]))
                    tx = find_x(T, gtop - 6, T_bot, ct[0])
                    if tx is not None:
                        yb = lane(gtop - 6, -4, 8, sx, tx)
                        used.append((tx, T_bot, yb))
                        pts = [(sx, S[1] - 6), (sx, yb), (tx, yb), (tx, T_bot + 6)]
                    else:
                        used.pop()
            else:                                          # corredor logo acima da origem
                tx = find_x(T, S[1] - 8, T_bot, ct[0])
                if tx is not None:
                    yh = lane(S[1] - 8, -5, 4, cs[0], tx)
                    used.append((tx, T_bot, yh))
                    pts = [(cs[0], yh), (tx, yh), (tx, T_bot + 6)]
        elif T[1] > S_bot:                                 # alvo abaixo da origem
            tx = find_x(T, S_bot + 8, T[1], ct[0])
            if tx is not None:
                yh = lane(S_bot + 8, 5, 7, cs[0], tx)
                used.append((tx, yh, T[1]))
                pts = [(cs[0], yh), (tx, yh), (tx, T[1] - 6)]
        else:                                              # mesma faixa: contorna por baixo
            yh = lane(max(S_bot, T_bot) + 10, 5, 5, cs[0], ct[0])
            pts = [(cs[0], yh), (ct[0], yh)]
        if pts:
            routes[r["id"]] = pts
    return routes


def view_xml(vname, layer):
    keys = [k for k, e in E.items() if layer is None or e["layer"] == layer]
    keyset = set(keys)
    # deslocamento vertical para visões por camada
    top = min(E[k]["y"] for k in keys if not E[k]["parent"])
    dy = 20 - top if layer else 0
    dobj = {k: _id() for k in keys}
    conns = {k: [] for k in keys}
    for r in R:
        if not r["show"] or (r["show"] == "layer" and layer is None) or r["src"] not in keyset or r["tgt"] not in keyset:
            continue
        if r["tgt"] in ancestors(r["src"]) or r["src"] in ancestors(r["tgt"]):
            continue
        conns[r["src"]].append((_id(), r))
    # o Archi exige que o alvo liste as conexões que chegam nele (targetConnections)
    incoming = {k: [] for k in keys}
    for k in keys:
        for cid, r in conns[k]:
            incoming[r["tgt"]].append(cid)
    routes = plan_routes(keys, [r for k in keys for _, r in conns[k]], dy)
    ROUTES[vname] = {rid: pts for rid, pts in routes.items()}
    B = {k: (E[k]["x"], E[k]["y"] + dy, E[k]["w"], E[k]["h"]) for k in keys}

    def bendpoints(r, ind):
        pts = routes.get(r["id"])
        if not pts:
            return ""
        s_, t_ = B[r["src"]], B[r["tgt"]]
        cs = (s_[0] + s_[2] / 2, s_[1] + s_[3] / 2)
        ct = (t_[0] + t_[2] / 2, t_[1] + t_[3] / 2)
        bp = "".join(f'\n{ind}  <bendpoint startX="{round(px - cs[0])}" startY="{round(py - cs[1])}" '
                     f'endX="{round(px - ct[0])}" endY="{round(py - ct[1])}"/>' for px, py in pts)
        return bp + f"\n{ind}"

    def child(k, ind, px, py):
        e = E[k]
        x, y = e["x"] - px, e["y"] - py + (dy if not e["parent"] else 0)
        fill = f' fillColor="{e["fill"]}"' if e["fill"] else ""
        if e["type"] == "Grouping":
            fill += ' textAlignment="1"'
        tc = f' targetConnections="{" ".join(incoming[k])}"' if incoming[k] else ""
        lines = [f'{ind}<child xsi:type="archimate:DiagramObject" id="{dobj[k]}"{tc}{fill} '
                 f'archimateElement="{e["id"]}">',
                 f'{ind}  <bounds x="{x}" y="{y}" width="{e["w"]}" height="{e["h"]}"/>']
        for cid, r in conns[k]:
            bp = bendpoints(r, ind + "  ")
            end = f">{bp}</sourceConnection>" if bp else "/>"
            lines.append(f'{ind}  <sourceConnection xsi:type="archimate:Connection" id="{cid}" '
                         f'source="{dobj[k]}" target="{dobj[r["tgt"]]}" archimateRelationship="{r["id"]}"{end}')
        for ck, ce in E.items():
            if ce["parent"] == k and ck in keyset:
                lines.extend(child(ck, ind + "  ", e["x"], e["y"]))
        lines.append(f"{ind}</child>")
        return lines

    # grupos de camada primeiro (ficam atrás); demais elementos raiz depois
    roots = [k for k in keys if not E[k]["parent"]]
    roots.sort(key=lambda k: 0 if E[k]["type"] == "Grouping" and E[k]["w"] > 1500 else 1)
    # elementos dentro do retângulo de um grupo de camada são aninhados nele visualmente
    out = [f'    <element xsi:type="archimate:ArchimateDiagramModel" name="{a(vname)}" id="{_id()}">']
    for k in roots:
        out.extend(child(k, "      ", 0, 0))
    out.append("    </element>")
    return out


def build_xml():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
             'xmlns:archimate="http://www.archimatetool.com/archimate" '
             f'name="Grana Amiga – Arquitetura de Solução (GS 2026/2 CitizenTech)" id="{_id()}" version="4.9.0">']
    for fname, ftype in FOLDERS:
        items = [e for e in E.values() if FOLDER[e["type"]] == ftype]
        if not items:
            lines.append(f'  <folder name="{fname}" id="{_id()}" type="{ftype}"/>')
            continue
        lines.append(f'  <folder name="{fname}" id="{_id()}" type="{ftype}">')
        lines.extend(element_xml(e) for e in items)
        lines.append("  </folder>")
    lines.append(f'  <folder name="Relations" id="{_id()}" type="relations">')
    lines.extend(rel_xml(r) for r in R)
    lines.append("  </folder>")
    lines.append(f'  <folder name="Views" id="{_id()}" type="diagrams">')
    for vname, layer in VIEWS:
        lines.extend(view_xml(vname, layer))
    lines.append("  </folder>")
    lines.append("  <purpose>Arquitetura de Soluções (TOGAF ADM, fases A a D) da Grana Amiga, CitizenTech de educação e "
                 "organização financeira para famílias de baixa renda. Equipe 2TDSPR: Cassio Ribeiro (RM 567295), "
                 "Davi Isac Colin Pereira (RM 567265), Hugo Souza de Jesus (RM 568542), Matheus Peres Moraes de Jesus "
                 "(RM 567300), Pedro Gonçalves Rodrigues (RM 567651).</purpose>")
    lines.append("</archimate:model>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    (out / "GranaAmiga-Arquitetura.archimate").write_text(build_xml(), encoding="utf-8")
    (out / "modelo.json").write_text(json.dumps({"E": E, "R": R, "VIEWS": VIEWS, "ROUTES": ROUTES},
                                                ensure_ascii=False), encoding="utf-8")
    n_rel = len(R)
    print(f"{len(E)} elementos, {n_rel} relacionamentos, {len(VIEWS)} visões -> {out}")
