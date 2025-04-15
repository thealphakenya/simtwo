from app import app as flask_app  # Import the Flask app from app.py
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# Initialize FastAPI
app = FastAPI()

# Mount Flask app at root (Flask will handle routes for this part)
app.mount("/", WSGIMiddleware(flask_app))

# Additional FastAPI endpoints can go here, e.g., for async tasks
@app.get("/fastapi-endpoint")
async def fastapi_endpoint():
    return {"message": "This is a FastAPI endpoint!"}