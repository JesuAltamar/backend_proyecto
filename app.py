from datetime import date, datetime, timedelta
from flask import Flask, request, jsonify
import pymysql
from pymysql.cursors import DictCursor
from flask_cors import CORS  
from werkzeug.security import generate_password_hash, check_password_hash
import traceback
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from google.cloud import dialogflow_v2 as dialogflow
from foto_perfil_api import register_foto_routes
from dotenv import load_dotenv
from gemini_service import GeminiPsychologistService
import uuid

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️ ERROR: GEMINI_API_KEY no encontrada en .env")
    GEMINI_API_KEY = 'AIzaSyCJgpAe9dh6gBxnP-A3KwuAaOFbQU38b38'

gemini_service = GeminiPsychologistService(GEMINI_API_KEY)

app = Flask(__name__)
print("📋 Rutas registradas:")
for rule in app.url_map.iter_rules():
    print(rule.endpoint, "->", rule)

app.secret_key = 'jesus_key_251206'

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'altamarjesu76@gmail.com',
    'password': 'dcfh wvtw iylu gdvf'
}



CORS(app,
     resources={
         r"/*": {
             "origins": ["https://alegra-nu.vercel.app", "https://*.vercel.app", "http://localhost:*", "*"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }
     }
)

# Middleware adicional para CORS
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-Requested-With'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
    return response

# Manejar preflight para TODAS las rutas
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-Requested-With'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

 
app.config["JWT_SECRET_KEY"] = "super_secret_key"
app.config["JWT_ALGORITHM"] = "HS256"
jwt_manager = JWTManager(app)


def connect_to_db():
    # Validar TODAS las variables necesarias
    required_vars = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_PORT': os.getenv('DB_PORT', '3306')
    }
    
    # Mostrar qué variables están configuradas (sin mostrar password completo)
    print("🔍 Variables de entorno:")
    for key, value in required_vars.items():
        if key == 'DB_PASSWORD':
            print(f"  {key}: {'✅ Configurado' if value else '❌ NO configurado'}")
        else:
            print(f"  {key}: {value if value else '❌ NO configurado'}")
    
    # Verificar que todas las variables existan
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        raise RuntimeError(f"❌ ERROR: Faltan variables de entorno: {', '.join(missing_vars)}")
    
    try:
        connection = pymysql.connect(
            host=required_vars['DB_HOST'],
            user=required_vars['DB_USER'],
            password=required_vars['DB_PASSWORD'],
            db=required_vars['DB_NAME'],
            port=int(required_vars['DB_PORT']),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10  # ⬅️ IMPORTANTE: timeout de 10 segundos
        )
        print(f"✅ Conexión exitosa a la base de datos: {required_vars['DB_NAME']}")
        return connection
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print(f"   Host: {required_vars['DB_HOST']}")
        print(f"   Port: {required_vars['DB_PORT']}")
        print(f"   Database: {required_vars['DB_NAME']}")
        raise

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"
PROJECT_ID = "risk-assessment-bot-leim"

def detect_intent(message: str, session_id: str = "default") -> str:
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.TextInput(text=message, language_code="es")
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

