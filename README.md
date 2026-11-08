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
ollama pull qwen3.5:0.8b
```

**Baixar o modelo de Embeddings:**
```bash
ollama pull qwen3-embedding:0.6b
```
Dica de Hardware: No Windows, verifique a memória dedicada da sua Placa de Vídeo. No Mac (Apple Silicon), a memória é unificada (RAM). Escolha versões do Qwen compatíveis com a sua capacidade (0.8b, 2b, 9b, etc).

### 3. Configuração
Os nomes dos modelos, o caminho do PDF e os parâmetros de divisão em blocos ficam nas constantes do topo do `app.py` (`MODELO_LLM`, `MODELO_EMBEDDING`, `CAMINHO_PDF`, `TAMANHO_BLOCO`, ...). Se baixar outros modelos, altere lá.

Para usar outro documento, substitua o arquivo `base/politica_rh.pdf` (ou aponte `CAMINHO_PDF` para ele).

### 4. Executando o Projeto
Instale as dependências e rode a interface com o [uv](https://docs.astral.sh/uv/):

````bash
uv sync
uv run streamlit run app.py
````

Sem o uv, use `pip install -r requirements.txt` e depois `streamlit run app.py`.

Na primeira execução o app indexa o PDF (pode levar alguns segundos); depois o índice fica em cache enquanto o servidor estiver rodando.

Uma nova aba se abrirá automaticamente no seu navegador padrão com a interface do assistente.

## Privacidade e Segurança
Como os modelos e os embeddings estão rodando através do Ollama no seu próprio hardware, nenhum dado (nem os seus PDFs, nem as perguntas feitas no chat) é enviado para servidores externos. Você pode, inclusive, utilizar o assistente completamente desconectado da internet.