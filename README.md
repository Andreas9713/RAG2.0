# PrivateGPT Local

Solution RAG locale prête à l'emploi avec FastAPI, LangChain, ChromaDB et une interface Streamlit. L'ensemble fonctionne en containers Docker et s'appuie sur Ollama pour exécuter un LLM local (modèle par défaut `llama3.1`, repli `mistral`).

## Architecture
- **Ollama** : héberge les modèles `llama3.1` et `mistral`.
- **Backend FastAPI** : endpoints d'ingestion et de question/réponse, stockage vectoriel via ChromaDB, embeddings `all-MiniLM-L6-v2` (SentenceTransformers).
- **ChromaDB** : persistance des embeddings dans `./data/chroma`.
- **Streamlit** : interface simple pour charger des documents et chatter avec le modèle.

## Prérequis
- Docker et Docker Compose v2
- `make`
- [Ollama](https://ollama.com/download) installé sur la machine hôte
- Accès aux modèles `llama3.1` et `mistral` (script fourni)

## Initialisation
1. Copier le fichier d'exemple et ajuster les variables :
   ```bash
   cp .env.example .env
   # modifier API_TOKEN si nécessaire
   ```
2. Récupérer les modèles Ollama (nécessite un accès réseau) :
   ```bash
   make bootstrap
   ```
3. Démarrer la stack :
   ```bash
   make run
   ```
4. L'API FastAPI est disponible sur http://localhost:8000 et l'interface Streamlit sur http://localhost:8501.

## Utilisation
### Authentification
Toutes les routes sensibles requièrent l'en-tête `x-api-token` avec la valeur `API_TOKEN` définie dans `.env`.

### Ingestion
- **Depuis l'UI** : charger des fichiers (PDF, TXT, DOCX, Markdown) puis cliquer sur « Ingérer les fichiers ».
- **Depuis l'API** :
  ```bash
  curl -X POST http://localhost:8000/ingest \
    -H "Content-Type: application/json" \
    -H "x-api-token: <API_TOKEN>" \
    -d '{"paths": ["/data/documents/mon_fichier.pdf"]}'
  ```
- **Depuis Make** :
  ```bash
  make ingest PATHS="/data/documents/mon_fichier.pdf /data/documents/autre.md"
  ```

Les documents sont nettoyés, découpés (800 tokens, overlap 120) puis indexés dans Chroma.

### Pose de questions
Envoyer une requête `POST /query` :
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "x-api-token: <API_TOKEN>" \
  -d '{"question": "Quelle est la procédure ?", "top_k": 5}'
```
La réponse contient le texte généré et les sources associées.

### Endpoints
| Méthode | Route     | Description                               |
|---------|-----------|-------------------------------------------|
| GET     | `/health` | Vérifie l'état du backend                  |
| POST    | `/ingest` | Lance l'ingestion des fichiers fournis     |
| POST    | `/query`  | Retourne une réponse et les passages cités |

## Tests
Exécuter les tests unitaires (smoke) :
```bash
pip install -r requirements.txt
pytest
```
Ou via Docker :
```bash
docker compose run --rm backend pytest
```

## Gestion de la stack
- `make run` : build + démarrage en arrière-plan
- `make stop` : arrêt des containers
- `make ingest PATHS="..."` : ingestion manuelle par CLI
- `make reset` : purge des données Chroma et documents

## Dépannage
- **Modèle introuvable** : exécuter `make bootstrap` après avoir installé Ollama.
- **Erreur d'authentification** : vérifier la variable `API_TOKEN` côté backend et client.
- **Pas de réponses pertinentes** : s'assurer que des documents ont été ingérés et que `./data/chroma` contient des embeddings.
- **Problèmes de dépendances** : reconstruire les images avec `make stop && make run`.
- **Téléchargement des embeddings** : le premier lancement de SentenceTransformers peut nécessiter un accès réseau pour récupérer `all-MiniLM-L6-v2`. Pré-téléchargez le modèle ou placez-le dans `~/.cache/torch/sentence_transformers` pour un usage totalement hors-ligne.

## Sécurité & confidentialité
- Aucun appel vers des API externes n'est réalisé par l'application ; toutes les données restent sur la machine locale.
- Les fichiers sont stockés dans `./data/documents`. Supprimer ce dossier pour effacer toute trace.
