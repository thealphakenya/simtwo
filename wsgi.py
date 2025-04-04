import sys
import os

# Ensure the parent directory is added to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.app import app  # Now it should be able to find 'backend.app'
