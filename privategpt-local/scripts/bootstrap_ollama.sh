#!/usr/bin/env bash
set -euo pipefail

MODEL="${LLM_MODEL:-llama3.1}"

until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
  echo "Waiting for Ollama to be ready..."
  sleep 2
done

echo "Pulling primary model: ${MODEL}"
ollama pull "${MODEL}"

echo "Ensuring mistral fallback is available"
ollama pull mistral

echo "Ollama models ready."
