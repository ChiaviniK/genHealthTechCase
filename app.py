import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- Configuração da Página (Modo Kiosk) ---
st.set_page_config(page_title="Smart Triage - Hospital Santa Clara", page_icon="🏥", layout="centered")

# --- CSS para parecer um Totem Hospitalar ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 12px;
    }
    .big-font {
        font-size: 30px !important;
        font-weight: bold;
    }
    .stAlert {
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho ---
st.image("https://img.icons8.com/color/96/hospital-2.png", width=80)
st.title("Triagem Inteligente")
st.markdown("Bem-vindo ao Hospital Santa Clara. Por favor, preencha seus dados.")
st.progress(0)

# --- Formulário do Paciente (Simulação de Sensores + Input) ---
with st.form("triagem_form"):
    st.subheader("1. Identificação")
    nome = st.text_input("Nome Completo")
    idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
    
    st.markdown("---")
    st.subheader("2. Sinais Vitais (Simulado pelos Sensores do Totem)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        temp = st.slider("🌡️ Temperatura (°C)", 34.0, 42.0, 36.5)
    with col2:
        sat = st.slider("🫁 Saturação O2 (%)", 70, 100, 98)
    with col3:
        bpm = st.number_input("❤️ Batimentos (BPM)", 40, 200, 80)

    st.markdown("---")
    st.subheader("3. O que você está sentindo?")
    sintomas = st.text_area("Descreva seus sintomas (Ex: dor no peito, falta de ar...)", height=100)
    
    submit = st.form_submit_button("ANALISAR GRAVIDADE 🚑")

# --- O "Back-End" simulado no Front (Onde o aluno entra) ---
if submit:
    if not nome or not sintomas:
        st.error("Por favor, preencha nome e sintomas.")
    else:
        with st.spinner('A Inteligência Artificial está analisando seu caso...'):
            time.sleep(2) # Drama time
            
            # --- LÓGICA QUE O ALUNO DEVE DESENVOLVER (Aqui está simplificada) ---
            cor_pulseira = "Azul"
            msg = "Atendimento Não Urgente"
            
            # Regra simples de palavras-chave (NLP Básico)
            sintomas_lower = sintomas.lower()
            if "peito" in sintomas_lower or "ar" in sintomas_lower or "desmaio" in sintomas_lower:
                cor_pulseira = "Vermelho"
            elif temp >= 39 or sat < 90:
                cor_pulseira = "Laranja"
            elif temp >= 37.8 or bpm > 110:
                cor_pulseira = "Amarelo"
            else:
                cor_pulseira = "Verde"
            
            # --- Resultado na Tela ---
            st.markdown("---")
            st.markdown(f"<p class='big-font'>Classificação: <span style='color:{cor_pulseira};'>{cor_pulseira.upper()}</span></p>", unsafe_allow_html=True)
            
            if cor_pulseira == "Vermelho":
                st.error("🚨 DIRIGIA-SE IMEDIATAMENTE À SALA DE EMERGÊNCIA 01.")
            elif cor_pulseira == "Laranja":
                st.warning("⚠️ Atendimento Prioritário. Aguarde na Recepção A.")
            else:
                st.success("✅ Aguarde ser chamado pelo painel. Tempo estimado: 40 min.")
                
            # Exibir JSON para o aluno entender o que deve salvar no Banco
            st.markdown("---")
            st.caption("🔧 Dados enviados ao Servidor (Back-end):")
            st.json({
                "paciente": nome, 
                "sintomas": sintomas, 
                "vitals": {"temp": temp, "o2": sat, "bpm": bpm},
                "timestamp": datetime.now().isoformat(),
                "triagem_ia": cor_pulseira
            })
