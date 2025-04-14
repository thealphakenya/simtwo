from celery import Celery

celery_app = Celery(
    "trading_tasks",
    broker="redis://simtwo_redis:6379/0",  # Change localhost to Redis service name
    backend="redis://simtwo_redis:6379/0"  # Change localhost to Redis service name
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)