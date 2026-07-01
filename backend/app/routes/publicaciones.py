from flask import request, jsonify
from . import main_bp
from ..db import get_connection
from ..auth import require_auth, require_privileged, get_current_user

@main_bp.get("/api/publicaciones")
@require_auth
def get_publicaciones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.descripcion, p.autor_username, p.grupo_id, g.nombre, p.fecha_creacion,
               (SELECT COUNT(*) FROM publicacion_comentarios c WHERE c.publicacion_id = p.id AND c.eliminado = FALSE) as num_comentarios
        FROM publicaciones p
        LEFT JOIN grupos_trabajo g ON g.id = p.grupo_id
        WHERE p.eliminada = FALSE
        ORDER BY p.fecha_creacion DESC
    """)
    rows = [
        {
            "id": r[0],
            "descripcion": r[1],
            "autor_username": r[2],
            "grupo_id": r[3],
            "grupo_nombre": r[4],
            "fecha": str(r[5]),
            "num_comentarios": r[6]
        } for r in cur.fetchall()
    ]
    conn.close()
    return jsonify(rows)


@main_bp.post("/api/publicaciones")
@require_privileged
def crear_publicacion():
    user = get_current_user()
    data = request.get_json() or {}
    
    descripcion = (data.get("descripcion") or "").strip()
    autor_username = (data.get("autor_username") or "").strip()
    
    if not descripcion:
        return jsonify({"error": "La descripción no puede estar vacía"}), 400
    if len(descripcion) > 2000:
        return jsonify({"error": "La descripción no puede exceder los 2000 caracteres"}), 400
    if not autor_username:
        return jsonify({"error": "Debe especificar el autor de la publicación"}), 400

    grupo_id = user.get("grupo_id") # Null si es admin, el ID del grupo si es coordinador

    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO publicaciones
            (descripcion, autor_username, grupo_id)
        VALUES (%s, %s, %s) RETURNING id, fecha_creacion
    """, (descripcion, autor_username, grupo_id))
    
    nuevo = cur.fetchone()
    nuevo_id, fecha = nuevo[0], str(nuevo[1])
    
    # También obtenemos el nombre del grupo si aplica, para retornar los datos completos
    grupo_nombre = None
    if grupo_id:
        cur.execute("SELECT nombre FROM grupos_trabajo WHERE id = %s", (grupo_id,))
        g_row = cur.fetchone()
        if g_row:
            grupo_nombre = g_row[0]

    # Generar notificaciones
    notif_texto = f"📢 Nueva publicación: {descripcion[:120]}"
    
    # Para admin
    cur.execute("""
        INSERT INTO notificaciones (para_rol, para_grupo_id, texto)
        VALUES ('admin', NULL, %s)
    """, (notif_texto,))
    
    # Para todos los grupos
    cur.execute("SELECT id FROM grupos_trabajo")
    grupos = cur.fetchall()
    for g in grupos:
        cur.execute("""
            INSERT INTO notificaciones (para_rol, para_grupo_id, texto)
            VALUES ('grupo', %s, %s)
        """, (g[0], notif_texto))

    conn.commit()
    conn.close()
    
    return jsonify({
        "id": nuevo_id,
        "descripcion": descripcion,
        "autor_username": autor_username,
        "grupo_id": grupo_id,
        "grupo_nombre": grupo_nombre,
        "fecha": fecha
    }), 201


@main_bp.delete("/api/publicaciones/<int:pub_id>")
@require_privileged
def eliminar_publicacion(pub_id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("UPDATE publicaciones SET eliminada = TRUE WHERE id = %s", (pub_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"ok": True})

@main_bp.get("/api/publicaciones/<int:pub_id>/comentarios")
@require_auth
def get_comentarios_pub(pub_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, autor_username, autor_rol, grupo_id, texto, fecha_creacion
        FROM publicacion_comentarios
        WHERE publicacion_id = %s AND eliminado = FALSE
        ORDER BY fecha_creacion ASC
    """, (pub_id,))
    rows = [{"id": r[0], "autor": r[1], "rol": r[2], "grupo_id": r[3],
             "texto": r[4], "fecha": str(r[5])} for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@main_bp.post("/api/publicaciones/<int:pub_id>/comentarios")
@require_auth
def crear_comentario_pub(pub_id):
    user = get_current_user()
    data = request.get_json() or {}
    texto = (data.get("texto") or "").strip()
    
    if not texto:
        return jsonify({"error": "El comentario no puede estar vacío"}), 400
    if len(texto) > 750:
        return jsonify({"error": "El comentario excede los 750 caracteres"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM publicaciones WHERE id = %s AND eliminada = FALSE", (pub_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Publicación no encontrada"}), 404

    cur.execute("""
        INSERT INTO publicacion_comentarios
            (publicacion_id, autor_username, autor_rol, grupo_id, texto)
        VALUES (%s, %s, %s, %s, %s) RETURNING id, fecha_creacion
    """, (pub_id, user["username"], user["rol"], user.get("grupo_id"), texto))
    nuevo = cur.fetchone()
    nuevo_id, fecha = nuevo[0], str(nuevo[1])

    conn.commit()
    conn.close()
    return jsonify({"id": nuevo_id, "autor": user["username"], "rol": user["rol"],
                    "texto": texto, "fecha": fecha}), 201

@main_bp.delete("/api/publicaciones/<int:pub_id>/comentarios/<int:com_id>")
@require_auth
def eliminar_comentario_pub(pub_id, com_id):
    user = get_current_user()
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT autor_username FROM publicacion_comentarios WHERE id = %s", (com_id,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Comentario no encontrado"}), 404
        
    autor_username = row[0]
    
    from ..auth import is_privileged
    if autor_username != user["username"] and not is_privileged(user):
        conn.close()
        return jsonify({"error": "No tienes permiso para eliminar este comentario"}), 403
        
    cur.execute("UPDATE publicacion_comentarios SET eliminado = TRUE WHERE id = %s", (com_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"ok": True})
