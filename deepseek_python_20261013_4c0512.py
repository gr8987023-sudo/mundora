"""
================================================================================
 MUNDORA — RPG WORLD ENGINE & BESTIARY
 Versão: 1.0 (Edição Completa)
 Autor: Projeto integrado
 Descrição: Ferramenta de criação de mundos de RPG com bestiário visual,
            sistema de inventário completo, equipamento, loja, crafting,
            gemas, baú, XP, habilidades, combate simulado e histórico.
 Como rodar:
     1. pip install streamlit openai python-dotenv
     2. Crie um arquivo .env com OPENAI_API_KEY=sua_chave (opcional)
     3. streamlit run mundora.py
================================================================================
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime
from typing import Any

import streamlit as st
from dotenv import load_dotenv

try:
    from openai import OpenAI
    OPENAI_DISPONIVEL = True
except ImportError:
    OPENAI_DISPONIVEL = False

load_dotenv()

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
APP_NAME = "MUNDORA"
APP_SUBTITLE = "RPG WORLD ENGINE & BESTIARY"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

st.set_page_config(
    page_title=f"{APP_NAME} — {APP_SUBTITLE}",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# ESTILO VISUAL
# ==============================================================================
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
  :root { --bg:#0a0d12; --panel:#111720; --line:#253241; --text:#e8edf4; --accent:#8ce6d1; }
  html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
  .stApp { background: radial-gradient(ellipse at 75% -10%, rgba(70,105,145,.20), transparent 40%), var(--bg); color:var(--text); }
  [data-testid="stSidebar"] { background:#0b1017; border-right:1px solid #202b37; }
  h1,h2,h3 { letter-spacing:-.035em; }
  .hero { padding:1.5rem 1.65rem; border:1px solid #293748; background:linear-gradient(120deg,rgba(22,34,47,.96),rgba(14,21,31,.94)); border-radius:18px; margin-bottom:1.3rem; }
  .eyebrow { font-family:'DM Mono',monospace; color:var(--accent); font-size:.70rem; letter-spacing:.18em; text-transform:uppercase; }
  .stat { border:1px solid #283646; border-radius:13px; padding:14px 16px; background:rgba(17,23,32,.74); min-height:85px; }
  .stat-label { color:#8b9aab; font-size:.73rem; text-transform:uppercase; letter-spacing:.1em; font-family:'DM Mono',monospace; }
  .stat-value { color:#e8edf4; font-size:1.23rem; font-weight:800; margin-top:7px; }
  .note { border-left:2px solid #8ce6d1; padding:.55rem .85rem; color:#aab8c8; background:rgba(140,230,209,.045); font-size:.88rem; }
  .tiny { font-family:'DM Mono',monospace; color:#8b9aab; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; }
  .item-card { border:1px solid #293748; border-radius:12px; padding:12px; background:rgba(17,23,32,.74); margin-bottom:8px; }
  .item-Comum { border-left:4px solid #8b9aab; }
  .item-Incomum { border-left:4px solid #6dd47e; }
  .item-Raro { border-left:4px solid #6db8ff; }
  .item-Épico { border-left:4px solid #c08aff; }
  .item-Lendário { border-left:4px solid #ffb347; }
  .item-Mítico { border-left:4px solid #ff5e5e; }
  .item-name { font-weight:800; font-size:1rem; color:#e8edf4; }
  .item-meta { font-family:'DM Mono',monospace; font-size:.68rem; color:#8b9aab; text-transform:uppercase; letter-spacing:.08em; margin-top:4px; }
  .item-desc { color:#aab8c8; font-size:.85rem; margin-top:6px; }
  .gold-display { font-family:'DM Mono',monospace; color:#ffb347; font-size:1.1rem; font-weight:700; }
  .slot-empty { border:2px dashed #293748; border-radius:12px; padding:16px; text-align:center; color:#5c6a7a; font-family:'DM Mono',monospace; font-size:.75rem; }
  .slot-filled { border:2px solid #8ce6d1; border-radius:12px; padding:12px; background:rgba(140,230,209,.05); }
  .xp-bar { height:12px; background:#1a2330; border-radius:6px; overflow:hidden; margin-top:6px; }
  .xp-fill { height:100%; background:linear-gradient(90deg,#8ce6d1,#8aa9ff); }
  div.stButton > button { border-radius:10px; border:1px solid #536c7a; min-height:2.5rem; font-weight:700; }
  div.stButton > button[kind="primary"] { background:#8ce6d1; color:#07110f; border-color:#8ce6d1; }
  div.stButton > button[kind="secondary"] { background:#151e29; color:#e8edf4; }
  [data-baseweb="tab-list"] { gap:6px; }
  [data-baseweb="tab"] { background:#111720; border:1px solid #273342; border-radius:10px 10px 0 0; padding:8px 12px; }
  [data-baseweb="tab-highlight"] { background:#8ce6d1; }
  input, textarea { background:#111720 !important; }
  hr { border-color:#253241; }
  footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CONSTANTES DO JOGO
# ==============================================================================
GENRES = ["Fantasia sombria", "Fantasia heroica", "Ficção científica", "Cyberpunk",
          "Horror cósmico", "Pós-apocalíptico", "Solarpunk", "Steampunk",
          "Mitológico", "Mistura livre"]
TONES = ["Misterioso", "Aventureiro", "Melancólico", "Épico",
         "Leve e encantador", "Tenso e perigoso", "Satírico"]
SCALES = ["Uma cidade", "Uma região", "Um continente", "Um planeta",
          "Um sistema de mundos", "Um multiverso"]
NARRATION_STYLES = ["Clara e cinematográfica", "Crônica de explorador",
                    "Relatório de arquivo", "Lenda oral", "Diário pessoal",
                    "Narrador de mesa de RPG"]

MAP_DATA = {
    "Pisul": "Continente Central. Montanha com símbolo de olho no topo. Coração do mundo.",
    "Sibinis": "Ilha Ocidental. Florestas densas e névoa constante.",
    "Claic": "Ilha Ocidental. Árvores retorcidas e solo instável.",
    "Soline": "Ilha Oriental. Montanhas isoladas e laboratórios abandonados.",
    "Chiyia": "Região Norte. Passagem montanhosa fria, fronteira com terras geladas.",
    "Sodema": "Região Sul. Terras áridas e cheias de ruínas antigas.",
    "Terras Geladas (Vialist, Kind, Siam)": "Extremo norte. Regiões inóspitas e cheias de segredos.",
}

CREATURE_BANK = {
    "Aberração Biomecânica": {
        "visual": "Criatura orgânica-mecânica com um olho gigante, tentáculos e engrenagens. Estilo surrealista e biomecânico.",
        "habilidades": ["Golpe de Tentáculo", "Visão Analítica", "Reestruturação Biomolecular"],
        "habitat": "Florestas densas e ruínas de Claïc ou Sibinis.",
    },
    "Aberração Mutante": {
        "visual": "Evolução caótica, múltiplos olhos, armadura biomecânica assimétrica e tentáculos segmentados. Altamente instável.",
        "habilidades": ["Feixe Ocular Múltiplo", "Engrenagens Trituradoras", "Fúria Mutante"],
        "habitat": "Zonas de alta energia ou áreas contaminadas por experimentos antigos.",
    },
    "Sentinela Abissal": {
        "visual": "Entidade flutuante, armadura em zigue-zague, tentáculos laterais, olho central e base mecânica. Parece um totem cósmico.",
        "habilidades": ["Feixe Ocular Perfurante", "Chicote de Tentáculos Múltiplos", "Pulso de Engrenagens"],
        "habitat": "Pico da montanha central de Pisul, guardando ruínas antigas.",
    },
    "Fragmento Caótico": {
        "visual": "Artefato flutuante, lâminas afiadas, energia instável, partículas e mecanismos integrados.",
        "habilidades": ["Lâminas Flutuantes", "Explosão de Esporos", "Pulso de Energia Instável"],
        "habitat": "Pode ser encontrado ou invocado nas ruínas de Pisul.",
    },
    "Entidade N40": {
        "visual": "Mecha orgânico pesado, múltiplos módulos e máscaras, blindagem espessa e garras mecânicas. Catalogado como 'N40-identificado'.",
        "habilidades": ["Ataque em Área (360 Graus)", "Ativação de Escudo Frontal", "Descarga de Sobrecarga"],
        "habitat": "Laboratórios secretos na ilha isolada de Soline.",
    },
}

RARITIES = {
    "Comum":    {"mult": 1.0,  "peso": 45, "cor": "#8b9aab"},
    "Incomum":  {"mult": 1.6,  "peso": 25, "cor": "#6dd47e"},
    "Raro":     {"mult": 2.8,  "peso": 15, "cor": "#6db8ff"},
    "Épico":    {"mult": 4.5,  "peso": 9,  "cor": "#c08aff"},
    "Lendário": {"mult": 8.0,  "peso": 5,  "cor": "#ffb347"},
    "Mítico":   {"mult": 15.0, "peso": 1,  "cor": "#ff5e5e"},
}

ITEM_CATEGORIES = ["Arma", "Armadura", "Escudo", "Elmo", "Botas", "Anel",
                   "Amuleto", "Consumível", "Artefato", "Ferramenta",
                   "Material", "Gema", "Relíquia", "Outro"]

EQUIPMENT_SLOTS = ["Arma", "Armadura", "Escudo", "Elmo", "Botas", "Anel", "Amuleto"]

ITEM_TEMPLATES = {
    "Arma": [
        ("Lâmina de Eco", "Corta através de ilusões.", 45, "+8 ATK"),
        ("Rifle de Plasma N40", "Rajadas de energia instável.", 80, "+14 ATK"),
        ("Garra Biomecânica", "Aumenta dano corpo a corpo.", 60, "+10 ATK"),
        ("Cajado do Olho", "Amplifica magia.", 70, "+12 MAG"),
    ],
    "Armadura": [
        ("Placas em Zigue-Zague", "Reduz dano físico em 40%.", 55, "+12 DEF"),
        ("Manto da Névoa", "Aumenta evasão em florestas.", 40, "+6 DEF, +4 EVA"),
    ],
    "Escudo": [("Broquel de Soline", "Bloqueia projéteis.", 50, "+10 DEF")],
    "Elmo": [("Máscara do Observador", "Visão no escuro.", 45, "+4 DEF, +2 PER")],
    "Botas": [("Grevas de Explorador", "Movimento silencioso.", 35, "+3 DEF, +3 VEL")],
    "Anel": [("Anel de Ferro-Vivo", "Regenera 1 HP por turno.", 90, "+2 REGEN")],
    "Amuleto": [("Amuleto do Limiar", "Resiste a maldições.", 75, "+5 RES")],
    "Consumível": [
        ("Poção de Restauração", "Recupera 50 de HP.", 25, "Cura 50 HP"),
        ("Elixir de Fúria", "+30% dano por 3 turnos.", 35, "Buff ATK"),
        ("Ração de Explorador", "Recupera 15 de HP.", 10, "Cura 15 HP"),
        ("Antídoto Biomecânico", "Remove efeitos de corrupção.", 20, "Remove debuff"),
    ],
    "Artefato": [
        ("Fragmento Caótico", "Dano massivo instável.", 200, "+30 ATK (risco)"),
        ("Bússola de Ecos", "Aponta para a verdade mais próxima.", 90, "+5 PER"),
        ("Chave de Duas Sombras", "Abre portas que não existem de dia.", 120, "Acesso especial"),
    ],
    "Ferramenta": [
        ("Kit de Arrombamento", "Abre fechaduras mecânicas.", 30, "+8 LAD"),
        ("Lanterna de Sal Lunar", "Revela criaturas invisíveis.", 40, "Detecção"),
    ],
    "Material": [
        ("Sal Lunar", "Ingrediente para rituais.", 15, "-"),
        ("Ferro de Túmulo", "Absorve memórias.", 25, "-"),
        ("Âmbar de Sonho", "Armazena sonhos.", 20, "-"),
    ],
    "Gema": [
        ("Rubi de Fogo", "Encaixa em armas.", 100, "+5 ATK"),
        ("Safira Gélida", "Encaixa em armaduras.", 100, "+5 DEF"),
        ("Esmeralda Vital", "Encaixa em acessórios.", 120, "+5 HP máx"),
    ],
    "Relíquia": [
        ("Olho de Pisul", "Revela segredos das ruínas.", 300, "+10 PER"),
        ("Coração de Soline", "Núcleo de energia dos N40.", 250, "+15 ENERGIA"),
    ],
    "Outro": [
        ("Mapa Rasgado", "Mostra uma rota parcial.", 5, "-"),
        ("Amuleto Desconhecido", "Efeito ainda não identificado.", 50, "?"),
    ],
}

BASE_STATS = {
    "HP Máx": 100, "HP Atual": 100,
    "Mana Máx": 50, "Mana Atual": 50,
    "ATK": 10, "DEF": 5, "MAG": 5, "VEL": 5,
    "PER": 5, "RES": 5, "LAD": 3, "REGEN": 0, "ENERGIA": 50,
}

XP_PER_LEVEL = 100

SKILL_TREE = {
    "Golpe Poderoso": {"custo": 1, "tipo": "ATK", "efeito": "+5 ATK permanente", "requisito": None},
    "Pele de Ferro":  {"custo": 1, "tipo": "DEF", "efeito": "+5 DEF permanente", "requisito": None},
    "Mente Afiada":   {"custo": 1, "tipo": "MAG", "efeito": "+5 MAG permanente", "requisito": None},
    "Passo Leve":     {"custo": 1, "tipo": "VEL", "efeito": "+5 VEL permanente", "requisito": None},
    "Olho de Águia":  {"custo": 1, "tipo": "PER", "efeito": "+5 PER permanente", "requisito": None},
    "Regeneração":    {"custo": 2, "tipo": "REGEN", "efeito": "+2 REGEN por turno", "requisito": "Pele de Ferro"},
    "Mestre do Caos": {"custo": 3, "tipo": "ATK", "efeito": "+15 ATK permanente", "requisito": "Golpe Poderoso"},
}

# ==============================================================================
# FUNÇÕES DE ITEM
# ==============================================================================
def get_item_template(cat: str):
    return random.choice(ITEM_TEMPLATES.get(cat, ITEM_TEMPLATES["Outro"]))

def create_item(name, category, rarity="Comum", description="", quantity=1,
                value=0, effect="", durability=100):
    return {
        "id": f"{datetime.now().timestamp()}_{random.randint(1000,9999)}",
        "name": name, "category": category, "rarity": rarity,
        "description": description, "quantity": quantity,
        "value": value, "effect": effect, "equipped": False,
        "durability": durability, "max_durability": durability,
        "sockets": [], "enchantments": [],
    }

def generate_random_item():
    cat = random.choice(ITEM_CATEGORIES)
    name, desc, base, eff = get_item_template(cat)
    rar = random.choices(list(RARITIES.keys()),
                         weights=[RARITIES[r]["peso"] for r in RARITIES], k=1)[0]
    val = int(base * RARITIES[rar]["mult"])
    return create_item(name, cat, rar, desc, 1, val, eff)

def generate_gem():
    g = random.choice(ITEM_TEMPLATES["Gema"])
    return create_item(g[0], "Gema", "Raro", g[1], 1, g[2], g[3])

# ==============================================================================
# ESTADO GLOBAL
# ==============================================================================
def ensure_state():
    defaults = {
        "library": [], "last_world": "", "last_title": "",
        "last_mode": "Gerador local", "last_kind": "Mundo",
        "gold": 500, "inventory_capacity": 60,
        "inventory": [
            create_item("Poção de Restauração", "Consumível", "Comum",
                        "Cura 50 HP.", 3, 25, "Cura 50 HP"),
            create_item("Lâmina de Eco", "Arma", "Incomum",
                        "Corta através de ilusões.", 1, 72, "+8 ATK"),
            create_item("Placas em Zigue-Zague", "Armadura", "Raro",
                        "Reduz dano físico em 40%.", 1, 154, "+12 DEF"),
        ],
        "equipped": {slot: None for slot in EQUIPMENT_SLOTS},
        "stash": [],
        "stats": dict(BASE_STATS),
        "level": 1, "xp": 0, "xp_next": XP_PER_LEVEL,
        "skill_points": 3, "unlocked_skills": [],
        "history": [],
        "shop_stock": [generate_random_item() for _ in range(6)],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_state()

# ==============================================================================
# SISTEMAS AUXILIARES
# ==============================================================================
def add_xp(amount: int):
    st.session_state.xp += amount
    while st.session_state.xp >= st.session_state.xp_next:
        st.session_state.xp -= st.session_state.xp_next
        st.session_state.level += 1
        st.session_state.skill_points += 1
        st.session_state.xp_next = int(XP_PER_LEVEL * (1 + st.session_state.level * 0.4))
        st.session_state.stats["HP Máx"] += 10
        st.session_state.stats["HP Atual"] = st.session_state.stats["HP Máx"]
        st.session_state.stats["Mana Máx"] += 5
        st.session_state.stats["Mana Atual"] = st.session_state.stats["Mana Máx"]

def log_history(action: str, detail: str):
    st.session_state.history.insert(0, {
        "ação": action, "detalhe": detail,
        "data": datetime.now().strftime("%d/%m %H:%M"),
    })

def save_to_library(title, content, category, mode):
    st.session_state.library.insert(0, {
        "title": title, "content": content, "category": category,
        "mode": mode, "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })

def _pick(bank, key):
    return random.choice(bank.get(key, ["?"]))

# ==============================================================================
# GERADORES LOCAIS
# ==============================================================================
WORLD_SEEDS = {
    "Fantasia sombria": {
        "titles": ["As Terras do Último Sino", "O Reino sob a Cinza", "Véu de Sal e Ossos"],
        "landscape": ["florestas que sussurram nomes esquecidos", "pântanos cobertos por lanternas azuis"],
        "wonder": ["promessas podem ser ouvidas pelos mortos"],
        "resource": ["sal lunar", "ferro de túmulo"],
        "threat": ["uma praga apaga o nome das pessoas"],
        "hub": ["Vigília Baixa", "Porto das Velas"],
    },
    "Ficção científica": {
        "titles": ["Órbita de Ébano", "O Protocolo Ícaro"],
        "landscape": ["colônias construídas dentro de asteroides ocos"],
        "wonder": ["memórias podem ser transmitidas entre corpos"],
        "resource": ["hélio-3", "núcleos de dobra"],
        "threat": ["uma estação envia mensagens com data de amanhã"],
        "hub": ["Estação Miragem", "Nova Ceres"],
    },
    "Cyberpunk": {
        "titles": ["Neon de Baixa Maré", "Distrito Fantasma"],
        "landscape": ["megablocos iluminados por anúncios holográficos"],
        "wonder": ["identidades digitais podem ganhar autonomia"],
        "resource": ["chips de identidade"],
        "threat": ["uma atualização apagará a identidade de milhares"],
        "hub": ["Baixa Aurora", "Setor 17"],
    },
}

GENERIC_BANK = {
    "titles": ["O Atlas das Possibilidades"], "landscape": ["planícies mutáveis"],
    "wonder": ["as leis do mundo mudam"], "resource": ["fragmentos de origem"],
    "threat": ["uma fronteira se expande"], "hub": ["Ponte do Nexo"],
}

VARIATION_TWISTS = [
    "A região mais segura passa a ser a mais imprevisível.",
    "Uma cultura considerada extinta retorna com conhecimento incompreensível.",
    "O principal recurso do mundo começa a desaparecer.",
    "A passagem do tempo é diferente em duas regiões vizinhas.",
    "Uma facção rival tenta resolver o conflito por meios pacíficos.",
    "As lendas locais são registros históricos editados.",
    "O clima reage às decisões de uma comunidade específica.",
    "Uma rota conhecida conecta-se a um mundo com regras diferentes.",
]

def local_world(data):
    genre = data["genre"]
    bank = WORLD_SEEDS.get(genre, GENERIC_BANK)
    title = data.get("name", "").strip() or _pick(bank, "titles")
    map_regions = "\n".join([f"- **{k}:** {v}" for k, v in MAP_DATA.items()])
    return f"""# {title}

