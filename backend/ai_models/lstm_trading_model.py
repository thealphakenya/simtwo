# backend/ai_models/lstm_trading_model.py

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dropout, Dense
from .base import BaseTradingModel

class LSTMTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=None):
        """
        time_steps: Number of time steps for the model (default is 10)
        n_features: Number of features for the model. If not provided, defaults to 1.
        """
        self.time_steps = time_steps
        self.n_features = n_features if n_features is not None else 1
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            Input(shape=(self.time_steps, self.n_features)),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, X, y, epochs=10, batch_size=32):
        X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict(self, X):
        X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
        return self.model.predict(X, verbose=0)