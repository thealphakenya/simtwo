import numpy as np import tensorflow as tf from tensorflow.keras.models import Sequential from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout from sklearn.preprocessing import StandardScaler from collections import deque import random

--- Base Trading Model ---

class BaseTradingModel: def train(self, X, y, epochs=10, batch_size=32): raise NotImplementedError

def predict(self, X):
    raise NotImplementedError

--- Reinforcement Learning Model ---

class ReinforcementLearning(BaseTradingModel): def init(self, api_key, api_secret, time_steps=10, n_features=10): self.api_key = api_key self.api_secret = api_secret self.time_steps = time_steps self.n_features = n_features self.scaler = StandardScaler() self.model = self.build_model() self.memory = deque(maxlen=2000) self.gamma = 0.95 self.epsilon = 1.0 self.epsilon_min = 0.01 self.epsilon_decay = 0.995 self.batch_size = 32

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

def train_model(self, data, target, epochs=50, batch_size=32):
    for e in range(epochs):
        for i in range(0, len(data), batch_size):
            state = data[i:i+batch_size]
            next_state = data[i+1:i+batch_size+1] if i+1 < len(data) else state
            action = self.act(state)
            reward = self.calculate_reward(action, target[i])
            done = True if i + 1 >= len(data) else False
            self.remember(state, action, reward, next_state, done)
            self.replay()

def calculate_reward(self, action, actual_price):
    reward = 0
    if action == 2:
        reward = 1 if actual_price > 30000 else -1
    elif action == 0:
        reward = 1 if actual_price < 30000 else -1
    return reward

--- LSTM Trading Model ---

class LSTMTradingModel(BaseTradingModel): def init(self, time_steps=10, n_features=10): self.time_steps = time_steps self.n_features = n_features self.model = self.build_model()

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

--- GRU Trading Model ---

class GRUTradingModel(BaseTradingModel): def init(self, time_steps=10, n_features=10): self.time_steps = time_steps self.n_features = n_features self.model = self.build_model()

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

--- Transformer Trading Model ---

class TransformerTradingModel(BaseTradingModel): def init(self, time_steps=10, n_features=10): self.time_steps = time_steps self.n_features = n_features self.model = self.build_model()

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
    X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
    self.model.fit(X, y, epochs=epochs, batch_size=batch_size)

def predict(self, X):
    X = np.array(X).reshape((X.shape[0], self.time_steps, self.n_features))
    return self.model.predict(X)

--- TradingAI High-Level Wrapper ---

class TradingAI: def init(self, model_type='lstm', time_steps=10, n_features=10, api_key=None, api_secret=None): self.model_type = model_type.lower() self.model = self._init_model(model_type, time_steps, n_features, api_key, api_secret)

def _init_model(self, model_type, time_steps, n_features, api_key, api_secret):
    if model_type == 'lstm':
        return LSTMTradingModel(time_steps, n_features)
    elif model_type == 'gru':
        return GRUTradingModel(time_steps, n_features)
    elif model_type == 'transformer':
        return TransformerTradingModel(time_steps, n_features)
    elif model_type == 'reinforcement':
        return ReinforcementLearning(api_key, api_secret, time_steps, n_features)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

def train(self, X, y=None, epochs=10, batch_size=32):
    if hasattr(self.model, 'train_model'):
        self.model.train_model(X, y, epochs, batch_size)
    else:
        self.model.train(X, y, epochs=epochs, batch_size=batch_size)

def predict(self, X):
    return self.model.predict(X)

