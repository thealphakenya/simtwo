FROM python:3.8-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/backend

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000"]
