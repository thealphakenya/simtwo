import multiprocessing

# WSGI application path (module:app) — adjust if your wsgi.py is not at root level
wsgi_app = "app:app"  # Assuming your FastAPI instance is in 'app.py'

# Binding IP and Port
bind = "0.0.0.0:5000"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Adjust based on system resources

# Worker class (sync is default; 'gevent' or 'uvicorn.workers.UvicornWorker' for async)
worker_class = "sync"  # Use 'sync' for default synchronous workers or 'uvicorn.workers.UvicornWorker' for async workers

# Logging
loglevel = "info"
accesslog = "-"  # '-' means logs will be sent to stdout
errorlog = "-"   # '-' means logs will be sent to stderr

# Timeout for requests (in seconds)
timeout = 30

# Enable automatic restart on code change (for development only! This is generally disabled in production)
reload = False  # Set to True if you want auto-reload for development purposes

# Preload app for performance (loads the application code before forking workers, useful for memory efficiency)
preload_app = True
