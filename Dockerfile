# On utilise une image Python légère
FROM python:3.11-slim

# On définit le dossier de travail dans le conteneur
WORKDIR /app

# On installe les dépendances système nécessaires (ex: pour SQLite ou compilation)
RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# On copie d'abord requirements.txt pour profiter du cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le reste du projet
COPY . .

# On crée le dossier /data qui sera persistant sur Hugging Face
RUN mkdir -p /data

# On expose le port 8000 (celui de FastAPI)
EXPOSE 8000

# On lance l'application avec Uvicorn
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]