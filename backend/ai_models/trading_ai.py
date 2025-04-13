# backend/ai_models/trading_ai.py
from .lstm_trading_model import LSTMTradingModel
from .gru_trading_model import GRUTradingModel
from .transformer_trading_model import TransformerTradingModel
from .reinforcement_learning import ReinforcementLearning

class TradingAI:
    def __init__(self, model_type='LSTM', time_steps=10, n_features=None, api_key=None, api_secret=None):
        self.model = self._init_model(model_type, time_steps, n_features, api_key, api_secret)

    def _init_model(self, model_type, time_steps, n_features, api_key, api_secret):
        if model_type == 'LSTM':
            # Pass only time_steps, as n_features is optional and handled in LSTMTradingModel
            return LSTMTradingModel(time_steps, n_features)
        elif model_type == 'GRU':
            return GRUTradingModel(time_steps, n_features)
        elif model_type == 'Transformer':
            return TransformerTradingModel(time_steps, n_features)
        elif model_type == 'ReinforcementLearning':
            return ReinforcementLearning(api_key, api_secret)
        else:
            raise ValueError("Invalid model type specified")

    def predict(self, data):
        return self.model.predict(data)

    def train(self, X, y, epochs=10, batch_size=32):
        self.model.train(X, y, epochs, batch_size)