import streamlit as st
import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta

# --- Configuração ---
st.set_page_config(page_title="HealthTech: Smart Triage", page_icon="🏥", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; height: 50px; }
    .success-box { padding: 1rem; background-color: #d4edda; color: #155724; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- GERAÇÃO DE DADOS (Carga Histórica) ---
@st.cache_data
def gerar_dados_iniciais():
    # ... (Mesma lógica de antes para gerar o CSV histórico bruto) ...
    num_pacientes = 500
    dados = []
    nomes = ['Ana', 'Bruno', 'Carlos', 'Diana', 'Eduardo', 'Fernanda']
    sintomas_lista = ["dor no peito", "febre", "dor de cabeça", "fratura exposta"]
    
    for i in range(num_pacientes):
        dados.append({
            'id': 1000 + i,
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 10000))).isoformat(),
            'paciente': {'nome': f"{random.choice(nomes)}", 'idade': random.randint(18, 90)},
            'sinais_vitais': {'temp': round(random.uniform(36, 40),1), 'sat_o2': random.randint(80, 100)},
            'sintomas': random.choice(sintomas_lista)
        })
    return pd.DataFrame(dados)

df_historico = gerar_dados_iniciais()

# --- MENU ---
menu = st.sidebar.radio("Sistema", ["🚑 Totem (Paciente)", "💾 API Gateway (JSONs)"])

if menu == "🚑 Totem (Paciente)":
    col1, col2 = st.columns([1, 5])
    with col1: st.image("https://img.icons8.com/color/96/hospital-2.png", width=70)
    with col2: st.title("Autoatendimento")
    
    st.info("ℹ️ Este terminal captura os dados e envia para a fila de processamento (JSON).")

    with st.form("form_triagem"):
        nome = st.text_input("Nome Completo")
        idade = st.number_input("Idade", 0, 120)
        queixa = st.text_area("Descreva o que sente")
        
        st.markdown("**Sensores:**")
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temp (°C)", 36.5)
        sat = c2.number_input("Sat O2 (%)", 98)
        bpm = c3.number_input("BPM", 80)
        
        enviar = st.form_submit_button("Enviar para Triagem")

    if enviar and nome:
        # --- O DESAFIO PLENO: GERAR JSON, NÃO SQL ---
        payload = {
            "protocolo_id": random.randint(10000, 99999),
            "timestamp_coleta": datetime.now().isoformat(),
            "paciente": {
                "nome_completo": nome,
                "idade": idade
            },
            "dados_clinicos": {
                "queixa_principal": queixa,
                "sinais_vitais": {
                    "temperatura": temp,
                    "saturacao_o2": sat,
                    "frequencia_cardiaca": bpm
                }
            },
            "origem": "Totem_01"
        }
        
        json_str = json.dumps(payload, indent=4, ensure_ascii=False)
        
        st.success("✅ Dados capturados e serializados!")
        st.warning("⚠️ O sistema de triagem (Backend Python) deve processar este arquivo.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.code(json_str, language="json")
        with col_b:
            st.download_button(
                label="📥 Baixar Payload (.json)",
                data=json_str,
                file_name=f"triagem_{payload['protocolo_id']}.json",
                mime="application/json",
                help="O aluno deve criar um script Python que leia este JSON e insira no Banco."
            )

elif menu == "💾 API Gateway (JSONs)":
    st.title("📂 Central de Integração")
    st.markdown("Baixe o **Lote Histórico (Batch)** para testar seu script de importação.")
    
    # Converte o dataframe histórico inteiro para um JSONzão
    json_batch = df_historico.to_json(orient="records", date_format="iso", indent=4)
    
    st.download_button(
        label="📥 Baixar Lote Histórico (2000 registros JSON)",
        data=json_batch,
        file_name="historico_batch_raw.json",
        mime="application/json",
        help="Use este arquivo para popular seu banco inicialmente."
    )
    
    st.markdown("---")
    st.subheader("Desafio Técnico (Pleno)")
    st.markdown("""
    1. Ler o arquivo JSON via Python (`json.load`).

    """)
