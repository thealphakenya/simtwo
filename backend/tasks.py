from backend.celery_app import celery_app
from backend.trading_logic.order_execution import OrderExecution
from backend.data.data_fetcher import DataFetcher
from backend.app import config  # Ensure config is correctly exposed in app.py

@celery_app.task
def run_trading_job_task():
    print("Running trading job...")

    # Initialize fetcher and executor using app configuration
    fetcher = DataFetcher(
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
        trade_symbol=config.TRADE_SYMBOL,
        use_external=config.USE_EXTERNAL_DATA
    )
    
    executor = OrderExecution(config.API_KEY, config.API_SECRET)

    try:
        # Fetch market data
        market_data = fetcher.fetch_data()
        if market_data:
            # Evaluate market signal and execute trade
            signal = executor.evaluate_market_signal(market_data)
            if signal == "BUY":
                executor.execute_buy_order()
            elif signal == "SELL":
                executor.execute_sell_order()
            else:
                print("No clear signal.")
    except Exception as e:
        print(f"Error in trading job: {str(e)}")
        # Consider logging the error here for better traceability