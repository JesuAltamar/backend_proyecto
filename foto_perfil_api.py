# foto_perfil_api.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import os
import uuid
import pymysql
import traceback

# Configuración
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'fotos_perfil')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Crear carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def connect_to_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='alegra',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
    )

def register_foto_routes(app):
    
    @app.route('/api/foto/upload', methods=['POST'])
    @jwt_required()
    def upload_foto():
        print("🔍 Función upload_foto iniciada")
        try:
            user_id = int(get_jwt_identity())
            print(f"🔍 User ID: {user_id}")
            
            data = request.get_json()
            print(f"🔍 Data recibida: {data is not None}")
            
            if not data or 'foto_base64' not in data:
                print("❌ No se recibió imagen o datos incorrectos")
                return jsonify({'success': False, 'message': 'No se recibió imagen'}), 400
            
            foto_base64 = data.get('foto_base64')
            print(f"🔍 Base64 recibido: {len(foto_base64) if foto_base64 else 0} caracteres")
            
            # Limpiar prefijo data:image/...;base64,
            if ',' in foto_base64:
                foto_base64 = foto_base64.split(',')[1]
            
            # Decodificar base64
            image_data = base64.b64decode(foto_base64)
            print(f"🔍 Imagen decodificada: {len(image_data)} bytes")
            
            # Verificar que la carpeta existe
            if not os.path.exists(UPLOAD_FOLDER):
                print(f"❌ La carpeta {UPLOAD_FOLDER} no existe")
                return jsonify({'success': False, 'message': 'Carpeta de uploads no encontrada'}), 500
            
            # Generar nombre único
            filename = f"perfil_{user_id}_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            print(f"🔍 Guardando en: {filepath}")
            
            # Guardar archivo
            with open(filepath, 'wb') as f:
                f.write(image_data)
            print("✅ Archivo guardado exitosamente")
            
            foto_url = f"/uploads/fotos_perfil/{filename}"
            
            # Actualizar base de datos
            print("🔍 Actualizando base de datos...")
            connection = connect_to_db()
            try:
                with connection.cursor() as cursor:
                    # Obtener foto anterior para eliminarla
                    cursor.execute("SELECT avatar_url FROM usuario WHERE id = %s", (user_id,))
                    old_photo = cursor.fetchone()
                    
                    # Actualizar con nueva foto
                    cursor.execute(
                        "UPDATE usuario SET avatar_url = %s WHERE id = %s",
                        (foto_url, user_id)
                    )
                    connection.commit()
                    print("✅ Base de datos actualizada")
                    
                    # Eliminar foto anterior si existe
                    if old_photo and old_photo['avatar_url']:
                        old_filename = old_photo['avatar_url'].split('/')[-1]
                        old_filepath = os.path.join(UPLOAD_FOLDER, old_filename)
                        if os.path.exists(old_filepath):
                            try:
                                os.remove(old_filepath)
                                print(f"✅ Foto anterior eliminada: {old_filename}")
                            except Exception as e:
                                print(f"⚠️ No se pudo eliminar foto anterior: {e}")
            finally:
                connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Foto actualizada correctamente',
                'foto_url': foto_url
            }), 200
        
        except Exception as e:
            print(f"❌ Error en upload_foto: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

    @app.route('/api/usuario/perfil', methods=['GET'])
    @jwt_required()
    def get_user_profile():
        try:
            user_id = int(get_jwt_identity())
            print(f"🔍 Obteniendo perfil para user_id: {user_id}")
            
            connection = connect_to_db()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, nombre, correo, genero, telefono, 
                               fecha_nacimiento, avatar_url, updated_at
                        FROM usuario 
                        WHERE id = %s
                    """, (user_id,))
                    user = cursor.fetchone()
                    
                    if not user:
                        return jsonify({
                            'success': False,
                            'message': 'Usuario no encontrado'
                        }), 404
                    
                    # Verificar si el archivo de avatar existe
                    if user.get('avatar_url'):
                        filename = user['avatar_url'].split('/')[-1]
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        if not os.path.exists(filepath):
                            print(f"⚠️ Archivo de avatar no existe: {filepath}")
                            # Limpiar la referencia en la BD
                            cursor.execute("UPDATE usuario SET avatar_url = NULL WHERE id = %s", (user_id,))
                            connection.commit()
                            user['avatar_url'] = None
                            print("✅ Referencia de avatar limpiada en BD")
                    
                    # Formatear fechas si existen
                   # Línea ~152 en foto_perfil_api.py
                if user['fecha_nacimiento'] and hasattr(user['fecha_nacimiento'], 'strftime'):
                   user['fecha_nacimiento'] = user['fecha_nacimiento'].strftime('%Y-%m-%d')
                if user.get('updated_at'):
                    user['updated_at'] = user['updated_at'].isoformat()
                    
                    print(f"✅ Perfil encontrado: {user['nombre']}, Avatar: {user.get('avatar_url', 'Sin avatar')}")
                    
            finally:
                connection.close()
            
            return jsonify({
                'success': True,
                'usuario': user
            }), 200
        
        except Exception as e:
            print(f"❌ Error en get_user_profile: {e}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

    @app.route('/api/foto/delete', methods=['DELETE'])
    @jwt_required()
    def delete_foto():
        try:
            user_id = int(get_jwt_identity())
            print(f"🔍 Eliminando foto para user_id: {user_id}")
            
            connection = connect_to_db()
            try:
                with connection.cursor() as cursor:
                    # Obtener foto actual
                    cursor.execute("SELECT avatar_url FROM usuario WHERE id = %s", (user_id,))
                    user = cursor.fetchone()
                    
                    if not user or not user['avatar_url']:
                        return jsonify({
                            'success': False,
                            'message': 'No hay foto para eliminar'
                        }), 400
                    
                    # Eliminar archivo físico
                    filename = user['avatar_url'].split('/')[-1]
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            print(f"✅ Archivo eliminado: {filepath}")
                        except Exception as e:
                            print(f"⚠️ No se pudo eliminar archivo: {e}")
                    
                    # Actualizar base de datos
                    cursor.execute("UPDATE usuario SET avatar_url = NULL WHERE id = %s", (user_id,))
                    connection.commit()
                    print("✅ Base de datos actualizada (avatar eliminado)")
            finally:
                connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Foto eliminada correctamente'
            }), 200
        
        except Exception as e:
            print(f"❌ Error en delete_foto: {e}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

    @app.route('/uploads/fotos_perfil/<filename>')
    def serve_foto(filename):
        """Servir archivos de fotos de perfil"""
        try:
            from flask import send_from_directory
            return send_from_directory(UPLOAD_FOLDER, filename)
        except Exception as e:
            print(f"❌ Error sirviendo foto {filename}: {e}")
            from flask import abort
            abort(404)