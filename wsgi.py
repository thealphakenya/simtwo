import sys
import os

# =============================
# 🛣️ Set Up Python Path
# =============================

# Get absolute path to the current directory (project root)
app_root = os.path.abspath(os.path.dirname(__file__))

# Add root and backend directories to sys.path for module resolution
if app_root not in sys.path:
    sys.path.insert(0, app_root)

backend_path = os.path.join(app_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# =============================
# 🚀 Import Flask App
# =============================
from app import app  # Make sure `app.py` is in the root directory and defines `app = Flask(__name__)`
