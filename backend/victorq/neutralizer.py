# backend/victorq/neutralizer.py

# Define shared classes or functions here
class TradingHelper:
    @staticmethod
    def calculate_position_size(balance, risk_factor=0.01):
        """
        Calculate position size based on account balance and risk factor.
        """
        return balance * risk_factor