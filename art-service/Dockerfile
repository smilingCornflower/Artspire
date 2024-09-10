FROM python:3.12.5-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential libpq-dev \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

# COPY secrets /app/secrets
COPY src /app/src

WORKDIR /app/src

EXPOSE 8000

CMD ["python3", "main.py"]
