class BaseTradingModel:
    def train(self, X, y, epochs=10, batch_size=32):
        raise NotImplementedError

    def predict(self, X):
        raise NotImplementedError