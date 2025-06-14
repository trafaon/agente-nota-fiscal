import streamlit as st
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import zipfile
import numpy as np
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
import toml

# --- Setup inicial ---
st.set_page_config(page_title="NF Insights", page_icon="🧾")
st.title("🔍 Análise Inteligente de Notas Fiscais")

with st.expander("ℹ️ Como funciona"):
    st.markdown("""
    Este app permite fazer perguntas sobre os dados das Notas Fiscais.
    Exemplos:
    - Qual o valor total das notas?
    - Quem foi o fornecedor com maior volume?
    - Quais os produtos mais vendidos?
    - Quantas notas fiscais foram emitidas?
    """)

# --- Carregar chave da OpenAI ---
def get_openai_key():
    try:
        config = toml.load(".streamlit/secrets.toml")
        return config.get("OPENAI_API_KEY")
    except:
        load_dotenv()
        key = os.getenv("OPENAI_API_KEY")
        if key:
            return key
        return st.text_input("🔐 Digite sua chave da OpenAI:", type="password")

openai_key = get_openai_key()
if not openai_key:
    st.stop()

# --- Descompactar arquivos, se necessário ---
zip_path = "202401_NFs.zip"
extract_path = Path("nfs_extraidos")

if Path(zip_path).exists():
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# --- Carregar CSVs ---
def read_csv_safe(path):
    try:
        return pd.read_csv(path, encoding="latin1", sep=None, engine='python')
    except Exception as e:
        st.error(f"Erro ao ler {path}: {e}")
        return pd.DataFrame()

cab = read_csv_safe(extract_path / "202401_NFs_Cabecalho.csv")
itens = read_csv_safe(extract_path / "202401_NFs_Itens.csv")

# --- Merge ---
df = pd.merge(itens, cab, how="left", on="CHAVE DE ACESSO")

# --- Modelo LLM + embeddings ---
Settings.llm = OpenAI(model="gpt-4o", api_key=openai_key)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_key)

# --- Documento base para indexação ---
summary = f"""
Total de notas: {len(cab)}
Total de itens: {len(itens)}
Colunas no cabeçalho: {', '.join(cab.columns[:5])}...
Colunas nos itens: {', '.join(itens.columns[:5])}...
"""
docs = [Document(text=summary)]
index = VectorStoreIndex.from_documents(docs)
query_engine_index = index.as_query_engine()

