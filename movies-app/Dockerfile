# ─────────────────────────────────────────────
# Stage 1 : builder — installe les dépendances
# ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /install

# Copier uniquement requirements pour profiter du cache Docker
COPY requirements.txt .

# Installer dans un dossier isolé (pas dans le système)
RUN pip install --no-cache-dir --prefix=/install/packages -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2 : image finale — légère
# ─────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Récupérer les packages installés au stage 1
COPY --from=builder /install/packages /usr/local

# Copier le code de l'application
COPY . .

# Port exposé par Flask
EXPOSE 5000

# Variables d'environnement par défaut (surchargées par docker-compose)
ENV ES_URL=http://elasticsearch:9200 \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Healthcheck : vérifie que l'API répond
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Lancer l'application Flask
CMD ["python", "app.py"]
