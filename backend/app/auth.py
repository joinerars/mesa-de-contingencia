import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from werkzeug.security import check_password_hash
from .db import get_connection, SCHEMA

SECRET = os.getenv("JWT_SECRET", "mesa-contingencia-secret-key-2026")
ALGO = "HS256"
TTL_HOURS = 8


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT u.id, u.username, u.password_hash, u.rol, u.grupo_id, g.nombre,
               u.centro_id, c.nombre, u.session_version
        FROM {SCHEMA}.usuarios u
        LEFT JOIN {SCHEMA}.grupos_trabajo g ON g.id = u.grupo_id
        LEFT JOIN {SCHEMA}.centros_atencion c ON c.id = u.centro_id
        WHERE u.username = %s AND u.activo = 1
    """, (username,))
    row = cur.fetchone()
    if not row or not check_password_hash(row[2], password):
        conn.close()
        return None

    # Incrementar session_version invalida todos los tokens anteriores
    new_version = (row[8] or 1) + 1
    cur.execute(f"""
        UPDATE {SCHEMA}.usuarios SET session_version = %s WHERE id = %s
    """, (new_version, row[0]))
    conn.commit()
    conn.close()

    user = {
        "id": row[0], "username": row[1], "rol": row[3],
        "grupo_id": row[4], "grupo_nombre": row[5],
        "centro_id": row[6], "centro_nombre": row[7],
    }
    payload = {
        **user,
        "sv": new_version,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TTL_HOURS),
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGO)
    return token, user


def logout_token(token):
    pass  # JWT es stateless; la invalidación ocurre en el próximo login


def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    # Verificar session_version contra BD
    sv_token = payload.get("sv")
    user_id = payload.get("id")
    if sv_token is None or user_id is None:
        return None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT session_version FROM {SCHEMA}.usuarios WHERE id = %s AND activo = 1", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row or row[0] != sv_token:
            return None  # Sesión anterior invalidada o usuario desactivado
    except Exception:
        # Si la BD no responde, confiar en el JWT (evita deslogueos por timeout)
        pass

    payload.pop("exp", None)
    payload.pop("sv", None)
    return payload


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
