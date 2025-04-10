import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, GRU, Dropout, Input, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import time
from sklearn.metrics import mean_squared_error
from sklearn.decomposition import PCA

# --- Base class for common structure ---
class BaseTradingModel:
    def __init__(self, time_steps=10, n_features=10, model=None):
        self.model = model
        self.time_steps = time_steps
        self.n_features = n_features
        self.scaler = StandardScaler()

    def train(self, data, target, epochs=50, batch_size=32):
        """
        Train the model on provided data.
        """
        # Scaling the features
        X_train, X_val, y_train, y_val = train_test_split(data, target, test_size=0.2, random_state=42)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)

        self.model.fit(X_train_scaled, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_val_scaled, y_val))

    def predict(self, data):
        """
        Make predictions using the trained model.
        """
        data_scaled = self.scaler.transform(data)
        return self.model.predict(data_scaled)

    def save_model(self, file_path):
        """
        Save the trained model to a file.
        """
        self.model.save(file_path)

    def load_model(self, file_path):
        """
        Load a trained model from a file.
        """
        self.model = tf.keras.models.load_model(file_path)

    def evaluate(self, data, target):
        """
        Evaluate the model on validation or test set.
        """
        data_scaled = self.scaler.transform(data)
        y_pred = self.model.predict(data_scaled)
        mse = mean_squared_error(target, y_pred)
        return mse


# --- LSTM Model ---
class LSTMTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        model = Sequential([
            LSTM(64, input_shape=(time_steps, n_features), activation='relu', return_sequences=True),
            Dropout(0.2),
            LSTM(32, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        super().__init__(time_steps, n_features, model)


# --- GRU Model ---
class GRUTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        model = Sequential([
            GRU(64, input_shape=(time_steps, n_features), activation='relu', return_sequences=True),
            Dropout(0.2),
            GRU(32, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        super().__init__(time_steps, n_features, model)


# --- Transformer Model ---
class TransformerTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        inputs = Input(shape=(time_steps, n_features))
        x = MultiHeadAttention(num_heads=4, key_dim=64)(inputs, inputs)
        x = LayerNormalization()(x)
        x = GlobalAveragePooling1D()(x)
        x = Dense(32, activation='relu')(x)
        x = Dropout(0.2)(x)
        output = Dense(1, activation='linear')(x)

        model = Model(inputs=inputs, outputs=output)
        model.compile(optimizer='adam', loss='mean_squared_error')
        super().__init__(time_steps, n_features, model)


# --- Backtesting Evaluation ---
def backtest_evaluation(model, historical_data, window_size=10):
    """
    Evaluate the model using a backtesting approach.
    """
    # Use the model to predict based on historical data
    predictions = []
    actual = []
    for i in range(window_size, len(historical_data)):
        train_data = historical_data[i - window_size:i]
        test_data = historical_data[i]
        prediction = model.predict(train_data.reshape(1, window_size, -1))  # 3D array: [samples, time_steps, features]
        predictions.append(prediction)
        actual.append(test_data)
    
    # Calculate the Mean Squared Error (MSE) between predictions and actual values
    mse = mean_squared_error(actual, predictions)
    return mse


# --- Auto-Training with Drift Detection ---
def detect_drift(previous_model, new_data, threshold=0.05):
    """
    Detect drift in model performance and decide if retraining is required.
    If the performance drops below the threshold, retrain the model.
    """
    # Evaluate model performance on new data
    previous_predictions = previous_model.predict(new_data)
    previous_model_performance = mean_squared_error(new_data['target'], previous_predictions)
    
    # If drift is detected (e.g., performance drops), retrain the model
    if previous_model_performance > threshold:
        return True
    return False

def auto_train(model, data, target, model_file='trading_model.h5', retrain_interval=3600):
    """
    Train the model periodically (every `retrain_interval` seconds).
    """
    while True:
        # Train the model if it’s the time to do so
        model.train(data, target)
        model.save_model(model_file)
        
        # Wait for the next training cycle
        time.sleep(retrain_interval)  # wait for `retrain_interval` seconds before retraining


# --- Example of usage ---
if __name__ == "__main__":
    # Load your data (replace with actual data loading)
    historical_data = pd.read_csv("historical_data.csv")  # Example data loading
    X = historical_data.drop(columns=['target'])  # Example features (e.g., price, indicators)
    y = historical_data['target']  # Target variable (e.g., future price)

    # Initialize model
    trading_model = LSTMTradingModel(time_steps=10, n_features=X.shape[1])

    # Train model
    trading_model.train(X, y, epochs=50, batch_size=32)

    # Backtesting evaluation
    mse = backtest_evaluation(trading_model, X)
    print(f"Backtesting MSE: {mse}")

    # Detect drift and retrain if necessary
    if detect_drift(trading_model, X):
        print("Model drift detected. Retraining...")
        trading_model.train(X, y, epochs=50, batch_size=32)
    
    # Save the model
    trading_model.save_model('trading_model.h5')
