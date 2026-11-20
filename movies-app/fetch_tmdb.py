"""
fetch_tmdb.py
Récupère les films populaires depuis l'API TMDB et les indexe dans Elasticsearch.

Usage :
  1. Mets ta clé API TMDB dans la variable TMDB_API_KEY ci-dessous
  2. Lance : python fetch_tmdb.py

API TMDB utilisée :
  - GET /movie/popular           → liste des films populaires (paginée)
  - GET /movie/{id}?append_to_response=credits → détails + casting
  - Images : https://image.tmdb.org/t/p/w500{poster_path}

Elasticsearch :
  - Index cible : movies
  - Enrichissement : genres (noms), réalisateur, acteurs principaux, langue
"""

import os
import time
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# ─────────────────────────────────────────────────────
# ⚙️  CONFIGURATION — via variables d'environnement
#     En local  : crée un fichier .env et mets ta clé
#     En Docker : passe TMDB_API_KEY dans docker-compose
# ─────────────────────────────────────────────────────
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

TMDB_BASE    = "https://api.themoviedb.org/3"
TMDB_IMG     = "https://image.tmdb.org/t/p/w500"
LANGUAGE     = "fr-FR"          # Titres et descriptions en français
PAGES        = 5                # Nombre de pages à récupérer (20 films/page → 100 films)
DELAY        = 0.25             # Pause entre chaque appel API (éviter le rate limit)

ES_URL       = os.environ.get("ES_URL", "http://localhost:9200")
INDEX        = "movies"

# Correspondance code langue ISO → nom lisible
LANG_MAP = {
    "fr": "Français",
    "en": "Anglais",
    "ja": "Japonais",
    "ko": "Coréen",
    "es": "Espagnol",
    "de": "Allemand",
    "it": "Italien",
    "pt": "Portugais",
    "zh": "Chinois",
    "hi": "Hindi",
    "ar": "Arabe",
    "ru": "Russe",
    "da": "Danois",
    "sv": "Suédois",
    "nl": "Néerlandais",
}


# ─────────────────────────────────────────────────────
# APPELS API TMDB
# ─────────────────────────────────────────────────────

