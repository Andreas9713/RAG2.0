PROJECT_NAME=privategpt-local
DOCKER_COMPOSE=docker compose
LLM_MODEL?=llama3.1
API_TOKEN?=$(shell grep -E '^API_TOKEN=' .env 2>/dev/null | cut -d= -f2-)

.PHONY: bootstrap up down logs ingest query reset

bootstrap:
	@echo "[bootstrap] Starting Ollama service and pulling models..."
	$(DOCKER_COMPOSE) up -d ollama
	./scripts/bootstrap_ollama.sh
	@echo "[bootstrap] Building images..."
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

ingest:
	@if [ -z "$(path)" ]; then echo "Usage: make ingest path=/absolute/path"; exit 1; fi
	@if [ -z "$(API_TOKEN)" ]; then echo "API_TOKEN is not set"; exit 1; fi
	curl -X POST http://localhost:8000/ingest \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $(API_TOKEN)" \
	-d '{"paths": ["$(path)"]}'

query:
	@if [ -z "$(question)" ]; then echo "Usage: make query question=\"...\" [top_k=3]"; exit 1; fi
	@if [ -z "$(API_TOKEN)" ]; then echo "API_TOKEN is not set"; exit 1; fi
	curl -X POST http://localhost:8000/query \
	-H "Content-Type: application/json" \
	-H "Authorization: $(API_TOKEN)" \
	-d '{"question": "$(question)", "top_k": $(or $(top_k),5)}'

reset: down
	@echo "Removing persisted volumes..."
	rm -rf chroma ollama
	@echo "Done."
