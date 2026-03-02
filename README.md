# Demo pgvector + FastAPI + Docker Compose

Projet minimal pour tester rapidement la recherche vectorielle avec **PostgreSQL + pgvector** et un backend **FastAPI**, orchestrés avec **Docker Compose**.

## 1. Prérequis

- **Docker** et **Docker Compose** installés
- (Optionnel) Une clé API OpenAI dans la variable d'environnement `OPENAI_API_KEY` si vous voulez de "vrais" embeddings de texte.
  - Sans clé, des embeddings pseudo-aléatoires déterministes sont utilisés, ce qui reste suffisant pour tester l'intégration pgvector.

## 2. Structure du projet

- `docker-compose.yml` : services PostgreSQL + FastAPI
- `Dockerfile` : image pour l'API FastAPI
- `requirements.txt` : dépendances Python
- `db/init.sql` : création de l'extension pgvector + table `documents`
- `app/main.py` : API FastAPI (`/health`, `/search`)
- `app/vector_utils.py` : connexion PostgreSQL + fonctions embeddings & recherche
- `scripts/demo.py` : script de démonstration (insertion + recherche)

## 3. Lancer l'environnement

Depuis la racine du projet :

```bash
docker compose up --build
```

Cela va :

- Démarrer PostgreSQL avec l'extension **pgvector**
- Créer la base `vectordb` et la table `documents` via `db/init.sql`
- Exposer l'API FastAPI sur le port **8001** de l'hôte (mapping `8001:8000`)

Accès :

- API FastAPI : **http://localhost:8001**
- Page d'accueil (infos) : http://localhost:8001/
- Documentation Swagger : http://localhost:8001/docs
- Endpoint de santé : http://localhost:8001/health

## 4. Utiliser le script de démo (insertion + recherche)

Dans un autre terminal, une fois les services démarrés :

```bash
docker compose exec api python scripts/demo.py
```

Ce script va :

1. Se connecter à PostgreSQL
2. Insérer 3–5 documents dans la table `documents` avec un embedding chacun
3. Calculer un embedding pour une requête exemple
4. Faire une recherche vectorielle dans PostgreSQL et afficher le document le plus proche

Vous pouvez personnaliser le texte de requête en définissant `DEMO_QUERY` :

```bash
docker compose exec -e DEMO_QUERY="Je veux parler de PostgreSQL" api python scripts/demo.py
```

## 5. Tester l'API `/search`

1. Assurez-vous que la table `documents` contient des données :
  - Soit en exécutant `scripts/demo.py` (voir section précédente)
  - Soit en insérant vous-même des lignes dans `documents`
2. Appelez l'endpoint `/search` avec un JSON de la forme `{ "query": "..." }`.

### Exemple avec `curl`

```bash
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Quelle technologie pour faire de la recherche vectorielle ?"}'
```

Réponse typique :

```json
{
  "id": 3,
  "content": "pgvector permet de stocker et rechercher des embeddings.",
  "distance": 0.123456
}
```

### Exemple avec `httpie`

```bash
http POST :8001/search query="Je veux parler de PostgreSQL"
```

## 6. Variables d'environnement principales

- **Base de données** (définies dans `docker-compose.yml`) :
  - `POSTGRES_HOST=db`
  - `POSTGRES_PORT=5432`
  - `POSTGRES_DB=vectordb`
  - `POSTGRES_USER=postgres`
  - `POSTGRES_PASSWORD=postgres`
- **Embeddings** :
  - `OPENAI_API_KEY` (optionnel) : si défini, l'API utilise le modèle `text-embedding-3-small` pour calculer de "vrais" embeddings de texte.
  - Sinon, des vecteurs pseudo-aléatoires déterministes sont utilisés (mêmes entrées → mêmes vecteurs). La « similarité » n’est alors pas sémantique : le document renvoyé peut sembler sans rapport avec la requête ; avec une clé OpenAI, les résultats sont cohérents.

## 7. Arrêter les services

```bash
docker compose down
```

Pour supprimer aussi les données PostgreSQL persistées :

```bash
docker compose down -v
```

## 8. Résumé

- `docker compose up --build` pour tout lancer
- `docker compose exec api python scripts/demo.py` pour insérer des docs et tester une recherche vectorielle en ligne de commande
- `POST /search` sur `http://localhost:8000/search` pour tester la recherche via l'API FastAPI

