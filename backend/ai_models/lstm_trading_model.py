import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dropout, Dense
from .base import BaseTradingModel

class LSTMTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=None):
        """
        Initializes the LSTM model with the given time steps and features.

        Args:
        - time_steps (int): Number of time steps the model will look back for predictions (default 10).
        - n_features (int): Number of features to be used for the model (default 1).
        """
        self.time_steps = time_steps
        self.n_features = n_features if n_features is not None else 1
        self.model = self.build_model()

    def build_model(self):
        """
        Builds and compiles the LSTM model.

        Returns:
        - model (Sequential): The compiled LSTM model.
        """
        model = Sequential([
            Input(shape=(self.time_steps, self.n_features)),  # Input layer with time steps and features
            LSTM(50, return_sequences=True),  # LSTM layer with return_sequences=True for the next LSTM layer
            Dropout(0.2),  # Dropout to prevent overfitting
            LSTM(50, return_sequences=False),  # Second LSTM layer
            Dropout(0.2),  # Dropout again
            Dense(1)  # Output layer predicting the next value
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')  # Using Adam optimizer and MSE for regression tasks
        return model

    def _prepare_input(self, X):
        """
        Cleans and reshapes the input data to be suitable for the model.

        Args:
        - X (DataFrame or ndarray): The input data.

        Returns:
        - X (ndarray): The reshaped input data.
        """
        # If input data is a pandas DataFrame, remove datetime columns
        if isinstance(X, pd.DataFrame):
            X = X.select_dtypes(exclude=['datetime64[ns]', 'datetime64']).values
        
        X = np.array(X)
        
        # Ensure data is 3D: (batch_size, time_steps, n_features)
        if X.ndim != 3:
            try:
                X = X.reshape((X.shape[0], self.time_steps, self.n_features))
            except Exception as e:
                raise ValueError(f"Failed to reshape input to (batch_size, {self.time_steps}, {self.n_features}): {e}")
        
        return X

    def train(self, X, y, epochs=10, batch_size=32):
        """
        Trains the LSTM model on the provided training data.

        Args:
        - X (ndarray or DataFrame): The input features for training.
        - y (ndarray or DataFrame): The target values for training.
        - epochs (int): The number of epochs to train the model (default 10).
        - batch_size (int): The batch size for training (default 32).
        
        Returns:
        - history (History): The training history object containing loss and other metrics.
        """
        # Prepare the input data
        X = self._prepare_input(X)
        
        # Train the model and return the training history
        return self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, X):
        """
        Makes predictions using the trained LSTM model.

        Args:
        - X (ndarray or DataFrame): The input data for prediction.

        Returns:
        - prediction (ndarray): The predicted values from the model.
        """
        # Prepare the input data
        X = self._prepare_input(X)
        
        # Predict and return the result
        return self.model.predict(X, verbose=0)