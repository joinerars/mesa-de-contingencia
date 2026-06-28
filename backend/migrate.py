from app.db import get_connection

conn = get_connection()
cur = conn.cursor()

stmts = [
    "ALTER TABLE MesaDeContingencia.miembros ADD cedula NVARCHAR(20)",
    "ALTER TABLE MesaDeContingencia.miembros ADD tlf_alternativo NVARCHAR(50)",
]

for s in stmts:
    try:
        cur.execute(s)
        conn.commit()
        print(f"OK: {s[:60]}")
    except Exception as e:
        print(f"SKIP ({e}): {s[:60]}")

conn.close()
print("Migracion completa.")
