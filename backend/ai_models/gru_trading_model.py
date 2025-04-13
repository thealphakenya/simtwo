import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dropout, Dense
import logging
from .base import BaseTradingModel

logger = logging.getLogger(__name__)

class GRUTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential([
            GRU(50, input_shape=(self.time_steps, self.n_features), return_sequences=True),
            Dropout(0.2),
            GRU(50),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def _clean_input(self, data):
        data = np.asarray(data).astype(np.float32)
        if data.ndim == 2:
            if data.shape[0] < self.time_steps:
                raise ValueError(f"Not enough data: got {data.shape[0]} rows, need at least {self.time_steps}.")
            try:
                data = np.array([
                    data[i:i + self.time_steps]
                    for i in range(len(data) - self.time_steps + 1)
                ])
                data = data.reshape((data.shape[0], self.time_steps, self.n_features))
            except Exception as e:
                logger.error("Reshape error in _clean_input: %s", str(e))
                raise
        elif data.ndim != 3 or data.shape[1] != self.time_steps or data.shape[2] != self.n_features:
            raise ValueError(f"Expected input shape (samples, {self.time_steps}, {self.n_features}), got {data.shape}.")
        return data

    def train(self, X, y, epochs=10, batch_size=32):
        X = self._clean_input(X)
        y = np.asarray(y).reshape(-1, 1)
        if len(X) != len(y):
            raise ValueError(f"X and y length mismatch: {len(X)} vs {len(y)}.")
        logger.info(f"Training GRU model: X={X.shape}, y={y.shape}")
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, X):
        X = self._clean_input(X)
        logger.info(f"Predicting with GRU model on input shape: {X.shape}")
        return self.model.predict(X, verbose=0)