"""Add fecha_actualizacion to solicitudes in both schemas."""
import os
from dotenv import load_dotenv
import pymssql

load_dotenv()

conn = pymssql.connect(
    server=os.getenv("DB_SERVER"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"),
    tds_version="7.4",
)
cur = conn.cursor()

for schema in ["MesaDeContingencia", "MesaDeContingenciaTest"]:
    print(f"Migrating {schema}...")
    try:
        cur.execute(f"""
            ALTER TABLE {schema}.solicitudes
            ADD fecha_actualizacion DATETIME2 NULL
        """)
        conn.commit()
        print(f"  Added fecha_actualizacion")
    except Exception as e:
        conn.rollback()
        print(f"  Skipped (maybe exists): {e}")

conn.close()
print("Done.")
