import sys
import os

# Ensure the 'backend' directory is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Now import the application
from backend.app import app  # Ensure your Flask app is properly imported

if __name__ == "__main__":
    app.run()
