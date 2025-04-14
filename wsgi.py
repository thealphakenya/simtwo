import sys
import os

# Get the absolute path to the directory where wsgi.py is located
base_dir = os.path.abspath(os.path.dirname(__file__))

# Add the base directory to sys.path
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Add the backend directory to sys.path
backend_path = os.path.join(base_dir, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app instance from app.py
from app import app  # Ensure that app.py contains `app = FastAPI()`