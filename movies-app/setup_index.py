"""
setup_index.py
Crée l'index 'movies' dans Elasticsearch avec un mapping optimisé.
Exécuter AVANT seed_data.py.

Usage : python setup_index.py
"""

import os
from elasticsearch import Elasticsearch

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
INDEX_NAME = "movies"

# Mapping de l'index — définit comment chaque champ est stocké/analysé
MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                # Analyseur français : minuscules + stopwords + stemming
                "french_custom": {
                    "type": "french",
                    "stopwords": "_french_"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            # Champs texte — analysés pour la recherche full-text
            "title": {
                "type": "text",
                "analyzer": "french_custom",
                "fields": {
                    # Sous-champ keyword pour le tri et les agrégations exactes
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {
                "type": "text",
                "analyzer": "french_custom"
            },
            "director": {
                "type": "keyword"          # Valeur exacte (pas d'analyse)
            },
            "actors": {
                "type": "keyword"          # Tableau de keywords (multi-valeurs)
            },
            "genre": {
                "type": "keyword"          # Filtrage et agrégations
            },
            "language": {
                "type": "keyword"
            },
            # Champs numériques — pour les filtres et les stats
            "year": {
                "type": "integer"
            },
            "rating": {
                "type": "float"
            },
            "votes": {
                "type": "integer"
            },
            # URL de l'affiche — non indexé (juste stocké)
            "poster_url": {
                "type": "keyword",
                "index": False
            }
        }
    }
}


def create_index():
    es = Elasticsearch(ES_URL)

    # Vérifier que ES est accessible
    if not es.ping():
        print("❌ Elasticsearch non accessible sur", ES_URL)
        print("   Assure-toi que Docker tourne : docker-compose up -d")
        return

    print(f"✅ Connecté à Elasticsearch ({ES_URL})")

    # Supprimer l'index s'il existe déjà (reset propre)
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"🗑️  Index '{INDEX_NAME}' supprimé (reset)")

    # Créer l'index avec le mapping
    es.indices.create(index=INDEX_NAME, body=MAPPING)
    print(f"✅ Index '{INDEX_NAME}' créé avec le mapping !")

    # Vérifier le résultat
    info = es.indices.get(index=INDEX_NAME)
    props = info[INDEX_NAME]["mappings"]["properties"]
    print(f"\n📋 Champs indexés : {list(props.keys())}")
    print("\n👉 Lance maintenant : python seed_data.py")


if __name__ == "__main__":
    create_index()
