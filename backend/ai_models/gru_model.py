# backend/ai_models/gru_model.py

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout

class GRUTradingModel:
    def __init__(self, time_steps=60, n_features=1):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(GRU(units=50, return_sequences=True, input_shape=(self.time_steps, self.n_features)))
        model.add(Dropout(0.2))
        model.add(GRU(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))  # Predict one output
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        return self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

    def predict(self, x_input):
        return self.model.predict(x_input)