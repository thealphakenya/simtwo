import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
from .base import BaseTradingModel
import logging

class LSTMTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            LSTM(50, input_shape=(self.time_steps, self.n_features), return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def _validate_and_reshape(self, X):
        X = np.array(X)
        expected_shape = self.time_steps * self.n_features
        if X.ndim == 1:
            if X.size % expected_shape != 0:
                raise ValueError(f"Input data size {X.size} is not compatible with (time_steps={self.time_steps}, n_features={self.n_features})")
            X = X.reshape((-1, self.time_steps, self.n_features))
        elif X.ndim == 2 and X.shape[1] == self.time_steps * self.n_features:
            X = X.reshape((-1, self.time_steps, self.n_features))
        elif X.ndim != 3 or X.shape[1:] != (self.time_steps, self.n_features):
            raise ValueError(f"Cannot reshape input with shape {X.shape} into (batch, {self.time_steps}, {self.n_features})")
        return X

    def train(self, X, y, epochs=10, batch_size=32):
        try:
            X = self._validate_and_reshape(X)
            self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
        except Exception as e:
            logging.error(f"Training failed: {e}")

    def predict(self, X):
        try:
            X = self._validate_and_reshape(X)
            return self.model.predict(X, verbose=0)
        except Exception as e:
            logging.error(f"Prediction failed: {e}")
            return None