# gunicorn.conf.py

import multiprocessing

# WSGI application path (module:app) — adjust if your wsgi.py is not at root level
wsgi_app = "wsgi:app"

# Binding IP and Port
bind = "0.0.0.0:5000"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class (sync is default; 'gevent' or 'uvicorn.workers.UvicornWorker' for async)
worker_class = "sync"

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Timeout for requests
timeout = 30

# Enable automatic restart on code change (for development only!)
reload = False

# Preload app for performance
preload_app = True
