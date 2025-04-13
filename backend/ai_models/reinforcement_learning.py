import numpy as np
import random
from collections import deque
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from .base import BaseTradingModel
from core.status_manager import StatusManager

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
        self.status_manager = StatusManager(confidence_threshold=0.85)

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
        return self.model.predict(state, verbose=0)[0][0]

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.choice([0, 1, 2])
        return self.predict(state)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.gamma * self.model.predict(
                    self.scaler.transform(next_state.reshape(1, -1)), verbose=0
                )[0][0]
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
        reward = 1 if (action == 2 and actual_price > 30000) or (action == 0 and actual_price < 30000) else -1
        return reward