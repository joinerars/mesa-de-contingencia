from app.db import get_connection

def run():
    conn = get_connection()
    cur = conn.cursor()
    tablas = [
        "MesaDeContingencia.notificaciones",
        "MesaDeContingencia.actividad_comentarios",
        "MesaDeContingencia.actividad_miembros",
        "MesaDeContingencia.actividades",
        "MesaDeContingencia.solicitudes",
        "MesaDeContingencia.miembros_grupos",
        "MesaDeContingencia.miembros",
    ]
    for t in tablas:
        cur.execute(f"DELETE FROM {t}")
        print(f"Limpiado: {t} ({cur.rowcount} filas)")
    conn.commit()
    conn.close()
    print("Listo. Grupos y usuarios intactos.")

if __name__ == "__main__":
    run()
