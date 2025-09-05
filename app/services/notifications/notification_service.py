import io
from flask import Flask
from flask_socketio import SocketIO, emit

class NotificationService:
    """Servicio de notificaciones en tiempo real"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configurar manejadores de WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Manejar conexión de cliente"""
            print(f'Cliente conectado: {request.sid}')
            emit('connected', {'status': 'connected', 'sid': request.sid})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Manejar desconexión de cliente"""
            print(f'Cliente desconectado: {request.sid}')
    
    def send_notification(self, user_id: int, message: str, notification_type: str = 'info'):
        """Enviar notificación a un usuario específico"""
        notification = {
            'id': int(time.time()),
            'message': message,
            'type': notification_type,
            'timestamp': time.time(),
            'read': False
        }
        
        room = f'user_{user_id}'
        self.socketio.emit('notification', notification, room=room)
        return notification

# Instancia global del servicio
notification_service = None

def init_notification_service(app: Flask):
    """Inicializar el servicio de notificaciones"""
    global notification_service
    notification_service = NotificationService(app)
    return notification_service
