# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code
COPY . .

# Expose the application's port
EXPOSE 5000

# Default command to start the application
CMD ["python", "backend/app.py"]