import time
import logging

class StatusManager:
    def __init__(self, confidence_threshold=0.85, cooldown_seconds=60):
        self.confidence_threshold = confidence_threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_trade_time = 0
        self.state = 'monitoring'  # or 'trading'

    def can_trade(self, confidence):
        now = time.time()
        if confidence >= self.confidence_threshold and (now - self.last_trade_time) > self.cooldown_seconds:
            logging.info(f"Confidence {confidence:.2f} passed threshold. Ready to trade.")
            return True
        return False

    def update_trade_status(self, traded=False):
        if traded:
            self.last_trade_time = time.time()
            self.state = 'cooldown'
            logging.info("Trade executed. Entering cooldown period.")
        else:
            self.state = 'monitoring'

    def get_status(self):
        return {
            "state": self.state,
            "cooldown_remaining": max(0, self.cooldown_seconds - (time.time() - self.last_trade_time)),
            "can_trade": self.state != 'cooldown'
        }