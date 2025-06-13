import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import CSVReader
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool
import zipfile
import re

# --- FUNÇÃO PARA EXTRAIR ZIP ---
def extract_zip(zip_path, extract_path):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path, exist_ok=True)
    if not os.path.exists(os.path.join(extract_path, "202401_NFs_Cabecalho.csv")):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

# --- SETUP INICIAL ---
st.set_page_config(page_title="Pergunte sobre Notas Fiscais!", page_icon="🧾")
st.title("Pergunte sobre as Notas Fiscais de 2024")

with st.expander("Como funciona?"):
    st.write("""
        Faça perguntas em linguagem natural sobre os dados das 100 notas fiscais selecionadas.
        Exemplos:  
        - Qual o maior valor de nota?  
        - Qual item teve maior volume entregue (em quantidade)?  
        - Quantas notas são do fornecedor X?  
    """)

# --- EXTRAÇÃO DOS ARQUIVOS ---
zip_path = "202401_NFs.zip"
extract_path = "nfs_extraido"
extract_zip(zip_path, extract_path)

cabecalho_path = os.path.join(extract_path, "202401_NFs_Cabecalho.csv")
itens_path = os.path.join(extract_path, "202401_NFs_Itens.csv")

# --- AMBIENTE E LLM ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ GROQ_API_KEY não encontrada no .env")
    st.stop()

Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = Groq(model="llama3-8b-8192", api_key=groq_api_key)

# --- INDEXAÇÃO DOS DADOS ---
@st.cache_resource(show_spinner="Indexando os dados, aguarde...")  # Cache para performance
def build_query_engine():
    reader = CSVReader()
    cabecalho_docs = reader.load_data(file=Path(cabecalho_path))
    itens_docs = reader.load_data(file=Path(itens_path))

    cabecalho_index = VectorStoreIndex.from_documents(cabecalho_docs)
    itens_index = VectorStoreIndex.from_documents(itens_docs)

    cabecalho_engine = cabecalho_index.as_query_engine()
    itens_engine = itens_index.as_query_engine()

    tools = [
        QueryEngineTool(
            query_engine=cabecalho_engine,
            metadata={"name": "cabecalho", "description": "Dados gerais das notas fiscais (fornecedor, valor, datas)."}
        ),
        QueryEngineTool(
            query_engine=itens_engine,
            metadata={"name": "itens", "description": "Itens detalhados das notas fiscais (produto, quantidade, unidade)."}
        )
    ]

    return SubQuestionQueryEngine.from_defaults(tools=tools)

query_engine = build_query_engine()

# --- INTERFACE DE PERGUNTAS ---
st.subheader("Faça sua pergunta")
user_question = st.text_input("Digite sua pergunta aqui:")

if st.button("Perguntar") or user_question:
    if user_question.strip() == "":
        st.warning("Digite uma pergunta.")
    else:
        with st.spinner("Consultando a IA..."):
            resposta = query_engine.query(user_question)

            st.markdown("### ✅ Resposta:")

            if hasattr(resposta, "response"):
                texto = resposta.response.strip()
            else:
                texto = str(resposta).strip()

            texto_formatado = re.sub(r'(?<=is )(.*?)(?=,| with)', r'**\1**', texto)
            texto_formatado = re.sub(r'(\d+ transactions?)', r'**\1**', texto_formatado)

            st.markdown(texto_formatado)

            if hasattr(resposta, "source_nodes"):
                arquivos = list({n.metadata.get("filename", "desconhecido") for n in resposta.source_nodes})
                if arquivos:
                    st.markdown("**📁 Arquivos utilizados:**")
                    for arq in arquivos:
                        st.markdown(f"- `{arq}`")

st.caption("Feito com 🧠 LlamaIndex + Groq + Streamlit")
