import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Panthus Pro", layout="wide", page_icon="🦁")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
<style>
    /* Fundo principal e textos */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Títulos e Subtítulos */
    h1, h2, h3 {
        color: #FFD700 !important; /* Dourado Panthus */
        font-weight: 700;
    }

    /* Estilização dos CARDS de Preço */
    [data-testid="stMetric"] {
        background-color: #1A1C23;
        border: 2px solid #FFD700;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* Valores de Preço dentro do card */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 28px !important;
    }

    /* Rótulo da Meta (%) */
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important;
        font-size: 16px !important;
        font-weight: bold;
    }
    
    /* Delta (Lucro R$) */
    [data-testid="stMetricDelta"] {
        background-color: #2D2F36;
        border-radius: 5px;
        padding: 2px 5px;
    }

    /* Inputs de dados */
    .stNumberInput label {
        color: #FFD700 !important;
        font-weight: bold;
    }

    /* Divisores */
    hr {
        border-top: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "panthus2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("## 🔒 Área Restrita - Panthus Pro")
    st.text_input("Digite sua chave de acesso:", type="password", key="password", on_change=password_entered)
    if "password_correct" in st.session_state:
        st.error("🚫 Chave incorreta.")
    return False

if not check_password():
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🦁 Panthus: Precificação Reversa (PRO)")
st.markdown("---")

st.subheader("⚙️ Configurações do Produto")
col_a, col_b, col_c = st.columns(3)

with col_a:
    custo = st.number_input("Custo do Produto (R$)", min_value=0.01, value=50.00, step=1.00)
with col_b:
    peso = st.number_input("Peso (kg)", min_value=0.001, value=0.500, step=0.100, format="%.3f")
with col_c:
    imposto_perc = st.number_input("Imposto (%)", min_value=0.0, value=8.5, step=0.5) / 100

st.markdown("---")

# --- MOTOR DE CÁLCULO (Oculto no Visual) ---
def calcular_lucro_real(venda_teste, custo, peso, imposto_perc, marketplace):
    comm = 0.0
    frete = 0.0
    
    if marketplace == "Shopee":
        rate = 0.14
        if venda_teste <= 79.99: rate=0.20; fixed=4.00
        elif venda_teste <= 99.99: fixed=16.00
        elif venda_teste <= 199.99: fixed=20.00
        else: fixed=26.00
        comm = (venda_teste * rate) + fixed
        
    elif marketplace == "Mercado Livre":
        rate = 0.19
        fixed = 0.0
        if venda_teste < 79:
            if venda_teste < 12.50: fixed = venda_teste/2
            elif venda_teste < 29: fixed = 6.25
            elif venda_teste < 50: fixed = 6.50
            else: fixed = 6.75
        comm = (venda_teste * rate) + fixed
        if venda_teste >= 79:
            if peso <= 0.3: frete = 17.90
            elif peso <= 0.5: frete = 18.90
            elif peso <= 1.0: frete = 20.90
            elif peso <= 2.0: frete = 22.90
            elif peso <= 5.0: frete = 27.90
            else: frete = 45.90
    
    # ... (Demais regras simplificadas para performance)
    elif marketplace == "Shein": comm = venda_teste * 0.16; frete = 4.0 if peso < 0.3 else 5.0
    elif marketplace == "TikTok": comm = (venda_teste * 0.06) + 4.00; frete = venda_teste * 0.06
    elif marketplace == "Magalu": comm = (venda_teste * 0.18) + (3.0 if venda_teste < 79 else 0); frete = 19.90 if venda_teste >= 79 else 0
    elif marketplace == "Americanas": comm = venda_teste * 0.19; frete = 18.90 if venda_teste >= 79 else 0

    imposto_val = venda_teste * imposto_perc
    total_custos = custo + comm + frete + imposto_val
    lucro_liquido = venda_teste - total_custos
    margem_real = (lucro_liquido / venda_teste) if venda_teste > 0 else 0
    return margem_real, lucro_liquido

def encontrar_preco_ideal(target_margin, custo, peso, imposto_perc, marketplace):
    preco_teste = custo * 1.2
    for _ in range(4000):
        m, l = calcular_lucro_real(preco_teste, custo, peso, imposto_perc, marketplace)
        if m < target_margin: preco_teste += 0.50
        else: return preco_teste, l
    return 0.0, 0.0

# --- EXIBIÇÃO ---
marketplaces = ["Mercado Livre", "Shopee", "Shein", "TikTok", "Magalu", "Americanas"]
margens_alvo = [0.05, 0.15, 0.30, 0.50]

for mkt in marketplaces:
    st.markdown(f"### {mkt}")
    cols = st.columns(4)
    for i, alvo in enumerate(margens_alvo):
        p, l = encontrar_preco_ideal(alvo, custo, peso, imposto_perc, mkt)
        with cols[i]:
            if p > 0:
                st.metric(label=f"META {alvo*100:.0f}%", value=f"R$ {p:.2f}", delta=f"LUCRO R$ {l:.2f}")
            else:
                st.error("N/A")
    st.markdown("<br>", unsafe_allow_html=True)

if st.button("Sair / Logout"):
    st.session_state["password_correct"] = False
    st.rerun
