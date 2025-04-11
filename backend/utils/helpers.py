# backend/utils/helpers.py

def format_response(status: str, data: dict = None):
    return {
        "status": status,
        "data": data or {}
    }

class Timer:
    import time

    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = self.time.time()

    def stop(self):
        if self.start_time is None:
            raise RuntimeError("Timer not started.")
        return self.time.time() - self.start_time

def get_safe_position_size(balance: float, price: float, risk_percentage: float = 1.0) -> float:
    """
    Calculate a safe position size based on balance, price, and risk %.

    Args:
        balance (float): Total available balance.
        price (float): Price of the asset.
        risk_percentage (float): % of balance to risk per trade.

    Returns:
        float: Safe position size.
    """
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    position_size = (balance * (risk_percentage / 100)) / price
    return round(position_size, 6)