## 1. Visão geral
{title} é um cenário de {genre.lower()}, marcado por {_pick(bank, 'landscape')}. Tom {data['tone'].lower()}.

## 2. Geografia do Mundo (Baseado no Mapa)
{map_regions}

## 3. Identidade
- **Escala:** {data['scale']}
- **Local de partida:** {_pick(bank, 'hub')}
- **Recurso valioso:** {_pick(bank, 'resource')}

## 4. Conflito principal
O perigo surge quando {_pick(bank, 'threat')}.

## 5. Gancho de aventura
Um mensageiro chega com um mapa que mostra uma rota inexistente para Pisul.
"""

def local_variant(data):
    return f"""# Variação — {data.get('name')}

**Mudança principal:** {random.choice(VARIATION_TWISTS)}
**Foco:** {data.get('focus')}
"""

def local_asset(data):
    kind = data["kind"]
    if kind == "Criatura":
        n = data.get("name", "").strip() or random.choice(list(CREATURE_BANK.keys()))
        c = CREATURE_BANK.get(n, list(CREATURE_BANK.values())[0])
        return f"""# Criatura: {n}

**Visual:** {c['visual']}
**Habilidades:** {', '.join(c['habilidades'])}
**Habitat:** {c['habitat']}
"""
    if kind == "Personagem":
        n = data.get("name", "").strip() or "NEX-07"
        return f"""# Personagem: {n}

