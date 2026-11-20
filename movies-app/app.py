"""
app.py — Backend Flask pour l'app de recommandation de films
Démontre les fonctionnalités clés d'Elasticsearch :
  - Recherche full-text (match, multi_match)
  - Filtres (term, range)
  - Requête booléenne (bool query)
  - Recommandations (more_like_this)
  - Agrégations (terms, avg, stats)

Usage : python app.py
API disponible sur http://localhost:5000
"""

import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from elasticsearch import Elasticsearch

app = Flask(__name__)
CORS(app)

# Lire l'URL ES depuis la variable d'environnement (Docker) ou fallback local
ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
INDEX = "movies"

es = Elasticsearch(ES_URL)


# ─────────────────────────────────────────────
# PAGE PRINCIPALE
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Sert le frontend HTML."""
    return render_template("index.html")


# ─────────────────────────────────────────────
# ROUTE 1 : RECHERCHE FULL-TEXT + FILTRES
# ─────────────────────────────────────────────

@app.route("/api/search")
def search():
    """
    Recherche des films avec :
      - q       : texte libre (cherche dans title + description)
      - genre   : filtre par genre (keyword exact)
      - year_min / year_max : plage d'années
      - rating_min : note minimale
      - size    : nombre de résultats (défaut 12)

    Démonstration ES : bool query (must + filter)
    """
    q = request.args.get("q", "")
    genre = request.args.get("genre", "")
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    rating_min = request.args.get("rating_min", type=float)
    size = request.args.get("size", 12, type=int)

    # Construction de la requête bool
    must_clauses = []
    filter_clauses = []

    # -- Clause MUST : recherche full-text sur titre + description
    if q:
        must_clauses.append({
            "multi_match": {
                "query": q,
                "fields": ["title^3", "description", "director", "actors"],
                # ^3 = le titre a 3× plus de poids dans le score
                "fuzziness": "AUTO"  # Tolérance aux fautes de frappe
            }
        })

    # -- Clauses FILTER : filtres exacts (n'affectent pas le score)
    if genre:
        filter_clauses.append({"term": {"genre": genre}})

    if year_min or year_max:
        range_filter = {"range": {"year": {}}}
        if year_min:
            range_filter["range"]["year"]["gte"] = year_min
        if year_max:
            range_filter["range"]["year"]["lte"] = year_max
        filter_clauses.append(range_filter)

    if rating_min:
        filter_clauses.append({"range": {"rating": {"gte": rating_min}}})

    # Si aucun critère, retourner tous les films (match_all)
    if not must_clauses and not filter_clauses:
        es_query = {"match_all": {}}
    else:
        es_query = {
            "bool": {
                "must": must_clauses if must_clauses else [{"match_all": {}}],
                "filter": filter_clauses
            }
        }

    # Exécution de la requête
    response = es.search(
        index=INDEX,
        query=es_query,
        size=size,
        sort=[{"_score": "desc"}, {"rating": "desc"}]
    )

    hits = response["hits"]["hits"]
    total = response["hits"]["total"]["value"]

    movies = []
    for hit in hits:
        movie = hit["_source"]
        movie["id"] = hit["_id"]
        movie["score"] = round(hit["_score"] or 0, 2)
        movies.append(movie)

    return jsonify({
        "movies": movies,
        "total": total,
        "query": q
    })


# ─────────────────────────────────────────────
# ROUTE 2 : RECOMMANDATIONS (More Like This)
# ─────────────────────────────────────────────

@app.route("/api/recommendations/<movie_id>")
def recommendations(movie_id):
    """
    Retourne des films similaires à celui donné.
    Utilise la requête 'more_like_this' d'Elasticsearch :
    ES analyse les champs texte et genre du film source,
    puis trouve les films avec le plus de termes en commun.

    Démonstration ES : more_like_this query
    """
    try:
        # Récupérer le film source
        source_doc = es.get(index=INDEX, id=movie_id)
        source_movie = source_doc["_source"]

        response = es.search(
            index=INDEX,
            query={
                "more_like_this": {
                    "fields": ["title", "description", "genre", "director"],
                    "like": [{"_index": INDEX, "_id": movie_id}],
                    "min_term_freq": 1,       # Un terme suffit
                    "max_query_terms": 25,    # Jusqu'à 25 termes comparés
                    "min_doc_freq": 1,
                    "minimum_should_match": "20%"
                }
            },
            size=4  # 4 recommandations
        )

        recs = []
        for hit in response["hits"]["hits"]:
            movie = hit["_source"]
            movie["id"] = hit["_id"]
            movie["similarity_score"] = round(hit["_score"] or 0, 2)
            recs.append(movie)

        return jsonify({
            "source_movie": source_movie["title"],
            "recommendations": recs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 404


# ─────────────────────────────────────────────
# ROUTE 3 : AGRÉGATIONS (Stats & Graphiques)
# ─────────────────────────────────────────────

@app.route("/api/stats")
def stats():
    """
    Retourne des statistiques sur la collection de films.
    Utilise les agrégations Elasticsearch :
      - terms agg : top genres
      - avg agg   : note moyenne
      - stats agg : min/max/avg sur les années
      - top_hits  : meilleur film par genre

    Démonstration ES : aggregations
    """
    response = es.search(
        index=INDEX,
        size=0,  # On veut seulement les agrégations, pas les documents
        aggs={
            # Répartition par genre (top 10)
            "by_genre": {
                "terms": {
                    "field": "genre",
                    "size": 10
                },
                # Sous-agrégation : note moyenne par genre
                "aggs": {
                    "avg_rating": {
                        "avg": {"field": "rating"}
                    }
                }
            },
            # Statistiques globales sur les notes
            "rating_stats": {
                "stats": {"field": "rating"}
            },
            # Statistiques sur les années
            "year_stats": {
                "stats": {"field": "year"}
            },
            # Répartition par langue
            "by_language": {
                "terms": {
                    "field": "language",
                    "size": 10
                }
            },
            # Top 5 films les mieux notés
            "top_rated": {
                "top_hits": {
                    "size": 5,
                    "sort": [{"rating": "desc"}],
                    "_source": ["title", "rating", "genre", "year"]
                }
            }
        }
    )

    aggs = response["aggregations"]

    # Formater les données pour le frontend
    genres = [
        {
            "genre": bucket["key"],
            "count": bucket["doc_count"],
            "avg_rating": round(bucket["avg_rating"]["value"] or 0, 1)
        }
        for bucket in aggs["by_genre"]["buckets"]
    ]

    languages = [
        {"language": b["key"], "count": b["doc_count"]}
        for b in aggs["by_language"]["buckets"]
    ]

    top_rated = [
        hit["_source"]
        for hit in aggs["top_rated"]["hits"]["hits"]
    ]

    return jsonify({
        "genres": genres,
        "rating_stats": aggs["rating_stats"],
        "year_stats": aggs["year_stats"],
        "languages": languages,
        "top_rated": top_rated,
        "total_movies": response["hits"]["total"]["value"]
    })


# ─────────────────────────────────────────────
# ROUTE 4 : AUTOCOMPLETE (Suggest)
# ─────────────────────────────────────────────

@app.route("/api/autocomplete")
def autocomplete():
    """
    Suggestion d'autocomplete sur les titres de films.
    Utilise un prefix query sur le champ keyword.

    Démonstration ES : prefix query
    """
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify({"suggestions": []})

    response = es.search(
        index=INDEX,
        query={
            "match_phrase_prefix": {
                "title": {
                    "query": q,
                    "max_expansions": 10
                }
            }
        },
        _source=["title", "year", "genre"],
        size=5
    )

    suggestions = [
        {
            "title": hit["_source"]["title"],
            "year": hit["_source"]["year"],
            "genre": hit["_source"].get("genre", [])
        }
        for hit in response["hits"]["hits"]
    ]

    return jsonify({"suggestions": suggestions})


# ─────────────────────────────────────────────
# ROUTE 5 : DÉTAIL D'UN FILM
# ─────────────────────────────────────────────

@app.route("/api/movie/<movie_id>")
def get_movie(movie_id):
    """Retourne les détails complets d'un film par son ID."""
    try:
        doc = es.get(index=INDEX, id=movie_id)
        movie = doc["_source"]
        movie["id"] = doc["_id"]
        return jsonify(movie)
    except Exception as e:
        return jsonify({"error": "Film non trouvé"}), 404


# ─────────────────────────────────────────────
# ROUTE 6 : SANTÉ ES (Debug)
# ─────────────────────────────────────────────

@app.route("/api/health")
def health():
    """Vérifie l'état de connexion à Elasticsearch."""
    try:
        info = es.info()
        count = es.count(index=INDEX)
        return jsonify({
            "status": "ok",
            "es_version": info["version"]["number"],
            "movies_indexed": count["count"]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    print("🎬 Démarrage de l'app de recommandation de films")
    print("   Elasticsearch :", ES_URL)
    print("   Index         :", INDEX)
    print("   Frontend      : http://localhost:5000")
    print()

    # Vérifier la connexion ES au démarrage
    if es.ping():
        count = es.count(index=INDEX).get("count", 0)
        print(f"✅ Elasticsearch connecté — {count} films indexés")
    else:
        print("⚠️  Elasticsearch non accessible — lance docker-compose up -d")

    debug = os.environ.get("FLASK_ENV", "production") != "production"
    app.run(debug=debug, host="0.0.0.0", port=5000)
