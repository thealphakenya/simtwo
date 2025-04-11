import logging
from ..ai_models.model import TradingAI  # Go up one level to access ai_models

class TradingLogic:
    def __init__(self):
        self.model = TradingAI()
        logging.basicConfig(level=logging.INFO)

    def analyze_market(self, market_data):
        """
        Use AI model to analyze market data and generate trading signals.
        """
        try:
            signal = self.model.predict(market_data)
            logging.info(f"Generated trading signal: {signal}")
            return signal
        except Exception as e:
            logging.error(f"Failed to analyze market: {e}")
            return {"error": str(e)}

    def should_buy(self, signal):
        return signal == "buy"

    def should_sell(self, signal):
        return signal == "sell"