import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from .base import BaseTradingModel

class TransformerTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            Dense(64, input_dim=self.n_features * self.time_steps, activation='relu'),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, X, y, epochs=10, batch_size=32):
        X = np.array(X).reshape((X.shape[0], self.time_steps * self.n_features))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict(self, X):
        X = np.array(X).reshape((X.shape[0], self.time_steps * self.n_features))
        return self.model.predict(X, verbose=0)