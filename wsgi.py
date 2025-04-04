# wsgi.py
import sys
import os

# Add the 'backend' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import your application logic
from backend.trading_logic import order_execution

# Assuming your Flask app is defined in backend.app
from backend.app import app

# This ensures that the app can be run directly (optional, for local testing)
if __name__ == "__main__":
    app.run()
