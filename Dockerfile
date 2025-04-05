# Use Python 3.8 slim image as the base image for the build stage
FROM python:3.8-slim AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file to cache dependencies
COPY requirements.txt ./

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --default-timeout=300 --retries=10 --no-cache-dir -r requirements.txt

# Use a base image with TensorFlow for the production stage
FROM tensorflow/tensorflow:2.8.0

# Set the working directory inside the container
WORKDIR /app

# Copy the installed dependencies from the builder image to the app container
COPY --from=builder /app /app

# Optionally, move files as needed (example here for 'training_logic')
RUN mv /app/backend/training_logic /app/backend/trading_logic || true

# Set the PYTHONPATH to include your app directory and backend directory
ENV PYTHONPATH=/app:/app/backend

# Expose port 5000 for the Flask application
EXPOSE 5000

# Environment variables for webhook secret and Binance API keys
ENV WEBHOOK_SECRET=your_webhook_secret_key
ENV BINANCE_API_KEY=your_binance_api_key
ENV BINANCE_SECRET_KEY=your_binance_api_secret

# Set a health check to verify that the app is running
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --silent --fail http://localhost:5000/health || exit 1

# Start the Flask application with Gunicorn (multi-threaded for production)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
