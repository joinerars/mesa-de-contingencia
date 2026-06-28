# Mesa de Contingencia — MVP

## Requisitos previos
- Python 3.10+
- Node.js 16+
- ODBC Driver 18 for SQL Server (ya instalado)

---

## 1. Configurar credenciales

Editar `backend/.env` y poner la contraseña real:

```
DB_SERVER=gipsy-sql-srv.database.windows.net
DB_NAME=gipsyIDB
DB_USER=MesaApp
DB_PASSWORD=TU_CONTRASEÑA_AQUI
DB_DRIVER=ODBC Driver 18 for SQL Server
```

---

## 2. Inicializar la base de datos (una sola vez)

```powershell
cd backend
pip install -r requirements.txt
python -m app.init_db
```

---

## 3. Levantar el backend

```powershell
cd backend
python run.py
```

Verifica en: http://localhost:5000/api/health

---

## 4. Levantar el frontend

```powershell
cd frontend
npm install   # solo la primera vez
npm run dev
```

Abre: http://localhost:5173

---

## Flujo de uso

1. **Módulo Miembros y Grupos** → registrar personas y crear grupos con su representante
2. **Módulo Solicitudes** → ingresar solicitudes de emergencia y asignarlas a un grupo
3. **Módulo Actividades** → ver el tablero Kanban y avanzar los estados: Por ejecutar → En ejecución → Ejecutado
