# Exposé : Maîtriser Elasticsearch

## 1. Introduction
Elasticsearch est un moteur de recherche et d’analyse distribué, open source, basé sur Apache Lucene. Il permet de stocker, rechercher et analyser de grandes quantités de données rapidement et en quasi temps réel.

### Cas d’usage
- Recherche de texte (sites web, e-commerce)
- Analyse de logs (SIEM, monitoring)
- Analytics temps réel (dashboards)

---

## Schéma général d'un cluster Elasticsearch

```mermaid
graph TD;
  A[Client/API] -->|requêtes| B[Node 1 (Master)]
  A -->|requêtes| C[Node 2 (Data)]
  A -->|requêtes| D[Node 3 (Data)]
  B --> E[Index 1: Shard 1, Shard 2, Replica]
  C --> F[Index 2: Shard 1, Replica]
  D --> G[Index 3: Shard 1, Shard 2]
```


---

## 2. Concepts Clés

### Cluster, Node, Index, Shard, Replica
- **Cluster** : Ensemble de nœuds travaillant ensemble.
- **Node** : Instance d’Elasticsearch (machine physique ou virtuelle).
- **Index** : Base logique contenant des documents.
- **Shard** : Partition d’un index pour la distribution.
- **Replica** : Copie d’un shard pour la tolérance aux pannes.

### Document, Mapping, Type
- **Document** : Unité de données (format JSON).
- **Mapping** : Schéma des documents (types de champs).
- **Type** : Catégorie de documents (déprécié depuis ES 7).

### Analyseur, Tokenizer, Filtres
- **Analyseur** : Prépare le texte pour la recherche (découpe, normalise).
- **Tokenizer** : Découpe le texte en tokens.
- **Filtres** : Modifient les tokens (minuscules, stopwords, etc.).

#### Exemple d'analyseur
Texte : "Les Chats dorment beaucoup."
1. Tokenizer : ["Les", "Chats", "dorment", "beaucoup"]
2. Filtres : ["les", "chats", "dorment", "beaucoup"] (minuscule)
3. Stopwords : ["chats", "dorment", "beaucoup"] (suppression de "les")

**But** : Améliorer la pertinence des recherches.

### API REST & Requêtes JSON
- Communication via HTTP/JSON (CRUD, recherche, agrégations).

#### Exemple de requête avancée (booléenne)
```json
GET /mon_index/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "nom": "Alice" } },
        { "range": { "age": { "gte": 25 } } }
      ],
      "must_not": [
        { "term": { "status": "inactif" } }
      ]
    }
  }
}
```

---

## 3. Fonctionnalités Principales
- **Recherche full-text** : Puissante, tolérante aux fautes.
- **Recherche structurée** : Filtres, booléens, plages.
- **Agrégations** : Statistiques, regroupements, analytics.
- **Indexation en temps réel** : Données disponibles quasi instantanément.
- **Scalabilité** : Ajout de nœuds facile.
- **Tolérance aux pannes** : Réplication automatique.

---

## 4. Écosystème Elastic Stack
- **Kibana** : Visualisation et exploration des données.
- **Logstash** : Pipeline d’ingestion et de transformation.
- **Beats** : Collecte légère de données.
- **Intégrations** : Clients pour Python, Java, etc.

---

## 5. Prise en Main (TP)

### Installation rapide
- Docker :
  ```bash
  docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.13.0
  ```
- Accès : http://localhost:9200

### Indexation et Recherche
- Créer un index :
  ```bash
  PUT /mon_index
  ```
- Indexer un document :
  ```bash
  POST /mon_index/_doc
  {
    "nom": "Alice",
    "age": 30
  }
  ```
- Rechercher :
  ```bash
  GET /mon_index/_search
  {
    "query": { "match": { "nom": "Alice" } }
  }
  ```

### TP : Mapping personnalisé
- Créer un mapping explicite :
  ```bash
  PUT /utilisateurs
  {
    "mappings": {
      "properties": {
        "nom": { "type": "text" },
        "age": { "type": "integer" },
        "date_inscription": { "type": "date" }
      }
    }
  }
  ```
- Indexer et rechercher en utilisant ce mapping.

### Agrégations
- Exemple :
  ```bash
  GET /mon_index/_search
  {
    "size": 0,
    "aggs": {
      "age_moyen": { "avg": { "field": "age" } }
    }
  }
  ```

### Visualisation (Kibana)
- Accès à Kibana : http://localhost:5601
- Création de dashboard, visualisation de données.

### Intégration avec Python (elasticsearch-py)
```python
from elasticsearch import Elasticsearch
es = Elasticsearch('http://localhost:9200')
doc = {"nom": "Alice", "age": 30}
es.index(index="mon_index", document=doc)
res = es.search(index="mon_index", query={"match": {"nom": "Alice"}})
print(res['hits']['hits'])
```

---

## 6. Bonnes Pratiques & Conseils
- Définir le mapping explicitement pour les champs critiques.
- Utiliser les agrégations avec modération (coût mémoire).
- Surveiller la santé du cluster (shards, nœuds).
- Sécuriser l’accès (authentification, SSL).

- Utiliser l’API _cat pour surveiller :
  ```bash
  GET /_cat/indices?v
  GET /_cat/health?v
  GET /_cat/nodes?v
  ```
- Gérer les erreurs : surveiller les logs, utiliser les alertes Kibana.
- Optimiser les requêtes : préférer les filtres pour les recherches exactes, limiter la taille des résultats.

---

## 7. Ressources pour Approfondir
- [Documentation officielle Elasticsearch (fr)](https://www.elastic.co/guide/fr/elasticsearch/reference/current/index.html)
- [Elasticsearch: The Definitive Guide (en)](https://www.elastic.co/guide/en/elasticsearch/guide/current/index.html)
- [Cours OpenClassrooms](https://openclassrooms.com/fr/courses/6204541-initiez-vous-a-elasticsearch)
- [Playground Elastic](https://www.elastic.co/fr/cloud/elasticsearch-service/signup)

---

## 8. Questions Fréquentes
- Comment choisir le nombre de shards ?
- Comment optimiser les performances ?
- Que faire en cas de panne d’un nœud ?

- Comment fonctionne le scoring ?
- Comment gérer les données volumineuses (hot/warm/cold nodes) ?
- Comment faire des recherches sur des champs imbriqués (nested) ?

---

## 9. Aller plus loin

- Découvrir les scripts dans les requêtes (Painless)
- Utiliser les pipelines d’ingestion pour transformer les données à l’indexation
- Sécuriser avec Elastic Security (X-Pack)
- Tester les snapshots et la restauration

---

**Pour progresser : pratique régulière, lecture de la doc officielle, et exploration de cas concrets !**

---

**N’hésite pas à adapter ce document pour ton PPT et ton TP !**
