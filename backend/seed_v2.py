"""
Ejecutar UNA sola vez:  python seed_v2.py
- Hace nullable representante_principal_id
- Crea tabla usuarios
- Agrega creado_por_grupo_id a solicitudes
- Inserta los 7 grupos predefinidos
- Crea usuario admin + 1 usuario por grupo
"""
from werkzeug.security import generate_password_hash
from app.db import get_connection

GRUPOS = [
    ("💻 Dotación Tecnológica y Digital",
     "Coordinación de Apoyo Tecnológico y Telecomunicaciones",
     "tecnologia"),
    ("🧠 Apoyo Psicológico",
     "Coordinar material audiovisual y grupos psicológicos a la comunidad de la Facultad",
     "psicologia"),
    ("💰 Gestión Económica",
     "Coordinar y gestionar donativos para la contingencia actual",
     "economia"),
    ("🗣️ Censo y Comunicaciones",
     "Generar canal efectivo para las necesidades de la comunidad de la Facultad",
     "comunicaciones"),
    ("⚕️ Asistencia Médica",
     "Orientar la actuación del personal de salud",
     "medica"),
    ("🤝 Relaciones Interinstitucionales",
     "Coordinación de Donaciones Internacionales y Entes Afines",
     "relaciones"),
    ("📦 Acopio de Insumos",
     "Coordinar con el Centro de Acopio de la UCV o la FCU los insumos médicos y generales",
     "acopio"),
]

def run():
    conn = get_connection()
    cur = conn.cursor()

    pasos = [
        # Hacer nullable representante_principal_id
        "ALTER TABLE MesaDeContingencia.grupos_trabajo DROP CONSTRAINT FK_grupo_representante",
        "ALTER TABLE MesaDeContingencia.grupos_trabajo ALTER COLUMN representante_principal_id INT NULL",
        # Tabla usuarios
        """
        CREATE TABLE MesaDeContingencia.usuarios (
            id            INT IDENTITY(1,1) PRIMARY KEY,
            username      NVARCHAR(100) NOT NULL,
            password_hash NVARCHAR(255) NOT NULL,
            rol           NVARCHAR(20)  NOT NULL DEFAULT 'grupo',
            grupo_id      INT,
            activo        BIT DEFAULT 1,
            CONSTRAINT UQ_usuario_username UNIQUE (username),
            CONSTRAINT CK_usuario_rol CHECK (rol IN ('admin', 'grupo'))
        )
        """,
        # FK opcional para grupo_id en usuarios (sin FK hacia grupos para simplificar)
        # Agregar creado_por_grupo_id a solicitudes
        "ALTER TABLE MesaDeContingencia.solicitudes ADD creado_por_grupo_id INT",
    ]

    for stmt in pasos:
        stmt = stmt.strip()
        try:
            cur.execute(stmt)
            conn.commit()
            print(f"  ✅ {stmt[:70]}")
        except Exception as e:
            conn.commit()
            print(f"  ⚠️  SKIP ({e.__class__.__name__}): {stmt[:70]}")

    # Insertar grupos
    print("\n📋 Insertando grupos...")
    grupo_ids = {}
    for nombre, desc, slug in GRUPOS:
        try:
            cur.execute("""
                INSERT INTO MesaDeContingencia.grupos_trabajo (nombre, descripcion)
                OUTPUT INSERTED.id VALUES (?, ?)
            """, nombre, desc)
            gid = cur.fetchone()[0]
            conn.commit()
            grupo_ids[slug] = gid
            print(f"  ✅ Grupo '{nombre}' → id={gid}")
        except Exception as e:
            conn.commit()
            print(f"  ⚠️  Ya existe o error: {nombre} — {e}")

    # Insertar usuario admin
    print("\n👤 Creando usuarios...")
    credentials = []
    try:
        cur.execute("""
            INSERT INTO MesaDeContingencia.usuarios (username, password_hash, rol, grupo_id)
            OUTPUT INSERTED.id VALUES (?, ?, 'admin', NULL)
        """, "admin", generate_password_hash("Admin2026!"))
        conn.commit()
        credentials.append(("admin", "Admin2026!", "admin", "—"))
        print("  ✅ admin")
    except Exception as e:
        print(f"  ⚠️  admin ya existe: {e}")

    # Insertar un usuario por grupo
    for nombre, _, slug in GRUPOS:
        if slug not in grupo_ids:
            continue
        pwd = f"{slug.capitalize()}2026!"
        gid = grupo_ids[slug]
        try:
            cur.execute("""
                INSERT INTO MesaDeContingencia.usuarios (username, password_hash, rol, grupo_id)
                OUTPUT INSERTED.id VALUES (?, ?, 'grupo', ?)
            """, slug, generate_password_hash(pwd), gid)
            conn.commit()
            credentials.append((slug, pwd, "grupo", nombre))
            print(f"  ✅ {slug} → grupo_id={gid}")
        except Exception as e:
            print(f"  ⚠️  {slug} ya existe: {e}")

    conn.close()

    print("\n" + "="*60)
    print("CREDENCIALES DE ACCESO (guardar en lugar seguro)")
    print("="*60)
    print(f"{'Usuario':<20} {'Contraseña':<25} {'Rol':<8} Grupo")
    print("-"*60)
    for u, p, r, g in credentials:
        print(f"{u:<20} {p:<25} {r:<8} {g}")
    print("="*60)

if __name__ == "__main__":
    run()
