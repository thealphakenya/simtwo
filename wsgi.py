import sys
import os
import logging
import traceback

# ===========================
# 📜 Logging Setup
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("🔧 Bootstrapping WSGI...")

# ===========================
# 📂 Debug Filesystem & Paths
# ===========================
try:
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Initial sys.path: {sys.path}")

    # Add backend directory to Python path
    backend_path = "/app/backend"
    if backend_path not in sys.path:
        sys.path.append(backend_path)
        logging.info(f"✅ Added {backend_path} to sys.path.")

    logging.info(f"Updated sys.path: {sys.path}")

    # Debug directory structure
    logging.info(f"📁 /app contents: {os.listdir('/app')}")
    if os.path.exists(backend_path):
        logging.info(f"📁 {backend_path} contents: {os.listdir(backend_path)}")
    else:
        logging.warning(f"⚠️ Directory not found: {backend_path}")

except Exception as e:
    logging.error(f"❌ Filesystem/path check failed: {e}")
    traceback.print_exc()

# ===========================
# 🧪 Test Module Imports
# ===========================
try:
    from trading_logic.order_execution import OrderExecution
    logging.info("✅ Successfully imported OrderExecution module.")
except Exception as e:
    logging.error("❌ Could not import from trading_logic:")
    traceback.print_exc()

# ===========================
# 🚀 Import Flask App
# ===========================
try:
    from app import app  # Ensure app.py exists in the root directory and contains 'app = Flask(__name__)'
    logging.info("✅ Successfully imported Flask app.")
except Exception as e:
    logging.critical("❌ Failed to import Flask app:")
    traceback.print_exc()

    # Fallback Flask app to provide meaningful error if app fails to load
    from flask import Flask, jsonify
    fallback_app = Flask(__name__)

    @fallback_app.route("/", defaults={"path": ""})
    @fallback_app.route("/<path:path>")
    def fallback_handler(path):
        return jsonify({
            "status": "error",
            "message": "Flask app failed to load due to import error.",
            "details": str(e),
            "hint": "Check logs for missing files, modules, or circular imports."
        }), 500

    app = fallback_app

# ===========================
# 🧪 Local Debug Mode
# ===========================
if __name__ == "__main__":
    logging.info("🧪 Running app locally for debug purposes...")
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)  # Ensure debugging and proper binding
    except Exception as e:
        logging.critical("🔥 Flask failed to start:")
        traceback.print_exc()
