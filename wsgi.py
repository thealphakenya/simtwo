import sys
import os

# Get absolute path to the current directory (where wsgi.py lives)
app_root = os.path.abspath(os.path.dirname(__file__))

# Add project root to sys.path
if app_root not in sys.path:
    sys.path.insert(0, app_root)

# Add backend to sys.path
backend_path = os.path.join(app_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Now import the FastAPI app
from app import app  # This assumes your FastAPI instance is named `app` in app.py