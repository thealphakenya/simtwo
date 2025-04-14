# backend/ai_models/trainer.py

import numpy as np
from sklearn.model_selection import train_test_split
from backend.ai_models.lstm_model import LSTMTradingModel
from backend.ai_models.gru_model import GRUTradingModel
from backend.ai_models.transformer_model import TransformerTradingModel
from backend.ai_models.rl_model import RLTradingModel

def train_model(model, data, labels, epochs=10, batch_size=32):
    """
    Function to train a given model.

    Parameters:
    - model: The trading model to train (LSTM, GRU, etc.)
    - data: Input data for training
    - labels: Labels (targets) for training
    - epochs: Number of epochs to train
    - batch_size: Batch size for training

    Returns:
    - Trained model
    """
    if isinstance(model, (LSTMTradingModel, GRUTradingModel, TransformerTradingModel)):
        # Split data into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(data, labels, test_size=0.2, random_state=42)
        
        # Train the model
        print(f"Training {model.__class__.__name__} model...")
        
        # Fit the model with the training data
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_val, y_val))
        
        print(f"{model.__class__.__name__} training complete.")
        
        return model

    elif isinstance(model, RLTradingModel):
        # In the case of reinforcement learning, training is handled differently
        print("Training Reinforcement Learning model...")

        # Placeholder for RL model training (update with your RL logic)
        for epoch in range(epochs):
            # Simulate some environment and training loop for RL (this is just a dummy loop)
            for state in range(100):  # Assuming 100 states as an example
                action = model.choose_action(state)
                reward = np.random.rand()  # Example reward (replace with real reward logic)
                next_state = (state + 1) % 100
                model.learn(state, action, reward, next_state)

        print(f"Reinforcement Learning model training complete.")
        
        return model

    else:
        raise ValueError(f"Unsupported model type: {type(model)}")