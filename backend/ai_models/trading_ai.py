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
        self.model_type = model_type.upper()
        self.time_steps = time_steps
        self.n_features = n_features
        logger.info("Initializing TradingAI with model_type=%s", self.model_type)
        self.model = self._init_model(self.model_type, time_steps, n_features, api_key, api_secret)

    def _init_model(self, model_type, time_steps, n_features, api_key, api_secret):
        logger.debug("Requested model_type: '%s'", model_type)
        model_type = model_type.strip().upper()

        if model_type == 'LSTM':
            return LSTMTradingModel(time_steps, n_features)
        elif model_type == 'GRU':
            return GRUTradingModel(time_steps, n_features)
        elif model_type == 'TRANSFORMER':
            return TransformerTradingModel(time_steps, n_features)
        elif model_type == 'REINFORCEMENTLEARNING':
            return RLTradingModel(state_size=100, action_size=3)
        else:
            logger.warning("Invalid model_type '%s'. Defaulting to LSTM.", model_type)
            return LSTMTradingModel(time_steps, n_features)

    def _prepare_input(self, data, time_steps, n_features):
        if isinstance(data, pd.DataFrame):
            datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
            if datetime_cols:
                logger.warning("Dropping datetime columns from input data: %s", datetime_cols)
                data = data.drop(columns=datetime_cols)
            data = data.select_dtypes(include=[np.number])

        data = np.asarray(data).astype(np.float32)
        original_len = len(data)

        if original_len < time_steps:
            logger.error("Insufficient data: got %d rows, require at least %d.", original_len, time_steps)
            return np.empty((0, time_steps, n_features))
        elif original_len == time_steps:
            reshaped_data = data.reshape((1, time_steps, n_features))
            logger.debug("Input data exactly matches time_steps. Reshaped to %s", reshaped_data.shape)
            return reshaped_data

        try:
            num_sequences = original_len - time_steps
            reshaped_data = np.array([
                data[i:i + time_steps]
                for i in range(num_sequences)
            ])
            reshaped_data = reshaped_data.reshape((-1, time_steps, n_features))
            logger.debug("Reshaped input to %s", reshaped_data.shape)
            return reshaped_data
        except Exception as e:
            logger.error("Error while reshaping data: %s", str(e))
            return np.empty((0, time_steps, n_features))

    def predict(self, data):
        if isinstance(self.model, RLTradingModel):
            logger.warning("Predict called on RLTradingModel. Returning dummy action.")
            return self.model.choose_action(0)

        processed = self._prepare_input(data, self.time_steps, self.n_features)
        if processed.size == 0:
            logger.warning("No data to predict on after preprocessing.")
            return None

        try:
            logger.info("Predicting on input shape: %s", processed.shape)
            prediction = self.model.predict(processed)
            logger.debug("Raw prediction output shape: %s", prediction.shape)
            return prediction.flatten().tolist()
        except Exception as e:
            logger.error("Prediction failed: %s", str(e))
            return None

    def train(self, data, labels):
        if isinstance(self.model, RLTradingModel):
            logger.warning("Training RLTradingModel in dummy loop.")
            for state in range(99):
                action = self.model.choose_action(state)
                reward = np.random.rand()
                next_state = (state + 1) % 100
                self.model.learn(state, action, reward, next_state)
            return "RL model trained (dummy loop)"

        processed = self._prepare_input(data, self.time_steps, self.n_features)
        if processed.size == 0:
            logger.warning("No data to train on after preprocessing.")
            return None
        return self.model.train(processed, labels)

    def fit_predict(self, data, labels):
        logger.info("Running fit_predict sequence.")
        self.train(data, labels)
        return self.predict(data)