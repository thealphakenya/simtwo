import sys
import os

# === ✅ Ensure /app is in Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

# === ✅ Ensure /backend is also in Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# === ✅ Import the Flask app
from app import app

# === ✅ Run the app (only if run directly, not by Gunicorn)
if __name__ == "__main__":
    app.run()
