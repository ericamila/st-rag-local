# 🤖 Agente de IA Local com RAG (Ollama + LangChain)

Este projeto demonstra como criar um assistente RAG (Retrieval-Augmented Generation) rodando 100% localmente na sua máquina. O agente é capaz de ler documentos internos (como PDFs) e responder a perguntas baseando-se neles, sem depender de internet ou de chaves de API pagas (como a da OpenAI).

---

## O que é um Assistente RAG?
Um assistente RAG permite que a Inteligência Artificial consulte uma base de conhecimento própria (seus arquivos e documentos) antes de formular uma resposta. Isso evita alucinações e garante que a IA utilize as regras e dados específicos da sua empresa.

---

## Passo a Passo de Instalação e Uso

### 1. Instalação do Ollama
O [Ollama](https://ollama.com) é o motor que vai rodar os modelos de IA localmente no seu computador.

1. Acesse o site oficial e baixe a versão para o seu sistema operacional (Windows ou Mac).
2. Siga o instalador padrão.
3. **Importante:** Após a instalação, reinicie o seu editor de código (ex: VS Code) e feche/abra novamente todos os terminais para que o comando `ollama` seja reconhecido.

### 2. Download dos Modelos (Qwen)
Você precisará de dois modelos: um para o chat (LLM) e outro para gerar os embeddings (transformar os textos do PDF em um formato pesquisável pela IA). 

Abra o seu terminal e execute os comandos abaixo. *(Nota: O exemplo utiliza a família de modelos Qwen, adaptando a versão de acordo com a memória de vídeo/RAM disponível na sua máquina).*

**Baixar o modelo de chat (LLM):**
```bash
ollama pull qwen2.5:0.5b
```

**Baixar o modelo de Embeddings:**
```bash
ollama pull qwen:0.5b
```
Dica de Hardware: No Windows, verifique a memória dedicada da sua Placa de Vídeo. No Mac (Apple Silicon), a memória é unificada (RAM). Escolha versões do Qwen compatíveis com a sua capacidade (0.5b, 1.5b, 7b, etc).

### 3. Configuração do Código (Python + LangChain)
Se você possui um script configurado para a OpenAI, instale a integração do Ollama para o LangChain:

````bash
pip install langchain-ollama
````
No seu código Python, substitua as chamadas da OpenAI pelas do Ollama:

````python
# Importações necessárias
from langchain_ollama import OllamaEmbeddings, ChatOllama

# 1. Configurando os Embeddings Locais
embeddings = OllamaEmbeddings(
    model="qwen:0.5b" # Use o nome exato do modelo baixado
)

# 2. Configurando o Chat (LLM Local)
chat = ChatOllama(
    model="qwen2.5:0.5b", # Use o nome exato do modelo baixado
    reasoning=False       # Desativa o log de raciocínio longo na tela (opcional)
)
````
### 4. Executando o Projeto
Este projeto utiliza o Streamlit para a interface gráfica. Para rodar o chat no seu navegador, abra o terminal na pasta do projeto e execute:

````bash
streamlit run app.py
````
(Substitua app.py pelo nome do seu arquivo principal, se for diferente).

Uma nova aba se abrirá automaticamente no seu navegador padrão com a interface do assistente.

## Privacidade e Segurança
Como os modelos e os embeddings estão rodando através do Ollama no seu próprio hardware, nenhum dado (nem os seus PDFs, nem as perguntas feitas no chat) é enviado para servidores externos. Você pode, inclusive, utilizar o assistente completamente desconectado da internet.