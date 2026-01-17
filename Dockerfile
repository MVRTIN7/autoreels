FROM python:3.11-slim

# Instalar ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Crear carpeta app
WORKDIR /app

# Copiar archivos
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto
EXPOSE 8080

# Ejecutar app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
