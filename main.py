from app import app as flask_app  # Import the Flask app
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# Initialize FastAPI
app = FastAPI()

# Mount Flask app on root (the Flask app will handle routes)
app.mount("/", WSGIMiddleware(flask_app))