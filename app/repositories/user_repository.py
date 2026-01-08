"""
User Repository - Sistema POS O'Data
===================================
Repository específico para usuarios con operaciones especializadas.
"""

from typing import Optional, List, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.exceptions import ValidationError, NotFoundError

class UserRepository(BaseRepository[User]):
    """Repository para usuarios con operaciones especializadas"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        return User.query.filter_by(username=username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return User.query.filter_by(email=email).first()
    
    def get_by_username_or_404(self, username: str) -> User:
        """Obtener usuario por username o lanzar 404"""
        user = self.get_by_username(username)
        if not user:
            raise NotFoundError("User", username)
        return user
    
    def get_by_email_or_404(self, email: str) -> User:
        """Obtener usuario por email o lanzar 404"""
        user = self.get_by_email(email)
        if not user:
            raise NotFoundError("User", email)
        return user
    
    def create_user(self, username: str, email: str, password: str, **kwargs) -> User:
        """Crear usuario con validaciones específicas"""
        # Validar unicidad
        if self.get_by_username(username):
            raise ValidationError(f"Username '{username}' already exists", field="username")
        
        if self.get_by_email(email):
            raise ValidationError(f"Email '{email}' already exists", field="email")
        
        # Validar formato de email
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValidationError("Invalid email format", field="email")
        
        # Validar longitud de username
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long", field="username")
        
        return self.create(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = self.get_by_username(username)
        if user and user.check_password(password) and user.is_active:
            user.update_last_login()
            return user
        return None
    
    def get_active_users(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener usuarios activos"""
        return self.get_all(page=page, per_page=per_page, is_active=True)
    
    def get_by_role(self, role: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener usuarios por rol"""
        return self.get_all(page=page, per_page=per_page, role=role)
    
    def search_users(self, search_term: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Buscar usuarios en múltiples campos"""
        search_fields = ['username', 'email', 'first_name', 'last_name']
        return self.search(search_term, search_fields, page, per_page)
    
    def update_password(self, user_id: int, new_password: str) -> User:
        """Actualizar contraseña de usuario"""
        user = self.get_by_id_or_404(user_id)
        user.set_password(new_password)
        self.db.session.commit()
        return user
    
    def deactivate_user(self, user_id: int) -> User:
        """Desactivar usuario"""
        return self.update(user_id, is_active=False)
    
    def activate_user(self, user_id: int) -> User:
        """Activar usuario"""
        return self.update(user_id, is_active=True)
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de usuarios"""
        total_users = self.count()
        active_users = self.count(is_active=True)
        admin_users = self.count(role='admin')
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'admin_users': admin_users,
            'regular_users': total_users - admin_users
        }
