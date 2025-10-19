# foto_perfil_api.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import cloudinary
import cloudinary.uploader
import pymysql
import traceback
import os

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def connect_to_db():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )

def register_foto_routes(app):
    
    @app.route('/api/foto/upload', methods=['POST', 'OPTIONS'])
    @jwt_required(optional=True)
    def upload_foto():
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'success': False, 'message': 'No autenticado'}), 401
            
            user_id = int(user_id)
            data = request.get_json()
            
            if not data or 'foto_base64' not in data:
                return jsonify({'success': False, 'message': 'No imagen'}), 400
            
            foto_base64 = data['foto_base64']
            
            print(f"📤 Subiendo foto a Cloudinary para usuario {user_id}")
            
            # Subir a Cloudinary
            upload_result = cloudinary.uploader.upload(
                foto_base64,
                folder="alegra/perfiles",
                public_id=f"perfil_{user_id}",
                overwrite=True,
                resource_type="image",
                transformation=[
                    {'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face'}
                ]
            )
            
            foto_url = upload_result['secure_url']
            print(f"✅ Foto subida: {foto_url}")
            
            # Actualizar base de datos
            connection = connect_to_db()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE usuario SET avatar_url = %s WHERE id = %s", (foto_url, user_id))
                    connection.commit()
                    print(f"✅ BD actualizada para usuario {user_id}")
            finally:
                connection.close()
            
            return jsonify({'success': True, 'foto_url': foto_url}), 200
        
        except Exception as e:
            print(f"❌ Error subiendo foto: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/usuario/perfil', methods=['GET', 'OPTIONS'])
    @jwt_required(optional=True)
    def get_user_profile():
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'success': False, 'message': 'No autenticado'}), 401
            
            connection = connect_to_db()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, nombre, correo, genero, telefono, 
                               fecha_nacimiento, avatar_url, rol
                        FROM usuario WHERE id = %s
                    """, (int(user_id),))
                    user = cursor.fetchone()
                    
                    if not user:
                        return jsonify({'success': False, 'message': 'No encontrado'}), 404
                    
                    # Formatear fecha solo si NO es string
                    if user.get('fecha_nacimiento') and not isinstance(user['fecha_nacimiento'], str):
                        user['fecha_nacimiento'] = user['fecha_nacimiento'].strftime('%Y-%m-%d')
            finally:
                connection.close()
            
            return jsonify({'success': True, 'usuario': user}), 200
        
        except Exception as e:
            print(f"❌ Error obteniendo perfil: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'Error interno'}), 500

    @app.route('/api/foto/delete', methods=['DELETE', 'OPTIONS'])
    @jwt_required(optional=True)
    def delete_foto():
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'success': False, 'message': 'No autenticado'}), 401
            
            user_id = int(user_id)
            
            # Eliminar de Cloudinary
            try:
                cloudinary.uploader.destroy(f"alegra/perfiles/perfil_{user_id}")
                print(f"✅ Foto eliminada de Cloudinary para usuario {user_id}")
            except Exception as e:
                print(f"⚠️ Error eliminando de Cloudinary: {e}")
            
            # Actualizar BD
            connection = connect_to_db()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE usuario SET avatar_url = NULL WHERE id = %s", (user_id,))
                    connection.commit()
            finally:
                connection.close()
            
            return jsonify({'success': True, 'message': 'Foto eliminada'}), 200
        
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'Error interno'}), 500