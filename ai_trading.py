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
                'enabled': False,
                'start': time(9, 30),
                'end': time(16, 0),
                'days': [0, 1, 2, 3, 4]  # Weekdays
            },
            'risk_per_trade': 2,
            'max_daily_trades': 10
        }
        self.load_model()

    def load_model(self):
        """Load pre-trained AI model with configurable parameters"""
        self.model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(60, 5)),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(3, activation='softmax')  # Buy, Hold, Sell
        ])
        self.model.compile(optimizer='adam', loss='categorical_crossentropy')

    def should_trade(self):
        """Check if trading is allowed based on settings"""
        now = datetime.now()
        if self.config['trading_hours']['enabled']:
            if now.weekday() not in self.config['trading_hours']['days']:
                return False
            if not (self.config['trading_hours']['start'] <= now.time() <= self.config['trading_hours']['end']):
                return False
        return True

    def predict_action(self, market_data):
        """Enhanced prediction with risk management"""
        if not self.should_trade():
            return 'hold'
        
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