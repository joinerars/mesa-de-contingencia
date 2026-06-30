"""Run once to create all tables: python -m app.init_db"""
import os
import re
from .db import get_connection

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema_supabase.sql")

def init():
    sql = open(SCHEMA_FILE, encoding="utf-8").read()
    # En PostgreSQL podemos ejecutar todo el bloque de una vez, pero si queremos imprimir:
    # Separar por punto y coma (sencillo, aunque puede fallar con strings, aquí es seguro)
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    conn = get_connection()
    cursor = conn.cursor()
    for stmt in statements:
        print(f"Ejecutando: {stmt[:60]}...")
        cursor.execute(stmt)
        conn.commit()
    conn.close()
    print("✅ Tablas PostgreSQL creadas correctamente.")

if __name__ == "__main__":
    init()
