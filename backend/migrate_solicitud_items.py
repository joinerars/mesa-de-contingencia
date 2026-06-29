"""Create solicitud_items table in both schemas."""
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
            CREATE TABLE {schema}.solicitud_items (
                id          INT IDENTITY(1,1) PRIMARY KEY,
                solicitud_id INT NOT NULL
                    REFERENCES {schema}.solicitudes(id) ON DELETE CASCADE,
                nombre      NVARCHAR(200) NOT NULL,
                cantidad    INT NOT NULL DEFAULT 1
            )
        """)
        conn.commit()
        print(f"  Created solicitud_items")
    except Exception as e:
        conn.rollback()
        print(f"  Skipped: {e}")

conn.close()
print("Done.")
