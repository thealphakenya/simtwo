import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))  # Root of the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))  # Add 'backend' folder

# Log the current sys.path to verify the paths
print("Debug: Current sys.path in wsgi.py:", sys.path)

# Import the Flask app instance from backend/app.py
from app import app  # 'app' here refers to the Flask instance inside 'backend/app.py'

if __name__ == "__main__":
    app.run(debug=True)
