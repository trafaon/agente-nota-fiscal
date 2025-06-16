import streamlit as st
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import zipfile
import numpy as np
import toml
from supabase import create_client, Client
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.experimental.query_engine import PandasQueryEngine

# --- Setup inicial ---
st.set_page_config(page_title="NF Insights", page_icon="🧾")
st.title("🔍 Análise Inteligente de Notas Fiscais")

with st.expander("ℹ️ Como funciona"):
    st.markdown("""
    Este app permite fazer perguntas sobre os dados das Notas Fiscais.
    Exemplos:
    - Qual o valor total das notas?
    - Quem foi o fornecedor com maior volume?
    - Quantos itens foram vendidos do produto X?
    - Quais os produtos mais vendidos?
    - Quantas notas fiscais foram emitidas?
    - Quais os CFOPs mais utilizados?
    - Qual mês teve maior emissão?
    - Quantos fornecedores únicos existem?
    """)

# --- Chaves e autenticação ---
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

def get_supabase_client():
    try:
        config = toml.load(".streamlit/secrets.toml")
        url = config["SUPABASE_URL"]
        key = config["SUPABASE_KEY"]
    except:
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        st.error("Credenciais da Supabase não encontradas.")
        st.stop()
    return create_client(url, key)

# --- Função para subir CSV ---
def subir_csv_para_supabase(tabela, csv_path):
    df = pd.read_csv(csv_path, encoding="latin1", sep=None, engine='python')

    df.columns = (
        df.columns
        .str.encode('latin1')
        .str.decode('utf-8', errors='ignore')
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(" ", "_")
    )

    df = df.replace({np.nan: None})

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) or isinstance(df[col].iloc[0], pd.Timestamp):
            df[col] = df[col].astype(str)

    if "chave_de_acesso" not in df.columns:
        st.error("❌ A coluna 'chave_de_acesso' não foi encontrada no CSV.")
        st.stop()

    data = df.to_dict(orient="records")
    for i, chunk in enumerate([data[i:i + 500] for i in range(0, len(data), 500)]):
        st.info(f"Enviando chunk {i+1} de {tabela} ({len(chunk)} registros)...")
        try:
            if tabela == "itens":
                supabase.table(tabela).upsert(chunk, on_conflict="chave_de_acesso,número_produto").execute()
            else:
                supabase.table(tabela).upsert(chunk, on_conflict="chave_de_acesso").execute()
        except Exception as e:
            st.error(f"Erro ao enviar chunk {i+1} para {tabela}: {e}")
            st.stop()

openai_key = get_openai_key()
if not openai_key:
    st.stop()

zip_path = "202401_NFs.zip"
extract_path = Path("nfs_extraidos")

supabase: Client = get_supabase_client()

def limpar_tabelas():
    supabase.table("itens").delete().neq("id", 0).execute()
    supabase.table("cabecalho").delete().neq("id", 0).execute()

if Path(zip_path).exists():
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    limpar_tabelas()
    subir_csv_para_supabase("cabecalho", extract_path / "202401_NFs_Cabecalho.csv")
    subir_csv_para_supabase("itens", extract_path / "202401_NFs_Itens.csv")

cab = pd.DataFrame(supabase.table("cabecalho").select("*").execute().data)
itens = pd.DataFrame(supabase.table("itens").select("*").execute().data)

if cab.empty or itens.empty:
    st.error("⚠️ As tabelas 'cabecalho' ou 'itens' estão vazias.")
    st.stop()

cab.columns = cab.columns.str.upper()
itens.columns = itens.columns.str.upper()

df = pd.merge(itens, cab, how="left", on="CHAVE_DE_ACESSO", suffixes=("_item", "_cab"))

Settings.llm = OpenAI(model="gpt-4o", api_key=openai_key)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_key)

summary = f"""
Total de notas: {len(cab)}
Total de itens: {len(itens)}
Colunas no cabeçalho: {', '.join(cab.columns[:5])}...
Colunas nos itens: {', '.join(itens.columns[:5])}...
"""
docs = [Document(text=summary)]
index = VectorStoreIndex.from_documents(docs)
query_engine_index = index.as_query_engine()

pandas_engine = PandasQueryEngine(df=df)


def encontrar_coluna(possibilidades, df):
    for p in possibilidades:
        for c in df.columns:
            if p.lower() in c.lower():
                return c
    return possibilidades[0]

