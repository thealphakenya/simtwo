import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout

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
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def _clean_input(self, data):
        if isinstance(data, pd.DataFrame):
            data = data.select_dtypes(exclude=['datetime64[ns]'])
        data = np.array(data)
        if data.ndim != 3:
            try:
                data = data.reshape((data.shape[0], self.time_steps, self.n_features))
            except Exception as e:
                raise ValueError(f"Failed to reshape input to (batch_size, {self.time_steps}, {self.n_features}): {e}")
        return data

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        x_train = self._clean_input(x_train)
        return self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

    def predict(self, x_input):
        x_input = self._clean_input(x_input)
        return self.model.predict(x_input)