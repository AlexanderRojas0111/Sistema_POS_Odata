from abc import ABC, abstractmethod
from typing import Dict, Any, List
import uuid
from datetime import datetime
import json
import redis
from flask import current_app

class BaseAgent(ABC):
    def __init__(self, agent_id: str = None, name: str = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.state: Dict[str, Any] = {}
        self.message_queue: List[Dict[str, Any]] = []
        self.redis_client = redis.from_url(current_app.config['REDIS_URL'])
        
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un mensaje recibido y retorna una respuesta"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una tarea asignada"""
        pass
    
    def send_message(self, to_agent: str, content: Dict[str, Any]) -> None:
        """Envía un mensaje a otro agente usando Redis pub/sub"""
        message = {
            'from_agent': self.agent_id,
            'to_agent': to_agent,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': str(uuid.uuid4())
        }
        # Publicar mensaje en el canal del agente destino
        self.redis_client.publish(f"agent:{to_agent}", json.dumps(message))
        self.message_queue.append(message)
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Actualiza el estado del agente"""
        self.state.update(new_state)
        # Guardar estado en Redis
        self.redis_client.set(
            f"agent_state:{self.agent_id}",
            json.dumps(self.state)
        )
    
    def get_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual del agente"""
        # Intentar obtener estado de Redis
        state_json = self.redis_client.get(f"agent_state:{self.agent_id}")
        if state_json:
            self.state = json.loads(state_json)
        return self.state
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el agente a un diccionario"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'state': self.get_state(),
            'message_queue_size': len(self.message_queue)
        }
    
    def log_activity(self, activity: str, details: Dict[str, Any] = None) -> None:
        """Registra una actividad del agente"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.agent_id,
            'activity': activity,
            'details': details or {}
        }
        # Guardar log en Redis
        self.redis_client.rpush(
            f"agent_log:{self.agent_id}",
            json.dumps(log_entry)
        ) 