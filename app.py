import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha) ---
st.set_page_config(page_title="Panthus Pro", layout="wide", page_icon="🦁")

# --- SISTEMA DE LOGIN SIMPLES ---
def check_password():
    """Retorna True se o usuário tiver a senha correta."""
    
    def password_entered():
        """Checa se a senha inserida bate com a correta."""
        if st.session_state["password"] == "panthus2026": # <--- SUA SENHA AQUI
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não armazena a senha
        else:
            st.session_state["password_correct"] = False

    # Verifica se já está logado
    if st.session_state.get("password_correct", False):
        return True

    # Interface de Login
    st.markdown("## 🔒 Área Restrita - Panthus Pro")
    st.text_input(
        "Digite sua chave de acesso:", 
        type="password", 
        key="password", 
        on_change=password_entered
    )
    
    if "password_correct" in st.session_state:
        st.error("🚫 Chave incorreta. Tente novamente ou assine o plano.")
        st.markdown("[Clique aqui para Assinar por R$ 19,90](https://kiwify.com.br/SEU_LINK)") # <--- SEU LINK DE VENDA
        
    return False

if not check_password():
    st.stop()  # Para o código aqui se não tiver senha

# =========================================================
# DAQUI PARA BAIXO É O SEU CÓDIGO DA CALCULADORA (SÓ RODA SE LOGADO)
# =========================================================

st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #dcdcdc; }
</style>
""", unsafe_allow_html=True)

st.title("🦁 Panthus: Precificação Reversa (PRO)")
st.markdown("---")

# --- BARRA LATERAL (ENTRADAS) ---
with st.sidebar:
    st.header("1. Dados do Produto")
    custo = st.number_input("Custo do Produto (R$)", min_value=0.01, value=50.00, step=1.00)
    peso = st.number_input("Peso (kg)", min_value=0.001, value=0.500, step=0.100, format="%.3f")
    imposto_perc = st.number_input("Sua Taxa de Imposto (%)", min_value=0.0, value=8.5, step=0.5) / 100
    
    st.markdown("---")
    if st.button("Sair / Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- MOTOR DE CÁLCULO ---
def calcular_lucro_real(venda_teste, custo, peso, imposto_perc, marketplace):
    comm = 0.0
    frete = 0.0
    
    # 1. SHOPEE (CNPJ 2026)
    if marketplace == "Shopee":
        rate = 0.14
        fixed = 0.0
        if venda_teste <= 79.99: rate=0.20; fixed=4.00
        elif venda_teste <= 99.99: fixed=16.00
        elif venda_teste <= 199.99: fixed=20.00
        else: fixed=26.00
        comm = (venda_teste * rate) + fixed
        frete = 0.0 
        
    # 2. MERCADO LIVRE (Premium)
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

    # 3. SHEIN (Taxa Corretagem)
    elif marketplace == "Shein":
        comm = venda_teste * 0.16
        if peso <= 0.3: frete = 4.00
        elif peso <= 2.0: frete = 5.00
        elif peso <= 5.0: frete = 15.00
        else: frete = 32.00

    # 4. TIKTOK (6% + 4.00)
    elif marketplace == "TikTok":
        comm = (venda_teste * 0.06) + 4.00
        frete = venda_teste * 0.06 
            
    # 5. MAGALU (Semanal)
    elif marketplace == "Magalu":
        rate = 0.18
        fixed = 3.00 if (10 <= venda_teste < 79) else 0.0
        comm = (venda_teste * rate) + fixed
        if venda_teste >= 79:
            if peso <= 0.5: frete = 19.90
            elif peso <= 1.0: frete = 21.90
            elif peso <= 2.0: frete = 23.90
            else: frete = 25.90

    # 6. AMERICANAS (19%)
    elif marketplace == "Americanas":
        comm = venda_teste * 0.19
        if venda_teste >= 79:
            if peso <= 0.5: frete = 18.90
            elif peso <= 1.0: frete = 20.90
            elif peso <= 2.0: frete = 22.90
            else: frete = 24.90

    imposto_val = venda_teste * imposto_perc
    total_custos = custo + comm + frete + imposto_val
    lucro_liquido = venda_teste - total_custos
    margem_real = (lucro_liquido / venda_teste) if venda_teste > 0 else 0
    
    return margem_real, lucro_liquido

def encontrar_preco_ideal(target_margin, custo, peso, imposto_perc, marketplace):
    preco_teste = custo * 1.2
    step = 0.50 
    for _ in range(2000):
        margem_atual, lucro = calcular_lucro_real(preco_teste, custo, peso, imposto_perc, marketplace)
        if margem_atual < target_margin:
            preco_teste += step
        elif margem_atual >= target_margin:
            return preco_teste, lucro
    return 0.0, 0.0

# --- INTERFACE PRINCIPAL ---
marketplaces = ["Mercado Livre", "Shopee", "Shein", "TikTok", "Magalu", "Americanas"]
margens_alvo = [0.05, 0.10, 0.15, 0.50] 

tab1, tab2 = st.tabs(["💰 Sugestão de Preços", "📊 Simulação Livre"])

with tab1:
    st.subheader("Sugestão de Preço para atingir a Margem Líquida")
    st.write(f"Custo: R$ {custo} | Peso: {peso}kg | Imposto: {imposto_perc*100}%")
    for mkt in marketplaces:
        st.markdown(f"### {mkt}")
        cols = st.columns(4)
        for i, alvo in enumerate(margens_alvo):
            preco_sugerido, lucro_real = encontrar_preco_ideal(alvo, custo, peso, imposto_perc, mkt)
            with cols[i]:
                if preco_sugerido > 0:
                    st.metric(label=f"Meta: {alvo*100:.0f}%", value=f"R$ {preco_sugerido:.2f}", delta=f"Lucro: R$ {lucro_real:.2f}")
                else:
                    st.error("Inviável")
        st.divider()

with tab2:
    st.write("Simule um preço de venda específico.")
    venda_livre = st.number_input("Preço de Venda (R$)", value=custo*2)
    if st.button("Calcular"):
        res_data = []
        for mkt in marketplaces:
            m, l = calcular_lucro_real(venda_livre, custo, peso, imposto_perc, mkt)
            res_data.append({"Plataforma": mkt, "Margem %": f"{m*100:.2f}%", "Lucro R$": f"R$ {l:.2f}", "Status": "✅" if l > 0 else "🔻"})
        st.table(pd.DataFrame(res_data))
