import sys
import os

# Add the app root and backend to sys.path
app_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, app_root)  # Ensure app root is the first in the sys.path

backend_path = os.path.join(app_root, 'backend')
sys.path.insert(0, backend_path)  # Ensure backend is included in sys.path

from app import app  # Import the Flask app
