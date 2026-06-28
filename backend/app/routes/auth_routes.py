from flask import request, jsonify
from . import main_bp
from ..auth import login_user, logout_token, get_current_user, require_auth

@main_bp.post("/api/login")
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400
    result = login_user(username, password)
    if not result:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
    token, user = result
    return jsonify({"token": token, "user": user})

@main_bp.post("/api/logout")
@require_auth
def logout():
    auth = request.headers.get("Authorization", "")[7:]
    logout_token(auth)
    return jsonify({"ok": True})

@main_bp.get("/api/me")
@require_auth
def me():
    return jsonify(get_current_user())
