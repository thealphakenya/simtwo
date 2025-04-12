import json
import os
from typing import Dict, List

# File paths
MEMORY_FILE = "conversation_memory.json"
WEIGHTS_FILE = "strategy_weights.json"

# Default fallback
default_weights = {
    "lstm": 0.33,
    "trading_ai": 0.33,
    "rl": 0.34
}

# Ensure files exist
def _ensure_files():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f)

    if not os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE, "w") as f:
            json.dump(default_weights, f)

_ensure_files()

# Conversation memory functions
def load_memory() -> List[Dict[str, str]]:
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def reset_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

def append_conversation(user_input: str, reply: str):
    memory = load_memory()
    memory.append({"user": user_input, "ai": reply})
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Strategy weight management
def get_strategy_weights() -> Dict[str, float]:
    try:
        with open(WEIGHTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return default_weights

def update_strategy_weights(new_weights: Dict[str, float]):
    weights = get_strategy_weights()
    weights.update(new_weights)
    # Normalize to ensure sum = 1
    total = sum(weights.values())
    if total == 0:
        total = 1
    normalized_weights = {k: v / total for k, v in weights.items()}
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(normalized_weights, f, indent=2)