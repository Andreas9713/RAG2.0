import argparse
import os
import re
from pathlib import Path
from typing import Iterable, List, Tuple

import docx2txt
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from pypdf import PdfReader
import tiktoken

from . import rag

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".docx"}
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))


def _clean_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text)
    return cleaned.strip()


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _read_docx(path: Path) -> str:
    return docx2txt.process(str(path)) or ""


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".docx":
        return _read_docx(path)
    if suffix in {".md", ".markdown", ".txt"}:
        return _read_text(path)
    raise ValueError(f"Extension non prise en charge: {suffix}")


def _chunk_text(text: str) -> Iterable[str]:
    if not text:
        return []
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    if not tokens:
        return []
    stride = max(CHUNK_SIZE - CHUNK_OVERLAP, 1)
    for start in range(0, len(tokens), stride):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk_tokens = tokens[start:end]
        yield encoding.decode(chunk_tokens)


def _create_documents(path: Path) -> List[Document]:
    raw_text = _load_file(path)
    cleaned_text = _clean_text(raw_text)
    chunks = list(_chunk_text(cleaned_text))
    documents = [
        Document(page_content=chunk, metadata={"source": str(path.resolve())})
        for chunk in chunks
        if chunk.strip()
    ]
    return documents


def ingest_paths(paths: List[str]) -> Tuple[List[str], List[str]]:
    persist_dir = os.getenv("CHROMA_DB_DIR", "/data/chroma")
    os.makedirs(persist_dir, exist_ok=True)

    all_documents: List[Document] = []
    processed: List[str] = []
    skipped: List[str] = []

    for path_str in paths:
        path = Path(path_str).expanduser().resolve()
        if not path.exists() or not path.is_file():
            skipped.append(path_str)
            continue
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            skipped.append(path_str)
            continue
        documents = _create_documents(path)
        if not documents:
            skipped.append(path_str)
            continue
        all_documents.extend(documents)
        processed.append(path_str)

    if not all_documents:
        return processed, skipped

    embeddings = rag.get_embeddings()
    vector_dir = Path(persist_dir)
    if not vector_dir.exists() or not any(vector_dir.iterdir()):
        vectorstore = Chroma.from_documents(  # type: ignore
            documents=all_documents,
            embedding=embeddings,
            persist_directory=persist_dir,
        )
    else:
        vectorstore = rag.get_vectorstore()
        vectorstore.add_documents(all_documents)
    vectorstore.persist()
    rag.get_vectorstore.cache_clear()
    rag.get_vectorstore()

    return processed, skipped


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingestion locale de documents")
    parser.add_argument(
        "--paths",
        nargs="+",
        required=True,
        help="Liste des fichiers à ingérer",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    ingest_paths(args.paths)


if __name__ == "__main__":
    main()
