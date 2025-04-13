from .lstm_trading_model import LSTMTradingModel
from .gru_trading_model import GRUTradingModel
from .transformer_trading_model import TransformerTradingModel
from .reinforcement_learning import ReinforcementLearning

class TradingAI:
    def __init__(self, api_key=None, api_secret=None, model_type='lstm', time_steps=10, n_features=10):
        self.model_type = model_type.lower()
        self.model = self._init_model(model_type, time_steps, n_features, api_key, api_secret)

    def _init_model(self, model_type, time_steps, n_features, api_key, api_secret):
        if model_type == 'lstm':
            return LSTMTradingModel(time_steps, n_features)
        elif model_type == 'gru':
            return GRUTradingModel(time_steps, n_features)
        elif model_type == 'transformer':
            return TransformerTradingModel(time_steps, n_features)
        elif model_type == 'reinforcement':
            return ReinforcementLearning(api_key, api_secret, time_steps, n_features)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def train(self, X, y=None, epochs=10, batch_size=32):
        if hasattr(self.model, 'train_model'):
            self.model.train_model(X, y, epochs, batch_size)
        else:
            self.model.train(X, y, epochs=epochs, batch_size=batch_size)

    def predict(self, X):
        return self.model.predict(X)