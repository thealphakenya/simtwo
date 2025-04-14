import logging
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

logger = logging.getLogger(__name__)

class ExchangeClient:
    def __init__(self, api_key: str, api_secret: str, use_testnet: bool = False, use_futures: bool = False):
        if not api_key or not api_secret:
            logger.error("Missing API key or secret!")
            raise ValueError("API credentials required.")

        self.use_futures = use_futures
        self.client = Client(api_key, api_secret)

        if use_testnet:
            self.client.API_URL = "https://testnet.binance.vision/api"
            if use_futures:
                self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

        logger.info("Binance client initialized. Testnet: %s | Futures: %s", use_testnet, use_futures)

    # -------- SPOT --------
    def place_market_order(self, symbol: str, side: str, quantity: float):
        try:
            logger.info("Placing spot market order: %s %s %f", side, symbol, quantity)
            return self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
        except Exception as e:
            logger.error("Market order failed: %s", str(e))
            return None

    def get_balance(self):
        try:
            return self.client.get_account().get("balances", [])
        except Exception as e:
            logger.error("Balance fetch error: %s", str(e))
            return []

    # -------- MARGIN (Spot Margin Trading) --------
    def place_margin_order(self, symbol: str, side: str, quantity: float, is_buy: bool = True):
        try:
            logger.info("Placing margin order: %s %s %f", side, symbol, quantity)
            order_type = "MARKET"  # Can be customized for different types (LIMIT, etc.)
            return self.client.create_margin_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity
            )
        except Exception as e:
            logger.error("Margin order failed: %s", str(e))
            return None

    def borrow_margin(self, asset: str, amount: float):
        try:
            logger.info("Borrowing margin for %s: %f", asset, amount)
            return self.client.sapi_post(f"/sapi/v1/margin/loan", params={"asset": asset, "amount": amount})
        except Exception as e:
            logger.error("Margin borrowing failed: %s", str(e))
            return None

    def repay_margin(self, asset: str, amount: float):
        try:
            logger.info("Repaying margin for %s: %f", asset, amount)
            return self.client.sapi_post(f"/sapi/v1/margin/repay", params={"asset": asset, "amount": amount})
        except Exception as e:
            logger.error("Margin repayment failed: %s", str(e))
            return None

    # -------- FUTURES --------
    def place_futures_order(self, symbol: str, side: str, quantity: float, order_type="MARKET"):
        try:
            if not self.use_futures:
                raise ValueError("Futures trading not enabled for this client.")

            logger.info("Placing futures %s order: %s %f", order_type, side, quantity)
            return self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity
            )
        except Exception as e:
            logger.error("Futures order error: %s", str(e))
            return None

    def set_leverage(self, symbol: str, leverage: int):
        try:
            if not self.use_futures:
                raise ValueError("Futures trading not enabled.")

            logger.info("Setting leverage for %s to %dx", symbol, leverage)
            return self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
        except Exception as e:
            logger.error("Set leverage error: %s", str(e))
            return None

    def get_futures_balance(self):
        try:
            return self.client.futures_account_balance()
        except Exception as e:
            logger.error("Futures balance error: %s", str(e))
            return []

    def get_open_futures_positions(self):
        try:
            return self.client.futures_position_information()
        except Exception as e:
            logger.error("Futures positions fetch error: %s", str(e))
            return []

    # -------- TRAILING STOP (Futures) --------
    def place_trailing_stop_order(self, symbol: str, side: str, quantity: float, activation_price: float, callback_rate: float):
        try:
            if not self.use_futures:
                raise ValueError("Futures trading not enabled.")

            logger.info("Placing trailing stop order: %s %s %f with activation at %f and callback rate of %f", 
                        side, symbol, quantity, activation_price, callback_rate)
            return self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_STOP_MARKET,
                quantity=quantity,
                stopPrice=activation_price,
                price=activation_price * (1 - callback_rate / 100)  # Trigger at callback rate
            )
        except Exception as e:
            logger.error("Trailing stop order failed: %s", str(e))
            return None

    # -------- TAKE PROFIT (Futures) --------
    def place_take_profit_order(self, symbol: str, side: str, quantity: float, price: float):
        try:
            if not self.use_futures:
                raise ValueError("Futures trading not enabled.")

            logger.info("Placing take profit order: %s %s %f at price %f", side, symbol, quantity, price)
            return self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=price,
                timeInForce=TIME_IN_FORCE_GTC
            )
        except Exception as e:
            logger.error("Take profit order failed: %s", str(e))
            return None

    # -------- ORDER CANCELLATION --------
    def cancel_order(self, symbol: str, order_id: str, is_futures: bool = False):
        try:
            if is_futures:
                if not self.use_futures:
                    raise ValueError("Futures trading not enabled.")
                logger.info("Canceling futures order with ID: %s", order_id)
                return self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            else:
                logger.info("Canceling spot order with ID: %s", order_id)
                return self.client.cancel_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            logger.error("Order cancellation failed: %s", str(e))
            return None

    # -------- ORDER STATUS --------
    def get_order_status(self, symbol: str, order_id: str, is_futures: bool = False):
        try:
            if is_futures:
                if not self.use_futures:
                    raise ValueError("Futures trading not enabled.")
                logger.info("Fetching futures order status for order ID: %s", order_id)
                return self.client.futures_get_order(symbol=symbol, orderId=order_id)
            else:
                logger.info("Fetching spot order status for order ID: %s", order_id)
                return self.client.get_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            logger.error("Order status fetch failed: %s", str(e))
            return None

    # -------- STOP-LOSS ORDER (Spot or Futures) --------
    def place_stop_loss_order(self, symbol: str, side: str, quantity: float, stop_price: float, is_futures: bool = False):
        try:
            if is_futures:
                if not self.use_futures:
                    raise ValueError("Futures trading not enabled.")
                logger.info("Placing stop-loss order (Futures): %s %s %f at stop price %f", 
                            side, symbol, quantity, stop_price)
                return self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=ORDER_TYPE_STOP_MARKET,
                    quantity=quantity,
                    stopPrice=stop_price
                )
            else:
                logger.info("Placing stop-loss order (Spot): %s %s %f at stop price %f", 
                            side, symbol, quantity, stop_price)
                return self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=ORDER_TYPE_STOP_MARKET,
                    quantity=quantity,
                    stopPrice=stop_price
                )
        except Exception as e:
            logger.error("Stop-loss order failed: %s", str(e))
            return None