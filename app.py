import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import CSVReader
import zipfile

# Função para extrair o ZIP (executa uma única vez)
def extract_zip(zip_path, extract_path):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path, exist_ok=True)
    # Só extrai se ainda não tiver extraído
    if not os.path.exists(os.path.join(extract_path, "202401_NFs_Cabecalho.csv")):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

# --- PARTE DE SETUP ---
st.set_page_config(page_title="Pergunte sobre Notas Fiscais!", page_icon="🧾")
st.title("Pergunte sobre as Notas Fiscais de 2024")

with st.expander("Como funciona?"):
    st.write("""
        Faça perguntas em linguagem natural sobre os dados das 100 notas fiscais selecionadas.
        Exemplos:  
        - Qual o fornecedor que teve maior montante recebido?  
        - Qual item teve maior volume entregue (em quantidade)?  
        - Quantas notas são do fornecedor X?  
    """)

# Caminho do arquivo ZIP e extração
zip_path = "202401_NFs.zip"  # Ajuste se estiver em outro lugar
extract_path = "nfs_extraido"
extract_zip(zip_path, extract_path)

cabecalho_path = os.path.join(extract_path, "202401_NFs_Cabecalho.csv")
itens_path = os.path.join(extract_path, "202401_NFs_Itens.csv")

# --- AMBIENTE E LLM ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY não encontrada no .env")
    st.stop()

# Definir modelos de embeddings e LLM
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = Groq(model="llama3-8b-8192", api_key=groq_api_key)

# --- INDEXAÇÃO DOS DADOS ---
@st.cache_resource(show_spinner="Indexando os dados, aguarde um instante...")
def load_index():
    reader = CSVReader()
    cabecalho_docs = reader.load_data(file=Path(cabecalho_path))
    itens_docs = reader.load_data(file=Path(itens_path))
    docs = cabecalho_docs + itens_docs
    index = VectorStoreIndex.from_documents(docs)
    return index

index = load_index()
query_engine = index.as_query_engine()

# --- INTERFACE ---
st.subheader("Faça sua pergunta")
user_question = st.text_input("Digite sua pergunta aqui:")

if st.button("Perguntar") or user_question:
    if user_question.strip() == "":
        st.warning("Digite uma pergunta para obter resposta.")
    else:
        with st.spinner("Consultando..."):
            resposta = query_engine.query(user_question)
            st.markdown("### ✅ Resposta:")

            # Se for uma string direta (como parece)
            if hasattr(resposta, "response"):
                texto = resposta.response.strip()
            else:
                texto = str(resposta).strip()
            
            # Formatação opcional: negrito em valores detectados
            import re
            texto_formatado = re.sub(r'(?<=is )(.*?)(?=,| with)', r'**\1**', texto)
            texto_formatado = re.sub(r'(\d+ transactions?)', r'**\1**', texto_formatado)
            
            st.markdown(texto_formatado)
            
            # Mostrar fontes usadas (opcional)
            if hasattr(resposta, "source_nodes"):
                arquivos = list({n.metadata.get("filename", "desconhecido") for n in resposta.source_nodes})
                if arquivos:
                    st.markdown("**📁 Arquivos utilizados na resposta:**")
                    for arq in arquivos:
                        st.markdown(f"- `{arq}`")

st.caption("App demo usando Streamlit + LlamaIndex + Groq + Embeddings HF")
