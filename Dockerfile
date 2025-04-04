FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    for i in $(seq 1 5); do pip install --no-cache-dir -r requirements.txt && break || sleep 15; done

COPY . /app

ENV PYTHONPATH=/app
ENV FLASK_APP=backend.app
ENV FLASK_ENV=production

RUN ls -R /app

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
