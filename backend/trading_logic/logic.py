import logging
from ..ai_models.trading_ai import TradingAI  # Correct import path

class TradingLogic:
    def __init__(self):
        self.model = TradingAI()  # Initialize the TradingAI model
        logging.basicConfig(level=logging.INFO)

    def analyze_market(self, market_data):
        """
        Use AI model to analyze market data and generate trading signals.
        """
        try:
            signal = self.model.predict(market_data)  # Use the predict method of TradingAI
            logging.info(f"Generated trading signal: {signal}")
            return signal
        except Exception as e:
            logging.error(f"Failed to analyze market: {e}")
            return {"error": str(e)}

    def should_buy(self, signal):
        return signal == "buy"

    def should_sell(self, signal):
        return signal == "sell"