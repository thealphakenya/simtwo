# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file from the backend directory
COPY backend/requirements.txt . 
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Install dependencies from the requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y numpy && pip install numpy==1.21.6

# Copy the entire application source code from the backend directory
COPY backend/ .

# Expose the application's port (assuming Flask uses 5000)
EXPOSE 5000

# Set environment variable for Flask to listen on all network interfaces
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Default command to start the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
