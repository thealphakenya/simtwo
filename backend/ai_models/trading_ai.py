import logging
import pandas as pd
import numpy as np

from backend.ai_models.lstm_model import LSTMTradingModel
from backend.ai_models.gru_model import GRUTradingModel
from backend.ai_models.transformer_model import TransformerTradingModel
from backend.ai_models.rl_model import RLTradingModel
from backend.exchange_api import ExchangeClient  # Adjust to your client
from backend.exchange.exchange_data import fetch_ohlcv_data as external_ohlcv_data  # Import external data fetch
from sklearn.preprocessing import StandardScaler  # For scaling

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TradingAI:
    def __init__(self, model_type="LSTM", time_steps=60, n_features=1, api_key=None, api_secret=None, use_external=False, scale_data=False):
        """
        Initialize the TradingAI class with model type, data preprocessing, and API credentials.
        """
        self.model_type = model_type.strip().upper()
        self.time_steps = time_steps
        self.n_features = n_features
        self.use_external = use_external  # Flag to use external data source
        self.scale_data = scale_data  # Flag for scaling data
        self.exchange = ExchangeClient(api_key, api_secret)
        logger.info("Initializing TradingAI with model_type=%s", self.model_type)
        self.model = self._init_model(self.model_type, time_steps, n_features, api_key, api_secret)
        self.scaler = StandardScaler() if scale_data else None  # Initialize scaler if required

    def _init_model(self, model_type, time_steps, n_features, api_key, api_secret):
        """
        Initialize the model based on the specified model type.
        """
        if model_type == 'LSTM':
            return LSTMTradingModel(time_steps, n_features)
        elif model_type == 'GRU':
            return GRUTradingModel(time_steps, n_features)
        elif model_type == 'TRANSFORMER':
            return TransformerTradingModel(time_steps, n_features)
        elif model_type in ['REINFORCEMENTLEARNING', 'REINFORCEMENT']:
            return RLTradingModel(state_size=100, action_size=3)
        else:
            logger.warning("Invalid model_type '%s'. Defaulting to LSTM.", model_type)
            return LSTMTradingModel(time_steps, n_features)

    def _prepare_input(self, data, time_steps, n_features):
        """
        Preprocess data to be fed into the model, including reshaping and scaling.
        """
        if isinstance(data, pd.DataFrame):
            datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
            if datetime_cols:
                logger.warning("Dropping datetime columns from input data: %s", datetime_cols)
                data = data.drop(columns=datetime_cols)
            data = data.select_dtypes(include=[np.number])

        # Scaling data if necessary
        if self.scaler:
            data = self.scaler.fit_transform(data)

        data = np.asarray(data).astype(np.float32)
        original_len = len(data)

        if original_len < time_steps:
            logger.error("Insufficient data: got %d rows, require at least %d.", original_len, time_steps)
            return np.empty((0, time_steps, n_features))

        try:
            reshaped_data = np.array([data[i:i + time_steps] for i in range(original_len - time_steps + 1)])
            reshaped_data = reshaped_data.reshape((-1, time_steps, n_features))
            logger.debug("Reshaped input to %s", reshaped_data.shape)
            return reshaped_data
        except Exception as e:
            logger.error("Error while reshaping data: %s", str(e))
            return np.empty((0, time_steps, n_features))

    def predict(self, data):
        """
        Predict the next market movement using the trained model.
        """
        if isinstance(self.model, RLTradingModel):
            logger.warning("Predict called on RLTradingModel. Returning dummy action.")
            return [self.model.choose_action(0)]

        processed = self._prepare_input(data, self.time_steps, self.n_features)
        if processed.size == 0:
            logger.warning("No data to predict on after preprocessing.")
            return None

        try:
            prediction = self.model.predict(processed)
            if isinstance(prediction, np.ndarray):
                return prediction.flatten().tolist()
            elif isinstance(prediction, (float, int)):
                return [float(prediction)]
            else:
                logger.error("Unexpected prediction type: %s", type(prediction))
                return None
        except Exception as e:
            logger.error("Prediction failed: %s", str(e))
            return None

    def execute_trade(self, prediction, symbol="BTCUSDT", quantity=0.001):
        """
        Execute a trade based on the prediction (BUY/SELL) signal.
        """
        try:
            if prediction[-1] > prediction[-2]:
                logger.info("Signal: Buy %s", symbol)
                self.exchange.place_order(symbol=symbol, side="BUY", quantity=quantity)
            elif prediction[-1] < prediction[-2]:
                logger.info("Signal: Sell %s", symbol)
                self.exchange.place_order(symbol=symbol, side="SELL", quantity=quantity)
            else:
                logger.info("Signal: Hold - no clear movement.")
        except Exception as e:
            logger.error("Trade execution failed: %s", str(e))

# Global instance (optional singleton)
trading_ai_instance = TradingAI(model_type="LSTM", time_steps=60, n_features=1, use_external=False)

def run_trading_job():
    """
    Run the trading job by fetching market data, making predictions, and executing trades.
    """
    try:
        if trading_ai_instance.use_external:
            logger.info("Using external data for trading job.")
            df = external_ohlcv_data(symbol="BTCUSDT", interval="1m", limit=100)  # External data fetch
        else:
            logger.info("Using Binance API data for trading job.")
            df = fetch_ohlcv_data(symbol="BTCUSDT", interval="1m", limit=100)  # Original method from exchange

        logger.info("Fetched %d OHLCV data points.", len(df))

        prediction = trading_ai_instance.predict(df)

        if prediction is None or len(prediction) < 2:
            logger.warning("Could not fetch valid prediction for trade.")
            return

        trading_ai_instance.execute_trade(prediction)
    except Exception as e:
        logger.error("Error in run_trading_job: %s", str(e))
        logger.exception("Exception traceback")
