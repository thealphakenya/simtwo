# model.py
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd

class TradingAI:
    def __init__(self, model=None):
        # If no model is provided, a new one will be created
        self.model = model if model else self.create_model()

    def create_model(self):
        """Create a basic neural network model."""
        model = Sequential([
            Dense(128, input_dim=10, activation='relu'),
            Dense(64, activation='relu'),
            Dense(1, activation='linear')  # Regression output for price prediction or trading signal
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, data, target, epochs=50, batch_size=32):
        """Train the model using historical market data."""
        X_train, X_val, y_train, y_val = train_test_split(data, target, test_size=0.2, random_state=42)
        # Scaling the data for better performance
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_val = scaler.transform(X_val)
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_val, y_val))

    def predict(self, data):
        """Predict future prices or signals using the trained model."""
        return self.model.predict(data)

    def save_model(self, file_path):
        """Save the trained model to a file."""
        self.model.save(file_path)

    def load_model(self, file_path):
        """Load a saved model from a file."""
        self.model = tf.keras.models.load_model(file_path)