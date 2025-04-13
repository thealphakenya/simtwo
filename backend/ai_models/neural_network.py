import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
import logging

logger = logging.getLogger(__name__)

class NeuralNetwork:
    def __init__(self, input_dim, output_dim):
        self.model = self.build_model(input_dim, output_dim)

    def build_model(self, input_dim, output_dim):
        model = Sequential([
            Input(shape=(input_dim,)),  # Input layer (fixing the input shape warning)
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(output_dim, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        x_train = np.array(x_train)  # Ensure it's a NumPy array
        logger.info(f"Training on data of shape: {x_train.shape}, labels of shape: {y_train.shape}")
        self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, x_input):
        x_input = np.array(x_input)  # Ensure input is NumPy array

        # Ensure the input has the correct shape
        if len(x_input.shape) == 1:  # Add feature dimension if it's 1D
            x_input = np.expand_dims(x_input, axis=-1)

        if len(x_input.shape) == 2:  # Add sample dimension if it's 2D
            x_input = np.expand_dims(x_input, axis=0)

        # Ensure the data has the correct shape (samples, time_steps, features)
        if len(x_input.shape) != 3:
            raise ValueError(f"Input shape must be (samples, time_steps, features). Got {x_input.shape}")

        # Making prediction and logging it
        try:
            prediction = self.model.predict(x_input, verbose=0)
            logger.info(f"Prediction: {prediction}")
            return prediction
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None