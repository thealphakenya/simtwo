import sys
import os

# Set up the correct path for backend
app_root = os.path.abspath(os.path.dirname(__file__))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

backend_path = os.path.join(app_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import app  # Import the Flask app
