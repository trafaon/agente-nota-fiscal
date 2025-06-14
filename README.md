# 🧾 Agente de Notas Fiscais

Um aplicativo inteligente que permite fazer perguntas em linguagem natural sobre dados de notas fiscais usando IA.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agente-nota-fiscal.streamlit.app/)

## 🎯 Acesso Rápido

**🚀 [Executar App Online](https://agente-nota-fiscal.streamlit.app/)** - Clique para usar diretamente no browser!

## 🚀 Funcionalidades

- **Consultas em Linguagem Natural**: Faça perguntas sobre suas notas fiscais como se estivesse conversando
- **Análise Inteligente**: Processa arquivos CSV de cabeçalho e itens das notas fiscais
- **Interface Intuitiva**: Interface web simples e fácil de usar
- **Respostas Contextualizadas**: Mostra as fontes dos dados utilizados nas respostas

## 📋 Exemplos de Perguntas

- "Qual o fornecedor que teve maior montante recebido?"
- "Qual item teve maior volume entregue (em quantidade)?"
- "Quantas notas são do fornecedor X?"
- "Qual foi o valor total das notas fiscais?"
- "Quais são os principais produtos comprados?"

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)**: Framework para interface web
- **[LlamaIndex](https://www.llamaindex.ai/)**: Framework para aplicações de IA com documentos
- **[Groq](https://groq.com/)**: LLM para processamento de linguagem natural
- **[HuggingFace](https://huggingface.co/)**: Embeddings para busca semântica
- **Python**: Linguagem de programação principal

## 📁 Estrutura do Projeto

```
agente-nota-fiscal/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── .env                  # Variáveis de ambiente (não versionado)
├── 202401_NFs.zip        # Arquivo ZIP com dados das NFs
└── README.md             # Este arquivo
```
### 🎛️ Modo desenvolvedor

O app inclui um modo de desenvolvedor que exibe logs detalhados sobre carregamento, detecção de separadores e merge dos dados. Ative via checkbox na barra lateral para fins de depuração.

## ⚙️ Instalação e Configuração

### 1. Clone o repositório
```bash
git clone https://github.com/trafaon/agente-nota-fiscal.git
cd agente-nota-fiscal
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
GROQ_API_KEY=sua_chave_api_groq_aqui
```

### 4. Execute a aplicação
```bash
streamlit run app.py
```

## 🔑 Configuração da API

### Obtendo a chave da API Groq:
1. Acesse [console.groq.com](https://console.groq.com)
2. Faça login ou crie uma conta
3. Navegue até "API Keys"
4. Crie uma nova chave
5. Adicione a chave no arquivo `.env`

## 📊 Formato dos Dados

O aplicativo espera um arquivo ZIP contendo dois CSVs:
- `202401_NFs_Cabecalho.csv`: Dados do cabeçalho das notas fiscais
- `202401_NFs_Itens.csv`: Dados dos itens das notas fiscais

## 🚀 Deploy

### Streamlit Cloud
1. Faça fork deste repositório
2. Conecte sua conta GitHub ao [Streamlit Cloud](https://share.streamlit.io)
3. Adicione a variável `GROQ_API_KEY` nos secrets do Streamlit Cloud
4. Deploy automático a cada push no repositório

### Local
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🐛 Reportar Problemas

Encontrou um bug ou tem uma sugestão? Abra uma [issue](https://github.com/trafaon/agente-nota-fiscal/issues) no GitHub.

## 👤 Autor

**skynet (2) group** - (https://github.com/trafaon)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
