FROM python:3.10-bullseye

WORKDIR /app

ENV CUDA_VISIBLE_DEVICES=-1 \
    TF_CPP_MIN_LOG_LEVEL=3 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libatlas-base-dev \
    libopenblas-dev \
    supervisor && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./backend /app/backend
COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app/backend/ai_models"

RUN find /app -name '__pycache__' -type d -exec rm -r {} +

COPY . /app

EXPOSE 5000 8765

COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
