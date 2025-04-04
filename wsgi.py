import sys
import os
import logging

# Set up logging to STDOUT so Docker can capture it
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Log current working directory
logging.info(f"Current working directory: {os.getcwd()}")

# Log sys.path to check where Python is looking for modules
logging.info(f"sys.path: {sys.path}")

# Optional: list root dir to help debug Docker build structure
try:
    logging.info(f"Contents of /app: {os.listdir('/app')}")
except Exception as e:
    logging.error(f"Error reading /app directory: {e}")

# Optional: check /app/backend visibility
backend_directory = '/app/backend'
if os.path.exists(backend_directory):
    logging.info(f"Contents of {backend_directory}: {os.listdir(backend_directory)}")
else:
    logging.warning(f"Directory does not exist: {backend_directory}")

# Now attempt to import the Flask app
try:
    from app import app  # Make sure your file is named app.py and in /app
    logging.info("Successfully imported app from app.py")
except ModuleNotFoundError as e:
    logging.error(f"ModuleNotFoundError: {e}")
    raise

# Optionally run Flask app directly
if __name__ == "__main__":
    app.run()
