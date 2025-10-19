# foto_perfil_api.py
from flask import request, jsonify, send_from_directory, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import os
import uuid
import pymysql
import traceback

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'fotos_perfil')
MAX_FILE_SIZE = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            if ',' in foto_base64:
                foto_base64 = foto_base64.split(',')[1]
            
            image_data = base64.b64decode(foto_base64)
            
            if len(image_data) > MAX_FILE_SIZE:
                return jsonify({'success': False, 'message': 'Imagen muy grande'}), 400
            
            filename = f"perfil_{user_id}_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            foto_url = f"/uploads/fotos_perfil/{filename}"
            
            connection = connect_to_db()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT avatar_url FROM usuario WHERE id = %s", (user_id,))
                    old = cursor.fetchone()
                    
                    cursor.execute("UPDATE usuario SET avatar_url = %s WHERE id = %s", (foto_url, user_id))
                    connection.commit()
                    
                    if old and old.get('avatar_url'):
                        old_file = os.path.join(UPLOAD_FOLDER, old['avatar_url'].split('/')[-1])
                        if os.path.exists(old_file):
                            os.remove(old_file)
            finally:
                connection.close()
            
            return jsonify({'success': True, 'foto_url': foto_url}), 200
        
        except Exception as e:
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
                    
                    if user.get('fecha_nacimiento') and not isinstance(user['fecha_nacimiento'], str):
                        user['fecha_nacimiento'] = user['fecha_nacimiento'].strftime('%Y-%m-%d')
            finally:
                connection.close()
            
            return jsonify({'success': True, 'usuario': user}), 200
        
        except Exception as e:
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'Error interno'}), 500

    @app.route('/uploads/fotos_perfil/<filename>')
    def serve_foto(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except:
            abort(404)