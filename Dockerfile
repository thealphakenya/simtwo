FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt gunicorn  # Ensure gunicorn is installed

ENV FLASK_APP=backend.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PYTHONPATH=/app:/app/backend

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
