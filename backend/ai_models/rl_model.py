import numpy as np
import random

class RLTradingModel:
    def __init__(
        self,
        state_size,
        action_size,
        learning_rate=0.1,
        discount_factor=0.95,
        exploration_rate=1.0
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = 0.995
        self.exploration_min = 0.01

    def _validate_state(self, state):
        if state >= self.q_table.shape[0]:
            # Expand Q-table if state is out of bounds
            extra_rows = state - self.q_table.shape[0] + 1
            self.q_table = np.vstack([self.q_table, np.zeros((extra_rows, self.action_size))])

    def choose_action(self, state):
        self._validate_state(state)
        if random.uniform(0, 1) < self.exploration_rate:
            return random.randint(0, self.action_size - 1)
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        self._validate_state(state)
        self._validate_state(next_state)

        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error
        self._decay_exploration()

    def _decay_exploration(self):
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay