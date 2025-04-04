FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=backend/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PYTHONPATH=/app  # Add this line to set PYTHONPATH

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
