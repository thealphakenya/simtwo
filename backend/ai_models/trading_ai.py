import logging
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
        # Debug log for incoming model_type
        print(f"[DEBUG] Requested model_type: '{model_type}'")

        # Normalize model_type safely
        model_type = (model_type or 'LSTM').strip().upper()

        if model_type == 'LSTM':
            return LSTMTradingModel(time_steps, n_features)
        elif model_type == 'GRU':
            return GRUTradingModel(time_steps, n_features)
        elif model_type == 'TRANSFORMER':
            return TransformerTradingModel(time_steps, n_features)
        elif model_type == 'REINFORCEMENTLEARNING':
            return RLTradingModel(api_key, api_secret)
        else:
            logger.warning("Invalid model_type '%s'. Defaulting to LSTM.", model_type)
            return LSTMTradingModel(time_steps, n_features)

    def predict(self, data):
        return self.model.predict(data)

    def train(self, data):
        return self.model.train(data)