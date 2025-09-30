#!/usr/bin/env bash
set -euo pipefail

PRIMARY_MODEL=${OLLAMA_PRIMARY_MODEL:-llama3.1}
FALLBACK_MODEL=${OLLAMA_FALLBACK_MODEL:-mistral}

if ! command -v ollama >/dev/null 2>&1; then
  echo "[bootstrap] ollama n'est pas installé. Veuillez suivre https://ollama.com/download pour l'installer." >&2
  exit 1
fi

echo "[bootstrap] Récupération du modèle principal : ${PRIMARY_MODEL}"
ollama pull "${PRIMARY_MODEL}"

if [ "${FALLBACK_MODEL}" != "${PRIMARY_MODEL}" ]; then
  echo "[bootstrap] Récupération du modèle de secours : ${FALLBACK_MODEL}"
  ollama pull "${FALLBACK_MODEL}"
fi

echo "[bootstrap] Modèles prêts."
