"""Run once to create all tables: python -m app.init_db"""
import os
import re
from .db import get_connection

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

def init():
    sql = open(SCHEMA_FILE, encoding="utf-8").read()
    # Split on blank lines between statements (no semicolons needed)
    statements = [s.strip() for s in re.split(r'\n\s*\n', sql) if s.strip()]
    conn = get_connection()
    cursor = conn.cursor()
    for stmt in statements:
        print(f"Ejecutando: {stmt[:60]}...")
        cursor.execute(stmt)
        conn.commit()
    conn.close()
    print("✅ Tablas creadas correctamente.")

if __name__ == "__main__":
    init()
