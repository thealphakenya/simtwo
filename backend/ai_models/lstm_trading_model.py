import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
from .base import BaseTradingModel

class LSTMTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10):
        self.time_steps = time_steps
        self.n_features = None
        self.model = None

    def build_model(self, n_features):
        model = Sequential([
            LSTM(50, input_shape=(self.time_steps, n_features), return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, X, y, epochs=10, batch_size=32):
        X = np.array(X)
        if X.ndim != 3:
            self.n_features = X.shape[1]
            X = X.reshape((X.shape[0], self.time_steps, self.n_features))
        else:
            self.n_features = X.shape[2]

        self.model = self.build_model(self.n_features)
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict(self, X):
        X = np.array(X)
        if self.n_features is None:
            if X.ndim == 3:
                self.n_features = X.shape[2]
            else:
                self.n_features = X.shape[1]
        if X.ndim != 3:
            X = X.reshape((X.shape[0], self.time_steps, self.n_features))
        return self.model.predict(X, verbose=0)