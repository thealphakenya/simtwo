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
        model.add(Input(shape=(self.time_steps, self.n_features)))  # Input layer with time steps and features
        model.add(LSTM(units=50, return_sequences=True))  # LSTM layer with return_sequences=True for the next LSTM layer
        model.add(Dropout(0.2))  # Dropout to prevent overfitting
        model.add(LSTM(units=50, return_sequences=False))  # Second LSTM layer
        model.add(Dropout(0.2))  # Dropout again
        model.add(Dense(units=1))  # Output layer predicting the next value
        model.compile(optimizer='adam', loss='mean_squared_error')  # Using Adam optimizer and MSE for regression tasks
        return model

    def _clean_input(self, data):
        """
        Cleans the input data by removing datetime columns (if a DataFrame is provided)
        and reshaping it to the required format (batch_size, time_steps, n_features).
        
        Args:
        - data (DataFrame or ndarray): Input data for training/prediction.
        
        Returns:
        - data (ndarray): Cleaned and reshaped input data.
        """
        # If input data is a DataFrame, remove any datetime columns
        if isinstance(data, pd.DataFrame):
            data = data.select_dtypes(exclude=['datetime64[ns]'])
        
        # Convert data to numpy array
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
        Trains the LSTM model on the provided training data.
        
        Args:
        - x_train (ndarray or DataFrame): Input features for training.
        - y_train (ndarray or DataFrame): Target values for training.
        - epochs (int): Number of epochs to train the model (default 10).
        - batch_size (int): Batch size for training (default 32).
        
        Returns:
        - history (History): The training history object containing loss and other metrics.
        """
        # Clean and reshape input data
        x_train = self._clean_input(x_train)
        
        # Train the model and return the training history
        return self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, x_input):
        """
        Makes predictions using the trained LSTM model.
        
        Args:
        - x_input (ndarray or DataFrame): Input data for prediction.
        
        Returns:
        - prediction (ndarray): The predicted values from the model.
        """
        # Clean and reshape input data
        x_input = self._clean_input(x_input)
        
        # Predict and return the result
        return self.model.predict(x_input, verbose=0)