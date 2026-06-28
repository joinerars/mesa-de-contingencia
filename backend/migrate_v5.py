from app.db import get_connection

def run():
    conn = get_connection()
    cur = conn.cursor()
    stmts = [
        "ALTER TABLE MesaDeContingencia.solicitudes ADD lat FLOAT",
        "ALTER TABLE MesaDeContingencia.solicitudes ADD lng FLOAT",
        # solicitante_id → FK a miembros
        "ALTER TABLE MesaDeContingencia.solicitudes ADD solicitante_id INT",
    ]
    for s in stmts:
        try:
            cur.execute(s); conn.commit(); print("OK:", s)
        except Exception as e:
            conn.commit(); print("SKIP:", e)
    conn.close(); print("Listo.")

if __name__ == "__main__":
    run()
