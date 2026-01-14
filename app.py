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
</style>
""", unsafe_allow_html=True)

# --- 1. GERAÇÃO DE DADOS (Simulando o Banco Legado) ---
# Função para criar os dados caso não existam (igual ao script anterior, mas embutido)
@st.cache_data
def gerar_dados_iniciais():
    num_pacientes = 500 # Reduzi para o SQL não ficar gigante no exemplo
    data_base = datetime.now() - timedelta(days=30)
    
    nomes = ['Joao', 'Maria', 'Jose', 'Ana', 'Pedro', 'Carla', 'Lucas', 'Julia', 'Marcos', 'Fernanda']
    sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Almeida']
    sintomas_txt = ["dor no peito", "corte no dedo", "enxaqueca", "febre alta", "unha encravada", "dor abdominal", "acidente moto", "falta de ar"]
    
    dados = []
    for i in range(num_pacientes):
        dt = data_base + timedelta(minutes=random.randint(0, 43200))
        temp = np.round(np.random.normal(37, 1.5), 1)
        # Inserindo erro de sensor (0.0)
        if random.random() < 0.03: temp = 0.0
        
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
    """Gera o script DDL para criar a tabela no Workbench"""
    sql = """
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
    return sql

def gerar_sql_insert(df):
    """Transforma o DataFrame em comandos INSERT INTO"""
    inserts = []
    for index, row in df.iterrows():
        # Tratamento de strings para SQL (aspas simples)
        nome = row['nome_paciente']
        queixa = row['queixa']
        data = row['data_hora']
        pressao = row['pressao']
        
        query = f"INSERT INTO atendimentos (id_atendimento, data_hora, nome_paciente, idade, queixa, temp, saturacao, bpm, pressao) VALUES ({row['id_atendimento']}, '{data}', '{nome}', {row['idade']}, '{queixa}', {row['temp']}, {row['saturacao']}, {row['bpm']}, '{pressao}');"
        inserts.append(query)
    
    return "\n".join(inserts)

# --- INTERFACE DO STREAMLIT ---

# Sidebar para Navegação
menu = st.sidebar.radio("Navegação", ["🚑 Totem Triagem (Paciente)", "💾 Área TI & Dados (SQL)"])

if menu == "🚑 Totem Triagem (Paciente)":
    # --- TELA 1: O TOTEM DE AUTOATENDIMENTO ---
    st.image("https://img.icons8.com/color/96/hospital-2.png", width=60)
    st.title("Triagem Rápida")
    st.markdown("Preencha seus dados para classificação de risco.")
    
    with st.form("form_triagem"):
        col1, col2 = st.columns(2)
        with col1: nome = st.text_input("Nome")
        with col2: idade = st.number_input("Idade", 1, 120)
        
        sintomas = st.text_area("O que você sente?")
        
        st.caption("Sensores lendo sinais vitais...")
        c1, c2, c3 = st.columns(3)
        temp_lida = c1.number_input("Temp (°C)", value=36.5)
        sat_lida = c2.number_input("Sat O2 (%)", value=98)
        bpm_lido = c3.number_input("BPM", value=80)
        
        enviar = st.form_submit_button("Gerar Senha de Atendimento")
        
    if enviar:
        st.success("✅ Aguarde ser chamado no painel.")
        st.info(f"Dados enviados para o banco de dados: {nome}, {sintomas}")

elif menu == "💾 Área TI & Dados (SQL)":
    # --- TELA 2: O DESAFIO DOS ALUNOS (GERAÇÃO DE SQL) ---
    st.title("📂 Central de Engenharia de Dados")
    st.markdown("""
    **Instruções para a Equipe de Dados:**
    1. Visualize os dados brutos gerados pelos totens abaixo.
    2. Baixe o script **`create_database.sql`** para criar a estrutura no MySQL Workbench.
    3. Baixe o script **`populate_data.sql`** para inserir os dados históricos.
    4. Conecte o Power BI ao seu Banco de Dados Local.
    """)
    
    st.markdown("---")
    st.subheader("1. Visualização dos Dados (Histórico)")
    
    # Checkbox para mostrar tabela
    if st.checkbox("🔍 Ver Tabela de Dados Brutos"):
        st.dataframe(df_pacientes, use_container_width=True)
        st.caption(f"Total de registros: {len(df_pacientes)}")

    st.markdown("---")
    st.subheader("2. Download dos Scripts SQL")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Botão para baixar o CREATE TABLE
        script_create = gerar_sql_create_table()
        st.download_button(
            label="📥 Baixar 1_create_database.sql",
            data=script_create,
            file_name="1_create_database.sql",
            mime="text/plain",
            help="Script DDL: Cria o Banco e a Tabela"
        )
        st.code(script_create, language="sql")

    with col_b:
        # Botão para baixar os INSERTS
        script_insert = gerar_sql_insert(df_pacientes)
        st.download_button(
            label="📥 Baixar 2_populate_data.sql",
            data=script_insert,
            file_name="2_populate_data.sql",
            mime="text/plain",
            help="Script DML: Insere todos os registros na tabela"
        )
        st.warning("⚠️ Este arquivo contém comandos INSERT. Execute APÓS criar a tabela.")

    st.markdown("---")
    st.error("🔒 **Lembrete LGPD:** Ao conectar o Power BI, lembre-se de tratar a coluna 'nome_paciente'.")