**Arquétipo:** {data.get('archetype', 'Aliado ambíguo')}
**Visual:** {data.get('visual_style', 'Tecno-orgânico')}
**Origem:** {data.get('origin', 'desconhecida')}
"""
    if kind == "Item especial":
        n = data.get("name", "").strip() or "Artefato Desconhecido"
        return f"""# Item Especial: {n}

**Raridade:** {data.get('rarity', 'Comum')}
**Efeito:** {data.get('effect', 'Nenhum')}
"""
    return f"# {kind}: {data.get('name', 'Elemento')}\n\n**Contexto:** {data.get('context', 'mundo em transformação')}\n"

AI_INSTRUCTIONS = """Você é MUNDORA, IA de design de mundos e RPG. Responda em português claro,
organizado e criativo. Crie conteúdo original, priorize consistência interna e ferramentas práticas para o narrador."""

def generate_with_ai(task, data, api_key, model):
    if not OPENAI_DISPONIVEL:
        raise RuntimeError("Biblioteca openai não instalada.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": AI_INSTRUCTIONS},
            {"role": "user", "content": f"Tarefa: {task}\n\nParâmetros:\n{json.dumps(data, ensure_ascii=False, indent=2)}"},
        ],
        max_tokens=2400,
    )
    return response.choices[0].message.content.strip()

def run_generation(task, data, local_fn, api_key, model, prefer_ai):
    if prefer_ai and api_key:
        try:
            return generate_with_ai(task, data, api_key, model), "IA conectada", None
        except Exception as exc:
            return local_fn(data), "Modo local (reserva)", f"IA não respondeu: {type(exc).__name__}."
    return local_fn(data), "Gerador local", None

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(f"<div class='eyebrow'>{APP_NAME} / LAB</div>", unsafe_allow_html=True)
    st.markdown("# 🌌 Mundora")
    st.caption("RPG World Engine completo")
    st.divider()

    stats = st.session_state.stats
    st.markdown(f"<div class='stat-label'>Nível {st.session_state.level}</div>", unsafe_allow_html=True)
    xp_pct = int((st.session_state.xp / st.session_state.xp_next) * 100) if st.session_state.xp_next else 0
    st.markdown(f"<div class='xp-bar'><div class='xp-fill' style='width:{xp_pct}%'></div></div>", unsafe_allow_html=True)
    st.caption(f"XP: {st.session_state.xp}/{st.session_state.xp_next}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='stat-label'>💰 Ouro</div><div class='gold-display'>{st.session_state.gold}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='stat-label'>🎒 Itens</div><div class='stat-value'>{len(st.session_state.inventory)}/{st.session_state.inventory_capacity}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='stat-label'>❤️ HP</div><div class='stat-value'>{stats['HP Atual']}/{stats['HP Máx']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-label'>✨ Pontos de Habilidade</div><div class='stat-value'>{st.session_state.skill_points}</div>", unsafe_allow_html=True)

    st.divider()
    api_key_input = st.text_input("Chave da API (opcional)", value="", type="password")
    api_key = api_key_input.strip() or os.getenv("OPENAI_API_KEY", "").strip()
    model_name = st.text_input("Modelo de IA", value=DEFAULT_MODEL)
    prefer_ai = st.toggle("Usar IA conectada", value=bool(api_key))
    if prefer_ai and api_key:
        st.success("IA conectada")
    else:
        st.info("Modo local")
    st.caption("v1.0 · Central Completa")

# ==============================================================================
# HEADER
# ==============================================================================
st.markdown(f"""<div class="hero"><div class="eyebrow">{APP_SUBTITLE}</div>
<h1>RPG World Engine · Edição Completa</h1>
<p>Crie mundos, gerencie inventário, equipe itens, evolua habilidades, negocie no mercado e muito mais.</p></div>""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"<div class='stat'><div class='stat-label'>Biblioteca</div><div class='stat-value'>{len(st.session_state.library)}</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='stat'><div class='stat-label'>Nível</div><div class='stat-value'>{st.session_state.level}</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='stat'><div class='stat-label'>Ouro</div><div class='stat-value'>{st.session_state.gold}</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='stat'><div class='stat-label'>Itens</div><div class='stat-value'>{len(st.session_state.inventory)}</div></div>", unsafe_allow_html=True)
with c5:
    eq_count = sum(1 for v in st.session_state.equipped.values() if v)
    st.markdown(f"<div class='stat'><div class='stat-label'>Equipados</div><div class='stat-value'>{eq_count}/7</div></div>", unsafe_allow_html=True)

