import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
import logging

logger = logging.getLogger(__name__)

class LSTMTradingModel:
    def __init__(self, time_steps=60, n_features=1):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Input(shape=(self.time_steps, self.n_features)))
        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def _clean_input(self, data):
        if isinstance(data, pd.DataFrame):
            data = data.select_dtypes(include=[np.number])

        data = np.asarray(data).astype(np.float32)

        if data.ndim == 2:
            if data.shape[0] < self.time_steps:
                raise ValueError(f"Input has {data.shape[0]} rows, which is less than time_steps={self.time_steps}.")
            try:
                data = np.array([
                    data[i:i + self.time_steps]
                    for i in range(len(data) - self.time_steps + 1)
                ])
                data = data.reshape((data.shape[0], self.time_steps, self.n_features))
            except Exception as e:
                logger.error("Failed reshaping data in _clean_input: %s", str(e))
                raise
        elif data.ndim != 3 or data.shape[1] != self.time_steps or data.shape[2] != self.n_features:
            raise ValueError(f"Input shape must be (samples, {self.time_steps}, {self.n_features}). Got {data.shape}.")

        return data

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        x_train = self._clean_input(x_train)
        y_train = np.asarray(y_train).reshape(-1, 1)
        if len(x_train) != len(y_train):
            raise ValueError(f"Mismatch between x_train ({len(x_train)}) and y_train ({len(y_train)}).")
        logger.info(f"Training on data shape: {x_train.shape}, labels shape: {y_train.shape}")
        return self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, x_input):
        x_input = self._clean_input(x_input)
        logger.info(f"Predicting on input shape: {x_input.shape}")
        return self.model.predict(x_input, verbose=0)