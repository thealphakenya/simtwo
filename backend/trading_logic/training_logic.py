class TradingLogic:
    def __init__(self, strategy_name="default"):
        self.strategy_name = strategy_name

    def evaluate_market(self, market_data):
        """
        Evaluate market data and return a trading decision.
        """
        if not market_data:
            return "HOLD"

        price = market_data.get("price", 0)
        if price > 100:
            return "SELL"
        elif price < 50:
            return "BUY"
        else:
            return "HOLD"

    def set_strategy(self, name):
        """
        Set a new trading strategy.
        """
        self.strategy_name = name

    def __str__(self):
        return f"TradingLogic(strategy_name={self.strategy_name})"