# ==================== CHAT ====================
@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """Endpoint de chat con análisis completo"""
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        session_id = data.get("sessionId") or data.get("session_id", str(uuid.uuid4()))
        user_id = data.get("user_id")
        
        if not message:
            return jsonify({"success": False, "error": "Mensaje vacío"}), 400
        
        # Obtener respuesta de Gemini con análisis
        response = gemini_service.send_message(message, session_id)
        
        # Guardar mensaje usuario
        conn = None
        try:
            conn = connect_to_db()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_interacciones 
                    (session_id, mensaje, remitente, usuario_id, fecha, sentimiento, tema) 
                    VALUES (%s, %s, 'user', %s, NOW(), %s, %s)
                """, (session_id, message, user_id, 
                      response.get('sentimiento'), response.get('tema')))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Error guardando mensaje usuario: {e}")
        finally:
            if conn:
                conn.close()
        
        # Guardar respuesta bot
        chat_bot_id = None
        conn = None
        try:
            conn = connect_to_db()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_interacciones 
                    (session_id, mensaje, remitente, usuario_id, fecha, 
                     is_crisis, crisis_level, sentimiento, tema) 
                    VALUES (%s, %s, 'bot', %s, NOW(), %s, %s, %s, %s)
                """, (session_id, response['message'], user_id,
                      response['is_crisis'], response['crisis_level'],
                      response.get('sentimiento'), response.get('tema')))
                chat_bot_id = cur.lastrowid
                conn.commit()
                
                # Actualizar analytics diarios
                cur.execute("""
                    INSERT INTO chat_analytics (fecha, sentimiento_positivo, sentimiento_neutral, sentimiento_negativo, total_mensajes)
                    VALUES (CURDATE(), 
                            CASE WHEN %s = 'positivo' THEN 1 ELSE 0 END,
                            CASE WHEN %s = 'neutral' THEN 1 ELSE 0 END,
                            CASE WHEN %s = 'negativo' THEN 1 ELSE 0 END,
                            1)
                    ON DUPLICATE KEY UPDATE
                        sentimiento_positivo = sentimiento_positivo + CASE WHEN %s = 'positivo' THEN 1 ELSE 0 END,
                        sentimiento_neutral = sentimiento_neutral + CASE WHEN %s = 'neutral' THEN 1 ELSE 0 END,
                        sentimiento_negativo = sentimiento_negativo + CASE WHEN %s = 'negativo' THEN 1 ELSE 0 END,
                        total_mensajes = total_mensajes + 1
                """, (response.get('sentimiento'), response.get('sentimiento'), response.get('sentimiento'),
                      response.get('sentimiento'), response.get('sentimiento'), response.get('sentimiento')))
                
                # Actualizar contador de temas
                if response.get('tema'):
                    cur.execute("""
                        INSERT INTO chat_temas (tema, contador)
                        VALUES (%s, 1)
                        ON DUPLICATE KEY UPDATE
                            contador = contador + 1
                    """, (response.get('tema'),))
                
                conn.commit()
        except Exception as e:
            print(f"⚠️ Error guardando respuesta bot: {e}")
        finally:
            if conn:
                conn.close()
        
        # 🚨 CREAR NOTIFICACIÓN SI HAY CRISIS
        if response['is_crisis'] and response['crisis_level'] in ['moderate', 'severe']:
            crear_notificacion_crisis(user_id, chat_bot_id, message, response['crisis_level'])
        
        return jsonify({
            "success": True,
            "reply": response['message'],
            "is_crisis": response['is_crisis'],
            "crisis_level": response['crisis_level'],
            "session_id": session_id,
            "timestamp": response['timestamp']
        }), 200
        
    except Exception as e:
        print(f"❌ Error en /api/chat: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "Error procesando mensaje"}), 500
    
# ==================== ANÁLISIS DE CHAT ====================

@app.route('/api/admin/chat/sentimientos', methods=['GET'])
def get_chat_sentimientos():
    """Obtiene análisis de sentimientos agregado"""
    connection = None
    try:
        dias = int(request.args.get('dias', 7))
        connection = connect_to_db()
        
        with connection.cursor() as cursor:
            # Verificar si hay datos
            cursor.execute("SELECT COUNT(*) as total FROM chat_analytics")
            count = cursor.fetchone()
            
            if count['total'] == 0:
                return jsonify({
                    'success': True,
                    'sentimientos': {'positivo': 0, 'neutral': 0, 'negativo': 0},
                    'porcentajes': {'positivo': 0.0, 'neutral': 0.0, 'negativo': 0.0}
                }), 200
            
            # Query CORRECTA
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(sentimiento_positivo), 0) as positivo,
                    COALESCE(SUM(sentimiento_neutral), 0) as neutral,
                    COALESCE(SUM(sentimiento_negativo), 0) as negativo,
                    COALESCE(SUM(total_mensajes), 0) as total
                FROM chat_analytics
                WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """, (dias,))
            
            sentimientos = cursor.fetchone()
            total = sentimientos['total'] if sentimientos['total'] > 0 else 1
            
            return jsonify({
                'success': True,
                'sentimientos': {
                    'positivo': int(sentimientos['positivo']),
                    'neutral': int(sentimientos['neutral']),
                    'negativo': int(sentimientos['negativo']),
                },
                'porcentajes': {
                    'positivo': round((sentimientos['positivo'] / total) * 100, 1),
                    'neutral': round((sentimientos['neutral'] / total) * 100, 1),
                    'negativo': round((sentimientos['negativo'] / total) * 100, 1),
                }
            }), 200
            
    except Exception as e:
        print(f"❌ Error obteniendo sentimientos: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/admin/chat/temas', methods=['GET'])
def get_chat_temas():
    """Obtiene temas más consultados"""
    try:
        limit = int(request.args.get('limit', 5))
        
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tema, contador
                FROM chat_temas
                ORDER BY contador DESC
                LIMIT %s
            """, (limit,))
            temas = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'temas': temas
            }), 200
            
    except Exception as e:
        print(f"Error obteniendo temas: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/admin/chat/tendencias', methods=['GET'])
def get_chat_tendencias():
    """Obtiene tendencias semanales"""
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(fecha, '%a') as dia,
                    total_mensajes
                FROM chat_analytics
                WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ORDER BY fecha ASC
            """)
            tendencias = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'tendencias': tendencias
            }), 200
            
    except Exception as e:
        print(f"Error obteniendo tendencias: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# ==================== EMAIL ====================
def send_email(to_email, subject, html_content):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = to_email
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# ==================== PASSWORD RESET ====================
@app.route('/api/password/request-reset', methods=['POST'])
def request_password_reset():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "JSON inválido"}), 400

        correo = data.get("correo")
        if not correo:
            return jsonify({"success": False, "message": "El correo es requerido"}), 400

        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM usuario WHERE correo = %s", (correo,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({"success": True, "message": "Si el correo existe, recibirás un enlace"}), 200
            
            token = secrets.token_urlsafe(64)
            expires_at = datetime.now() + timedelta(hours=1)
            
            cursor.execute("""
                INSERT INTO password_resets (usuario_id, token, expires_at) 
                VALUES (%s, %s, %s)
            """, (usuario['id'], token, expires_at))
            connection.commit()
            
            reset_url = f"http://localhost:8080/#/reset-password?token={token}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; text-align: center;">Recuperación de Contraseña</h1>
                    </div>
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p>Hola <strong>{usuario['nombre']}</strong>,</p>
                        <p>Has solicitado restablecer tu contraseña:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Restablecer Contraseña
                            </a>
                        </div>
                        <p><strong>Este enlace expirará en 1 hora.</strong></p>
                    </div>
                </body>
            </html>
            """
            
            email_sent = send_email(correo, "Recuperación de Contraseña - Alegra", html_content)
            
            if email_sent:
                return jsonify({"success": True, "message": "Email enviado"}), 200
            else:
                return jsonify({"success": False, "message": "Error al enviar email"}), 500

    except Exception as e:
        print(f"❌ Error en request_password_reset: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": "Error interno"}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/password/verify-token', methods=['POST'])
def verify_reset_token():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token:
            return jsonify({"success": False, "message": "Token requerido"}), 400

        token = token.strip()
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pr.id, pr.usuario_id, u.correo, u.nombre
                FROM password_resets pr
                JOIN usuario u ON pr.usuario_id = u.id
                WHERE pr.token = %s AND pr.expires_at > NOW() AND pr.used = 0
            """, (token,))
            
            reset_record = cursor.fetchone()
            
            if not reset_record:
                return jsonify({"success": False, "message": "Token inválido o expirado"}), 400
            
            return jsonify({
                "success": True,
                "message": "Token válido",
                "usuario": {"nombre": reset_record['nombre'], "correo": reset_record['correo']}
            }), 200

    except Exception as e:
        print(f"❌ Error en verify_reset_token: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": "Error interno"}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/password/reset', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get("token")
        new_password = data.get("password")
        
        if not token or not new_password:
            return jsonify({"success": False, "message": "Token y contraseña requeridos"}), 400
        
        token = token.strip()
        
        if len(new_password) < 6:
            return jsonify({"success": False, "message": "Contraseña debe tener al menos 6 caracteres"}), 400

        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pr.id, pr.usuario_id, u.nombre, u.correo
                FROM password_resets pr
                JOIN usuario u ON pr.usuario_id = u.id
                WHERE pr.token = %s AND pr.expires_at > NOW() AND pr.used = 0
            """, (token,))
            
            reset_record = cursor.fetchone()
            
            if not reset_record:
                return jsonify({"success": False, "message": "Token inválido o expirado"}), 400
            
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE usuario SET password = %s WHERE id = %s", (hashed_password, reset_record['usuario_id']))
            cursor.execute("UPDATE password_resets SET used = 1 WHERE id = %s", (reset_record['id']))
            connection.commit()
            
            return jsonify({
                "success": True,
                "message": "Contraseña actualizada",
                "usuario": {"nombre": reset_record['nombre'], "correo": reset_record['correo']}
            }), 200

    except Exception as e:
        print(f"❌ Error en reset_password: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": "Error interno"}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# ==================== WEB ====================
