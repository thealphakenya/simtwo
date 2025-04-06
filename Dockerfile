FROM python:3.8-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/backend

RUN mkdir -p /app/frontend
COPY ./frontend /app/frontend/

EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
