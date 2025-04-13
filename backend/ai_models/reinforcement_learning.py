import numpy as np
import random
from collections import deque
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import logging

from .base import BaseTradingModel
from backend.core.status_manager import StatusManager  # Fixed import

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
        try:
            state = self.scaler.transform(state.reshape(1, -1))
            pred = self.model.predict(state, verbose=0)
            logger.debug(f"Prediction shape: {pred.shape}, content: {pred}")
            if isinstance(pred, np.ndarray):
                return float(pred[0][0]) if pred.ndim == 2 else float(pred[0])
            return float(pred)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return 0.0

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            action = random.choice([0, 1, 2])
            logger.debug(f"Random action selected: {action}")
            return action
        prediction = self.predict(state)
        logger.debug(f"Predicted action value: {prediction}")
        return 2 if prediction > 0.5 else 0  # Example decision logic

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            try:
                target = reward
                if not done:
                    next_state_scaled = self.scaler.transform(next_state.reshape(1, -1))
                    target += self.gamma * self.model.predict(next_state_scaled, verbose=0)[0][0]
                state_scaled = self.scaler.transform(state.reshape(1, -1))
                self.model.fit(state_scaled, np.array([target]), epochs=1, verbose=0)
            except Exception as e:
                logger.error(f"Replay step failed: {e}")
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train_model(self, data, target, epochs=50, batch_size=32):
        data = self.scaler.fit_transform(data)
        for e in range(epochs):
            logger.info(f"Epoch {e+1}/{epochs}")
            for i in range(0, len(data) - self.time_steps, batch_size):
                state = data[i:i + self.time_steps].reshape(-1)
                next_state = data[i + 1:i + self.time_steps + 1].reshape(-1) \
                    if i + self.time_steps + 1 < len(data) else state
                action = self.act(state)
                reward = self.calculate_reward(action, target[i])
                done = i + self.time_steps + 1 >= len(data)
                self.remember(state, action, reward, next_state, done)
                self.replay()

    def calculate_reward(self, action, actual_price):
        if (action == 2 and actual_price > 30000) or (action == 0 and actual_price < 30000):
            reward = 1
        else:
            reward = -1
        logger.debug(f"Action: {action}, Price: {actual_price}, Reward: {reward}")
        return reward