def query(pergunta):
    pergunta = pergunta.lower()

    col_valor = encontrar_coluna(["valor_nota_fiscal"], df)
    col_forn = encontrar_coluna(["razao_social_emitente"], df)
    col_prod = encontrar_coluna(["descricao_do_produto", "descricao_do_produto_servico"], df)
    col_qtd = encontrar_coluna(["quantidade"], df)
    col_data_1 = encontrar_coluna(["data_emissao_item"], df)
    col_data_2 = encontrar_coluna(["data_emissao_cab"], df)
    col_cfop = encontrar_coluna(["cfop"], df)
    col_modelo = encontrar_coluna(["modelo"], df)

    try:
        if "valor total" in pergunta:
            total = df[col_valor].sum()
            return f"🧾 Valor total: R$ {total:,.2f}"

        elif "menor valor" in pergunta:
            menor = df[col_valor].min()
            return f"💸 Menor valor de nota: R$ {menor:,.2f}"

        elif "maior valor" in pergunta:
            maior = df[col_valor].max()
            return f"📌 Maior nota: R$ {maior:,.2f}"

        elif "maior fornecedor" in pergunta or "fornecedor com maior" in pergunta:
            df_filtrado = df.dropna(subset=[col_forn, col_valor])
            top = df_filtrado.groupby(col_forn)[col_valor].sum().sort_values(ascending=False).head(1)
            return f"🏢 Maior fornecedor: {top.index[0]} com R$ {top.values[0]:,.2f}"

        elif "mais vendido" in pergunta and "produto" in pergunta:
            df_filtrado = df.dropna(subset=[col_prod, col_qtd])
            top = df_filtrado.groupby(col_prod)[col_qtd].sum().sort_values(ascending=False).head(1)
            return f"🏆 Produto mais vendido: {top.index[0]} com {top.values[0]:,.0f} unidades"

        elif "produto mais pedido" in pergunta:
            top = df[col_prod].value_counts().head(1)
            return f"🛒 Produto mais pedido: {top.index[0]} com {top.values[0]} pedidos"

        elif "quantos itens" in pergunta and "produto" in pergunta:
            produto = pergunta.split("produto")[-1].strip()
            qtd = df[df[col_prod].str.contains(produto, case=False, na=False)][col_qtd].sum()
            return f"🔢 Foram vendidos {qtd:.0f} itens do produto '{produto}'"

        elif "quantas notas" in pergunta:
            return f"📄 Total de notas: {df['CHAVE_DE_ACESSO'].nunique()}"

        elif "quantos fornecedores" in pergunta:
            total = df[col_forn].nunique()
            return f"🏢 Total de fornecedores únicos: {total}"

        elif "cfop" in pergunta:
            top = df[col_cfop].value_counts().head(5)
            return f"📄 Top CFOPs:\n{top.to_string()}"

        elif "modelo" in pergunta or "tipo de nota" in pergunta:
            modelos = df[col_modelo].dropna().unique()
            return f"📄 Tipos de nota (modelo): {', '.join(str(m) for m in modelos)}"

        elif "mês" in pergunta:
            temp = df.copy()
            for col_data in [col_data_1, col_data_2]:
                if col_data in temp.columns:
                    temp[col_data] = pd.to_datetime(temp[col_data], errors='coerce')
                    if temp[col_data].notna().sum() > 0:
                        mes = temp[col_data].dt.month.value_counts().idxmax()
                        return f"📆 Mês com mais emissões: {mes}"
            return "⚠️ Nenhuma coluna de data válida encontrada."

    except Exception as e:
        return f"⚠️ Erro na análise: {str(e)}"

    return "❓ Pergunta não reconhecida ou dados insuficientes."

pandas_engine.query = query

tools = [
    QueryEngineTool(query_engine=query_engine_index, metadata=ToolMetadata(name="resumo", description="Consulta ao resumo")),
    QueryEngineTool(query_engine=pandas_engine, metadata=ToolMetadata(name="dados", description="Consulta aos dados das notas fiscais"))
]
agent = ReActAgent.from_tools(tools, verbose=False)

st.subheader("Faça sua pergunta")
q = st.text_input("Digite aqui sua pergunta:")
if st.button("Perguntar") and q:
    with st.spinner("Consultando..."):
        resposta = agent.query(q)
        st.markdown("### ✅ Resposta:")
        st.markdown(resposta.response if hasattr(resposta, 'response') else str(resposta))
