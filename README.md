# CineSearch — Recherche de films avec Elasticsearch

CineSearch est une application pédagogique de recherche et de recommandation de films. Elle combine une interface Flask, Elasticsearch et Kibana pour illustrer la recherche full-text, les filtres, les recommandations et les agrégations.

## Fonctionnalités

- Recherche full-text dans le titre, le synopsis, le réalisateur et les acteurs.
- Tolérance aux fautes de frappe avec `fuzziness`.
- Filtres par genre, année et note minimale.
- Autocomplétion des titres.
- Recommandations de films similaires avec `more_like_this`.
- Statistiques Elasticsearch :
  - répartition par genre et par langue ;
  - note moyenne et statistiques globales ;
  - films les mieux notés.
- Affichage de la requête Elasticsearch générée dans l’interface.
- Interface Kibana pour explorer les données.

## Architecture

```text
Navigateur
    │
    └── Flask (http://localhost:5000)
            │
            └── Elasticsearch (http://localhost:9200)
                    │
                    └── Index movies

Kibana (http://localhost:5601) ───┘
```

Les services sont définis dans [`docker-compose.yml`](docker-compose.yml) :

| Service | Rôle | Port |
|---|---|---:|
| `elasticsearch` | Moteur de recherche et stockage | 9200 |
| `kibana` | Exploration et visualisation | 5601 |
| `setup-index` | Création de l’index et du mapping | — |
| `movies-app` | API Flask et frontend | 5000 |
| `fetch-tmdb` | Import optionnel depuis TMDB | — |

Les données Elasticsearch sont conservées dans le volume Docker `es_data`.

## Prérequis

- Windows 10/11 ;
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) démarré ;
- Docker Compose ;
- une clé API TMDB uniquement pour l’import depuis TMDB.

## Installation et démarrage rapide

Depuis le dossier du projet :

```powershell
docker-compose up -d --build
```

Après le démarrage :

- Application : <http://localhost:5000>
- Elasticsearch : <http://localhost:9200>
- Kibana : <http://localhost:5601>

Le service `setup-index` crée automatiquement l’index `movies` avant le démarrage de l’application.

## Charger les données

### Option 1 — Jeu de données local

Cette option ajoute les films intégrés dans [`movies-app/seed_data.py`](movies-app/seed_data.py). Elle est adaptée à une démonstration sans clé API.

```powershell
docker-compose run --rm setup-index
docker-compose run --rm movies-app python seed_data.py
```

Si vous exécutez les scripts directement sur Windows, installez d’abord les dépendances :

```powershell
cd movies-app
pip install -r requirements.txt
python setup_index.py
python seed_data.py
python app.py
```

Dans ce cas, Elasticsearch doit être accessible sur `http://localhost:9200`.

### Option 2 — Import depuis TMDB

1. Copiez [`.env.example`](.env.example) vers `.env`.
2. Renseignez `TMDB_API_KEY` avec votre clé personnelle.
3. Lancez l’import :

```powershell
docker-compose run --rm fetch-tmdb
```

Le script récupère cinq pages de films populaires en français, enrichit les données avec les genres, le réalisateur et les acteurs, puis remplace le contenu de l’index `movies`.

> Ne versionnez jamais `.env` et ne partagez pas votre clé API.

## API Flask

Toutes les routes sont implémentées dans [`movies-app/app.py`](movies-app/app.py).

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/search` | Recherche et filtres |
| `GET` | `/api/autocomplete?q=...` | Suggestions de titres |
| `GET` | `/api/movie/<id>` | Détails d’un film |
| `GET` | `/api/recommendations/<id>` | Films similaires |
| `GET` | `/api/stats` | Agrégations et statistiques |
| `GET` | `/api/health` | État d’Elasticsearch et nombre de films |

### Paramètres de recherche

`/api/search` accepte les paramètres suivants :

- `q` : texte libre ;
- `genre` : genre exact ;
- `year_min` et `year_max` : bornes d’année ;
- `rating_min` : note minimale ;
- `size` : nombre de résultats, 12 par défaut.

Exemple :

```text
http://localhost:5000/api/search?q=espace&genre=Science-Fiction&rating_min=8
```

## Index Elasticsearch

L’index `movies` est créé par [`movies-app/setup_index.py`](movies-app/setup_index.py) avec un analyseur français.

Champs principaux :

| Champ | Type | Usage |
|---|---|---|
| `title` | `text` + `keyword` | Recherche, tri et autocomplétion |
| `description` | `text` | Recherche full-text |
| `director`, `actors`, `genre`, `language` | `keyword` | Filtres et agrégations |
| `year`, `votes` | `integer` | Filtres et statistiques |
| `rating` | `float` | Filtre et statistiques |
| `poster_url` | `keyword` non indexé | Affichage de l’affiche |

Pour recréer proprement l’index :

```powershell
docker-compose run --rm setup-index
```

Cette commande supprime l’index existant avant de le recréer. Il faut ensuite relancer l’un des imports de données.

## Commandes utiles

```powershell
# Voir l’état des services
docker-compose ps

# Voir les logs de l’application
docker-compose logs -f movies-app

# Voir les logs Elasticsearch
docker-compose logs -f elasticsearch

# Arrêter les services sans supprimer les données
docker-compose down

# Arrêter les services et supprimer les données Elasticsearch
docker-compose down -v
```

## Documentation complémentaire

- [`expose-elasticsearch.md`](expose-elasticsearch.md) : notions Elasticsearch, requêtes, agrégations et bonnes pratiques.
- [Documentation officielle Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Documentation TMDB API](https://developer.themoviedb.org/docs)

## Limites et sécurité

La configuration Docker est prévue pour un environnement local de démonstration : la sécurité Elasticsearch est désactivée et les ports sont exposés sur la machine. Pour une mise en production, activez l’authentification et TLS, protégez l’API Flask et configurez un réseau sécurisé.

## Licence et données

Les informations de films et les affiches importées depuis TMDB restent soumises aux conditions d’utilisation de [TMDB](https://www.themoviedb.org/documentation/api/terms-of-use).
