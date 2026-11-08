"""
Assistente RAG
- Streamlit (interface)
- LangChain com LCEL (orquestração)
- FAISS (banco vetorial)
- Ollama (embeddings + LLM)
"""

import textwrap
import warnings
from pathlib import Path

import streamlit as st
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# O langchain-community foi descontinuado e emite um DeprecationWarning na importação.
# Ele ainda funciona; o aviso é silenciado até migrarmos PyPDFLoader e FAISS.
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*langchain-community.*"
)
from langchain_community.document_loaders import PyPDFLoader  # noqa: E402
from langchain_community.vectorstores import FAISS  # noqa: E402

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
CAMINHO_PDF = Path(__file__).parent / "base" / "politica_rh.pdf"
MODELO_EMBEDDING = "qwen3-embedding:0.6b"
MODELO_LLM = "qwen3.5:0.8b"
TAMANHO_BLOCO = 1000
SOBREPOSICAO_BLOCO = 200
QTD_BLOCOS_CONTEXTO = 4  # quantos blocos o retriever devolve por pergunta
QTD_MENSAGENS_HISTORICO = 6  # últimas mensagens enviadas ao LLM como histórico

MENSAGEM_ERRO_OLLAMA = (
    "Não foi possível falar com o Ollama. Verifique se ele está rodando "
    "(`ollama serve`) e se os modelos foram baixados:\n\n"
    f"```\nollama pull {MODELO_LLM}\nollama pull {MODELO_EMBEDDING}\n```"
)

PROMPT = textwrap.dedent("""\
    Você é um assistente de RH que responde perguntas sobre políticas internas da empresa.
    Use APENAS as informações do contexto abaixo para responder.
    Se não encontrar a resposta, diga claramente que não sabe responder.
    Responda em português do Brasil, de forma clara e objetiva.

    Histórico da conversa:
    {history}

    Contexto:
    {context}

    Pergunta: {question}

    Resposta:""")


# ---------------------------------------------------------------------------
# Lógica do RAG
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Indexando documentos...")
def criar_retriever() -> VectorStoreRetriever:
    """Lê o PDF, divide em blocos e cria o índice vetorial (executado uma única vez)."""
    documentos = PyPDFLoader(str(CAMINHO_PDF)).load()
    separador = RecursiveCharacterTextSplitter(
        chunk_size=TAMANHO_BLOCO, chunk_overlap=SOBREPOSICAO_BLOCO
    )
    blocos = separador.split_documents(documentos)
    banco_vetores = FAISS.from_documents(
        blocos, OllamaEmbeddings(model=MODELO_EMBEDDING)
    )
    return banco_vetores.as_retriever(search_kwargs={"k": QTD_BLOCOS_CONTEXTO})


@st.cache_resource
def criar_chain_resposta():
    """Monta a chain prompt -> LLM -> texto."""
    llm = ChatOllama(model=MODELO_LLM, reasoning=False)
    return ChatPromptTemplate.from_template(PROMPT) | llm | StrOutputParser()


def formatar_docs(docs: list[Document]) -> str:
    """Junta só o texto dos blocos recuperados (sem os metadados)."""
    return "\n\n".join(doc.page_content for doc in docs)


def formatar_historico(mensagens: list[dict]) -> str:
    """Converte as últimas mensagens do chat em texto para o prompt."""
    recentes = mensagens[-QTD_MENSAGENS_HISTORICO:]
    if not recentes:
        return "(sem mensagens anteriores)"
    nomes = {"user": "Usuário", "assistant": "Assistente"}
    return "\n".join(f"{nomes[m['role']]}: {m['content']}" for m in recentes)


def paginas_das_fontes(docs: list[Document]) -> list[int]:
    """Páginas (numeradas a partir de 1) de onde vieram os blocos usados."""
    return sorted({doc.metadata["page"] + 1 for doc in docs if "page" in doc.metadata})


def exibir_fontes(paginas: list[int]) -> None:
    if paginas:
        with st.expander("Fontes"):
            st.write(f"{CAMINHO_PDF.name} — página(s) {', '.join(map(str, paginas))}")


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------
st.title("Assistente RAG — Políticas Internas")

try:
    retriever = criar_retriever()
except Exception:  # noqa: BLE001 — Ollama fora do ar ou modelo ausente
    st.error(MENSAGEM_ERRO_OLLAMA)
    st.stop()

chain = criar_chain_resposta()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        exibir_fontes(msg.get("paginas", []))

pergunta = st.chat_input("Pergunte sobre as políticas da empresa...")
if pergunta:
    historico = formatar_historico(st.session_state["messages"])
    st.session_state["messages"].append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Buscando..."):
                docs = retriever.invoke(pergunta)
            resposta = st.write_stream(
                chain.stream(
                    {
                        "context": formatar_docs(docs),
                        "question": pergunta,
                        "history": historico,
                    }
                )
            )
        except Exception:  # noqa: BLE001
            st.error(MENSAGEM_ERRO_OLLAMA)
            st.stop()
        paginas = paginas_das_fontes(docs)
        exibir_fontes(paginas)

    st.session_state["messages"].append(
        {"role": "assistant", "content": resposta, "paginas": paginas}
    )
