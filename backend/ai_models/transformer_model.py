# backend/ai_models/transformer_model.py

import tensorflow as tf
from tensorflow.keras import layers, models

class TransformerTradingModel:
    def __init__(self, time_steps=60, d_model=64, n_heads=2, ff_dim=128):
        self.time_steps = time_steps
        self.d_model = d_model
        self.model = self._build_model(n_heads, ff_dim)

    def _build_model(self, n_heads, ff_dim):
        inputs = layers.Input(shape=(self.time_steps, 1))
        x = layers.LayerNormalization(epsilon=1e-6)(inputs)

        attention_output = layers.MultiHeadAttention(num_heads=n_heads, key_dim=self.d_model)(x, x)
        x = layers.Add()([x, attention_output])
        x = layers.LayerNormalization(epsilon=1e-6)(x)

        ff_output = layers.Dense(ff_dim, activation='relu')(x)
        ff_output = layers.Dense(1)(ff_output)
        x = layers.Add()([x, ff_output])
        x = layers.GlobalAveragePooling1D()(x)
        outputs = layers.Dense(1)(x)

        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='mse')
        return model

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        return self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

    def predict(self, x_input):
        return self.model.predict(x_input)