st.write("")

# ==============================================================================
# ABAS PRINCIPAIS
# ==============================================================================
tabs = st.tabs(["✦ Mundo", "🗺️ Mapa", "⟳ Variar", "◇ Elementos", "🎒 Central de Itens", "📚 Biblioteca"])
tab_world, tab_map, tab_variant, tab_assets, tab_inventory, tab_library = tabs

# ------------------------ MUNDO ------------------------
with tab_world:
    st.markdown("## Defina a identidade do mundo")
    with st.form("world_form"):
        a, b = st.columns(2)
        with a:
            world_name = st.text_input("Nome do mundo (opcional)")
            genre = st.selectbox("Gênero", GENRES)
            tone = st.selectbox("Tom narrativo", TONES)
            scale = st.selectbox("Escala", SCALES, index=2)
        with b:
            narrative = st.selectbox("Voz da narração", NARRATION_STYLES)
            magic = st.slider("Magia / tecnologia", 1, 5, 3)
            intensity = st.slider("Intensidade de perigo", 1, 5, 3)
            themes = st.text_input("Temas centrais")
        seed = st.text_area("Detalhe especial (opcional)", height=80)
        submit = st.form_submit_button("✦ Gerar mundo", type="primary", use_container_width=True)

    if submit:
        data = {"name": world_name, "genre": genre, "tone": tone, "scale": scale,
                "narration_style": narrative, "magic": magic, "intensity": intensity,
                "themes": themes, "seed_detail": seed}
        with st.spinner("Gerando..."):
            result, mode, warning = run_generation("Criar mundo", data, local_world, api_key, model_name, prefer_ai)
        if warning:
            st.warning(warning)
        st.session_state.last_world = result
        st.session_state.last_kind = "Mundo"
        save_to_library(world_name or genre, result, "Mundo", mode)
        add_xp(20)
        log_history("Mundo criado", world_name or genre)
        st.success(f"Mundo gerado · {mode} · +20 XP")

    if st.session_state.last_world:
        st.divider()
        st.markdown(st.session_state.last_world)
        st.download_button("Baixar (.md)", data=st.session_state.last_world,
                          file_name="mundo.md", mime="text/markdown", use_container_width=True)

# ------------------------ MAPA ------------------------
with tab_map:
    st.markdown("## 🗺️ Geografia de MUNDORA")
    col1, col2 = st.columns([1, 2])
    with col1:
        for r, d in MAP_DATA.items():
            st.markdown(f"**{r}**")
            st.caption(d)
    with col2:
        st.info("O símbolo de olho em Pisul é o principal mistério do mundo.")
        st.markdown("### Ganchos de Exploração")
        st.markdown("- **Pisul:** Descobrir o que o Olho observa.\n- **Soline:** Investigar laboratórios N40.\n- **Sibinis:** Sobreviver às florestas.\n- **Sodema:** Encontrar artefatos antigos.")

