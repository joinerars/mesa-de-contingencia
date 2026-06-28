from app.db import get_connection

def run():
    conn = get_connection()
    cur = conn.cursor()
    stmts = [
        """
        CREATE TABLE MesaDeContingencia.actividad_miembros (
            actividad_id INT NOT NULL,
            miembro_id   INT NOT NULL,
            PRIMARY KEY (actividad_id, miembro_id),
            CONSTRAINT FK_am_actividad FOREIGN KEY (actividad_id)
                REFERENCES MesaDeContingencia.actividades(id),
            CONSTRAINT FK_am_miembro FOREIGN KEY (miembro_id)
                REFERENCES MesaDeContingencia.miembros(id)
        )
        """,
    ]
    for s in stmts:
        try:
            cur.execute(s.strip())
            conn.commit()
            print("OK:", s.strip()[:60])
        except Exception as e:
            conn.commit()
            print("SKIP:", e)
    conn.close()
    print("Listo.")

if __name__ == "__main__":
    run()
