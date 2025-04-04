import sys
import os
import logging

# Log current working directory
logging.info(f"Current working directory: {os.getcwd()}")

# Log sys.path to check where Python is looking for modules
logging.info(f"Current sys.path: {sys.path}")

# Log the contents of the /app/backend directory to check if it's correctly visible
backend_directory = '/app/backend'
logging.info(f"Contents of {backend_directory}: {os.listdir(backend_directory)}")

# Continue with the rest of the code...
