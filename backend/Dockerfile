FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --reload : le serveur redemarre tout seul quand un fichier change
# --reload-dir app : seulement le code du serveur ; un fichier de test modifie ne le fait plus redemarrer
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app"]
