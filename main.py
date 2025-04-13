from app import app as flask_app
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

app = FastAPI()

# Mount Flask app on root
app.mount("/", WSGIMiddleware(flask_app))