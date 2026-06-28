from flask import jsonify
from . import main_bp
from ..db import get_connection

@main_bp.get("/api/health")
def health():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'MesaDeContingencia'")
        row = cur.fetchone()
        conn.close()
        return jsonify({"status": "ok", "schema": row[0] if row else None})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
