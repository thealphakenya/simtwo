# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Flask to listen on all network interfaces and run in production mode
ENV FLASK_APP=backend/app.py
# Ensure FLASK_APP points to the correct location

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Expose port 5000 for Flask
EXPOSE 5000

# Run Flask in production mode
CMD ["flask", "run", "--host=0.0.0.0"]
