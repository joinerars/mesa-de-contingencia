import os
import pymssql
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

# Conectar a Azure SQL
print("Conectando a Azure SQL...")
conn_azure = pymssql.connect(
    server=os.getenv("DB_SERVER"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    tds_version="7.4",
)
cur_azure = conn_azure.cursor(as_dict=True)

# Conectar a Supabase PostgreSQL
print("Conectando a Supabase PostgreSQL...")
conn_pg = psycopg2.connect(os.getenv("DATABASE_URL"))
cur_pg = conn_pg.cursor()

SCHEMA = "MesaDeContingencia"

# Orden de tablas (respetando foreign keys)
TABLAS = [
    "miembros",
    "grupos_trabajo",
    "miembros_grupos",
    "centros_atencion",
    "centro_contactos",
    "usuarios",
    "insumos",
    "solicitudes",
    "solicitud_items",
    "actividades",
    "actividad_miembros",
    "actividad_comentarios",
    "notificaciones"
]

for tabla in TABLAS:
    print(f"\nMigrando {tabla}...")
    
    # 1. Leer de Azure
    cur_azure.execute(f"SELECT * FROM {SCHEMA}.{tabla}")
    filas = cur_azure.fetchall()
    
    if not filas:
        print(f"  Tabla vacía, saltando.")
        continue
        
    print(f"  {len(filas)} filas encontradas.")
    
    # 2. Insertar en PostgreSQL
    columnas = list(filas[0].keys())
    
    # En PostgreSQL, si migramos IDs IDENTITY, a veces tenemos que ajustar secuencias.
    # Pero aquí simplemente vamos a insertar los IDs tal cual, y luego actualizar la secuencia.
    
    cols_str = ",".join(columnas)
    placeholders = ",".join([f"%({col})s" for col in columnas])
    
    insert_sql = f"INSERT INTO {tabla} ({cols_str}) VALUES ({placeholders})"
    
    insertados = 0
    for fila in filas:
        try:
            # pymssql devuelve strings/ints, que psycopg2 maneja bien.
            cur_pg.execute(insert_sql, fila)
            insertados += 1
        except Exception as e:
            # Si hay error (ej. duplicado o null check), reportar y continuar o hacer rollback
            print(f"  Error en fila {fila.get('id', 'Unknown')}: {e}")
            conn_pg.rollback()
            continue
            
    conn_pg.commit()
    print(f"  Insertados: {insertados} / {len(filas)}")

    # 3. Actualizar la secuencia de la tabla (si tiene ID autoincremental)
    if "id" in columnas:
        try:
            cur_pg.execute(f"SELECT setval('{tabla}_id_seq', (SELECT MAX(id) FROM {tabla}))")
            conn_pg.commit()
            print(f"  Secuencia actualizada.")
        except Exception as e:
            conn_pg.rollback()
            print(f"  No se pudo actualizar secuencia o no aplica: {e}")

conn_azure.close()
conn_pg.close()
print("\n✅ Migración de datos completada.")
