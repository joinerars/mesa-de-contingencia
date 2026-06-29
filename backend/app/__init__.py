from flask import Flask, request, jsonify
from .routes import main_bp

def create_app():
    app = Flask(__name__)

    @app.after_request
    def apply_cors(response):
        origin = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response

    @app.route("/api/<path:path>", methods=["OPTIONS"])
    @app.route("/api/", methods=["OPTIONS"])
    def options_handler(path=""):
        return "", 204

    app.register_blueprint(main_bp)
    return app
