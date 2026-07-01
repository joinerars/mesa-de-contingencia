import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL no está definida en .env")
    exit(1)

# Por defecto usamos 'dev', pero puede sobreescribirse
schema = os.environ.get("DB_SCHEMA", "dev")

print(f"Ejecutando migración en el esquema: {schema}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Asegurar que estamos en el esquema correcto
    cur.execute(f"SET search_path TO {schema}")

    # Crear tabla de comentarios
    print("Creando tabla publicacion_comentarios...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS publicacion_comentarios (
            id              SERIAL PRIMARY KEY,
            publicacion_id  INT NOT NULL REFERENCES publicaciones(id) ON DELETE CASCADE,
            autor_username  VARCHAR(100) NOT NULL,
            autor_rol       VARCHAR(50),
            grupo_id        INT,
            texto           TEXT NOT NULL,
            eliminado       BOOLEAN DEFAULT FALSE,
            fecha_creacion  TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    conn.commit()
    print("¡Migración completada con éxito!")

except Exception as e:
    print(f"Error durante la migración: {e}")
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
