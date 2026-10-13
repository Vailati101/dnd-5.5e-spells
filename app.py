import streamlit as st
import requests

st.set_page_config(page_title="D&D Spellbook & Checker", page_icon="🪄", layout="wide")

# Lista de fontes de dados JSON do 5e.tools (PHB 2014 e PHB 2024/XPHB)
SOURCES = [
    {
        "url": "https://raw.githubusercontent.com/5etools-mirror-3/5etools-data/main/data/spells/spells-xphb.json",
        "edition": "D&D 5.5e (2024)",
        "code": "xphb"
    },
    {
        "url": "https://raw.githubusercontent.com/5etools-mirror-3/5etools-data/main/data/spells/spells-phb.json",
        "edition": "D&D 5e (2014)",
        "code": "phb"
    }
]

@st.cache_data
def carregar_magias():
    spells_data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for src in SOURCES:
        try:
            res = requests.get(src["url"], headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for s in data.get("spell", []):
                    s["edition"] = src["edition"]
                    s["source_code"] = src["code"]
                    spells_data.append(s)
        except Exception:
            pass
            
    return spells_data

if "grimorio" not in st.session_state:
    st.session_state.grimorio = set()

spells = carregar_magias()

st.title("🪄 D&D 5.5e Spellbook & Checker")
st.caption("Consulte magias e monte seu Grimório de magias preparadas para a sessão!")

aba_busca, aba_grimorio = st.tabs(["🔍 Buscar Magias", "📖 Meu Grimório (Preparadas)"])

with aba_busca:
    st.subheader("Todas as Magias")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        termo_busca = st.text_input("Digite o nome da magia:", placeholder="Ex: Acid Splash, Fireball...").lower().strip()
    with col2:
        filtro_edicao = st.selectbox("Edição:", ["Todas", "D&D 5.5e (2024)", "D&D 5e (2014)"])

    magias_filtradas = []
    for s in spells:
        nome_match = termo_busca in s.get("name", "").lower() if termo_busca else True
        edicao_match = (filtro_edicao == "Todas") or (s.get("edition") == filtro_edicao)
        if nome_match and edicao_match:
            magias_filtradas.append(s)

    st.write(f"Exibindo **{len(magias_filtradas)}** magia(s):")

    for spell in magias_filtradas[:50]:  # Limita a 50 para carregamento rápido na busca ampla
        nome = spell.get("name", "Sem Nome")
        edicao = spell.get("edition")
        nivel = spell.get("level", 0)
        nivel_txt = "Truque (Cantrip)" if nivel == 0 else f"Nível {nivel}"
        chave_unica = f"{nome}_{spell.get('source_code')}"

        with st.expander(f"✨ **{nome}** — *{nivel_txt}* [{edicao}]"):
            col_info, col_fav = st.columns([4, 1])
            
            with col_info:
                st.write(f"**Escola:** {str(spell.get('school', 'N/A')).upper()}")
                st.write(f"**Livro / Fonte:** {spell.get('source_code').upper()}")
                
                entries = spell.get("entries", [])
                for entry in entries:
                    if isinstance(entry, str):
                        st.write(entry)
            
            with col_fav:
                esta_no_grimorio = chave_unica in st.session_state.grimorio
                
                if esta_no_grimorio:
                    if st.button("❌ Remover", key=f"rem_{chave_unica}"):
                        st.session_state.grimorio.remove(chave_unica)
                        st.rerun()
                else:
                    if st.button("⭐ Preparar", key=f"add_{chave_unica}"):
                        st.session_state.grimorio.add(chave_unica)
                        st.rerun()

with aba_grimorio:
    st.subheader("📖 Magias Preparadas para o Dia")
    
    if not st.session_state.grimorio:
        st.info("Seu grimório está vazio. Vá na aba 'Buscar Magias' e marque com ⭐ as magias que deseja preparar!")
    else:
        st.success(f"Você tem **{len(st.session_state.grimorio)}** magia(s) preparada(s).")
        
        magias_preparadas = [s for s in spells if f"{s.get('name')}_{s.get('source_code')}" in st.session_state.grimorio]
        
        for spell in magias_preparadas:
            nome = spell.get("name")
            nivel = spell.get("level", 0)
            nivel_txt = "Truque (Cantrip)" if nivel == 0 else f"Nível {nivel}"
            chave_unica = f"{nome}_{spell.get('source_code')}"

            with st.expander(f"⭐ **{nome}** — *{nivel_txt}* [{spell.get('edition')}]"):
                st.write(f"**Escola:** {str(spell.get('school', 'N/A')).upper()}")
                entries = spell.get("entries", [])
                for entry in entries:
                    if isinstance(entry, str):
                        st.write(entry)
                
                if st.button("Despreparar", key=f"grim_rem_{chave_unica}"):
                    st.session_state.grimorio.remove(chave_unica)
                    st.rerun()
