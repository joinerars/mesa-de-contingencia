"""
Agrega direccion/lat/lng a centros_atencion, crea tabla centro_contactos,
y agrega password_plain a usuarios — en ambos schemas.
Uso: python backend/migrate_centros_v2.py
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

for S in ("MesaDeContingencia", "MesaDeContingenciaTest"):
    steps = [
        f"""IF NOT EXISTS (SELECT 1 FROM sys.columns c
                JOIN sys.tables t ON t.object_id=c.object_id
                JOIN sys.schemas s ON s.schema_id=t.schema_id
                WHERE s.name='{S}' AND t.name='centros_atencion' AND c.name='direccion')
            ALTER TABLE [{S}].centros_atencion ADD direccion NVARCHAR(500) NULL""",
        f"""IF NOT EXISTS (SELECT 1 FROM sys.columns c
                JOIN sys.tables t ON t.object_id=c.object_id
                JOIN sys.schemas s ON s.schema_id=t.schema_id
                WHERE s.name='{S}' AND t.name='centros_atencion' AND c.name='lat')
            ALTER TABLE [{S}].centros_atencion ADD lat FLOAT NULL""",
        f"""IF NOT EXISTS (SELECT 1 FROM sys.columns c
                JOIN sys.tables t ON t.object_id=c.object_id
                JOIN sys.schemas s ON s.schema_id=t.schema_id
                WHERE s.name='{S}' AND t.name='centros_atencion' AND c.name='lng')
            ALTER TABLE [{S}].centros_atencion ADD lng FLOAT NULL""",
        f"""IF NOT EXISTS (SELECT 1 FROM sys.columns c
                JOIN sys.tables t ON t.object_id=c.object_id
                JOIN sys.schemas s ON s.schema_id=t.schema_id
                WHERE s.name='{S}' AND t.name='usuarios' AND c.name='password_plain')
            ALTER TABLE [{S}].usuarios ADD password_plain NVARCHAR(100) NULL""",
        f"""IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                WHERE s.name='{S}' AND t.name='centro_contactos')
            CREATE TABLE [{S}].centro_contactos (
                id         INT IDENTITY(1,1) PRIMARY KEY,
                centro_id  INT NOT NULL,
                nombre     NVARCHAR(200) NOT NULL,
                cargo      NVARCHAR(150),
                telefono   NVARCHAR(50),
                email      NVARCHAR(200)
            )""",
    ]
    for i, sql in enumerate(steps):
        try:
            cur.execute(sql.strip())
            conn.commit()
            print(f"[{S}] paso {i+1} OK")
        except Exception as e:
            print(f"[{S}] paso {i+1} ERROR: {e}")

conn.close()
print("Listo.")
