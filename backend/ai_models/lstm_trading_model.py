import numpy as np
import pandas as pd
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

    def _prepare_input(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.select_dtypes(exclude=['datetime64[ns]', 'datetime64']).values
        X = np.array(X)
        if X.ndim != 3:
            try:
                X = X.reshape((X.shape[0], self.time_steps, self.n_features))
            except Exception as e:
                raise ValueError(f"Failed to reshape input to (batch_size, {self.time_steps}, {self.n_features}): {e}")
        return X

    def train(self, X, y, epochs=10, batch_size=32):
        X = self._prepare_input(X)
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict(self, X):
        X = self._prepare_input(X)
        return self.model.predict(X, verbose=0)