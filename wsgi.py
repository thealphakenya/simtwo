import sys
import os

# 📌 Ensure the app root and backend path are in the system path
app_root = os.path.abspath(os.path.dirname(__file__))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

# Ensure the backend folder is correctly added to the system path
backend_path = os.path.join(app_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# 🚀 Import the Flask app from app.py
from app import app

# To run the app with Gunicorn, the `app` variable from the `app.py` is used.
# Gunicorn will look for `app` when starting the server, so ensure it's referenced correctly.
