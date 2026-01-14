import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta

# --- Configuração da Página ---
st.set_page_config(page_title="Smart Triage & Admin", page_icon="🏥", layout="wide")

# --- CSS Personalizado ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; }
    .big-font { font-size: 24px !important; font-weight: bold; }
    .reportview-container { background: #f0f2f6 }
    .success-box { padding: 1rem; background-color: #d4edda; border-color: #c3e6cb; color: #155724; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 1. GERAÇÃO DE DADOS (Simulando o Banco Legado) ---
@st.cache_data
def gerar_dados_iniciais():
    num_pacientes = 500 
    data_base = datetime.now() - timedelta(days=30)
    
    nomes = ['Joao', 'Maria', 'Jose', 'Ana', 'Pedro', 'Carla', 'Lucas', 'Julia', 'Marcos', 'Fernanda']
    sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Almeida']
    sintomas_txt = ["dor no peito", "corte no dedo", "enxaqueca", "febre alta", "unha encravada", "dor abdominal", "acidente moto", "falta de ar"]
    
    dados = []
    for i in range(num_pacientes):
        dt = data_base + timedelta(minutes=random.randint(0, 43200))
        temp = np.round(np.random.normal(37, 1.5), 1)
        if random.random() < 0.03: temp = 0.0 # Erro proposital
        
        dados.append({
            'id_atendimento': 1000 + i,
            'data_hora': dt.strftime("%Y-%m-%d %H:%M:%S"),
            'nome_paciente': f"{random.choice(nomes)} {random.choice(sobrenomes)}",
            'idade': random.randint(18, 90),
            'queixa': random.choice(sintomas_txt),
            'temp': temp,
            'saturacao': random.randint(85, 100),
            'bpm': random.randint(50, 140),
            'pressao': random.choice(["12/8", "14/9", "18/10", "10/6"])
        })
    return pd.DataFrame(dados)

df_pacientes = gerar_dados_iniciais()

# --- 2. FUNÇÕES GERADORAS DE SQL ---

def gerar_sql_create_table():
    return """
CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

CREATE TABLE IF NOT EXISTS atendimentos (
    id_atendimento INT PRIMARY KEY,
    data_hora DATETIME,
    nome_paciente VARCHAR(100),
    idade INT,
    queixa TEXT,
    temp DECIMAL(4,1),
    saturacao INT,
    bpm INT,
    pressao VARCHAR(10)
);
    """

def gerar_sql_insert_bulk(df):
    inserts = []
    for index, row in df.iterrows():
        query = f"INSERT INTO atendimentos (id_atendimento, data_hora, nome_paciente, idade, queixa, temp, saturacao, bpm, pressao) VALUES ({row['id_atendimento']}, '{row['data_hora']}', '{row['nome_paciente']}', {row['idade']}, '{row['queixa']}', {row['temp']}, {row['saturacao']}, {row['bpm']}, '{row['pressao']}');"
        inserts.append(query)
    return "\n".join(inserts)

# --- INTERFACE DO STREAMLIT ---

menu = st.sidebar.radio("Navegação", ["🚑 Totem Triagem (Paciente)", "💾 Área TI & Dados (SQL)"])

if menu == "🚑 Totem Triagem (Paciente)":
    # --- TELA 1: O TOTEM DE AUTOATENDIMENTO ---
    col_img, col_title = st.columns([1, 5])
    with col_img: st.image("https://img.icons8.com/color/96/hospital-2.png", width=80)
    with col_title: st.title("Triagem Rápida")
    
    st.markdown("Preencha seus dados para classificação de risco.")
    
    with st.form("form_triagem"):
        col1, col2 = st.columns(2)
        with col1: nome = st.text_input("Nome Completo")
        with col2: idade = st.number_input("Idade", 1, 120, step=1)
        
        sintomas = st.text_area("O que você sente?")
        
        st.markdown("**Sinais Vitais (Leitura dos Sensores):**")
        c1, c2, c3, c4 = st.columns(4)
        temp_lida = c1.number_input("Temp (°C)", value=36.5, step=0.1)
        sat_lida = c2.number_input("Sat O2 (%)", value=98, step=1)
        bpm_lido = c3.number_input("BPM", value=80, step=1)
        pressao_lida = c4.text_input("Pressão", value="12/8")
        
        enviar = st.form_submit_button("Gerar Senha de Atendimento")
        
    if enviar:
        if not nome or not sintomas:
            st.error("Preencha todos os campos obrigatórios!")
        else:
            # Lógica de Classificação (Simulada)
            cor = "Verde"
            if temp_lida > 39 or sat_lida < 90: cor = "Vermelho"
            elif temp_lida > 37.5: cor = "Amarelo"
            
            # --- GERAÇÃO DO SQL INDIVIDUAL (AQUI ESTÁ A MUDANÇA) ---
            id_novo = random.randint(5000, 9999) # ID aleatório para o novo paciente
            timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Monta a string do comando SQL
            sql_individual = f"""INSERT INTO atendimentos (id_atendimento, data_hora, nome_paciente, idade, queixa, temp, saturacao, bpm, pressao) 
VALUES ({id_novo}, '{timestamp_now}', '{nome}', {idade}, '{sintomas}', {temp_lida}, {sat_lida}, {bpm_lido}, '{pressao_lida}');"""
            
            # Exibe Resultado
            st.markdown("---")
            st.success(f"✅ Triagem Concluída! Classificação sugerida: **{cor.upper()}**")
            
            col_res_1, col_res_2 = st.columns(2)
            
            with col_res_1:
                st.info("ℹ️ Copie o comando abaixo ou baixe o arquivo para inserir este paciente no seu Banco de Dados.")
                st.code(sql_individual, language="sql")
                
            with col_res_2:
                # Botão de Download do Registro Único
                st.download_button(
                    label="📥 Baixar SQL deste Paciente (.sql)",
                    data=sql_individual,
                    file_name=f"insert_paciente_{id_novo}.sql",
                    mime="text/plain"
                )

elif menu == "💾 Área TI & Dados (SQL)":
    # --- TELA 2: O DESAFIO DOS ALUNOS (GERAÇÃO DE SQL) ---
    st.title("📂 Central de Engenharia de Dados")
    st.markdown("""
    **Instruções para a Equipe de Dados:**
    Aqui você baixa a carga inicial (Histórico) para popular seu banco de dados.
    """)
    
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("1. Estrutura (DDL)")
        script_create = gerar_sql_create_table()
        st.download_button(
            label="📥 Baixar 1_create_database.sql",
            data=script_create,
            file_name="1_create_database.sql",
            mime="text/plain"
        )
        st.code(script_create, language="sql")

    with col_b:
        st.subheader("2. Carga Histórica (DML)")
        script_insert = gerar_sql_insert_bulk(df_pacientes)
        st.download_button(
            label="📥 Baixar 2_populate_data.sql",
            data=script_insert,
            file_name="2_populate_data.sql",
            mime="text/plain"
        )
        st.info(f"Contém {len(df_pacientes)} registros simulados.")

    st.markdown("---")
    if st.checkbox("🔍 Espiar dados brutos"):
        st.dataframe(df_pacientes)
