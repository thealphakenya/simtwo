# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV FLASK_APP=backend.app  # Updated for module-based import
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PYTHONPATH=/app:/app/backend  # Ensures backend modules are found

# Expose Flask's default port
EXPOSE 5000

# Run the application using Gunicorn (recommended for production)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
