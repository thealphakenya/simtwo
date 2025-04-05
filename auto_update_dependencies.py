FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install the auto-update script
COPY auto_update_dependencies.py /app/auto_update_dependencies.py

# Run the auto-update script to update dependencies if necessary
RUN python /app/auto_update_dependencies.py

# Ensure backend directory is available in the container (if required)
RUN mkdir -p /app/backend

# Run the application using Gunicorn
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000"]
