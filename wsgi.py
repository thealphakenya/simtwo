import sys
import os

# Add the /app directory and /app/backend directory to sys.path
app_root = os.path.abspath(os.path.dirname(__file__))
if app_root not in sys.path:
    sys.path.append(app_root)

backend_path = os.path.join(app_root, 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app import app  # Import the Flask app
