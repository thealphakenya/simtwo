FROM python:3.10-slim

WORKDIR /app

ENV CUDA_VISIBLE_DEVICES=-1 \
    TF_CPP_MIN_LOG_LEVEL=3 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ~/.docker && \
    echo '{
        "builder": {
            "gc": {
                "enabled": true
            }
        },
        "features": {
            "buildkit": true
        },
        "registry-mirrors": ["https://registry-1.docker.io"]
    }' > ~/.docker/config.json

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/
COPY ./frontend/build /app/frontend/build/
COPY ./backend /app/backend/

RUN pip install --no-cache-dir gunicorn

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:5000", "app:app"]