# Stage 1: Build dependencies (for smaller final image size)
FROM python:3.8-slim AS builder

WORKDIR /app

# Copy only the requirements file first to cache dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --default-timeout=300 --retries=10 --no-cache-dir -r requirements.txt

# Stage 2: The final production image
FROM tensorflow/tensorflow:2.8.0

WORKDIR /app

# Copy only necessary files from the builder stage
COPY --from=builder /app /app

# Optional: Rename training_logic if needed
RUN mv /app/backend/training_logic /app/backend/trading_logic || true

# Set Python path for imports
ENV PYTHONPATH=/app:/app/backend

# Expose port for Flask/Gunicorn
EXPOSE 5000

# Set environment variables
ENV WEBHOOK_SECRET=your_webhook_secret_key
ENV BINANCE_API_KEY=your_binance_api_key
ENV BINANCE_SECRET_KEY=your_binance_api_secret

# Healthcheck to ensure the app is running
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --silent --fail http://localhost:5000/health || exit 1

# Start the app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
