FROM python:3.12-slim

# Timeout y reintentos altos para tolerar redes lentas: con los valores por defecto (15 s) pip corta descargas a mitad de camino.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
ARG REQUISITOS=requirements.txt
RUN pip install -r ${REQUISITOS}

COPY . .

EXPOSE 5000
# Producción: migra y levanta gunicorn. En desarrollo, docker-compose.yml reemplaza el comando.
CMD ["sh", "-c", "alembic upgrade head && gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:app"]
