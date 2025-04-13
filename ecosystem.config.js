module.exports = {
  apps: [
    {
      name: "fastapi-app",
      script: "gunicorn", // Use gunicorn to serve the FastAPI app
      args: "-w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 app:app",
      interpreter: "python3", // Ensure you're using python3
      cwd: "/app", // Make sure the working directory is set to /app
      env: {
        PYTHONUNBUFFERED: "1", // Disable buffering for real-time logs
        PYTHONDONTWRITEBYTECODE: "1", // Prevent writing .pyc files
        PYTHONPATH: "/app", // Ensure the module path is set correctly
      },
    },
    {
      name: "ws-server",
      script: "ws_server.js", // Start your WebSocket server
      interpreter: "node", // Ensure Node.js is used for this script
      cwd: "/app", // Set the working directory to the root of the app
      env: {
        NODE_ENV: "production", // Set the environment to production
        PORT: "8765", // Set the port for the WebSocket server
      },
    },
  ],
};