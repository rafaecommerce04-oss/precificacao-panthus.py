import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre no topo)
st.set_page_config(page_title="Panthus Pro", layout="wide", page_icon="🦁")

# 2. ESTILO PANTHUS PRO (CSS para esconder menus e mudar cores)
st.markdown("""
<style>
    /* Esconde botões de Deploy, Menu Hambúrguer e Rodapé */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Fundo Escuro e Texto Branco */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Títulos em Dourado */
    h1, h2, h3 {
        color: #FFD700 !important;
        font-weight: 700;
    }

    /* Cards de Preço Profissionais */
    [data-testid="stMetric"] {
        background-color: #1A1C23;
        border: 2px solid #FFD700;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* Valores e Labels dentro dos cards */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #FFD700 !important; font-size: 16px !important; font-weight: bold; }
    
    /* Labels dos Inputs */
    .stNumberInput label { color: #FFD700 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. SISTEMA DE LOGIN
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

# 4. INTERFACE E INPUTS
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

# 5. REGRAS DE CÁLCULO
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
    preco_teste = custo * 1.1
    for _ in range(4000):
        m, l = calcular_lucro_real(preco_teste, custo, peso, imposto_perc, marketplace)
        if m < target_margin: preco_teste += 0.50
        else: return preco_teste, l
    return 0.0, 0.0

# 6. EXIBIÇÃO DOS RESULTADOS
marketplaces = ["Mercado Livre", "Shopee", "Shein", "TikTok", "Magalu", "Americanas"]
margens_alvo = [0.05, 0.15, 0.30]

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
    st.rerun()