# ------------------------ VARIAR ------------------------
with tab_variant:
    st.markdown("## Variação de realidade")
    with st.form("var_form"):
        vn = st.text_input("Nome da variação")
        bw = st.text_area("Mundo-base", value=st.session_state.last_world[:6000] if st.session_state.last_world else "", height=180)
        cf = st.selectbox("Foco", ["Equilibrada", "Ambiente", "Magia/tech", "Política", "História alternativa", "Sobrevivência"])
        vd = st.text_input("O que experimentar?")
        sv = st.form_submit_button("⟳ Gerar variação", type="primary", use_container_width=True)
    if sv:
        data = {"name": vn or "Linha alternativa", "base": bw, "focus": cf, "detail": vd}
        with st.spinner("Calculando divergências..."):
            result, mode, warning = run_generation("Variação", data, local_variant, api_key, model_name, prefer_ai)
        if warning:
            st.warning(warning)
        save_to_library(data["name"], result, "Variação", mode)
        add_xp(15)
        log_history("Variação", data["name"])
        st.success(f"Criada · {mode} · +15 XP")
        st.markdown(result)

# ------------------------ ELEMENTOS ------------------------
with tab_assets:
    st.markdown("## Expanda seu cenário")
    with st.form("asset_form"):
        kind = st.selectbox("O que criar?", ["Missão", "Personagem", "Facção", "Cidade", "Criatura", "Item especial", "Cena de abertura"])
        context = st.text_area("Contexto", value=st.session_state.last_world[:1500] if st.session_state.last_world else "", height=120)
        opts = {}
        if kind == "Personagem":
            ca, cb = st.columns(2)
            with ca:
                opts["name"] = st.text_input("Nome")
                opts["archetype"] = st.selectbox("Arquétipo", ["Aliado ambíguo", "Companheiro", "Rival", "Guardião", "Inventor"])
                opts["visual_style"] = st.selectbox("Visual", ["Tecno-orgânico", "Robótico", "Alienígena", "Fantasia sombria"])
            with cb:
                opts["origin"] = st.text_input("Origem")
                opts["signature_ability"] = st.text_input("Habilidade")
                opts["flaw"] = st.text_input("Limitação")
        elif kind == "Criatura":
            cl = ["Aleatório"] + list(CREATURE_BANK.keys())
            sc = st.selectbox("Criatura base", cl)
            if sc != "Aleatório":
                opts["name"] = sc
                st.info(f"**Visual:** {CREATURE_BANK[sc]['visual']}")
        elif kind == "Item especial":
            ic1, ic2 = st.columns(2)
            with ic1:
                opts["item_name"] = st.text_input("Nome do item")
                opts["item_category"] = st.selectbox("Categoria", ITEM_CATEGORIES, index=8)
            with ic2:
                opts["item_rarity"] = st.selectbox("Raridade", list(RARITIES.keys()), index=1)
                opts["item_value"] = st.number_input("Valor (ouro)", 0, 1000, 50, 10)
            opts["item_effect"] = st.text_input("Efeito")
            opts["add_to_inventory"] = st.checkbox("Adicionar ao inventário", value=True)
        req = st.text_input("Requisitos adicionais")
        sa = st.form_submit_button("◇ Criar elemento", type="primary", use_container_width=True)

    if sa:
        data = {"kind": kind, "context": context, "requirements": req}
        if kind == "Item especial":
            n = opts.get("item_name", "").strip()
            cat = opts.get("item_category", "Artefato")
            rar = opts.get("item_rarity", "Comum")
            val = opts.get("item_value", 50)
            eff = opts.get("item_effect", "")
            if not n:
                n, desc, base, eff2 = get_item_template(cat)
                val = int(base * RARITIES[rar]["mult"])
                eff = eff2
            data.update({"name": n, "category": cat, "rarity": rar, "value": val, "effect": eff})
            if opts.get("add_to_inventory"):
                if len(st.session_state.inventory) < st.session_state.inventory_capacity:
                    st.session_state.inventory.append(create_item(n, cat, rar, eff, 1, val, eff))
                    st.success(f"'{n}' adicionado ao inventário!")
                    log_history("Item criado", n)
                else:
                    st.warning("Inventário cheio!")
        if kind in ["Personagem", "Criatura"]:
            data.update(opts)
            if kind == "Criatura" and not opts.get("name"):
                data["name"] = random.choice(list(CREATURE_BANK.keys()))
        with st.spinner(f"Gerando {kind.lower()}..."):
            result, mode, warning = run_generation(kind, data, local_asset, api_key, model_name, prefer_ai)
        if warning:
            st.warning(warning)
        save_to_library(f"{kind} — {datetime.now().strftime('%d/%m %H:%M')}", result, kind, mode)
        add_xp(10)
        st.success(f"Criado · {mode} · +10 XP")
        st.markdown(result)

