"""
Agrega columna session_version a usuarios en ambos schemas.
Uso: python backend/migrate_session_version.py
"""
import pymssql, os
from dotenv import load_dotenv
load_dotenv()

conn = pymssql.connect(
    server=os.getenv("DB_SERVER"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"),
    tds_version="7.4",
)
cur = conn.cursor()

for schema in ("MesaDeContingencia", "MesaDeContingenciaTest"):
    sql = f"""
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns c
            JOIN sys.tables t ON t.object_id = c.object_id
            JOIN sys.schemas s ON s.schema_id = t.schema_id
            WHERE s.name = '{schema}' AND t.name = 'usuarios' AND c.name = 'session_version'
        )
        ALTER TABLE [{schema}].usuarios ADD session_version INT NOT NULL DEFAULT 1
    """
    try:
        cur.execute(sql)
        conn.commit()
        print(f"[{schema}] OK")
    except Exception as e:
        print(f"[{schema}] ERROR: {e}")

conn.close()
