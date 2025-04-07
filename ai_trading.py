import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from datetime import datetime, time

class TradingAI:
    def __init__(self, config=None):
        self.model = None
        self.config = config or {
            'aggressiveness': 3,  # 1-5 scale
            'stop_loss': 5,       # Percentage
            'trailing_stop': 'none',
            'trading_hours': {
                'enabled': True,
                'start': time(9, 30),
                'end': time(16, 0),
                'days': [0, 1, 2, 3, 4]  # Weekdays
            },
            'risk_per_trade': 2,
            'max_daily_trades': 10,
            'trade_cooldown': 5,   # Cooldown in minutes after each trade
            'lookback_window': 60  # The number of time steps for input (historical data window)
        }
        self.last_trade_time = None  # Track last trade time
        self.load_model()

    def load_model(self):
        """Load or initialize AI model with configurable parameters"""
        self.model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.config['lookback_window'], 5)),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(3, activation='softmax')  # Buy, Hold, Sell
        ])
        self.model.compile(optimizer='adam', loss='categorical_crossentropy')

    def should_trade(self):
        """Check if trading is allowed based on settings"""
        now = datetime.now()
        # Check if trading hours are enabled and validate the time window
        if self.config['trading_hours']['enabled']:
            if now.weekday() not in self.config['trading_hours']['days']:
                return False
            if not (self.config['trading_hours']['start'] <= now.time() <= self.config['trading_hours']['end']):
                return False

        # Check for trade cooldown (do not trade too frequently)
        if self.last_trade_time and (now - self.last_trade_time).total_seconds() < self.config['trade_cooldown'] * 60:
            return False

        return True

    def predict_action(self, market_data):
        """Enhanced prediction with risk management"""
        if not self.should_trade():
            return 'hold'

        # Reshaping market data to match the model input
        market_data = np.expand_dims(market_data, axis=0)  # Add batch dimension

        prediction = self.model.predict(market_data)
        action = np.argmax(prediction)
        confidence = np.max(prediction)

        # Adjust based on aggressiveness
        if self.config['aggressiveness'] < 3 and confidence < 0.7:
            return 'hold'
        if self.config['aggressiveness'] > 3 and confidence > 0.5:
            return ['sell', 'hold', 'buy'][action]

        return ['sell', 'hold', 'buy'][action]

    def calculate_position_size(self, balance, risk_percent=None):
        """Dynamic position sizing based on risk parameters"""
        risk = risk_percent or self.config['risk_per_trade']
        return balance * (risk / 100)

    def execute_trade(self, balance, action):
        """Execute the trade based on predicted action and risk parameters"""
        position_size = self.calculate_position_size(balance)

        if action == 'buy':
            return f"Buying {position_size} BTC"
        elif action == 'sell':
            return f"Selling {position_size} BTC"
        else:
            return "Holding position"

    def update_last_trade_time(self):
        """Update last trade time after a trade"""
        self.last_trade_time = datetime.now()
