CREATE TABLE MesaDeContingencia.miembros (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    nombre          NVARCHAR(200) NOT NULL,
    telefono        NVARCHAR(50),
    cargo           NVARCHAR(150),
    email           NVARCHAR(200),
    fecha_registro  DATETIME2 DEFAULT GETDATE()
)

CREATE TABLE MesaDeContingencia.grupos_trabajo (
    id                          INT IDENTITY(1,1) PRIMARY KEY,
    nombre                      NVARCHAR(200) NOT NULL,
    descripcion                 NVARCHAR(500),
    representante_principal_id  INT NOT NULL,
    fecha_creacion              DATETIME2 DEFAULT GETDATE()
)

CREATE TABLE MesaDeContingencia.miembros_grupos (
    miembro_id  INT NOT NULL,
    grupo_id    INT NOT NULL,
    PRIMARY KEY (miembro_id, grupo_id)
)

CREATE TABLE MesaDeContingencia.solicitudes (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    descripcion     NVARCHAR(MAX) NOT NULL,
    solicitante     NVARCHAR(200),
    contacto        NVARCHAR(200),
    fecha_creacion  DATETIME2 DEFAULT GETDATE()
)

CREATE TABLE MesaDeContingencia.actividades (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    solicitud_id        INT NOT NULL,
    grupo_id            INT NOT NULL,
    estado              NVARCHAR(50) NOT NULL DEFAULT 'Por ejecutar',
    fecha_asignacion    DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT CK_act_estado CHECK (estado IN ('Por ejecutar', 'En ejecución', 'Ejecutado'))
)

ALTER TABLE MesaDeContingencia.grupos_trabajo
    ADD CONSTRAINT FK_grupo_representante
    FOREIGN KEY (representante_principal_id)
    REFERENCES MesaDeContingencia.miembros(id)

ALTER TABLE MesaDeContingencia.miembros_grupos
    ADD CONSTRAINT FK_mg_miembro
    FOREIGN KEY (miembro_id) REFERENCES MesaDeContingencia.miembros(id)

ALTER TABLE MesaDeContingencia.miembros_grupos
    ADD CONSTRAINT FK_mg_grupo
    FOREIGN KEY (grupo_id) REFERENCES MesaDeContingencia.grupos_trabajo(id)

ALTER TABLE MesaDeContingencia.actividades
    ADD CONSTRAINT FK_act_solicitud
    FOREIGN KEY (solicitud_id) REFERENCES MesaDeContingencia.solicitudes(id)

ALTER TABLE MesaDeContingencia.actividades
    ADD CONSTRAINT FK_act_grupo
    FOREIGN KEY (grupo_id) REFERENCES MesaDeContingencia.grupos_trabajo(id)
