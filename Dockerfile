FROM ubuntu:latest
LABEL authors="nicolas"

# Utiliser une image Python comme base
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements.txt et installer les dépendances
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copier le reste des fichiers de l'application
COPY . .

# Exposer le port sur lequel l'application va tourner
EXPOSE 5000

# Définir la commande par défaut pour lancer l'application
CMD ["python", "app.py"]
