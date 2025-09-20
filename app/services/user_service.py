"""
User Service - Sistema POS O'Data
================================
Servicio de usuarios con lógica de negocio enterprise.
"""

from typing import Dict, Any, Optional, List
from app.repositories.user_repository import UserRepository
from app.exceptions import ValidationError, AuthenticationError, AuthorizationError
from app import db

class UserService:
    """Servicio de usuarios con lógica de negocio enterprise"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo usuario"""
        return self.user_repository.create_user(**user_data).to_dict()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuario"""
        user = self.user_repository.authenticate(username, password)
        if user:
            return user.to_dict()
        return None
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Obtener usuario por ID"""
        user = self.user_repository.get_by_id_or_404(user_id)
        return user.to_dict()
    
    def get_users(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Obtener usuarios con filtros"""
        result = self.user_repository.get_all(page=page, per_page=per_page, **filters)
        return {
            'users': [user.to_dict() for user in result['items']],
            'pagination': result['pagination']
        }
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar usuario"""
        user = self.user_repository.update(user_id, **user_data)
        return user.to_dict()
    
    def delete_user(self, user_id: int) -> bool:
        """Eliminar usuario (soft delete)"""
        return self.user_repository.deactivate_user(user_id)
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de usuarios"""
        return self.user_repository.get_user_stats()

    def get_user_by_username(self, username: str):
        """Obtener usuario por username (objeto ORM)"""
        return self.user_repository.get_by_username(username)