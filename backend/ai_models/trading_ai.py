import logging
import pandas as pd
import numpy as np  # ✅ Needed for array conversion and reshaping

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
        model_type_input = model_type or 'LSTM'
        model_type_clean = model_type_input.strip().lower()
        print(f"[DEBUG] Requested model_type: '{model_type_clean}'")

        if model_type_clean in ['lstm']:
            return LSTMTradingModel(time_steps, n_features)
        elif model_type_clean in ['gru']:
            return GRUTradingModel(time_steps, n_features)
        elif model_type_clean in ['transformer']:
            return TransformerTradingModel(time_steps, n_features)
        elif model_type_clean in ['reinforcement', 'reinforcementlearning', 'rl']:
            return RLTradingModel(api_key, api_secret)
        else:
            logger.warning("Invalid model_type '%s'. Defaulting to LSTM.", model_type_clean)
            return LSTMTradingModel(time_steps, n_features)

    def _prepare_input(self, data, time_steps, n_features):
        if isinstance(data, pd.DataFrame):
            datetime_cols = data.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns.tolist()
            if datetime_cols:
                logger.warning("Dropping datetime columns from input data: %s", datetime_cols)
            data = data.select_dtypes(exclude=['datetime64[ns]', 'datetime64'])

        data = np.array(data)

        # Check if data has the right shape for slicing and reshaping
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        if data.shape[0] < time_steps:
            logger.error("Not enough data points to reshape. Returning empty array.")
            return np.array([])

        try:
            reshaped_data = np.array([
                data[i:i+time_steps] for i in range(data.shape[0] - time_steps)
            ])
            reshaped_data = reshaped_data.reshape(-1, time_steps, n_features)
        except Exception as e:
            logger.error("Failed to reshape data: %s", e)
            return np.array([])

        return reshaped_data

    def predict(self, data):
        data = self._prepare_input(data, self.model.time_steps, self.model.n_features)
        if data.size == 0:
            logger.warning("Prediction aborted due to invalid input shape.")
            return None
        return self.model.predict(data)

    def train(self, data, labels):
        data = self._prepare_input(data, self.model.time_steps, self.model.n_features)
        if data.size == 0:
            logger.warning("Training aborted due to invalid input shape.")
            return None
        return self.model.train(data, labels)