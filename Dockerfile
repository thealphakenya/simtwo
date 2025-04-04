FROM python:3.9-slim

WORKDIR /app

COPY . /app  # Ensure the full app is copied
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
ENV FLASK_APP=backend.app
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
