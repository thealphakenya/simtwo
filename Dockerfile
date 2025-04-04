FROM tensorflow/tensorflow:2.8.0

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --default-timeout=300 --retries=10 --no-cache-dir -r requirements.txt

COPY . .

RUN mv /app/backend/training_logic /app/backend/trading_logic

ENV PYTHONPATH=/app:/app/backend

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
