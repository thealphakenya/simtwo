from backend.celery_app import celery_app
from backend.ai_models.trading_ai import trading_ai_instance

@celery_app.task
def run_trading_job_task():
    # Calling the method from the TradingAI instance
    trading_ai_instance.run_trading_job()