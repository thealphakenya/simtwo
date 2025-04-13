import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import logging
from .base import BaseTradingModel

logger = logging.getLogger(__name__)

class TransformerTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self._build_model()

    def _build_model(self):
        input_dim = self.time_steps * self.n_features
        model = Sequential([
            Dense(64, input_dim=input_dim, activation='relu'),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def _clean_input(self, data):
        data = np.asarray(data).astype(np.float32)
        if data.ndim == 3:
            expected_shape = (self.time_steps, self.n_features)
            if data.shape[1:] != expected_shape:
                raise ValueError(f"Expected shape (*, {self.time_steps}, {self.n_features}), got {data.shape}")
            data = data.reshape((data.shape[0], self.time_steps * self.n_features))
        elif data.ndim == 2:
            expected_dim = self.time_steps * self.n_features
            if data.shape[1] != expected_dim:
                raise ValueError(f"Expected flat input with {expected_dim} features, got {data.shape[1]}")
        else:
            raise ValueError(f"Invalid input shape: {data.shape}. Must be 2D or 3D array.")
        return data

    def train(self, X, y, epochs=10, batch_size=32):
        X = self._clean_input(X)
        y = np.asarray(y).reshape(-1, 1)
        if len(X) != len(y):
            raise ValueError(f"X and y length mismatch: {len(X)} vs {len(y)}.")
        logger.info(f"Training Transformer model: X={X.shape}, y={y.shape}")
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, X):
        X = self._clean_input(X)
        logger.info(f"Predicting with Transformer model on input shape: {X.shape}")
        return self.model.predict(X, verbose=0)