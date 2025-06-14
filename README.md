# 🧾 Agente de Notas Fiscais

Um aplicativo inteligente que permite fazer perguntas em linguagem natural sobre dados de notas fiscais usando IA.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agente-nota-fiscal.streamlit.app/)

## 🎯 Acesso Rápido

**🚀 [Executar App Online](https://agente-nota-fiscal.streamlit.app/)** - Use diretamente no navegador!

## 🚀 Funcionalidades

- **Consultas em Linguagem Natural**: Faça perguntas como se estivesse conversando  
- **Análise Inteligente**: Processa arquivos CSV com cabeçalho e itens das NFs  
- **Interface Intuitiva**: Interface web amigável com Streamlit  
- **Fallback de Chave API**: Lê primeiro de `secrets.toml`, depois `.env` ou input manual  
- **Modo Desenvolvedor**: Ative logs e debug de parsing e merge  

## 💬 Exemplos de Perguntas

- "Qual o valor total das notas fiscais?"
- "Quem foi o fornecedor com maior volume?"
- "Quantos itens foram vendidos do produto arroz?"
- "Qual foi o produto mais vendido?"
- "Quantas notas fiscais foram emitidas?"
- "Quais os CFOPs mais utilizados?"
- "Qual mês teve maior emissão?"
- "Quantos fornecedores únicos existem?"

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)** – Interface web
- **[LlamaIndex](https://www.llamaindex.ai/)** – Indexação e agentes com ferramentas
- **[OpenAI GPT-4o](https://openai.com/)** – LLM para interpretação e resposta
- **[OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)** – Para contexto semântico
- **Pandas + NumPy** – Análise de dados estruturados

## 📁 Estrutura do Projeto

