import logging
import pandas as pd
import numpy as np

from backend.ai_models.lstm_model import LSTMTradingModel
from backend.ai_models.gru_model import GRUTradingModel
from backend.ai_models.transformer_model import TransformerTradingModel
from backend.ai_models.rl_model import RLTradingModel

logger = logging.getLogger(__name__)

class TradingAI:
    def __init__(self, model_type="LSTM", time_steps=60, n_features=1, api_key=None, api_secret=None):
        logger.info("Initializing TradingAI with model_type=%s", model_type)
        self.model = self._init_model(model_type, time_steps, n_features, api_key, api_secret)

    def _init_model(self, model_type, time_steps, n_features, api_key, api_secret):
        print(f"[DEBUG] Requested model_type: '{model_type}'")
        model_type = (model_type or 'LSTM').strip().upper()

        if model_type == 'LSTM':
            return LSTMTradingModel(time_steps, n_features)
        elif model_type == 'GRU':
            return GRUTradingModel(time_steps, n_features)
        elif model_type == 'TRANSFORMER':
            return TransformerTradingModel(time_steps, n_features)
        elif model_type == 'REINFORCEMENTLEARNING':
            state_size = 100  # You can adjust this based on your use case
            action_size = 3   # e.g., Buy, Sell, Hold
            return RLTradingModel(state_size, action_size)
        else:
            logger.warning("Invalid model_type '%s'. Defaulting to LSTM.", model_type)
            return LSTMTradingModel(time_steps, n_features)

    def _prepare_input(self, data, time_steps, n_features):
        if isinstance(data, pd.DataFrame):
            # Dropping datetime columns
            datetime_cols = data.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns.tolist()
            if datetime_cols:
                logger.warning("Dropping datetime columns from input data: %s", datetime_cols)
            data = data.select_dtypes(exclude=['datetime64[ns]', 'datetime64'])

        data = np.array(data)
        if data.shape[0] < time_steps:
            logger.error("Not enough data points to reshape. Returning empty array.")
            return np.array([])  # Returning empty array if not enough data

        try:
            reshaped_data = np.array([
                data[i:i + time_steps]
                for i in range(len(data) - time_steps)
            ])
            reshaped_data = reshaped_data.reshape((reshaped_data.shape[0], time_steps, n_features))
            return reshaped_data
        except Exception as e:
            logger.error(f"Error while reshaping data: {e}")
            return np.array([])

    def predict(self, data):
        data = self._prepare_input(data, self.model.time_steps, self.model.n_features)
        if data.size == 0:
            return None
        return self.model.predict(data)

    def train(self, data, labels):
        data = self._prepare_input(data, self.model.time_steps, self.model.n_features)
        if data.size == 0:
            return None
        return self.model.train(data, labels)