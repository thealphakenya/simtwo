import numpy as np
import random
import logging

logger = logging.getLogger(__name__)

class RLTradingModel:
    def __init__(
        self,
        state_size,
        action_size,
        learning_rate=0.1,
        discount_factor=0.95,
        exploration_rate=1.0,
        exploration_decay=0.995,
        exploration_min=0.01
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.exploration_min = exploration_min
        self.q_table = np.zeros((state_size, action_size))
        logger.info("Initialized RLTradingModel with state_size=%d, action_size=%d", state_size, action_size)

    def _validate_state(self, state):
        if state >= self.q_table.shape[0]:
            extra_rows = state - self.q_table.shape[0] + 1
            logger.debug("Expanding Q-table by %d rows for new state: %d", extra_rows, state)
            self.q_table = np.vstack([self.q_table, np.zeros((extra_rows, self.action_size))])

    def choose_action(self, state):
        self._validate_state(state)
        if random.random() < self.exploration_rate:
            action = random.randint(0, self.action_size - 1)
            logger.debug("Exploration: chose random action %d", action)
        else:
            action = int(np.argmax(self.q_table[state]))
            logger.debug("Exploitation: chose best action %d", action)
        return action

    def learn(self, state, action, reward, next_state):
        self._validate_state(state)
        self._validate_state(next_state)

        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error

        logger.debug(
            "Updated Q-table at state=%d, action=%d | Reward=%.4f, TD Error=%.4f",
            state, action, reward, td_error
        )
        self._decay_exploration()

    def _decay_exploration(self):
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay
            self.exploration_rate = max(self.exploration_rate, self.exploration_min)
            logger.debug("Decayed exploration rate to %.4f", self.exploration_rate)