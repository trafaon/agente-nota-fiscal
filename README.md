# 🧾 Agente de Perguntas sobre Notas Fiscais (Streamlit + LlamaIndex + Groq)

Este projeto é uma aplicação web simples que permite fazer perguntas em linguagem natural sobre as notas fiscais de janeiro/2024, usando inteligência artificial.  
Basta rodar localmente com Streamlit e perguntar:  
- Qual fornecedor recebeu maior valor?
- Qual item teve maior volume entregue?
- Quantas notas são do fornecedor X?
- ...e muito mais!

---

## 🚀 Como rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/agente-nota-fiscal.git
cd agente-nota-fiscal
````

### 2. Adicione os arquivos necessários

* Coloque o arquivo `202401_NFs.zip` na pasta principal do projeto.
* **NÃO suba o arquivo `.env` para o GitHub.**
  Em vez disso, crie um arquivo chamado `.env` (veja o exemplo abaixo).

#### Exemplo de estrutura:

```
agente-nota-fiscal/
├── app.py
├── .env
├── 202401_NFs.zip
└── requirements.txt
```

### 3. Instale as dependências

Recomendo criar um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

Se não tiver o `requirements.txt`, use:

```bash
pip install streamlit llama-index-core llama-index-llms-groq llama-index-embeddings-huggingface python-dotenv
```

### 4. Crie seu arquivo `.env`

Crie um arquivo chamado `.env` na pasta principal e insira sua chave Groq:

```
GROQ_API_KEY=sua_chave_aqui
```

**Nunca suba o `.env` para o repositório.**
Inclua `.env` no `.gitignore`.

### 5. Execute o aplicativo

```bash
streamlit run app.py
```

Abra o navegador no link que aparecer no terminal (geralmente [http://localhost:8501](http://localhost:8501)).

---

## 📝 Exemplo de uso

* Digite perguntas em português sobre os dados das notas fiscais.
* Receba respostas automáticas, geradas por IA, baseadas nos arquivos CSV extraídos do ZIP.

---

## 📦 Notas sobre segurança

* **NUNCA compartilhe seu arquivo `.env` publicamente.**
* Um arquivo `.env.example` é fornecido apenas para mostrar o formato:

  ```
  GROQ_API_KEY=sua_chave_aqui
  ```
* Coloque sua própria chave no arquivo `.env` antes de rodar.

---

## 🛠️ Créditos e tecnologia

* [Streamlit](https://streamlit.io/) para a interface web
* [LlamaIndex](https://www.llamaindex.ai/) para integração com dados estruturados
* [Groq](https://groq.com/) como LLM API
* [Hugging Face Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

---

## 👩‍💻 Sobre

Desenvolvido para fins didáticos e exploratórios.
Dúvidas, sugestões ou melhorias?
Abra uma [issue](https://github.com/seu-usuario/agente-nota-fiscal/issues) ou envie um pull request!

---
