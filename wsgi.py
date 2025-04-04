import sys
import os

# Add 'backend' to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Flask app instance from backend/app.py
from app import app
