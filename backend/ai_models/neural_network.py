import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class NeuralNetwork:
    def __init__(self, input_dim, output_dim):
        """
        Initialize the neural network model.

        :param input_dim: Number of input features.
        :param output_dim: Number of output features (e.g., for regression or classification).
        """
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.model = self._build_model()

    def _build_model(self):
        """
        Build a simple feed-forward neural network.

        :return: Compiled Keras model.
        """
        model = Sequential()
        model.add(Dense(64, input_dim=self.input_dim, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(self.output_dim, activation='linear'))  # 'linear' for regression tasks, change for classification
        model.compile(optimizer='adam', loss='mean_squared_error')  # Change loss for classification tasks
        return model

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        """
        Train the neural network on the provided data.

        :param x_train: Training features.
        :param y_train: Training labels.
        :param epochs: Number of epochs for training.
        :param batch_size: Batch size for training.
        """
        try:
            logger.info(f"Training model with input shape {x_train.shape} and output shape {y_train.shape}")
            self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

    def predict(self, x_input):
        """
        Predict output for a given input.

        :param x_input: Input data for prediction.
        :return: Model's predictions.
        """
        try:
            prediction = self.model.predict(x_input, verbose=0)
            logger.debug(f"Prediction shape: {prediction.shape}, content: {prediction}")
            return prediction
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None

    def evaluate(self, x_test, y_test):
        """
        Evaluate the model on the test data.

        :param x_test: Test features.
        :param y_test: Test labels.
        :return: Model's performance on the test data.
        """
        try:
            performance = self.model.evaluate(x_test, y_test, verbose=0)
            logger.info(f"Model evaluation: Loss = {performance}")
            return performance
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return None