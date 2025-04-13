import sys
import os

# Get absolute path to the current directory (where wsgi.py lives)
app_root = os.path.abspath(os.path.dirname(__file__))

# Add project root to sys.path (if it's not already there)
if app_root not in sys.path:
    sys.path.insert(0, app_root)

# Add the backend folder to sys.path (if it's not already there)
backend_path = os.path.join(app_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# You might also need to add other folders depending on where your modules are located
# For example, if you have `core`, you can do this:
# core_path = os.path.join(app_root, 'core')
# if core_path not in sys.path:
#     sys.path.insert(0, core_path)

# Now import the FastAPI app from your app module (assuming it's inside app.py)
from app import app  # Assumes your FastAPI instance is named `app` in app.py