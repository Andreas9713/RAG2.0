import os
from functools import lru_cache
from typing import Dict, List

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma


@lru_cache(maxsize=1)
def get_embeddings() -> SentenceTransformerEmbeddings:
    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    return SentenceTransformerEmbeddings(model_name=model_name)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    persist_dir = os.getenv("CHROMA_DB_DIR", "/data/chroma")
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma(persist_directory=persist_dir, embedding_function=get_embeddings())


def _build_prompt() -> PromptTemplate:
    template = (
        "You are a privacy-first assistant. Use the following context to answer the question. "
        "If the answer cannot be determined from the context, say you do not know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\n\nAnswer in French."
    )
    return PromptTemplate(template=template, input_variables=["context", "question"])


def _build_chain(top_k: int, model_name: str) -> RetrievalQA:
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": top_k})
    llm = ChatOllama(model=model_name)
    prompt = _build_prompt()
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )


def answer_question(question: str, top_k: int) -> Dict[str, List]:
    primary_model = os.getenv("OLLAMA_PRIMARY_MODEL", "llama3.1")
    fallback_model = os.getenv("OLLAMA_FALLBACK_MODEL", "mistral")

    chain = _build_chain(top_k=top_k, model_name=primary_model)
    try:
        return chain.invoke({"query": question})
    except Exception:
        if fallback_model == primary_model:
            raise
        fallback_chain = _build_chain(top_k=top_k, model_name=fallback_model)
        return fallback_chain.invoke({"query": question})
