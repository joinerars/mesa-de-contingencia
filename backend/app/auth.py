import secrets
from functools import wraps
from flask import request, jsonify
from werkzeug.security import check_password_hash
from .db import get_connection

# Token store en memoria: {token: user_dict}
_tokens = {}

def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.username, u.password_hash, u.rol, u.grupo_id, g.nombre
        FROM MesaDeContingencia.usuarios u
        LEFT JOIN MesaDeContingencia.grupos_trabajo g ON g.id = u.grupo_id
        WHERE u.username = %s AND u.activo = 1
    """, username)
    row = cur.fetchone()
    conn.close()
    if not row or not check_password_hash(row[2], password):
        return None
    token = secrets.token_hex(32)
    user = {
        "id": row[0], "username": row[1], "rol": row[3],
        "grupo_id": row[4], "grupo_nombre": row[5]
    }
    _tokens[token] = user
    return token, user

def logout_token(token):
    _tokens.pop(token, None)

def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return _tokens.get(auth[7:])

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "No autenticado"}), 401
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "No autenticado"}), 401
        if user["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        return f(*args, **kwargs)
    return decorated