def tmdb_get(endpoint: str, params: dict = None) -> dict | None:
    """Effectue un appel GET à l'API TMDB avec gestion des erreurs."""
    url = f"{TMDB_BASE}{endpoint}"
    default_params = {
        "api_key": TMDB_API_KEY,
        "language": LANGUAGE,
    }
    if params:
        default_params.update(params)

    try:
        r = requests.get(url, params=default_params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 401:
            print(f"\n❌ Clé API invalide ! Vérifie TMDB_API_KEY dans ce fichier.")
        elif r.status_code == 429:
            print(f"⏳ Rate limit atteint, pause 10s...")
            time.sleep(10)
            return tmdb_get(endpoint, params)
        else:
            print(f"⚠️  Erreur HTTP {r.status_code} sur {endpoint}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de joindre TMDB. Vérifie ta connexion internet.")
        return None


def fetch_popular_movie_ids(pages: int) -> list[int]:
    """Récupère les IDs des films populaires sur N pages."""
    ids = []
    print(f"\n📡 Récupération des films populaires ({pages} pages × 20 films)...")

    for page in range(1, pages + 1):
        data = tmdb_get("/movie/popular", {"page": page})
        if not data:
            break

        page_ids = [m["id"] for m in data.get("results", [])]
        ids.extend(page_ids)
        print(f"   Page {page}/{pages} → {len(page_ids)} films récupérés")
        time.sleep(DELAY)

    print(f"✅ {len(ids)} IDs collectés\n")
    return ids


def fetch_movie_details(movie_id: int) -> dict | None:
    """
    Récupère les détails complets d'un film :
    genres (noms), crédits (réalisateur + acteurs), budget, etc.
    Utilise append_to_response pour faire 1 seul appel au lieu de 2.
    """
    data = tmdb_get(f"/movie/{movie_id}", {
        "append_to_response": "credits"
    })
    return data


def parse_movie(raw: dict) -> dict | None:
    """
    Transforme la réponse TMDB brute en document prêt pour Elasticsearch.
    Ne conserve que les champs utiles pour la recherche et les recommandations.
    """
    if not raw:
        return None

    # -- Titre et description
    title = raw.get("title") or raw.get("original_title", "")
    description = raw.get("overview", "").strip()
    if not title or not description:
        return None  # On saute les films sans synopsis

    # -- Année (extrait de "2023-07-19")
    release = raw.get("release_date", "")
    year = int(release[:4]) if release and len(release) >= 4 else None

    # -- Note et votes
    rating = round(raw.get("vote_average", 0.0), 1)
    votes  = raw.get("vote_count", 0)

    # -- Genres : TMDB retourne [{"id":28,"name":"Action"}, ...]
    genres = [g["name"] for g in raw.get("genres", [])]

    # -- Langue originale
    lang_code = raw.get("original_language", "")
    language  = LANG_MAP.get(lang_code, lang_code.upper())

    # -- Affiche
    poster_path = raw.get("poster_path", "")
    poster_url  = f"{TMDB_IMG}{poster_path}" if poster_path else ""

    # -- Crédits (réalisateur + top 5 acteurs)
    credits    = raw.get("credits", {})
    crew       = credits.get("crew", [])
    cast       = credits.get("cast", [])

    # Cherche le/les réalisateur(s) dans l'équipe technique
    directors = [p["name"] for p in crew if p.get("job") == "Director"]
    director  = " & ".join(directors) if directors else "Inconnu"

    # Top 5 acteurs (classés par ordre d'importance)
    actors = [p["name"] for p in sorted(cast, key=lambda x: x.get("order", 99))[:5]]

    # -- Document final pour ES
    return {
        "tmdb_id":     raw.get("id"),
        "title":       title,
        "description": description,
        "genre":       genres,
        "year":        year,
        "rating":      rating,
        "votes":       votes,
        "director":    director,
        "actors":      actors,
        "language":    language,
        "poster_url":  poster_url,
        "popularity":  round(raw.get("popularity", 0.0), 2),
    }


# ─────────────────────────────────────────────────────
# INDEXATION ELASTICSEARCH
# ─────────────────────────────────────────────────────

def index_movies(movies: list[dict]) -> None:
    """Insère tous les films dans Elasticsearch en une seule opération bulk."""
    es = Elasticsearch(ES_URL)

    if not es.ping():
        print("❌ Elasticsearch non accessible. Lance d'abord : docker-compose up -d")
        return

    if not es.indices.exists(index=INDEX):
        print(f"❌ L'index '{INDEX}' n'existe pas. Lance d'abord : python setup_index.py")
        return

    # Vider l'index avant de réindexer (évite les doublons)
    es.delete_by_query(index=INDEX, body={"query": {"match_all": {}}})
    es.indices.refresh(index=INDEX)
    print(f"🗑️  Index '{INDEX}' vidé (prêt pour les nouveaux films)")

    # Préparer les actions pour le bulk insert
    actions = [
        {"_index": INDEX, "_source": movie}
        for movie in movies
    ]

    success, errors = bulk(es, actions)
    es.indices.refresh(index=INDEX)

    print(f"\n✅ {success} films indexés dans Elasticsearch !")
    if errors:
        print(f"⚠️  {len(errors)} erreurs lors de l'indexation :")
        for err in errors[:5]:
            print(f"   {err}")

    count = es.count(index=INDEX)["count"]
    print(f"📊 Total dans l'index '{INDEX}' : {count} films")


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────

def main():
    print("═" * 55)
    print("  🎬 TMDB → Elasticsearch : Import films populaires")
    print("═" * 55)

    # Vérifier que la clé API a été configurée
    if not TMDB_API_KEY or TMDB_API_KEY == "COLLE_TA_CLÉ_API_ICI":
        print("\n❌ Tu n'as pas encore configuré ta clé API TMDB !")
        print("   → En local  : ajoute TMDB_API_KEY=ta_cle dans le fichier .env")
        print("   → En Docker : docker-compose run --rm fetch-tmdb (avec .env rempli)")
        print("   Obtiens ta clé sur : https://www.themoviedb.org/settings/api")
        return

    # Étape 1 : Récupérer les IDs des films populaires
    movie_ids = fetch_popular_movie_ids(PAGES)
    if not movie_ids:
        print("❌ Aucun film récupéré depuis TMDB.")
        return

    # Étape 2 : Récupérer les détails de chaque film
    movies = []
    errors = 0
    print(f"🔍 Récupération des détails pour {len(movie_ids)} films...\n")

    for i, movie_id in enumerate(movie_ids, 1):
        raw = fetch_movie_details(movie_id)
        movie = parse_movie(raw)

        if movie:
            movies.append(movie)
            title_display = movie["title"][:40].ljust(40)
            print(f"   [{i:3}/{len(movie_ids)}] ✅ {title_display} ({movie['year']}) ⭐{movie['rating']}")
        else:
            errors += 1
            print(f"   [{i:3}/{len(movie_ids)}] ⏭️  Film ignoré (pas de synopsis)")

        time.sleep(DELAY)  # Respecter le rate limit TMDB

    print(f"\n📦 {len(movies)} films prêts à indexer ({errors} ignorés sans synopsis)")

    # Étape 3 : Indexer dans Elasticsearch
    print("\n⚡ Indexation dans Elasticsearch...")
    index_movies(movies)

    print("\n🚀 Tout est prêt ! Lance maintenant : python app.py")
    print("   Puis ouvre : http://localhost:5000")
    print("═" * 55)


if __name__ == "__main__":
    main()
