import os
from pathlib import Path
from typing import List

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")
DATA_DIR = Path("/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="privategpt-local", layout="wide")
st.title("📚 privategpt-local")
st.write("Upload files, ingest them into Chroma, and chat with your private knowledge base.")

if not API_TOKEN:
    st.warning("API_TOKEN is not configured. Requests to the backend will fail until it is set.")


def _auth_headers() -> dict:
    if API_TOKEN:
        return {"Authorization": f"Bearer {API_TOKEN}"}
    return {}


def _post(endpoint: str, payload: dict) -> requests.Response:
    url = f"{BACKEND_URL}{endpoint}"
    return requests.post(url, json=payload, headers=_auth_headers(), timeout=120)


st.header("1. Upload documents")
uploaded_files = st.file_uploader("Choose files", type=["pdf", "txt", "docx", "md"], accept_multiple_files=True)
if uploaded_files:
    saved_files: List[Path] = []
    for file in uploaded_files:
        destination = DATA_DIR / file.name
        with destination.open("wb") as out:
            out.write(file.read())
        saved_files.append(destination)
    st.success(f"Saved {len(saved_files)} file(s) to {DATA_DIR}")

if st.button("Ingest /data into Chroma", use_container_width=True):
    with st.spinner("Ingesting documents..."):
        response = _post("/ingest", {"paths": ["/data"]})
        if response.ok:
            count = response.json().get("indexed", 0)
            st.success(f"Indexed {count} chunks from /data")
        else:
            st.error(f"Ingestion failed: {response.status_code} {response.text}")

st.header("2. Ask questions")
question = st.text_input("Ask a question about your documents")
top_k = st.slider("Number of sources", min_value=1, max_value=10, value=5)

if st.button("Query", use_container_width=True) and question:
    with st.spinner("Querying RAG backend..."):
        response = _post("/query", {"question": question, "top_k": top_k})
        if response.ok:
            data = response.json()
            st.subheader("Answer")
            st.write(data.get("answer", ""))
            sources: List[str] = data.get("sources", [])
            if sources:
                st.subheader("Sources")
                for source in sources:
                    st.write(f"- {source}")
            else:
                st.info("No sources returned.")
        else:
            st.error(f"Query failed: {response.status_code} {response.text}")
