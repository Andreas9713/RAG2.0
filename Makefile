ENV_FILE ?= .env
DOCKER_COMPOSE ?= docker compose

.PHONY: run stop ingest reset bootstrap

run:
$(DOCKER_COMPOSE) --env-file $(ENV_FILE) up -d --build

stop:
$(DOCKER_COMPOSE) --env-file $(ENV_FILE) down

ingest:
ifndef PATHS
$(error PATHS variable is required. Example: make ingest PATHS="data/documents/guide.pdf")
endif
$(DOCKER_COMPOSE) --env-file $(ENV_FILE) run --rm backend python -m backend.ingest --paths $(PATHS)

reset:
rm -rf data/chroma data/documents
mkdir -p data/chroma data/documents

bootstrap:
bash scripts/bootstrap_ollama.sh
