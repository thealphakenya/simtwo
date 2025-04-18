from backend.celery_app import celery_app
from backend.trading_logic.order_execution import OrderExecution
from backend.data.data_fetcher import DataFetcher
from backend.app import config  # Ensure config is correctly exposed in app.py
import logging

# Set up logging for better traceability
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@celery_app.task
def run_trading_job_task():
    logger.info("Running trading job...")

    # Initialize fetcher and executor using app configuration
    fetcher = DataFetcher(
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
        trade_symbol=config.TRADE_SYMBOL,
        use_external=config.USE_EXTERNAL_DATA
    )
    
    executor = OrderExecution(api_key=config.API_KEY, api_secret=config.API_SECRET)

    try:
        # Fetch market data
        market_data = fetcher.fetch_ohlcv_data(symbol=config.TRADE_SYMBOL, interval='1h', limit=100)
        if market_data is not None and not market_data.empty:
            logger.info(f"Fetched {len(market_data)} market data points.")

            # Evaluate market signal and execute trade
            signal = executor.evaluate_market_signal(market_data)
            if signal == "BUY":
                logger.info("Market signal is BUY. Executing buy order.")
                executor.execute_buy_order()
            elif signal == "SELL":
                logger.info("Market signal is SELL. Executing sell order.")
                executor.execute_sell_order()
            else:
                logger.info("No clear market signal. Holding off on any trade.")
        else:
            logger.warning("No market data received or data is empty.")
    except Exception as e:
        logger.error(f"Error in trading job: {str(e)}")
        # Optionally, log the exception traceback for more detailed debugging
        logger.exception("Exception occurred during trading job execution.")
