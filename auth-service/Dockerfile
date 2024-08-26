FROM python:3.12.5-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential libpq-dev \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

WORKDIR /app/src

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]