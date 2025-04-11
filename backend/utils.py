# backend/utils.py

def get_safe_position_size(balance: float, price: float, leverage: float = 1) -> float:
    """
    Calculate a safe position size based on the account balance, current price, and leverage.
    
    :param balance: The available balance in the account
    :param price: The current price of the asset
    :param leverage: The leverage applied for the position
    :return: The safe position size
    """
    # Example calculation: Safe position size is a percentage of balance based on leverage
    risk_factor = 0.01  # Risking 1% of the balance
    position_size = (balance * risk_factor) * leverage / price
    return position_size