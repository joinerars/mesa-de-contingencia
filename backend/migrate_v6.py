from app.db import get_connection

def run():
    conn = get_connection()
    cur = conn.cursor()
    stmts = [
        """
        CREATE TABLE MesaDeContingencia.actividad_comentarios (
            id              INT IDENTITY(1,1) PRIMARY KEY,
            actividad_id    INT NOT NULL,
            autor_username  NVARCHAR(80) NOT NULL,
            autor_rol       NVARCHAR(20) NOT NULL,
            grupo_id        INT NULL,
            texto           NVARCHAR(MAX) NOT NULL,
            fecha_creacion  DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (actividad_id) REFERENCES MesaDeContingencia.actividades(id)
        )
        """,
        """
        CREATE TABLE MesaDeContingencia.notificaciones (
            id              INT IDENTITY(1,1) PRIMARY KEY,
            para_rol        NVARCHAR(20) NOT NULL,
            para_grupo_id   INT NULL,
            actividad_id    INT NOT NULL,
            comentario_id   INT NOT NULL,
            texto           NVARCHAR(500) NOT NULL,
            leida           BIT DEFAULT 0,
            fecha_creacion  DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (actividad_id) REFERENCES MesaDeContingencia.actividades(id)
        )
        """,
    ]
    for s in stmts:
        try:
            cur.execute(s); conn.commit(); print("OK:", s.strip()[:60])
        except Exception as e:
            conn.commit(); print("SKIP:", e)
    conn.close(); print("Listo.")

if __name__ == "__main__":
    run()
