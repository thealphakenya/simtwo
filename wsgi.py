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
logging.info(f"Initial sys.path: {sys.path}")

# Add backend directory to Python path manually
backend_path = "/app/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)
    logging.info(f"Added {backend_path} to sys.path.")

# Log sys.path again after appending
logging.info(f"Updated sys.path: {sys.path}")

# Optional: list root dir to help debug Docker build structure
try:
    logging.info(f"Contents of /app: {os.listdir('/app')}")
except Exception as e:
    logging.error(f"Error reading /app directory: {e}")

# Optional: check /app/backend visibility
if os.path.exists(backend_path):
    try:
        logging.info(f"Contents of {backend_path}: {os.listdir(backend_path)}")
    except Exception as e:
        logging.error(f"Error reading {backend_path}: {e}")
else:
    logging.warning(f"Directory does not exist: {backend_path}")

# Try importing directly from backend now
try:
    from trading_logic.order_execution import OrderExecution  # Just to confirm import works here too
    logging.info("Successfully imported OrderExecution from trading_logic")
except ModuleNotFoundError as e:
    logging.error(f"Failed to import from trading_logic: {e}")
    raise

# Import the app AFTER fixing the path
try:
    from app import app
    logging.info("Successfully imported app from app.py")
except ModuleNotFoundError as e:
    logging.error(f"Failed to import app: {e}")
    raise

# Optionally run Flask app directly (usually not needed with gunicorn)
if __name__ == "__main__":
    app.run()
