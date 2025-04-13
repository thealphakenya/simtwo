FROM python:3.10-slim

WORKDIR /app

ENV CUDA_VISIBLE_DEVICES=-1 \
    TF_CPP_MIN_LOG_LEVEL=3 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl build-essential libatlas-base-dev libopenblas-dev python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip

COPY ./backend /app/backend

ENV PYTHONPATH="${PYTHONPATH}:/app/backend/ai_models"

RUN python -m pip install --no-cache-dir -r requirements.txt

RUN find /app -name '__pycache__' -type d -exec rm -r {} +

COPY . /app

EXPOSE 5000 8765

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]