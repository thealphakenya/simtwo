module.exports = {
  apps: [
    {
      name: "fastapi-app",
      script: "gunicorn",
      args: "-w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 app:app",
      interpreter: "python3",
      env: {
        PYTHONUNBUFFERED: "1",
        PYTHONDONTWRITEBYTECODE: "1"
      }
    },
    {
      name: "ws-server",
      script: "ws_server.js",
      interpreter: "node",
      env: {
        NODE_ENV: "production",
        PORT: "8765"
      }
    }
  ]
};