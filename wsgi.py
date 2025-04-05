import sys
import os
from flask import Flask

# Add the app directory and backend directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import the Flask app
from app import app

# Configure gunicorn to use the correct app
if __name__ == "__main__":
    app.run()
