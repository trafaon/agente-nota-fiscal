# 🧾 Agente de Notas Fiscais

Um aplicativo inteligente que permite fazer perguntas em linguagem natural sobre dados de notas fiscais usando IA.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agente-nota-fiscal.streamlit.app/)

## 🎯 Acesso Rápido

**🚀 [Executar App Online](https://agente-nota-fiscal.streamlit.app/)** - Use diretamente no navegador!

---

## 🚀 Funcionalidades

- **Consultas em Linguagem Natural**: Faça perguntas como se estivesse conversando  
- **Análise Inteligente**: Processa arquivos CSV com cabeçalho e itens das NFs  
- **Interface Intuitiva**: Interface web amigável com Streamlit  
- **Fallback de Chave API**: Lê primeiro de `secrets.toml`, depois `.env` ou input manual  
- **Modo Desenvolvedor**: Ative logs e debug de parsing e merge  

---

## 💬 Exemplos de Perguntas

- "Qual o valor total das notas fiscais?"
- "Quem foi o fornecedor com maior volume?"
- "Quantos itens foram vendidos do produto arroz?"
- "Qual foi o produto mais vendido?"
- "Quantas notas fiscais foram emitidas?"
- "Quais os CFOPs mais utilizados?"
- "Qual mês teve maior emissão?"
- "Quantos fornecedores únicos existem?"

---

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)** – Interface web
- **[LlamaIndex](https://www.llamaindex.ai/)** – Indexação e agentes com ferramentas
- **[OpenAI GPT-4o](https://openai.com/)** – LLM para interpretação e resposta
- **[OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)** – Para contexto semântico
- **Pandas + NumPy** – Análise de dados estruturados

---

## 📁 Estrutura do Projeto

📦 agente-nota-fiscal
├── .streamlit/
│   └── secrets.toml          # (opcional) credenciais da OpenAI e Supabase
├── nfs\_extraidos/            # Arquivos extraídos do .zip com NFs
├── 202401\_NFs.zip            # Arquivo compactado contendo os CSVs
├── app.py                    # Código principal com Streamlit + LlamaIndex
├── requirements.txt          # Dependências do projeto
├── .env                      # (opcional) fallback para chaves
└── README.md                 # Este arquivo

---

## 🧪 Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/trafaon/agente-nota-fiscal.git
cd agente-nota-fiscal
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
 ```

3. Instale as dependências:

```bash
Copiar
Editar
pip install -r requirements.txt
```

4. Configure suas chaves em .env ou .streamlit/secrets.toml:
```toml
Copiar
Editar
OPENAI_API_KEY = "sua-chave"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "sua-chave"
```

5. Coloque o arquivo 202401_NFs.zip na raiz do projeto com os arquivos:
202401_NFs_Cabecalho.csv
202401_NFs_Itens.csv

6. Execute o app:
```bash
Copiar
Editar
streamlit run app.py
```

## 🙋‍♀️ Contribuições

Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request* com melhorias, exemplos de perguntas ou novos formatos de NF.

---

## 🛡️ Aviso

Este projeto é experimental. Os dados utilizados devem estar corretamente formatados e validados. Nenhuma informação sensível é armazenada ou compartilhada.

---

Desenvolvido com ☕ por [skynet (2)](https://github.com/trafaon)
