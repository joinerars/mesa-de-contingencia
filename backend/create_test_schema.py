"""
Crea el schema MesaDeContingenciaTest en Azure SQL con todas las tablas
necesarias para el entorno de desarrollo/preview.

Uso:
    python backend/create_test_schema.py
"""
import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

S = "MesaDeContingenciaTest"

conn = pymssql.connect(
    server=os.getenv("DB_SERVER"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    tds_version="7.4",
)
cur = conn.cursor()

steps = [
    # Schema
    f"IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = '{S}') EXEC('CREATE SCHEMA [{S}]')",

    # Tablas base
    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='miembros')
    CREATE TABLE [{S}].miembros (
        id              INT IDENTITY(1,1) PRIMARY KEY,
        nombre          NVARCHAR(200) NOT NULL,
        cedula          NVARCHAR(20)  NULL,
        telefono        NVARCHAR(50),
        tlf_alternativo NVARCHAR(50),
        cargo           NVARCHAR(150),
        email           NVARCHAR(200),
        fecha_registro  DATETIME2 DEFAULT GETDATE()
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='grupos_trabajo')
    CREATE TABLE [{S}].grupos_trabajo (
        id                         INT IDENTITY(1,1) PRIMARY KEY,
        nombre                     NVARCHAR(200) NOT NULL,
        descripcion                NVARCHAR(500),
        representante_principal_id INT NULL,
        fecha_creacion             DATETIME2 DEFAULT GETDATE()
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='miembros_grupos')
    CREATE TABLE [{S}].miembros_grupos (
        miembro_id INT NOT NULL,
        grupo_id   INT NOT NULL,
        PRIMARY KEY (miembro_id, grupo_id)
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='centros_atencion')
    CREATE TABLE [{S}].centros_atencion (
        id          INT IDENTITY(1,1) PRIMARY KEY,
        nombre      NVARCHAR(200) NOT NULL,
        descripcion NVARCHAR(500),
        activo      BIT DEFAULT 1,
        fecha_creacion DATETIME2 DEFAULT GETDATE()
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='usuarios')
    CREATE TABLE [{S}].usuarios (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        username      NVARCHAR(100) NOT NULL UNIQUE,
        password_hash NVARCHAR(256) NOT NULL,
        rol           NVARCHAR(50)  NOT NULL DEFAULT 'grupo',
        grupo_id      INT NULL,
        centro_id     INT NULL,
        activo        BIT DEFAULT 1,
        fecha_creacion DATETIME2 DEFAULT GETDATE()
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='solicitudes')
    CREATE TABLE [{S}].solicitudes (
        id                    INT IDENTITY(1,1) PRIMARY KEY,
        descripcion           NVARCHAR(MAX) NOT NULL,
        creado_por_grupo_id   INT NULL,
        creado_por_centro_id  INT NULL,
        solicitante_id        INT NULL,
        ubicacion             NVARCHAR(500),
        fecha_hora            DATETIME2 NULL,
        prioridad             NVARCHAR(20) DEFAULT 'Normal',
        lat                   FLOAT NULL,
        lng                   FLOAT NULL,
        fecha_creacion        DATETIME2 DEFAULT GETDATE()
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='actividades')
    CREATE TABLE [{S}].actividades (
        id                  INT IDENTITY(1,1) PRIMARY KEY,
        solicitud_id        INT NOT NULL,
        grupo_id            INT NOT NULL,
        estado              NVARCHAR(50) NOT NULL DEFAULT 'Por ejecutar',
        fecha_asignacion    DATETIME2 DEFAULT GETDATE(),
        fecha_actualizacion DATETIME2 DEFAULT GETDATE(),
        CONSTRAINT CK_act_estado_test CHECK (estado IN ('Por ejecutar', 'En ejecución', 'Ejecutado'))
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='actividad_miembros')
    CREATE TABLE [{S}].actividad_miembros (
        actividad_id INT NOT NULL,
        miembro_id   INT NOT NULL,
        PRIMARY KEY (actividad_id, miembro_id)
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='actividad_comentarios')
    CREATE TABLE [{S}].actividad_comentarios (
        id              INT IDENTITY(1,1) PRIMARY KEY,
        actividad_id    INT NOT NULL,
        autor_username  NVARCHAR(100),
        autor_rol       NVARCHAR(50),
        grupo_id        INT NULL,
        texto           NVARCHAR(MAX) NOT NULL,
        fecha_creacion  DATETIME2 DEFAULT GETDATE()
    )
    """,

    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
                   WHERE s.name='{S}' AND t.name='notificaciones')
    CREATE TABLE [{S}].notificaciones (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        para_rol      NVARCHAR(50),
        para_grupo_id INT NULL,
        actividad_id  INT NULL,
        comentario_id INT NULL,
        texto         NVARCHAR(500),
        leida         BIT DEFAULT 0,
        fecha_creacion DATETIME2 DEFAULT GETDATE()
    )
    """,

    # Índice único en cédula (permite NULLs múltiples)
    f"""
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ_miembros_cedula_test')
    CREATE UNIQUE INDEX UQ_miembros_cedula_test
        ON [{S}].miembros (cedula)
        WHERE cedula IS NOT NULL
    """,

    # Usuario admin de prueba (password: admin123)
    f"""
    IF NOT EXISTS (SELECT 1 FROM [{S}].usuarios WHERE username = 'admin')
    INSERT INTO [{S}].usuarios (username, password_hash, rol, activo)
    VALUES ('admin',
            'pbkdf2:sha256:600000$placeholder$0000000000000000000000000000000000000000000000000000000000000000',
            'admin', 1)
    """,
]

for i, sql in enumerate(steps):
    try:
        cur.execute(sql.strip())
        conn.commit()
        print(f"[{i+1}/{len(steps)}] OK")
    except Exception as e:
        print(f"[{i+1}/{len(steps)}] ERROR: {e}")

conn.close()
print(f"\nSchema [{S}] listo en Azure SQL.")
print("Recuerda crear el usuario admin con la contraseña correcta manualmente o via script.")
