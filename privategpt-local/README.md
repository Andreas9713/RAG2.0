# privategpt-local

> Local Retrieval-Augmented Generation stack powered by Ollama, FastAPI, ChromaDB and Streamlit.

## Overview

This project bundles a fully offline RAG experience that runs completely on your machine. It uses:

- **Ollama** for serving local LLMs (defaults to `llama3.1` with automatic `mistral` fallback).
- **FastAPI** backend exposing ingestion and query endpoints powered by LangChain + ChromaDB.
- **Streamlit** web UI for uploading documents and chatting with the knowledge base.
- **ChromaDB** with persistent storage for embeddings stored on disk.

All services are orchestrated via Docker Compose to keep the stack reproducible.

## Prerequisites

- Docker & Docker Compose
- Sufficient disk space and RAM for running Ollama models
- (Optional) `make`

Copy `.env.example` to `.env` and adjust values (notably `API_TOKEN`).

```bash
cp .env.example .env
```

## Makefile commands

| Command | Description |
| --- | --- |
| `make bootstrap` | Download Ollama models and build service images. |
| `make up` | Start the stack (Ollama, ChromaDB, backend, web UI). |
| `make down` | Stop all services. |
| `make ingest path=/path/to/data` | Trigger ingestion for a local folder via API. |
| `make query question="..."` | Send a question to the backend RAG endpoint. |
| `make reset` | Stop services and remove Chroma/embedding volumes. |

## Services & Ports

| Service | Port | Description |
| --- | --- | --- |
| Ollama | 11434 | Serves local LLM models. |
| ChromaDB | 8001 (host) → 8000 (container) | Persistent vector store. |
| Backend | 8000 | FastAPI RAG endpoints. |
| Web | 8501 | Streamlit UI. |

## Usage

1. Bootstrap and start the stack:

   ```bash
   make bootstrap
   make up
   ```

2. Check the backend health:

   ```bash
   curl http://localhost:8000/health
   # {"ok": true}
   ```

3. Ingest documents (assumes files mounted under `./data`):

   ```bash
   curl -X POST http://localhost:8000/ingest \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_TOKEN" \
     -d '{"paths": ["/data"]}'
   ```

4. Ask a question:

   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -H "Authorization: $API_TOKEN" \
     -d '{"question": "What documents are available?", "top_k": 3}'
   ```

5. Open the Streamlit UI at [http://localhost:8501](http://localhost:8501) to upload files and chat.

## Troubleshooting

- Ensure Ollama has downloaded the required models (`make bootstrap`).
- Check container logs with `docker compose logs <service>`.
- Delete `./chroma` and `./ollama` directories if you need a clean slate and rerun `make bootstrap`.
- Verify `API_TOKEN` matches between `.env` and requests.

## Testing & CI

GitHub Actions runs static checks (`pyflakes`) and backend tests (`pytest`) automatically on each push. Locally you can run:

```bash
docker compose run --rm backend pytest -q
```

