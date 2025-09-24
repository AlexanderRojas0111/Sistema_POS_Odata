from app.models import User
from app.core.database import db
from app.schemas import UserCreate, UserUpdate
from app.utils.security import hash_password
from typing import List, Optional

class UsersCRUD:
    """Clase para operaciones CRUD de usuarios"""
    
    def get_all(self) -> List[User]:
        """Obtener todos los usuarios"""
        return User.query.all()
    
    def get(self, user_id: int) -> Optional[User]:
        """Obtener un usuario específico"""
        return User.query.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return User.query.filter_by(email=email).first()
    
    def create(self, user_data: UserCreate) -> User:
        """Crear un nuevo usuario"""
        user = User(
            username=user_data.username,
            email=user_data.email,
            role=user_data.role,
            is_active=user_data.is_active
        )
        user.set_password(user_data.password)
        
        db.session.add(user)
        return user
    
    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Actualizar un usuario"""
        user = self.get(user_id)
        if not user:
            return None
        
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.role is not None:
            user.role = user_data.role
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        return user
    
    def delete(self, user_id: int) -> bool:
        """Eliminar un usuario"""
        user = self.get(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        return True

# Instancia global del CRUD
users_crud = UsersCRUD() 