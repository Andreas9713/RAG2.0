import os
from pathlib import Path
from typing import List

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_TOKEN = os.getenv("API_TOKEN", "")
DATA_DIR = Path(os.getenv("DATA_DIR", "/data/documents"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

if "uploaded_paths" not in st.session_state:
    st.session_state["uploaded_paths"] = []

st.set_page_config(page_title="PrivateGPT Local", layout="wide")

st.title("🛡️ PrivateGPT Local")
st.caption("Chat privé avec vos documents locaux")

st.sidebar.header("Configuration")
st.sidebar.write(f"Backend: {BACKEND_URL}")
if API_TOKEN:
    st.sidebar.success("Token API chargé")
else:
    st.sidebar.warning("Aucun token API trouvé dans l'environnement")

uploaded_files = st.file_uploader(
    "Déposez vos fichiers (PDF, TXT, DOCX, Markdown)",
    type=["pdf", "txt", "docx", "md", "markdown"],
    accept_multiple_files=True,
)

new_paths: List[str] = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        destination = DATA_DIR / uploaded_file.name
        base_name = destination.stem
        suffix = destination.suffix
        counter = 1
        while destination.exists():
            destination = destination.with_name(f"{base_name}_{counter}{suffix}")
            counter += 1
        with open(destination, "wb") as fh:
            fh.write(uploaded_file.getbuffer())
        new_paths.append(str(destination))
    if new_paths:
        existing = set(st.session_state["uploaded_paths"])
        for path in new_paths:
            if path not in existing:
                st.session_state["uploaded_paths"].append(path)
        st.success(f"{len(new_paths)} fichier(s) sauvegardé(s) pour ingestion")

if st.session_state["uploaded_paths"]:
    st.subheader("Fichiers en attente d'ingestion")
    for path in st.session_state["uploaded_paths"]:
        st.write(path)

if st.button("Ingérer les fichiers"):
    if not st.session_state["uploaded_paths"]:
        st.warning("Aucun fichier à ingérer.")
    else:
        headers = {"x-api-token": API_TOKEN} if API_TOKEN else {}
        try:
            response = requests.post(
                f"{BACKEND_URL}/ingest",
                json={"paths": st.session_state["uploaded_paths"]},
                headers=headers,
                timeout=120,
            )
            response.raise_for_status()
            payload = response.json()
            st.success(
                f"Ingestion terminée. {len(payload.get('processed_files', []))} fichier(s) traité(s)."
            )
            skipped = payload.get("skipped_files", [])
            if skipped:
                st.warning(f"Fichiers ignorés : {', '.join(skipped)}")
            st.session_state["uploaded_paths"] = []
        except requests.RequestException as exc:  # pragma: no cover - UI feedback
            st.error(f"Erreur pendant l'ingestion : {exc}")

st.subheader("Poser une question")
question = st.text_area("Question", key="question_input")
top_k = st.slider("Nombre de documents à récupérer", min_value=1, max_value=10, value=5)

if st.button("Envoyer la question"):
    if not question.strip():
        st.warning("Merci de saisir une question.")
    else:
        headers = {"x-api-token": API_TOKEN} if API_TOKEN else {}
        try:
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"question": question, "top_k": top_k},
                headers=headers,
                timeout=120,
            )
            response.raise_for_status()
            payload = response.json()
            st.markdown("### Réponse")
            st.write(payload.get("answer", "Je ne sais pas."))
            sources = payload.get("sources", [])
            if sources:
                st.markdown("### Sources")
                for source in sources:
                    st.write(f"- **{source.get('source')}** : {source.get('snippet')}")
        except requests.RequestException as exc:  # pragma: no cover - UI feedback
            st.error(f"Erreur pendant la requête : {exc}")
