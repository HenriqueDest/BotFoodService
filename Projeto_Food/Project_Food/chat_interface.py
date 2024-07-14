import os
import subprocess

# Verifica se o transformers está instalado
try:
    import transformers
except ImportError:
    # Se não estiver instalado, instala o transformers
    subprocess.check_call([os.sys.executable, '-m', 'pip', 'install', 'transformers'])

# Continue com o resto do seu código
import sqlite3
import pandas as pd
from transformers import pipeline
import streamlit as st

# Configurar o pipeline do modelo de linguagem
nlp = pipeline("text-generation", model="microsoft/DialoGPT-small")

# Conectar ao banco de dados
conn = sqlite3.connect('dados_franquias.db', check_same_thread=False)

def query_database(query):
    df = pd.read_sql_query(query, conn)
    return df

def generate_response(question):
    if "taxa de franquia" in question.lower():
        df = query_database("SELECT taxa_franquias FROM taxas")
        return f"A taxa de franquia é: {df.iloc[0]['taxa_franquias']}."

    if "taxa de royalties" in question.lower():
        df = query_database("SELECT taxa_royalties FROM taxas")
        return f"A taxa de royalties é: {df.iloc[0]['taxa_royalties']}."

    if "operações fecharam em 2023" in question.lower():
        df = query_database("SELECT fechamento FROM franquias")
        return f"{df.iloc[0]['fechamento']} das operações fecharam em 2023."

    if "vendas de franquias" in question.lower():
        df = query_database("SELECT vendas FROM franquias")
        return f"Foram realizadas {df.iloc[0]['vendas']} vendas de franquias em 2023."

    if "desempenho do setor de food service em 2023" in question.lower():
        df = query_database("SELECT * FROM aberturas")
        return (f"O desempenho do setor de food service em 2023 foi:\n"
                f"Estados com maior abertura de estabelecimentos: {df.iloc[0]['maiores_aberturas']}.\n"
                f"Estados com menor abertura de estabelecimentos: {df.iloc[0]['menores_aberturas']}.")

    if "porcentagens de estabelecimentos em diferentes locais" in question.lower():
        df = query_database("SELECT local, porcentagem FROM locais")
        response = "As porcentagens de estabelecimentos em diferentes locais são:\n"
        for index, row in df.iterrows():
            response += f"{row['local']}: {row['porcentagem']}\n"
        return response.strip()

    if "principais culinárias no setor de food service" in question.lower():
        df = query_database("SELECT tipo, porcentagem FROM culinaria")
        response = "As principais culinárias no setor de food service são:\n"
        for index, row in df.iterrows():
            response += f"{row['tipo']}: {row['porcentagem']}\n"
        return response.strip()

    if "estados com maior abertura de estabelecimentos" in question.lower():
        df = query_database("SELECT maiores_aberturas FROM aberturas")
        return f"Os estados com maior abertura de estabelecimentos são: {df.iloc[0]['maiores_aberturas']}."

    if "estados com menor abertura de estabelecimentos" in question.lower():
        df = query_database("SELECT menores_aberturas FROM aberturas")
        return f"Os estados com menor abertura de estabelecimentos são: {df.iloc[0]['menores_aberturas']}."

    if "porcentagem de estabelecimentos no sudeste" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='Sudeste'")
        return f"A porcentagem de estabelecimentos no Sudeste é: {df.iloc[0]['porcentagem']}."

    if "porcentagem de estabelecimentos no sul" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='Sul'")
        return f"A porcentagem de estabelecimentos no Sul é: {df.iloc[0]['porcentagem']}."

    if "porcentagem de estabelecimentos no nordeste" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='Nordeste'")
        return f"A porcentagem de estabelecimentos no Nordeste é: {df.iloc[0]['porcentagem']}."

    if "porcentagem de estabelecimentos no centro-oeste" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='Centro-Oeste'")
        return f"A porcentagem de estabelecimentos no Centro-Oeste é: {df.iloc[0]['porcentagem']}."

    if "porcentagem de estabelecimentos no norte" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='Norte'")
        return f"A porcentagem de estabelecimentos no Norte é: {df.iloc[0]['porcentagem']}."

    if "porcentagem de estabelecimentos na rua" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='rua'")
        return f"A porcentagem de estabelecimentos na rua é: {df.iloc[0]['porcentagem']}."

    if "porcentagem de estabelecimentos em shoppings" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='shoppings'")
        return f"A porcentagem de estabelecimentos em shoppings é: {df.iloc[0]['porcentagem']}."

    if "porcentagem de estabelecimentos em outros lugares" in question.lower():
        df = query_database("SELECT porcentagem FROM locais WHERE local='outros lugares'")
        return f"A porcentagem de estabelecimentos em outros lugares é: {df.iloc[0]['porcentagem']}."

    # Se a pergunta não for reconhecida, retornar uma mensagem padrão
    return "No momento não consigo responder essa pergunta com precisão."

def chatbot_response(question):
    response = generate_response(question)
    return response

st.title("Chatbot sobre Franquias")
st.write("Digite sua pergunta sobre franquias no campo abaixo e pressione Enter:")

user_input = st.text_input("Você:", "")

if user_input:
    response = chatbot_response(user_input)
    st.write(f"Bot: {response}")