# ==============================================================================
# CENTRAL DE ITENS COMPLETA
# ==============================================================================
with tab_inventory:
    st.markdown("## 🎒 Central de Itens")
    st.caption("Equipamento, loja, crafting, baú, gemas, estatísticas, habilidades e histórico.")

    inv_tabs = st.tabs([
        "📦 Inventário", "⚔️ Equipamento", "🏪 Loja", "⚒️ Crafting",
        "🔐 Baú", "💎 Gemas", "📊 Personagem", "🌟 Habilidades", "📜 Histórico",
    ])
    (t_inv, t_equip, t_shop, t_craft,
     t_stash, t_gems, t_stats, t_skills, t_hist) = inv_tabs

    # ---------------- INVENTÁRIO ----------------
    with t_inv:
        st.markdown("### Ações Rápidas")
        a1, a2, a3, a4, a5 = st.columns(5)
        with a1:
            if st.button("🎲 Item Aleatório", use_container_width=True):
                if len(st.session_state.inventory) < st.session_state.inventory_capacity:
                    it = generate_random_item()
                    st.session_state.inventory.append(it)
                    log_history("Item gerado", it["name"])
                    st.rerun()
                else:
                    st.error("Inventário cheio.")
        with a2:
            if st.button("💰 +50 Ouro", use_container_width=True):
                st.session_state.gold += 50
                log_history("Ouro", "+50")
                st.rerun()
        with a3:
            if st.button("📦 Expandir (+10)", use_container_width=True):
                if st.session_state.gold >= 100:
                    st.session_state.gold -= 100
                    st.session_state.inventory_capacity += 10
                    log_history("Capacidade", "+10 slots")
                    st.rerun()
                else:
                    st.error("Ouro insuficiente (custa 100).")
        with a4:
            if st.button("🎁 Loot x3", use_container_width=True):
                for _ in range(3):
                    if len(st.session_state.inventory) < st.session_state.inventory_capacity:
                        st.session_state.inventory.append(generate_random_item())
                add_xp(15)
                log_history("Loot", "+3 itens")
                st.rerun()
        with a5:
            if st.button("🗑️ Limpar Inventário", use_container_width=True):
                st.session_state.inventory = []
                log_history("Limpeza", "Inventário esvaziado")
                st.rerun()

        with st.expander("➕ Adicionar Item Manualmente"):
            with st.form("add_man"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    nm = st.text_input("Nome")
                    ct = st.selectbox("Categoria", ITEM_CATEGORIES)
                with c2:
                    rr = st.selectbox("Raridade", list(RARITIES.keys()))
                    qt = st.number_input("Quantidade", 1, 99, 1)
                with c3:
                    vv = st.number_input("Valor unitário", 0, 9999, 10)
                    ef = st.text_input("Efeito")
                sm = st.form_submit_button("Adicionar ao inventário", type="primary", use_container_width=True)
            if sm and nm:
                st.session_state.inventory.append(create_item(nm, ct, rr, ef, qt, vv, ef))
                log_history("Item manual", nm)
                st.rerun()

        if st.session_state.inventory:
            st.markdown("### Seus Itens")
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                fc = st.selectbox("Categoria", ["Todas"] + ITEM_CATEGORIES)
            with f2:
                fr = st.selectbox("Raridade", ["Todas"] + list(RARITIES.keys()))
            with f3:
                fs = st.selectbox("Ordenar", ["Nome", "Raridade", "Valor", "Durabilidade"])
            with f4:
                fq = st.text_input("Buscar por nome")

            fl = st.session_state.inventory.copy()
            if fc != "Todas":
                fl = [i for i in fl if i["category"] == fc]
            if fr != "Todas":
                fl = [i for i in fl if i["rarity"] == fr]
            if fq:
                fl = [i for i in fl if fq.lower() in i["name"].lower()]
            ro = list(RARITIES.keys())
            if fs == "Nome":
                fl.sort(key=lambda x: x["name"])
            elif fs == "Raridade":
                fl.sort(key=lambda x: ro.index(x["rarity"]), reverse=True)
            elif fs == "Valor":
                fl.sort(key=lambda x: x["value"], reverse=True)
            elif fs == "Durabilidade":
                fl.sort(key=lambda x: x["durability"])

            st.caption(f"Exibindo {len(fl)} de {len(st.session_state.inventory)} itens")

            cols = st.columns(3)
            for idx, item in enumerate(fl):
                with cols[idx % 3]:
                    rc = item["rarity"]
                    eq = " ⚔️" if item.get("equipped") else ""
                    dur_pct = int((item["durability"] / item["max_durability"]) * 100) if item["max_durability"] else 100
                    st.markdown(f"""<div class="item-card item-{rc}">
                    <div class="item-name">{item['name']}{eq}</div>
                    <div class="item-meta">{item['category']} · {rc} · x{item['quantity']} · {item['value']}💰 · 🛠 {dur_pct}%</div>
                    <div class="item-desc">{item.get('effect') or item.get('description') or '-'}</div>
                    </div>""", unsafe_allow_html=True)

                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if item["category"] in EQUIPMENT_SLOTS:
                            if item.get("equipped"):
                                if st.button("Desc.", key=f"u_{item['id']}", use_container_width=True):
                                    st.session_state.equipped[item["category"]] = None
                                    item["equipped"] = False
                                    st.rerun()
                            else:
                                if st.button("Equip.", key=f"e_{item['id']}", use_container_width=True):
                                    slot = item["category"]
                                    old = st.session_state.equipped.get(slot)
                                    if old:
                                        old["equipped"] = False
                                    st.session_state.equipped[slot] = item
                                    item["equipped"] = True
                                    log_history("Equipou", item["name"])
                                    st.rerun()
                    with b2:
                        if item["category"] == "Consumível":
                            if st.button("Usar", key=f"c_{item['id']}", use_container_width=True):
                                if item["quantity"] > 1:
                                    item["quantity"] -= 1
                                else:
                                    st.session_state.inventory.remove(item)
                                log_history("Usou", item["name"])
                                st.rerun()
                    with b3:
                        if st.button("Vender", key=f"s_{item['id']}", use_container_width=True):
                            sp = int(item["value"] * 0.5)
                            st.session_state.gold += sp * item["quantity"]
                            st.session_state.inventory.remove(item)
                            log_history("Vendeu", f"{item['name']} por {sp * item['quantity']}")
                            st.rerun()

            st.divider()
            st.download_button(
                "📥 Exportar Inventário (.json)",
                data=json.dumps({"gold": st.session_state.gold, "items": st.session_state.inventory},
                                ensure_ascii=False, indent=2),
                file_name="inventario.json", mime="application/json", use_container_width=True,
            )
        else:
            st.markdown("<div class='note'>Inventário vazio. Gere itens ou adicione manualmente.</div>", unsafe_allow_html=True)

    # ---------------- EQUIPAMENTO ----------------
    with t_equip:
        st.markdown("### ⚔️ Slots de Equipamento")
        st.caption("Os efeitos dos itens equipados são somados às suas estatísticas.")

        cols = st.columns(4)
        for i, slot in enumerate(EQUIPMENT_SLOTS):
            with cols[i % 4]:
                it = st.session_state.equipped.get(slot)
                if it:
                    st.markdown(f"""<div class="slot-filled">
                    <div class="item-meta">{slot}</div>
                    <div class="item-name">{it['name']}</div>
                    <div class="item-desc">{it.get('effect', '-')}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Desequipar", key=f"ds_{slot}", use_container_width=True):
                        it["equipped"] = False
                        st.session_state.equipped[slot] = None
                        log_history("Desequipou", it["name"])
                        st.rerun()
                else:
                    st.markdown(f"""<div class="slot-empty">◯ {slot}<br>vazio</div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### Resumo de Efeitos")
        effects = [f"- **{s}**: {it['name']} → {it.get('effect', '-')}"
                   for s, it in st.session_state.equipped.items() if it]
        st.markdown("\n".join(effects) if effects else "_Nenhum item equipado._")

    # ---------------- LOJA ----------------
    with t_shop:
        st.markdown("### 🏪 Loja de Itens")
        st.caption("Compre itens com ouro. Estoque renovável.")

        sc1, sc2 = st.columns([1, 3])
        with sc1:
            if st.button("🔄 Renovar Estoque (20💰)", use_container_width=True):
                if st.session_state.gold >= 20:
                    st.session_state.gold -= 20
                    st.session_state.shop_stock = [generate_random_item() for _ in range(6)]
                    st.rerun()
                else:
                    st.error("Ouro insuficiente.")
            if st.button("🎲 Compra Rápida Aleatória", use_container_width=True):
                it = generate_random_item()
                if st.session_state.gold >= it["value"]:
                    st.session_state.gold -= it["value"]
                    if len(st.session_state.inventory) < st.session_state.inventory_capacity:
                        st.session_state.inventory.append(it)
                        log_history("Comprou", it["name"])
                        st.success(f"Comprou {it['name']} por {it['value']}💰")
                        st.rerun()
                else:
                    st.error("Ouro insuficiente.")

        st.divider()
        if not st.session_state.shop_stock:
            st.session_state.shop_stock = [generate_random_item() for _ in range(6)]

        st.markdown("#### Itens à Venda")
        cols = st.columns(3)
        for idx, item in enumerate(st.session_state.shop_stock):
            with cols[idx % 3]:
                rc = item["rarity"]
                st.markdown(f"""<div class="item-card item-{rc}">
                <div class="item-name">{item['name']}</div>
                <div class="item-meta">{item['category']} · {rc} · {item['value']}💰</div>
                <div class="item-desc">{item.get('effect', '-')}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Comprar ({item['value']}💰)", key=f"buy_{item['id']}", use_container_width=True):
                    if st.session_state.gold >= item["value"]:
                        if len(st.session_state.inventory) < st.session_state.inventory_capacity:
                            st.session_state.gold -= item["value"]
                            st.session_state.inventory.append(item)
                            st.session_state.shop_stock.remove(item)
                            log_history("Comprou", item["name"])
                            st.rerun()
                        else:
                            st.error("Inventário cheio.")
                    else:
                        st.error("Ouro insuficiente.")

    # ---------------- CRAFTING ----------------
    with t_craft:
        st.markdown("### ⚒️ Crafting (Forja)")
        st.caption("Combine 3 itens do inventário para tentar criar algo melhor. O resultado depende da raridade dos materiais.")

        if len(st.session_state.inventory) >= 3:
            st.markdown("#### Selecione 3 itens para combinar")
            names = [f"{i['name']} ({i['rarity']}) #{i['id'][-4:]}" for i in st.session_state.inventory]
            sel1 = st.selectbox("Material 1", names, key="cr1")
            sel2 = st.selectbox("Material 2", names, key="cr2")
            sel3 = st.selectbox("Material 3", names, key="cr3")

            if st.button("🔥 Fundir Itens", type="primary", use_container_width=True):
                i1 = st.session_state.inventory[names.index(sel1)]
                i2 = st.session_state.inventory[names.index(sel2)]
                i3 = st.session_state.inventory[names.index(sel3)]
                if len({i1["id"], i2["id"], i3["id"]}) < 3:
                    st.error("Selecione itens diferentes!")
                else:
                    total_val = i1["value"] + i2["value"] + i3["value"]
                    rp = list(RARITIES.keys())
                    max_rar = max(rp.index(i1["rarity"]), rp.index(i2["rarity"]), rp.index(i3["rarity"]))
                    new_rar_idx = min(len(rp) - 1, max_rar + random.choice([0, 1, 1, 2]))
                    new_rar = rp[new_rar_idx]
                    base = random.choice(ITEM_TEMPLATES["Artefato"] + ITEM_TEMPLATES["Arma"] + ITEM_TEMPLATES["Armadura"])
                    new_name = f"{base[0]} Fundido"
                    new_item = create_item(new_name, random.choice(["Arma", "Armadura", "Artefato"]),
                                           new_rar, "Item criado por fusão.", 1, total_val,
                                           "+12 ATK/DEF", durability=90)
                    for mat in [i1, i2, i3]:
                        if mat in st.session_state.inventory:
                            st.session_state.inventory.remove(mat)
                    st.session_state.inventory.append(new_item)
                    add_xp(25)
                    log_history("Craftou", new_name)
                    st.success(f"🔥 Criado: **{new_name}** ({new_rar})")
                    st.rerun()
        else:
            st.warning("Você precisa de pelo menos 3 itens para craftar.")

        st.divider()
        st.markdown("#### Encantamentos")
        st.caption("Adicione +5 em uma estatística a um item equipado, consumindo 50 de ouro.")
        eq_names = [f"{it['name']} ({slot})" for slot, it in st.session_state.equipped.items() if it]
        if eq_names:
            chosen = st.selectbox("Item para encantar", eq_names, key="ench_sel")
            ench_stat = st.selectbox("Estatística", ["ATK", "DEF", "MAG", "VEL", "PER", "RES"])
            if st.button("✨ Encantar (+5)", use_container_width=True):
                if st.session_state.gold >= 50:
                    st.session_state.gold -= 50
                    slot = chosen.split("(")[1].rstrip(")")
                    it = st.session_state.equipped[slot]
                    it["enchantments"].append(f"+5 {ench_stat}")
                    it["effect"] = (it.get("effect", "") + f" | +5 {ench_stat}").strip(" |")
                    log_history("Encantou", f"{it['name']} +5 {ench_stat}")
                    st.success(f"{it['name']} encantado com +5 {ench_stat}!")
                    st.rerun()
                else:
                    st.error("Ouro insuficiente.")
        else:
            st.info("Equipe um item para poder encantá-lo.")

    # ---------------- BAÚ ----------------
    with t_stash:
        st.markdown("### 🔐 Baú / Armazém")
        st.caption("Itens no baú não ocupam espaço no inventário.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Inventário: {len(st.session_state.inventory)} itens**")
            if st.session_state.inventory:
                item_names = [f"{i['name']} ({i['rarity']}) #{i['id'][-4:]}" for i in st.session_state.inventory]
                sel = st.selectbox("Mover para o baú", item_names, key="stash_in")
                if st.button("→ Enviar para o Baú", use_container_width=True):
                    it = st.session_state.inventory[item_names.index(sel)]
                    st.session_state.inventory.remove(it)
                    st.session_state.stash.append(it)
                    log_history("Baú", f"Guardou {it['name']}")
                    st.rerun()

        with c2:
            st.markdown(f"**Baú: {len(st.session_state.stash)} itens**")
            if st.session_state.stash:
                stash_names = [f"{i['name']} ({i['rarity']}) #{i['id'][-4:]}" for i in st.session_state.stash]
                sel2 = st.selectbox("Retirar do baú", stash_names, key="stash_out")
                if st.button("← Retirar do Baú", use_container_width=True):
                    if len(st.session_state.inventory) < st.session_state.inventory_capacity:
                        it = st.session_state.stash[stash_names.index(sel2)]
                        st.session_state.stash.remove(it)
                        st.session_state.inventory.append(it)
                        log_history("Baú", f"Retirou {it['name']}")
                        st.rerun()
                    else:
                        st.error("Inventário cheio.")

        st.divider()
        if st.session_state.stash:
            st.markdown("#### Conteúdo do Baú")
            cols = st.columns(3)
            for idx, item in enumerate(st.session_state.stash):
                with cols[idx % 3]:
                    st.markdown(f"""<div class="item-card item-{item['rarity']}">
                    <div class="item-name">{item['name']}</div>
                    <div class="item-meta">{item['category']} · {item['rarity']}</div>
                    <div class="item-desc">{item.get('effect', '-')}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Baú vazio.")

    # ---------------- GEMAS ----------------
    with t_gems:
        st.markdown("### 💎 Gemas e Sockets")
        st.caption("Encaixe gemas em itens equipados para adicionar bônus permanentes.")

        if st.button("🎲 Gerar Gema Aleatória (30💰)", use_container_width=True):
            if st.session_state.gold >= 30:
                st.session_state.gold -= 30
                gem = generate_gem()
                st.session_state.inventory.append(gem)
                log_history("Gema", f"Gerou {gem['name']}")
                st.success(f"Gerou {gem['name']}")
                st.rerun()
            else:
                st.error("Ouro insuficiente.")

        gems_in_inv = [i for i in st.session_state.inventory if i["category"] == "Gema"]
        if gems_in_inv:
            st.markdown("#### Suas Gemas")
            for g in gems_in_inv:
                st.markdown(f"- **{g['name']}** ({g['rarity']}) → {g.get('effect', '-')}")

        st.divider()
        st.markdown("#### Encaixar Gema em Item Equipado")
        eq_list = [f"{it['name']} ({slot})" for slot, it in st.session_state.equipped.items() if it]
        if gems_in_inv and eq_list:
            gem_sel = st.selectbox("Gema", [f"{g['name']} ({g['effect']}) #{g['id'][-4:]}" for g in gems_in_inv], key="gem_sel")
            item_sel = st.selectbox("Item equipado", eq_list, key="gem_item")
            if st.button("💎 Encaixar", type="primary", use_container_width=True):
                gem = gems_in_inv[[f"{g['name']} ({g['effect']}) #{g['id'][-4:]}" for g in gems_in_inv].index(gem_sel)]
                slot = item_sel.split("(")[1].rstrip(")")
                item = st.session_state.equipped[slot]
                item["sockets"].append(gem["name"])
                item["effect"] = (item.get("effect", "") + f" | 💎{gem['effect']}").strip(" |")
                st.session_state.inventory.remove(gem)
                log_history("Encaixou", f"{gem['name']} em {item['name']}")
                st.success(f"Gema encaixada em {item['name']}!")
                st.rerun()
        else:
            st.info("Você precisa de uma gema e um item equipado.")

    # ---------------- PERSONAGEM ----------------
    with t_stats:
        st.markdown("### 📊 Ficha do Personagem")
        stats = st.session_state.stats

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"#### Nível {st.session_state.level}")
            st.markdown(f"XP: {st.session_state.xp}/{st.session_state.xp_next}")
            st.markdown(f"Pontos de Habilidade: **{st.session_state.skill_points}**")
        with c2:
            st.markdown("#### Recursos")
            st.markdown(f"❤️ HP: **{stats['HP Atual']}/{stats['HP Máx']}**")
            st.markdown(f"✨ Mana: **{stats['Mana Atual']}/{stats['Mana Máx']}**")
            st.markdown(f"⚡ Energia: **{stats['ENERGIA']}**")
        with c3:
            st.markdown("#### Combate")
            st.markdown(f"⚔️ ATK: **{stats['ATK']}**")
            st.markdown(f"🛡 DEF: **{stats['DEF']}**")
            st.markdown(f"🔮 MAG: **{stats['MAG']}**")
            st.markdown(f"💨 VEL: **{stats['VEL']}**")
            st.markdown(f"👁 PER: **{stats['PER']}**")
            st.markdown(f"🌀 RES: **{stats['RES']}**")
            st.markdown(f"🥷 LAD: **{stats['LAD']}**")
            st.markdown(f"💚 REGEN: **{stats['REGEN']}**")

        st.divider()
        st.markdown("#### Simulador de Combate Rápido")
        if st.button("⚔️ Simular Combate", use_container_width=True):
            enemy_hp = random.randint(30, 80) + st.session_state.level * 10
            enemy_atk = random.randint(5, 15) + st.session_state.level * 2
            player_hp = stats["HP Atual"]
            rounds = 0
            log = []
            while player_hp > 0 and enemy_hp > 0 and rounds < 20:
                rounds += 1
                dmg = max(1, stats["ATK"] - random.randint(0, enemy_atk // 2))
                enemy_hp -= dmg
                log.append(f"R{rounds}: Você causou {dmg} de dano. (Inimigo: {max(0, enemy_hp)} HP)")
                if enemy_hp <= 0:
                    break
                edmg = max(1, enemy_atk - stats["DEF"] // 2)
                player_hp -= edmg
                log.append(f"R{rounds}: Inimigo causou {edmg} de dano. (Você: {max(0, player_hp)} HP)")
            if enemy_hp <= 0:
                gold_gain = random.randint(20, 60)
                xp_gain = random.randint(15, 40)
                st.session_state.gold += gold_gain
                add_xp(xp_gain)
                log_history("Combate", f"Vitória! +{gold_gain}💰 +{xp_gain}XP")
                st.success(f"🏆 Vitória em {rounds} turnos! +{gold_gain}💰 +{xp_gain}XP")
            else:
                st.error(f"💀 Derrota após {rounds} turnos.")
            with st.expander("Ver log do combate"):
                st.markdown("\n".join(log))

        if st.button("🔄 Restaurar HP/Mana (50💰)", use_container_width=True):
            if st.session_state.gold >= 50:
                st.session_state.gold -= 50
                stats["HP Atual"] = stats["HP Máx"]
                stats["Mana Atual"] = stats["Mana Máx"]
                log_history("Descanso", "HP/Mana restaurados")
                st.success("Restaurado!")
                st.rerun()
            else:
                st.error("Ouro insuficiente.")

    # ---------------- HABILIDADES ----------------
    with t_skills:
        st.markdown("### 🌟 Árvore de Habilidades")
        st.markdown(f"**Pontos disponíveis: {st.session_state.skill_points}**")

        for skill_name, info in SKILL_TREE.items():
            unlocked = skill_name in st.session_state.unlocked_skills
            req = info.get("requisito")
            req_ok = (req is None) or (req in st.session_state.unlocked_skills)
            can_unlock = (not unlocked) and req_ok and st.session_state.skill_points >= info["custo"]

            c1, c2 = st.columns([3, 1])
            with c1:
                if unlocked:
                    status = "✅ Desbloqueada"
                elif not req_ok:
                    status = f"🔒 Requer: {req}"
                else:
                    status = "🟢 Disponível"
                st.markdown(f"**{skill_name}** — *{info['efeito']}* (custo: {info['custo']} pts)")
                st.caption(status)
            with c2:
                if unlocked:
                    st.success("Ativa")
                elif can_unlock:
                    if st.button("Desbloquear", key=f"sk_{skill_name}", use_container_width=True):
                        st.session_state.skill_points -= info["custo"]
                        st.session_state.unlocked_skills.append(skill_name)
                        k = info["tipo"]
                        if k == "ATK":
                            st.session_state.stats["ATK"] += 5
                        elif k == "DEF":
                            st.session_state.stats["DEF"] += 5
                        elif k == "MAG":
                            st.session_state.stats["MAG"] += 5
                        elif k == "VEL":
                            st.session_state.stats["VEL"] += 5
                        elif k == "PER":
                            st.session_state.stats["PER"] += 5
                        elif k == "REGEN":
                            st.session_state.stats["REGEN"] += 2
                        log_history("Skill", f"Desbloqueou {skill_name}")
                        st.rerun()
                else:
                    st.button("Bloqueada", disabled=True, key=f"skb_{skill_name}", use_container_width=True)

    # ---------------- HISTÓRICO ----------------
    with t_hist:
        st.markdown("### 📜 Histórico de Ações")
        if st.session_state.history:
            for h in st.session_state.history[:50]:
                st.markdown(f"- **[{h['data']}]** {h['ação']}: {h['detalhe']}")
        else:
            st.info("Nenhuma ação registrada.")
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.history = []
            st.rerun()

# ==============================================================================
# BIBLIOTECA
# ==============================================================================
with tab_library:
    st.markdown("## Biblioteca da sessão")
    lib = st.session_state.library
    if not lib:
        st.markdown("<div class='note'>Biblioteca vazia.</div>", unsafe_allow_html=True)
    else:
        opts = [f"{i+1:02d} · {x['category']} · {x['title']}" for i, x in enumerate(lib)]
        sel = st.selectbox("Selecionar", range(len(opts)), format_func=lambda i: opts[i])
        st.markdown(lib[sel]["content"])
        j = json.dumps(lib, ensure_ascii=False, indent=2)
        combined = "\n\n---\n\n".join([f"# {x['title']}\n\n{x['content']}" for x in lib])
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("Exportar (.json)", data=j, file_name="biblioteca.json", mime="application/json", use_container_width=True)
        with d2:
            st.download_button("Exportar (.md)", data=combined, file_name="biblioteca.md", mime="text/markdown", use_container_width=True)
        if st.button("Limpar biblioteca"):
            st.session_state.library = []
            st.rerun()

# ==============================================================================
# FOOTER
# ==============================================================================
st.divider()
st.markdown("<div class='tiny'>MUNDORA · RPG WORLD ENGINE & BESTIARY · v1.0 COMPLETO</div>", unsafe_allow_html=True)