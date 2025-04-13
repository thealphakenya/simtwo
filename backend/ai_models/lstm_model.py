import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout

class LSTMTradingModel:
    def __init__(self, time_steps=60, n_features=1):
        """
        Initializes the LSTM model with the given time steps and features.

        Args:
        - time_steps (int): Number of time steps the model will look back for predictions (default 60).
        - n_features (int): Number of features to be used for the model (default 1).
        """
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self._build_model()

    def _build_model(self):
        """
        Builds and compiles the LSTM model.

        Returns:
        - model (Sequential): The compiled LSTM model.
        """
        model = Sequential()
        model.add(Input(shape=(self.time_steps, self.n_features)))  # Preferred way to define input shape
        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def _clean_input(self, data):
        """
        Cleans and reshapes the input data for the model.

        Args:
        - data (DataFrame or ndarray): Input data for training or prediction.

        Returns:
        - data (ndarray): Reshaped input suitable for the model.
        """
        if isinstance(data, pd.DataFrame):
            data = data.select_dtypes(exclude=['datetime64[ns]'])

        data = np.array(data)

        # Ensure data is 3D: (batch_size, time_steps, n_features)
        if data.ndim != 3:
            try:
                data = data.reshape((data.shape[0], self.time_steps, self.n_features))
            except Exception as e:
                raise ValueError(f"Failed to reshape input to (batch_size, {self.time_steps}, {self.n_features}): {e}")

        return data

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        """
        Trains the LSTM model.

        Args:
        - x_train (ndarray or DataFrame): Training input features.
        - y_train (ndarray or DataFrame): Training labels.
        - epochs (int): Number of epochs to train for (default 10).
        - batch_size (int): Batch size for training (default 32).

        Returns:
        - history: Training history object.
        """
        x_train = self._clean_input(x_train)
        return self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, x_input):
        """
        Predicts using the LSTM model.

        Args:
        - x_input (ndarray or DataFrame): Input data for prediction.

        Returns:
        - prediction (ndarray): Predicted values.
        """
        x_input = self._clean_input(x_input)
        return self.model.predict(x_input, verbose=0)