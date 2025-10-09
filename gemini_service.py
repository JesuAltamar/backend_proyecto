# gemini_service.py
import google.generativeai as genai
from datetime import datetime
from typing import Dict, Optional
import re

class GeminiPsychologistService:
    """Servicio especializado en salud mental con análisis mejorado"""
    
    SYSTEM_PROMPT = """Eres "Alegra", un asistente especializado en bienestar emocional y prevención del suicidio.

DIRECTRICES CRÍTICAS:
1. Detecta señales de riesgo suicida o crisis emocional
2. En crisis: proporciona líneas de ayuda INMEDIATAMENTE
3. Mantén tono empático, cálido y profesional sin juzgar
4. Valida emociones del usuario
5. Recomienda ayuda profesional cuando sea necesario

LÍNEAS DE CRISIS COLOMBIA:
Línea 106: Atención crisis 24/7
Línea 155: Orientación psicológica
WhatsApp: +57 300 754 8933 (Línea Amiga Bogotá)

IMPORTANTE: Nunca sustituyas ayuda profesional. Tu rol es apoyo inicial."""

    # 🔥 CLASIFICACIÓN MEJORADA DE CRISIS
    CRISIS_KEYWORDS_SEVERE = [
        # Intención directa de suicidio
        'me quiero morir', 'quiero morir', 'me voy a matar', 'voy a matarme',
        'me quiero suicidar', 'quiero suicidarme', 'voy a suicidarme',
        'me voy a suicidar', 'acabar con mi vida', 'terminar con mi vida',
        'quitarme la vida', 'ya no quiero vivir', 'mejor muerto', 'mejor muerta',
        'adiós mundo', 'despedida', 'último adiós', 'ya me voy',
        
        # Planes específicos
        'tengo un plan', 'ya tengo cómo', 'sé cómo hacerlo',
        'conseguí pastillas', 'voy a saltar', 'me voy a lanzar',
        
        # Autolesión grave
        'me corté', 'me cortaré', 'me quiero cortar', 'hacerme daño',
    ]
    
    CRISIS_KEYWORDS_MODERATE = [
        'suicidio', 'morir', 'muerte', 'no aguanto más', 'ya no puedo',
        'sin salida', 'no hay esperanza', 'todo perdido', 'desesperado',
        'desesperada', 'no vale la pena', 'estoy solo', 'estoy sola',
        'nadie me entiende', 'me quiero ir', 'quiero desaparecer',
        'autolesión', 'cortarme', 'lastimarme', 'dolor insoportable',
    ]
    
    # Temas comunes para análisis
    TEMAS = {
        'ansiedad': ['ansiedad', 'nervios', 'preocupado', 'estrés', 'pánico', 'angustia'],
        'depresión': ['depresión', 'triste', 'tristeza', 'desmotivado', 'vacío', 'sin ganas'],
        'estrés_laboral': ['trabajo', 'jefe', 'empleo', 'laboral', 'oficina', 'compañeros'],
        'relaciones': ['pareja', 'novio', 'novia', 'familia', 'padres', 'esposo', 'esposa'],
        'autoestima': ['autoestima', 'inseguro', 'insegura', 'no valgo', 'inútil', 'fracaso'],
        'soledad': ['solo', 'sola', 'soledad', 'aislado', 'aislada', 'nadie'],
        'trauma': ['trauma', 'abuso', 'violencia', 'maltrato', 'agresión'],
    }

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        try:
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash-exp',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            self.chat_sessions = {}
            print("✅ Gemini 2.0 Flash Experimental inicializado")
        except Exception as e:
            print(f"❌ Error inicializando Gemini: {e}")
            raise

    def _detect_crisis(self, message: str) -> bool:
        """Detecta si hay crisis"""
        message_lower = message.lower()
        
        for keyword in self.CRISIS_KEYWORDS_SEVERE:
            if keyword in message_lower:
                print(f"🚨 CRISIS SEVERA: '{keyword}'")
                return True
        
        for keyword in self.CRISIS_KEYWORDS_MODERATE:
            if keyword in message_lower:
                print(f"⚠️ Crisis moderada: '{keyword}'")
                return True
        
        return False

    def _get_crisis_level(self, message: str) -> Optional[str]:
        """Determina nivel: 'severe', 'moderate', None"""
        message_lower = message.lower()
        
        for keyword in self.CRISIS_KEYWORDS_SEVERE:
            if keyword in message_lower:
                return 'severe'
        
        for keyword in self.CRISIS_KEYWORDS_MODERATE:
            if keyword in message_lower:
                return 'moderate'
        
        return None

    def _analyze_sentiment(self, message: str) -> str:
        """Analiza sentimiento: positivo, neutral, negativo"""
        message_lower = message.lower()
        
        # Palabras negativas
        negative_words = ['mal', 'triste', 'solo', 'desesperado', 'ansioso', 
                         'deprimido', 'dolor', 'sufro', 'miedo', 'preocupado']
        
        # Palabras positivas
        positive_words = ['bien', 'feliz', 'contento', 'alegre', 'gracias',
                         'mejor', 'esperanza', 'ánimo', 'motivado']
        
        negative_count = sum(1 for word in negative_words if word in message_lower)
        positive_count = sum(1 for word in positive_words if word in message_lower)
        
        if negative_count > positive_count:
            return 'negativo'
        elif positive_count > negative_count:
            return 'positivo'
        else:
            return 'neutral'

    def _detect_theme(self, message: str) -> Optional[str]:
        """Detecta el tema principal del mensaje"""
        message_lower = message.lower()
        
        for tema, keywords in self.TEMAS.items():
            if any(keyword in message_lower for keyword in keywords):
                return tema
        
        return None

    def get_or_create_session(self, session_id: str):
        """Obtiene o crea sesión"""
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = self.model.start_chat(history=[])
            print(f"🆕 Nueva sesión: {session_id}")
        return self.chat_sessions[session_id]

    def send_message(self, message: str, session_id: str = 'default') -> Dict:
        """Envía mensaje con análisis completo"""
        try:
            # Análisis del mensaje
            is_crisis = self._detect_crisis(message)
            crisis_level = self._get_crisis_level(message)
            sentimiento = self._analyze_sentiment(message)
            tema = self._detect_theme(message)
            
            print(f"📩 Mensaje: {message[:100]}...")
            print(f"🚨 Crisis: {is_crisis} | Nivel: {crisis_level}")
            print(f"💭 Sentimiento: {sentimiento} | Tema: {tema}")
            
            chat = self.get_or_create_session(session_id)
            
            if crisis_level == 'severe':
                enhanced_message = f"""{self.SYSTEM_PROMPT}

⚠️ ALERTA CRÍTICA - RIESGO SUICIDA ALTO

Usuario: "{message}"

RESPONDE INMEDIATAMENTE:
1. Validación empática del dolor SIN minimizar
2. Línea 106 (Colombia) - ENFATIZAR disponibilidad 24/7
3. Mensaje de esperanza realista y breve
4. Invitación a seguir hablando

CRÍTICO: Este usuario necesita ayuda profesional AHORA."""
                response = chat.send_message(enhanced_message)
                
            elif crisis_level == 'moderate':
                enhanced_message = f"""{self.SYSTEM_PROMPT}

⚠️ SEÑAL DE ALERTA

Usuario: "{message}"

RESPONDE CON:
1. Empatía profunda
2. Validación de emociones
3. Mencionar Línea 106 disponible
4. Preguntas para entender mejor
5. Apoyo continuo"""
                response = chat.send_message(enhanced_message)
            else:
                prompt = f"{self.SYSTEM_PROMPT}\n\nUsuario: {message}"
                response = chat.send_message(prompt)
            
            print(f"✅ Respuesta: {response.text[:100]}...")
            
            return {
                'message': response.text,
                'is_crisis': is_crisis,
                'crisis_level': crisis_level,
                'sentimiento': sentimiento,
                'tema': tema,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
            if self._detect_crisis(message):
                return {
                    'message': '''Entiendo que estás en un momento muy difícil. Tu vida es valiosa.

🆘 AYUDA INMEDIATA:
📞 Línea 106 (Colombia): Crisis 24/7
📞 Línea 155: Orientación psicológica
📱 WhatsApp: +57 300 754 8933

Por favor, contacta AHORA. Hay personas capacitadas esperando ayudarte.

No estás solo/a. Tu vida importa.''',
                    'is_crisis': True,
                    'crisis_level': 'severe',
                    'sentimiento': 'negativo',
                    'tema': None,
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'message': 'Disculpa, problema técnico. Si necesitas ayuda urgente: Línea 106.',
                'is_crisis': False,
                'crisis_level': None,
                'sentimiento': 'neutral',
                'tema': None,
                'timestamp': datetime.now().isoformat()
            }

    def reset_session(self, session_id: str):
        """Reinicia sesión"""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
            print(f"🔄 Sesión reiniciada: {session_id}")

    def get_active_sessions(self) -> int:
        """Sesiones activas"""
        return len(self.chat_sessions)