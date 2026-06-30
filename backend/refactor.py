import glob
import os
import re

routes_path = os.path.join(os.path.dirname(__file__), "app", "routes", "*.py")
files = glob.glob(routes_path)

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. Eliminar import de SCHEMA
    content = content.replace("from ..db import get_connection, SCHEMA", "from ..db import get_connection")
    
    # 2. Reemplazar OUTPUT INSERTED.id por RETURNING id
    content = content.replace("OUTPUT INSERTED.id, INSERTED.fecha_creacion", "RETURNING id, fecha_creacion")
    content = content.replace("OUTPUT INSERTED.id", "RETURNING id")
    
    # 3. Eliminar {SCHEMA}.
    content = content.replace("{SCHEMA}.", "")
    
    # 4. GETDATE() a NOW()
    content = content.replace("GETDATE()", "NOW()")
    
    # 5. leida = 1 -> leida = TRUE (en comentarios.py)
    if "comentarios.py" in file:
        content = content.replace("leida = 1", "leida = TRUE")
        content = content.replace("leida = 0", "leida = FALSE")
        
    # 6. Activo = 1 -> activo = TRUE (en grupos.py)
    if "grupos.py" in file:
        content = content.replace("activo = 1", "activo = TRUE")
        content = content.replace("activo = 0", "activo = FALSE")
        
    # 7. LIKE a ILIKE en insumos.py y TOP a LIMIT
    if "insumos.py" in file:
        content = content.replace("LIKE %s", "ILIKE %s")
        # Cambiar SELECT TOP (%s) ... a SELECT ... LIMIT %s
        if "SELECT TOP (%s)" in content:
            # Es un poco complejo con regex simple, mejor lo hago manual luego.
            pass

    # 8. Eliminar la 'f' de los f-strings si ya no tienen {} (opcional, python no se queja si hay f-strings sin {})
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Archivos refactorizados exitosamente.")