# --- Query Engine com Pandas ---
class PandasQueryEngine:
    def __init__(self, df):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    def query(self, pergunta):
        pergunta = pergunta.lower()

        if any(p in pergunta for p in ["valor total", "soma dos valores", "quanto foi gasto"]):
            col = [c for c in self.df.columns if "valor total" in c.lower() or "valor nota fiscal" in c.lower()]
            if col:
                total = self.df[col[0]].sum()
                return f"🧾 Valor total das notas: R$ {total:,.2f}"

        if any(p in pergunta for p in ["maior valor", "nota mais alta", "nota com maior valor"]):
            col = [c for c in self.df.columns if "valor total" in c.lower() or "valor nota fiscal" in c.lower()]
            if col:
                max_val = self.df[col[0]].max()
                return f"📌 O maior valor encontrado em uma nota foi: R$ {max_val:,.2f}"

        if any(p in pergunta for p in ["maior fornecedor", "fornecedor com mais valor"]):
            fornecedores = [c for c in self.df.columns if "razão social emitente" in c.lower()]
            valores = [c for c in self.df.columns if "valor nota fiscal" in c.lower()]
            if fornecedores and valores:
                top = self.df.groupby(fornecedores[0])[valores[0]].sum().sort_values(ascending=False).head(1)
                fornecedor, valor = top.index[0], top.values[0]
                return f"🏢 Fornecedor com maior valor total: **{fornecedor}**, com R$ {valor:,.2f}"

        if any(p in pergunta for p in ["fornecedor com maior volume", "mais itens entregues", "quantidade por fornecedor"]):
            col_forn = [c for c in self.df.columns if "razão social emitente" in c.lower()]
            col_qtd = [c for c in self.df.columns if "quantidade" in c.lower()]
            if col_forn and col_qtd:
                top = self.df.groupby(col_forn[0])[col_qtd[0]].sum().sort_values(ascending=False).head(1)
                nome, qtd = top.index[0], top.values[0]
                return f"🚚 Fornecedor com maior volume (quantidade de itens): **{nome}**, com {qtd:,.0f} itens vendidos"

        if "quantos fornecedores" in pergunta or "número de fornecedores" in pergunta:
            col_forn = [c for c in self.df.columns if "razão social emitente" in c.lower()]
            if col_forn:
                total = self.df[col_forn[0]].nunique()
                return f"🔢 Total de fornecedores únicos: {total}"

        if "quantos itens" in pergunta or "quantidade" in pergunta:
            col_produto = [c for c in self.df.columns if "descri" in c.lower() or "produto" in c.lower()]
            col_quant = [c for c in self.df.columns if "quantidade" in c.lower()]
            if col_produto and col_quant:
                palavras = pergunta.split()
                filtro = next((p for p in palavras if len(p) > 3), None)
                if filtro:
                    df_filt = self.df[self.df[col_produto[0]].str.contains(filtro, case=False, na=False)]
                    total = df_filt[col_quant[0]].sum()
                    return f"📦 Quantidade total de '{filtro}' vendida: {total:,.0f}"

        if "produto mais vendido" in pergunta or "mais vendido" in pergunta:
            col_produto = [c for c in self.df.columns if "descri" in c.lower() or "produto" in c.lower()]
            col_quant = [c for c in self.df.columns if "quantidade" in c.lower()]
            if col_produto and col_quant:
                top = self.df.groupby(col_produto[0])[col_quant[0]].sum().sort_values(ascending=False).head(1)
                nome, qtd = top.index[0], top.values[0]
                return f"🏆 Produto mais vendido: **{nome}**, com {qtd:,.0f} unidades"

        if "quantas notas" in pergunta:
            return f"📑 Total de notas fiscais emitidas: {len(cab):,}"

        if "cfop" in pergunta:
            col_cfop = [c for c in self.df.columns if "cfop" in c.lower()]
            if col_cfop:
                top = self.df[col_cfop[0]].value_counts().head(5)
                return f"📄 Top CFOPs mais utilizados:\n{top.to_string()}"

        if "mês com mais notas" in pergunta or "qual mês teve mais emissão" in pergunta:
            col_data = [c for c in self.df.columns if "emissão" in c.lower() or "data" in c.lower()]
            if col_data:
                df_temp = self.df.copy()
                df_temp[col_data[0]] = pd.to_datetime(df_temp[col_data[0]], errors='coerce')
                df_temp['mes'] = df_temp[col_data[0]].dt.month
                top_mes = df_temp['mes'].value_counts().idxmax()
                return f"📆 O mês com maior número de emissões foi: {top_mes}"

        return "❓ Pergunta não reconhecida ou não há dados suficientes para responder."

pandas_engine = PandasQueryEngine(df)

# --- Ferramentas ---
tools = [
    QueryEngineTool(
        query_engine=query_engine_index,
        metadata=ToolMetadata(
            name="resumo",
            description="Consulta sobre contexto geral das notas fiscais"
        )
    ),
    QueryEngineTool(
        query_engine=pandas_engine,
        metadata=ToolMetadata(
            name="dados",
            description="Consultas diretas aos dados de notas fiscais"
        )
    )
]

agent = ReActAgent.from_tools(tools, verbose=False)

# --- Pergunta do usuário ---
st.subheader("Faça sua pergunta")
q = st.text_input("Digite aqui")
if st.button("Perguntar") and q:
    with st.spinner("Consultando..."):
        resposta = agent.query(q)
        st.markdown("### ✅ Resposta:")
        st.markdown(resposta.response if hasattr(resposta, 'response') else str(resposta))
