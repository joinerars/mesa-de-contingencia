from flask import jsonify
from . import main_bp
from ..db import get_connection

@main_bp.get("/api/health")
def health():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        row = cur.fetchone()
        conn.close()
        return jsonify({"status": "ok", "db_connected": bool(row)})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
