FROM python:3.8-slim AS builder

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --default-timeout=300 --retries=10 --no-cache-dir -r requirements.txt

FROM tensorflow/tensorflow:2.8.0

WORKDIR /app

COPY --from=builder /app /app

RUN mv /app/backend/training_logic /app/backend/trading_logic || true

COPY wsgi.py /app/

ENV PYTHONPATH=/app:/app/backend

RUN pip show gunicorn || (echo "Gunicorn not found, installing it..." && pip install gunicorn)

EXPOSE 5000

ENV WEBHOOK_SECRET=your_webhook_secret_key
ENV BINANCE_API_KEY=your_binance_api_key
ENV BINANCE_SECRET_KEY=your_binance_api_secret

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --silent --fail http://localhost:5000/health || (echo "Healthcheck failed at $(date)" && exit 1)

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--log-level", "debug", "wsgi:app"]
