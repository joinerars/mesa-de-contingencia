import os
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

def seed():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    try:
        # 1. Crear grupos
        grupos = [
            ("Grupo 1: Alerta Temprana", "Vigilancia epidemiológica"),
            ("Grupo 2: Logística", "Gestión de insumos"),
            ("Grupo 3: Comunicaciones", "Vocería oficial"),
            ("Grupo 4: Atención Médica", "Protocolos clínicos"),
            ("Grupo 5: Seguridad", "Resguardo de instalaciones"),
            ("Grupo 6: Apoyo Psicológico", "Salud mental"),
            ("Grupo 7: Enlace Institucional", "Relaciones interinstitucionales"),
        ]
        
        grupo_ids = []
        for nombre, desc in grupos:
            cur.execute(
                "INSERT INTO grupos_trabajo (nombre, descripcion) VALUES (%s, %s) RETURNING id",
                (nombre, desc)
            )
            grupo_ids.append(cur.fetchone()[0])
            
        print("✅ 7 Grupos creados")

        # 2. Crear admin
        admin_pass = "Admin2026!"
        admin_hash = generate_password_hash(admin_pass)
        cur.execute("""
            INSERT INTO usuarios (username, password_hash, password_plain, rol, activo)
            VALUES (%s, %s, %s, 'admin', TRUE)
        """, ("admin", admin_hash, admin_pass))
        print("✅ Usuario admin creado")

        # 3. Crear usuarios por grupo
        for i, g_id in enumerate(grupo_ids, 1):
            username = f"grupo{i}"
            password = f"Mesa{2026+i}*"
            pwd_hash = generate_password_hash(password)
            cur.execute("""
                INSERT INTO usuarios (username, password_hash, password_plain, rol, grupo_id, activo)
                VALUES (%s, %s, %s, 'grupo', %s, TRUE)
            """, (username, pwd_hash, password, g_id))
            
        print("✅ Usuarios de grupos creados")

        conn.commit()
        print("✅ Base de datos poblada exitosamente (Seed finalizado).")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error insertando datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed()
