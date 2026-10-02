# rafals - IA de moderation des avis (Detoxify multilingue), sans carte graphique (processeur seulement)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Telecharge le modele une fois, pendant la construction (environ 1 Go) : rien a telecharger au demarrage
RUN python -c "from detoxify import Detoxify; Detoxify('multilingual')"

COPY app.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