@app.route('/', methods=['GET'])
def index():
    """Ruta principal - Info de la API"""
    return jsonify({
        'status': 'online',
        'message': 'API Backend Alegra - Salud Mental',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'auth': {
                'login': 'POST /api/login',
                'registro': 'POST /api/usuariosip'
            },
            'usuarios': {
                'listar': 'GET /api/usuarios',
                'crear': 'POST /api/usuariosip',
                'editar': 'PUT /api/usuarios/<id>',
                'eliminar': 'DELETE /api/usuarios/<id>'
            },
            'tareas': {
                'listar': 'GET /api/tareas',
                'crear': 'POST /api/tareas',
                'editar': 'PUT /api/tareas/<id>',
                'eliminar': 'DELETE /api/tareas/<id>'
            },
            'chat': {
                'enviar': 'POST /api/chat'
            },
            'admin': {
                'estadisticas': 'GET /api/admin/estadisticas',
                'notificaciones': 'GET /api/admin/notificaciones'
            }
        },
        'docs': 'https://github.com/tu-usuario/tu-repo'
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para Railway"""
    try:
        # Verificar conexión a BD
        conn = connect_to_db()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503

# ==================== LOGIN ====================
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def api_login():
    # Manejar preflight request
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON inválido"}), 400

        correo = data.get("correo")
        password = data.get("password")

        if not correo or not password:
            return jsonify({"error": "Correo y contraseña requeridos"}), 400

        with connect_to_db() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM usuario WHERE correo=%s", (correo,))
                user = cur.fetchone()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        token = create_access_token(
            identity=str(user["id"]),
            additional_claims={"correo": user["correo"]}
        )

        return jsonify({
            "message": "Login exitoso",
            "token": token,
            "usuario": {
                "id": user["id"],
                "nombre": user["nombre"],
                "correo": user["correo"],
                "genero": user["genero"],
                "telefono": user["telefono"]
            }
        }), 200

    except Exception as e:
        print(f"Error en /api/login: {e}")
        return jsonify({"error": str(e)}), 500
    
# ==================== PERFIL USUARIO ====================
@app.route('/api/usuario/perfil', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def obtener_perfil():
    """Obtiene el perfil del usuario autenticado"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, correo, genero, telefono, fecha_nacimiento, avatar_url, rol
                FROM usuario 
                WHERE id = %s
            """, (user_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
            
         # Formatear fecha solo si NO es string
            if usuario.get('fecha_nacimiento') and not isinstance(usuario['fecha_nacimiento'], str):
             usuario['fecha_nacimiento'] = usuario['fecha_nacimiento'].strftime('%Y-%m-%d')
            return jsonify({
                'success': True,
                'usuario': usuario
            }), 200
            
    except Exception as e:
        print(f"❌ Error obteniendo perfil: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()



# ==================== USUARIOS ====================
@app.route('/api/usuarios', methods=['GET'])
def api_get_usuarios():
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM usuario")
                data = cur.fetchall()
        return jsonify(data)
    except Exception as e:  
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuariosip', methods=['POST'])
def api_add_usuario_desde_url():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400

        campos = ["nombre", "genero", "fecha_nacimiento", "telefono", "correo", "password"]
        for campo in campos:
            if campo not in data or not data[campo]:
                return jsonify({'error': f"Falta el campo: {campo}"}), 400

        nombre = data["nombre"]
        genero = data["genero"]
        fecha_nacimiento = data["fecha_nacimiento"]
        telefono = data["telefono"]
        correo = data["correo"]
        password = data["password"]

        try:
            if "-" in fecha_nacimiento:
                fecha_obj = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
            elif "/" in fecha_nacimiento:
                fecha_obj = datetime.strptime(fecha_nacimiento, "%Y/%m/%d").date()
            else:
                return jsonify({'error': 'Formato de fecha inválido'}), 400
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 400

        hashed_password = generate_password_hash(password)

        with connect_to_db() as conn:
            with conn.cursor() as cur:
                sql = """
                    INSERT INTO usuario (nombre, genero, fecha_nacimiento, telefono, correo, password)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql, (nombre, genero, fecha_obj, telefono, correo, hashed_password))
                conn.commit()
                new_id = cur.lastrowid

        return jsonify({'message': 'Usuario agregado', 'id': new_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:user_id>', methods=['PUT'])
def editar_usuario(user_id):
    try:
        data = request.json
        connection = connect_to_db()
        with connection.cursor() as cursor:
            sql = """
                UPDATE usuario
                SET nombre=%s, genero=%s, fecha_nacimiento=%s, telefono=%s, correo=%s
                WHERE id=%s
            """
            cursor.execute(sql, (
                data.get("nombre"),
                data.get("genero"),
                data.get("fecha_nacimiento"),
                data.get("telefono"),
                data.get("correo"),
                user_id
            ))
            connection.commit()
        return jsonify({"message": "Usuario actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
def eliminar_usuario(user_id):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM usuario WHERE id=%s", (user_id,))
            connection.commit()
        return jsonify({"message": "Usuario eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# ==================== Api TAREAS  ====================
@app.route('/api/tareas', methods=['GET'])
@jwt_required()
def obtener_tareas():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            categoria = request.args.get('categoria')
            estado = request.args.get('estado')
            
            query = """
                SELECT id, titulo, descripcion, fecha, estado, prioridad, 
                       categoria, fecha_creacion, usuario_id,
                       recordatorio_activo, email_recordatorio, 
                       fecha_recordatorio, hora_recordatorio
                FROM tareas 
                WHERE usuario_id = %s
            """
            user_id = int(get_jwt_identity())
            params = [user_id]
            
            if fecha_inicio:
                query += " AND fecha >= %s"
                params.append(fecha_inicio)
            if fecha_fin:
                query += " AND fecha <= %s"
                params.append(fecha_fin)
            if categoria:
                query += " AND categoria = %s"
                params.append(categoria)
            if estado:
                query += " AND estado = %s"
                params.append(estado)
            
            query += " ORDER BY fecha DESC, fecha_creacion DESC"
            cursor.execute(query, params)
            tareas = cursor.fetchall()
            
            for tarea in tareas:
                if tarea['fecha']:
                    tarea['fecha'] = tarea['fecha'].strftime('%Y-%m-%d')
                if tarea['fecha_creacion']:
                    tarea['fecha_creacion'] = tarea['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
                if tarea['fecha_recordatorio']:
                    tarea['fecha_recordatorio'] = tarea['fecha_recordatorio'].strftime('%Y-%m-%d')
                if tarea['hora_recordatorio']:
                    tarea['hora_recordatorio'] = str(tarea['hora_recordatorio'])
            
            return jsonify({'success': True, 'tareas': tareas, 'total': len(tareas)})
    except Exception as e:
        print(f"Error al obtener tareas: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/tareas/recordatorios', methods=['GET'])
@jwt_required()
def obtener_tareas_con_recordatorios():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            user_id = int(get_jwt_identity())
            
            query = """
                SELECT id, titulo, descripcion, fecha, estado, prioridad, 
                       categoria, recordatorio_activo, email_recordatorio, 
                       fecha_recordatorio, hora_recordatorio
                FROM tareas 
                WHERE usuario_id = %s 
                  AND recordatorio_activo = TRUE 
                  AND CONCAT(fecha_recordatorio, ' ', hora_recordatorio) > NOW()
                ORDER BY fecha_recordatorio ASC, hora_recordatorio ASC
            """
            cursor.execute(query, (user_id,))
            tareas = cursor.fetchall()
            
            for tarea in tareas:
                if tarea['fecha']:
                    tarea['fecha'] = tarea['fecha'].strftime('%Y-%m-%d')
                if tarea['fecha_recordatorio']:
                    tarea['fecha_recordatorio'] = tarea['fecha_recordatorio'].strftime('%Y-%m-%d')
                if tarea['hora_recordatorio']:
                    tarea['hora_recordatorio'] = str(tarea['hora_recordatorio'])
            
            return jsonify({'success': True, 'tareas': tareas, 'total': len(tareas)})
    except Exception as e:
        print(f"Error al obtener tareas con recordatorios: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/tareas', methods=['POST'])
@jwt_required()
def crear_tarea():
    try:
        data = request.get_json()
        print("📩 JSON recibido en /api/tareas:", data)
        user_id = int(get_jwt_identity())

        if not data.get('titulo'):
            return jsonify({'success': False, 'message': 'El título es requerido'}), 400

        titulo = data.get('titulo').strip()
        descripcion = data.get('descripcion', '').strip()
        fecha = data.get('fecha', date.today().strftime('%Y-%m-%d'))
        prioridad = data.get('prioridad', 'media')
        categoria = data.get('categoria', 'personal')
        
        # CAMPOS DE RECORDATORIO
        recordatorio_activo = data.get('recordatorio_activo', False)
        email_recordatorio = data.get('email_recordatorio')
        fecha_recordatorio = data.get('fecha_recordatorio')
        hora_recordatorio = data.get('hora_recordatorio')

        # Validaciones
        if prioridad not in ['baja', 'media', 'alta']:
            prioridad = 'media'
        if categoria not in ['personal', 'trabajo', 'salud', 'hogar', 'estudio', 'otro']:
            categoria = 'personal'

        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tareas (titulo, descripcion, fecha, estado, prioridad, 
                                    categoria, usuario_id, fecha_creacion,
                                    recordatorio_activo, email_recordatorio,
                                    fecha_recordatorio, hora_recordatorio)
                VALUES (%s, %s, %s, 'pendiente', %s, %s, %s, %s, %s, %s, %s, %s)
            """, (titulo, descripcion, fecha, prioridad, categoria, user_id, 
                  datetime.now(), recordatorio_activo, email_recordatorio,
                  fecha_recordatorio, hora_recordatorio))
            connection.commit()
            tarea_id = cursor.lastrowid

            cursor.execute("SELECT * FROM tareas WHERE id = %s", (tarea_id,))
            tarea = cursor.fetchone()

            # Formatear fechas para respuesta
            if tarea['fecha']:
                tarea['fecha'] = tarea['fecha'].strftime('%Y-%m-%d')
            if tarea['fecha_creacion']:
                tarea['fecha_creacion'] = tarea['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
            if tarea['fecha_recordatorio']:
                tarea['fecha_recordatorio'] = tarea['fecha_recordatorio'].strftime('%Y-%m-%d')
            if tarea['hora_recordatorio']:
                tarea['hora_recordatorio'] = str(tarea['hora_recordatorio'])

            return jsonify({'success': True, 'message': 'Tarea creada', 'tarea': tarea}), 201
    except Exception as e:
        print(f"Error al crear tarea: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/tareas/<int:tarea_id>', methods=['PUT'])
@jwt_required()
def actualizar_tarea(tarea_id):
    try:
        data = request.get_json()
        print(f"📩 Actualizando tarea {tarea_id} con: {data}")
        user_id = int(get_jwt_identity())

        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Verificar que la tarea existe y pertenece al usuario
            cursor.execute("SELECT * FROM tareas WHERE id = %s AND usuario_id = %s", (tarea_id, user_id))
            tarea_existente = cursor.fetchone()
            
            if not tarea_existente:
                return jsonify({'success': False, 'message': 'Tarea no encontrada'}), 404

            # Preparar campos a actualizar
            campos_actualizar = []
            valores = []

            if 'titulo' in data:
                campos_actualizar.append("titulo = %s")
                valores.append(data['titulo'].strip())
            
            if 'descripcion' in data:
                campos_actualizar.append("descripcion = %s")
                valores.append(data['descripcion'].strip())
            
            if 'fecha' in data:
                campos_actualizar.append("fecha = %s")
                valores.append(data['fecha'])
            
            if 'estado' in data:
                campos_actualizar.append("estado = %s")
                valores.append(data['estado'])
            
            if 'prioridad' in data:
                prioridad = data['prioridad']
                if prioridad not in ['baja', 'media', 'alta']:
                    prioridad = 'media'
                campos_actualizar.append("prioridad = %s")
                valores.append(prioridad)
            
            if 'categoria' in data:
                categoria = data['categoria']
                if categoria not in ['personal', 'trabajo', 'salud', 'hogar', 'estudio', 'otro']:
                    categoria = 'personal'
                campos_actualizar.append("categoria = %s")
                valores.append(categoria)

            # Campos de recordatorio
            if 'recordatorio_activo' in data:
                campos_actualizar.append("recordatorio_activo = %s")
                valores.append(data['recordatorio_activo'])
            
            if 'email_recordatorio' in data:
                campos_actualizar.append("email_recordatorio = %s")
                valores.append(data['email_recordatorio'])
            
            if 'fecha_recordatorio' in data:
                campos_actualizar.append("fecha_recordatorio = %s")
                valores.append(data['fecha_recordatorio'])
            
            if 'hora_recordatorio' in data:
                campos_actualizar.append("hora_recordatorio = %s")
                valores.append(data['hora_recordatorio'])

            if not campos_actualizar:
                return jsonify({'success': False, 'message': 'No hay campos para actualizar'}), 400

            # Ejecutar actualización
            query = f"UPDATE tareas SET {', '.join(campos_actualizar)} WHERE id = %s AND usuario_id = %s"
            valores.extend([tarea_id, user_id])
            
            cursor.execute(query, valores)
            connection.commit()

            # Obtener tarea actualizada
            cursor.execute("SELECT * FROM tareas WHERE id = %s", (tarea_id,))
            tarea_actualizada = cursor.fetchone()

            # Formatear fechas
            if tarea_actualizada['fecha']:
                tarea_actualizada['fecha'] = tarea_actualizada['fecha'].strftime('%Y-%m-%d')
            if tarea_actualizada['fecha_creacion']:
                tarea_actualizada['fecha_creacion'] = tarea_actualizada['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
            if tarea_actualizada['fecha_recordatorio']:
                tarea_actualizada['fecha_recordatorio'] = tarea_actualizada['fecha_recordatorio'].strftime('%Y-%m-%d')
            if tarea_actualizada['hora_recordatorio']:
                tarea_actualizada['hora_recordatorio'] = str(tarea_actualizada['hora_recordatorio'])

            return jsonify({'success': True, 'message': 'Tarea actualizada', 'tarea': tarea_actualizada}), 200

    except Exception as e:
        print(f"Error al actualizar tarea: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/tareas/<int:tarea_id>', methods=['DELETE'])
@jwt_required()
def eliminar_tarea(tarea_id):
    try:
        user_id = int(get_jwt_identity())
        
        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Verificar que la tarea existe y pertenece al usuario
            cursor.execute("SELECT * FROM tareas WHERE id = %s AND usuario_id = %s", (tarea_id, user_id))
            tarea = cursor.fetchone()
            
            if not tarea:
                return jsonify({'success': False, 'message': 'Tarea no encontrada'}), 404

            # Eliminar tarea
            cursor.execute("DELETE FROM tareas WHERE id = %s AND usuario_id = %s", (tarea_id, user_id))
            connection.commit()

            return jsonify({'success': True, 'message': 'Tarea eliminada'}), 200

    except Exception as e:
        print(f"Error al eliminar tarea: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/estadisticas', methods=['GET'])
@jwt_required()
def obtener_estadisticas():
    try:
        user_id = int(get_jwt_identity())
        connection = connect_to_db()
        
        with connection.cursor() as cursor:
            # Total de tareas
            cursor.execute("SELECT COUNT(*) as total FROM tareas WHERE usuario_id = %s", (user_id,))
            total = cursor.fetchone()['total']
            
            # Tareas completadas
            cursor.execute("SELECT COUNT(*) as completadas FROM tareas WHERE usuario_id = %s AND estado = 'completada'", (user_id,))
            completadas = cursor.fetchone()['completadas']
            
            # Tareas con recordatorio
            cursor.execute("SELECT COUNT(*) as recordatorios FROM tareas WHERE usuario_id = %s AND recordatorio_activo = TRUE", (user_id,))
            recordatorios = cursor.fetchone()['recordatorios']
            
            # Tareas pendientes
            pendientes = total - completadas
            
            estadisticas = {
                'total': total,
                'completadas': completadas,
                'pendientes': pendientes,
                'recordatorios': recordatorios
            }

            return jsonify({'success': True, 'estadisticas': estadisticas}), 200

    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# ==================== ADMIN ====================
@app.route('/api/admin/estadisticas', methods=['GET'])
def api_get_admin_stats():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_usuarios FROM usuario")
            total_usuarios = cursor.fetchone()['total_usuarios']

            cursor.execute("SELECT COUNT(*) AS total_tareas FROM tareas")
            total_tareas = cursor.fetchone()['total_tareas']

            promedio_tareas_por_usuario = 0.0
            if total_usuarios > 0:
                promedio_tareas_por_usuario = total_tareas / total_usuarios

            cursor.execute("SELECT COUNT(*) AS total_chat_interacciones FROM chat_interacciones")
            total_chat_interacciones = cursor.fetchone()['total_chat_interacciones']

            cursor.execute("SELECT COUNT(*) AS total_sesiones_juego FROM sesiones_juego")
            total_sesiones_juego = cursor.fetchone()['total_sesiones_juego']

        stats = {
            'total_usuarios': total_usuarios,
            'total_tareas': total_tareas,
            'promedio_tareas_por_usuario': round(promedio_tareas_por_usuario, 1),
            'total_chat_interacciones': total_chat_interacciones,
            'total_sesiones_juego': total_sesiones_juego
        }
        return jsonify(stats), 200

    except Exception as e:
        print(f"Error estadísticas admin: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/admin/usuarios-activos-semanal', methods=['GET'])
def api_get_weekly_active_users():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            query = """
                SELECT DATE(fecha) AS dia, COUNT(DISTINCT usuario_id) AS total
                FROM tareas
                WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY dia
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

        from datetime import timedelta
        hoy = datetime.today()
        actividad = {}

        for i in range(7):
            dia = (hoy - timedelta(days=6 - i)).strftime("%Y-%m-%d")
            actividad[dia] = 0

        for row in resultados:
            actividad[row['dia'].strftime("%Y-%m-%d")] = row['total']

        return jsonify(actividad), 200
    except Exception as e:
        print(f"Error weekly users: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# ==================== NOTIFICACIONES ====================
@app.route('/api/admin/notificaciones', methods=['GET'])
def obtener_notificaciones_admin():
    try:
        no_leidas = request.args.get('no_leidas', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        tipo = request.args.get('tipo')
        
        connection = connect_to_db()
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    n.id, n.tipo, n.titulo, n.mensaje, n.usuario_id,
                    n.chat_interaccion_id, n.leida, n.fecha_creacion,
                    u.nombre as nombre_usuario,
                    u.correo as correo_usuario,
                    u.telefono as telefono_usuario
                FROM notificaciones_admin n
                LEFT JOIN usuario u ON n.usuario_id = u.id
                WHERE 1=1
            """
            params = []
            
            if no_leidas:
                query += " AND n.leida = FALSE"
            
            if tipo:
                query += " AND n.tipo = %s"
                params.append(tipo)
            
            query += " ORDER BY n.fecha_creacion DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            notificaciones = cursor.fetchall()
            
            for notif in notificaciones:
                if notif['fecha_creacion']:
                    notif['fecha_creacion'] = notif['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("SELECT COUNT(*) as total FROM notificaciones_admin WHERE leida = FALSE")
            no_leidas_count = cursor.fetchone()['total']
            
            return jsonify({
                'success': True,
                'notificaciones': notificaciones,
                'total': len(notificaciones),
                'no_leidas': no_leidas_count
            }), 200
            
    except Exception as e:
        print(f"❌ Error notificaciones: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/admin/notificaciones/<int:notif_id>/marcar-leida', methods=['PUT'])
def marcar_notificacion_leida(notif_id):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE notificaciones_admin SET leida = TRUE WHERE id = %s", (notif_id,))
            connection.commit()
            return jsonify({'success': True, 'message': 'Notificación marcada'}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/admin/notificaciones/marcar-todas-leidas', methods=['PUT'])
def marcar_todas_notificaciones_leidas():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE notificaciones_admin SET leida = TRUE WHERE leida = FALSE")
            connection.commit()
            affected = cursor.rowcount
            return jsonify({'success': True, 'message': f'{affected} marcadas'}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/admin/notificaciones/<int:notif_id>', methods=['DELETE'])
def eliminar_notificacion(notif_id):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM notificaciones_admin WHERE id = %s", (notif_id,))
            connection.commit()
            return jsonify({'success': True, 'message': 'Eliminada'}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

def crear_notificacion_crisis(usuario_id, chat_id, mensaje, crisis_level):
    try:
        conn = connect_to_db()
        with conn.cursor() as cursor:
            nombre_usuario = "Anónimo"
            if usuario_id:
                cursor.execute("SELECT nombre FROM usuario WHERE id = %s", (usuario_id,))
                user = cursor.fetchone()
                if user:
                    nombre_usuario = user['nombre']
            
            titulo = f"🚨 CRISIS SEVERA - {nombre_usuario}" if crisis_level == 'severe' else f"⚠️ Crisis Moderada - {nombre_usuario}"
            mensaje_corto = mensaje[:200] + "..." if len(mensaje) > 200 else mensaje
            
            cursor.execute("""
                INSERT INTO notificaciones_admin 
                (tipo, titulo, mensaje, usuario_id, chat_interaccion_id, leida)
                VALUES ('crisis', %s, %s, %s, %s, FALSE)
            """, (titulo, mensaje_corto, usuario_id, chat_id))
            
            conn.commit()
            print(f"✅ Notificación creada: {titulo}")
            return True
    except Exception as e:
        print(f"❌ Error creando notificación: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

# ==================== ACTIVIDADES ====================

@app.route('/api/admin/actividades-recientes', methods=['GET'])
def api_get_recent_activities():
    """Obtiene la actividad más reciente de cada categoría"""
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Usuario más reciente
            cursor.execute("SELECT nombre, registro_at FROM usuario ORDER BY registro_at DESC LIMIT 1")
            u = cursor.fetchone()
            usuario = {
                "action": "Usuario registrado" if u else "No hay usuarios",
                "time": u["registro_at"].strftime("%Y-%m-%d %H:%M") if u and u["registro_at"] else "-",
                "detalle": u["nombre"] if u else "-"
            }

            # Tarea más reciente
            cursor.execute("SELECT titulo, fecha FROM tareas ORDER BY fecha DESC LIMIT 1")
            t = cursor.fetchone()
            tarea = {
                "action": "Tarea completada" if t else "No hay tareas",
                "time": t["fecha"].strftime("%Y-%m-%d %H:%M") if t and t["fecha"] else "-",
                "detalle": t["titulo"] if t else "-"
            }

            # Sesión más reciente
            cursor.execute("SELECT juego_nombre, fecha_inicio FROM sesiones_juego ORDER BY fecha_inicio DESC LIMIT 1")
            s = cursor.fetchone()
            sesion = {
                "action": "Sesión de juego" if s else "No hay sesiones",
                "time": s["fecha_inicio"].strftime("%Y-%m-%d %H:%M") if s and s["fecha_inicio"] else "-",
                "detalle": s["juego_nombre"] if s else "-"
            }

            # Chat más reciente - SOLO FECHA
            cursor.execute("SELECT fecha FROM chat_interacciones ORDER BY fecha DESC LIMIT 1")
            c = cursor.fetchone()
            chat = {
                "action": "Chat iniciado" if c else "No hay chats",
                "time": c["fecha"].strftime("%Y-%m-%d %H:%M") if c and c["fecha"] else "-",
                "detalle": "-"  # Solo mostrar fecha, sin mensaje
            }

        return jsonify([usuario, tarea, sesion, chat]), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/admin/actividades-usuario', methods=['GET'])
def api_get_user_activities():
    """Busca actividades del usuario más reciente con el nombre dado"""
    try:
        nombre_buscado = request.args.get("nombre")
        if not nombre_buscado:
            return jsonify([]), 400

        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Buscar usuario
            cursor.execute("""
                SELECT id, nombre, registro_at 
                FROM usuario 
                WHERE nombre LIKE %s 
                ORDER BY registro_at DESC 
                LIMIT 1
            """, (f"%{nombre_buscado}%",))
            u = cursor.fetchone()

            if not u:
                return jsonify([]), 200

            user_id = u["id"]
            user_name = u["nombre"]

            # Actividad de Registro
            registro = {
                "action": "Usuario registrado",
                "time": u["registro_at"].strftime("%Y-%m-%d %H:%M"),
                "detalle": f"Nombre: {user_name}"
            }

            # Actividad de tareas
            cursor.execute("SELECT titulo, fecha FROM tareas WHERE usuario_id=%s ORDER BY fecha DESC LIMIT 1", (user_id,))
            t = cursor.fetchone()
            tarea = {
                "action": "Tarea completada" if t else "No hay tareas",
                "time": t["fecha"].strftime("%Y-%m-%d %H:%M") if t and t["fecha"] else "-",
                "detalle": t["titulo"] if t else "-"
            }

            # Actividad de juegos
            cursor.execute("SELECT juego_nombre, fecha_inicio FROM sesiones_juego WHERE usuario_id=%s ORDER BY fecha_inicio DESC LIMIT 1", (user_id,))
            s = cursor.fetchone()
            sesion = {
                "action": "Sesión de juego" if s else "No hay sesiones",
                "time": s["fecha_inicio"].strftime("%Y-%m-%d %H:%M") if s and s["fecha_inicio"] else "-",
                "detalle": s["juego_nombre"] if s else "-"
            }

            # Actividad de chats - SOLO FECHA
            cursor.execute("SELECT fecha FROM chat_interacciones WHERE usuario_id=%s ORDER BY fecha DESC LIMIT 1", (user_id,))
            c = cursor.fetchone()
            chat = {
                "action": "Chat iniciado" if c else "No hay chats",
                "time": c["fecha"].strftime("%Y-%m-%d %H:%M") if c and c["fecha"] else "-",
                "detalle": "-"  # Solo fecha
            }

        return jsonify([registro, tarea, sesion, chat]), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# ==================== RACHA DIARIA ====================

def calcular_racha(ultima_actividad, fecha_actual):
    """Calcula si la racha continúa basándose en la última actividad"""
    if not ultima_actividad:
        return 0
    
    diff_days = (fecha_actual - ultima_actividad).days
    
    # Si pasó más de 1 día, se pierde la racha
    if diff_days > 1:
        return 0
    
    return diff_days

@app.route('/api/streak/<int:user_id>', methods=['GET'])
def obtener_racha(user_id):
    """Obtiene la racha actual del usuario"""
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Obtener estadísticas actuales
            cursor.execute("""
                SELECT racha_actual, racha_maxima, ultima_actividad 
                FROM user_streak_stats 
                WHERE user_id = %s
            """, (user_id,))
            stats = cursor.fetchone()
            
            if not stats:
                return jsonify({
                    'success': True,
                    'racha_actual': 0,
                    'racha_maxima': 0,
                    'ultima_actividad': None
                }), 200
            
            # Verificar si la racha sigue activa
            fecha_hoy = date.today()
            ultima_actividad = stats['ultima_actividad']
            diff_days = calcular_racha(ultima_actividad, fecha_hoy)
            
            racha_actual = stats['racha_actual']
            
            # Si pasó más de 1 día, resetear racha
            if diff_days > 1:
                racha_actual = 0
                cursor.execute("""
                    UPDATE user_streak_stats 
                    SET racha_actual = 0 
                    WHERE user_id = %s
                """, (user_id,))
                connection.commit()
            
            return jsonify({
                'success': True,
                'racha_actual': racha_actual,
                'racha_maxima': stats['racha_maxima'],
                'ultima_actividad': ultima_actividad.strftime('%Y-%m-%d') if ultima_actividad else None
            }), 200
            
    except Exception as e:
        print(f"Error al obtener racha: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/streak/completar-tarea', methods=['POST'])
def completar_tarea_racha():
    """Marca la tarea diaria como completada y actualiza la racha"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'user_id es requerido'}), 400
        
        fecha_hoy = date.today()
        
        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Verificar si ya completó la tarea hoy
            cursor.execute("""
                SELECT * FROM user_streaks 
                WHERE user_id = %s AND fecha = %s
            """, (user_id, fecha_hoy))
            tarea_hoy = cursor.fetchone()
            
            if tarea_hoy:
                return jsonify({
                    'success': False,
                    'message': 'Ya completaste tu tarea de hoy'
                }), 400
            
            # Obtener estadísticas actuales
            cursor.execute("""
                SELECT * FROM user_streak_stats 
                WHERE user_id = %s
            """, (user_id,))
            stats = cursor.fetchone()
            
            racha_actual = 0
            racha_maxima = 0
            
            if stats:
                ultima_actividad = stats['ultima_actividad']
                diff_days = calcular_racha(ultima_actividad, fecha_hoy)
                
                if diff_days == 1:
                    # Continuó la racha
                    racha_actual = stats['racha_actual'] + 1
                elif diff_days == 0:
                    # Mismo día (no debería pasar por el check anterior)
                    racha_actual = stats['racha_actual']
                else:
                    # Se perdió la racha, empezar de nuevo
                    racha_actual = 1
                
                racha_maxima = max(racha_actual, stats['racha_maxima'])
            else:
                # Primera vez
                racha_actual = 1
                racha_maxima = 1
            
            # Registrar actividad del día
            cursor.execute("""
                INSERT INTO user_streaks (user_id, fecha, tarea_completada)
                VALUES (%s, %s, TRUE)
            """, (user_id, fecha_hoy))
            
            # Actualizar o crear estadísticas
            if stats:
                cursor.execute("""
                    UPDATE user_streak_stats 
                    SET racha_actual = %s, racha_maxima = %s, ultima_actividad = %s
                    WHERE user_id = %s
                """, (racha_actual, racha_maxima, fecha_hoy, user_id))
            else:
                cursor.execute("""
                    INSERT INTO user_streak_stats 
                    (user_id, racha_actual, racha_maxima, ultima_actividad)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, racha_actual, racha_maxima, fecha_hoy))
            
            connection.commit()
            
            # Determinar mensaje motivacional
            mensaje = f"¡Felicidades! Llevas {racha_actual} días consecutivos 🔥"
            if racha_actual == racha_maxima and racha_actual > 1:
                mensaje = f"🎉 ¡Nuevo récord! {racha_actual} días consecutivos 🔥"
            elif racha_actual == 7:
                mensaje = f"🌟 ¡Una semana completa! {racha_actual} días 🔥"
            elif racha_actual == 30:
                mensaje = f"🏆 ¡Un mes entero! {racha_actual} días 🔥"
            
            return jsonify({
                'success': True,
                'racha_actual': racha_actual,
                'racha_maxima': racha_maxima,
                'mensaje': mensaje
            }), 200
            
    except Exception as e:
        print(f"Error al completar tarea de racha: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/streak/verificar-hoy/<int:user_id>', methods=['GET'])
def verificar_tarea_hoy(user_id):
    """Verifica si el usuario ya completó su tarea hoy"""
    try:
        fecha_hoy = date.today()
        
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM user_streaks 
                WHERE user_id = %s AND fecha = %s
            """, (user_id, fecha_hoy))
            tarea_hoy = cursor.fetchone()
            
            return jsonify({
                'success': True,
                'completada_hoy': tarea_hoy is not None
            }), 200
            
    except Exception as e:
        print(f"Error al verificar tarea de hoy: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/api/streak/historial/<int:user_id>', methods=['GET'])
def obtener_historial_racha(user_id):
    """Obtiene el historial de los últimos 30 días"""
    try:
        dias = int(request.args.get('dias', 30))
        
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT fecha, tarea_completada 
                FROM user_streaks 
                WHERE user_id = %s 
                  AND fecha >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                ORDER BY fecha DESC
            """, (user_id, dias))
            historial = cursor.fetchall()
            
            # Formatear fechas
            for item in historial:
                item['fecha'] = item['fecha'].strftime('%Y-%m-%d')
            
            return jsonify({
                'success': True,
                'historial': historial,
                'total_dias': len(historial)
            }), 200
            
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500
    finally:
        if 'connection' in locals():
            connection.close()








# ==================== MAIN ====================
if __name__ == '__main__':
    register_foto_routes(app)
    print("🚀 Iniciando servidor Flask...")
    # Usar el puerto de la variable de entorno PORT (Railway lo requiere)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False en producción