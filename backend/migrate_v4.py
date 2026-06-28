from app.db import get_connection

def run():
    conn = get_connection()
    cur = conn.cursor()
    stmts = [
        "ALTER TABLE MesaDeContingencia.solicitudes ADD ubicacion NVARCHAR(300)",
        "ALTER TABLE MesaDeContingencia.solicitudes ADD fecha_hora DATETIME2",
        "ALTER TABLE MesaDeContingencia.solicitudes ADD email_solicitante NVARCHAR(200)",
        "ALTER TABLE MesaDeContingencia.solicitudes ADD prioridad NVARCHAR(20) NOT NULL DEFAULT 'Normal'",
        "ALTER TABLE MesaDeContingencia.solicitudes ADD CONSTRAINT CK_sol_prioridad CHECK (prioridad IN ('Baja','Normal','Alta'))",
    ]
    for s in stmts:
        try:
            cur.execute(s); conn.commit()
            print("OK:", s[:70])
        except Exception as e:
            conn.commit(); print("SKIP:", e)
    conn.close(); print("Listo.")

if __name__ == "__main__":
    run()
