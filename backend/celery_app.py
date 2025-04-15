from celery import Celery
import os

# Create a Celery app instance
celery_app = Celery(
    "trading_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://simtwo_redis:6379/0"),  # Use env variable for flexibility
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://simtwo_redis:6379/0")  # Same here for backend
)

# Update Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)