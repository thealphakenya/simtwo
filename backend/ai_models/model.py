import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout
from sklearn.preprocessing import StandardScaler
from collections import deque
import random

# --- Base Trading Model ---
class BaseTradingModel:
    def train(self, X, y, epochs=10, batch_size=32):
        raise NotImplementedError("Train method must be implemented.")

    def predict(self, X):
        raise NotImplementedError("Predict method must be implemented.")


# --- LSTM Trading Model ---
class LSTMTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            LSTM(50, input_shape=(self.time_steps, self.n_features), return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, X, y, epochs=10, batch_size=32):
        X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size)

    def predict(self, X):
        X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
        return self.model.predict(X)


# --- GRU Trading Model ---
class GRUTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            GRU(50, input_shape=(self.time_steps, self.n_features), return_sequences=True),
            Dropout(0.2),
            GRU(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, X, y, epochs=10, batch_size=32):
        X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size)

    def predict(self, X):
        X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
        return self.model.predict(X)


# --- Transformer Trading Model (simplified as dense MLP) ---
class TransformerTradingModel(BaseTradingModel):
    def __init__(self, time_steps=10, n_features=10):
        self.time_steps = time_steps
        self.n_features = n_features
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            Dense(64, input_dim=self.n_features * self.time_steps, activation='relu'),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, X, y, epochs=10, batch_size=32):
        X = np.array(X).reshape((X.shape[0], self.n_features * self.time_steps))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size)

    def predict(self, X):
        X = np.array(X).reshape((X.shape[0], self.n_features * self.time_steps))
        return self.model.predict(X)


# --- Reinforcement Learning Model ---
class ReinforcementLearning(BaseTradingModel):
    def __init__(self, api_key, api_secret, time_steps=10, n_features=10):
        self.api_key = api_key
        self.api_secret = api_secret
        self.time_steps = time_steps
        self.n_features = n_features
        self.scaler = StandardScaler()
        self.model = self.build_model()

        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32

    def build_model(self):
        model = Sequential([
            Dense(64, input_dim=self.n_features * self.time_steps, activation='relu'),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def predict(self, state):
        state = self.scaler.transform(state.reshape(1, -1))
        return self.model.predict(state)[0][0]

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.choice([0, 1, 2])
        else:
            return self.predict(state)

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.gamma * self.model.predict(self.scaler.transform(next_state.reshape(1, -1)))[0][0]
            state = self.scaler.transform(state.reshape(1, -1))
            self.model.fit(state, np.array([target]), epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train(self, X, y, epochs=10, batch_size=32):
        for e in range(epochs):
            for i in range(0, len(X), batch_size):
                state = X[i]
                next_state = X[i+1] if i + 1 < len(X) else state
                action = self.act(state)
                reward = self.calculate_reward(action, y[i])
                done = i + 1 >= len(X)
                self.remember(state, action, reward, next_state, done)
                self.replay()

    def calculate_reward(self, action, actual_price):
        if action == 2:
            return 1 if actual_price > 30000 else -1
        elif action == 0:
            return 1 if actual_price < 30000 else -1
        return 0


# --- TradingAI Wrapper ---
class TradingAI:
    def __init__(self, model_type="lstm", **kwargs):
        model_classes = {
            "lstm": LSTMTradingModel,
            "gru": GRUTradingModel,
            "transformer": TransformerTradingModel,
            "rl": ReinforcementLearning
        }
        model_class = model_classes.get(model_type.lower())
        if not model_class:
            raise ValueError(f"Unknown model type: {model_type}")
        self.model = model_class(**kwargs)

    def train(self, X, y, epochs=10, batch_size=32):
        self.model.train(X, y, epochs, batch_size)

    def predict(self, X):
        return self.model.predict(X)


# --- Utility function ---
def train_model(model, X, y, epochs=10, batch_size=32):
    model.train(X, y, epochs, batch_size)
