# src/services/user_service.py (остается без изменений)
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib
from src.domain.interfaces import IUserService
from src.domain.entities import User, UserRole, Group
from src.repositories import user_repository, group_repository
from src.utils.validators import validate_email, validate_password

class UserService(IUserService):
    def __init__(self):
        pass
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = user_repository.get_by_email(email)
        if user and user.password_hash == self._hash_password(password):
            return user
        return None
    
    def register(self, name: str, email: str, password: str, role: str = "участник") -> User:
        if not validate_email(email):
            raise ValueError("Неверный формат email")
        
        if not validate_password(password):
            raise ValueError("Пароль должен содержать минимум 6 символов")
        
        existing_user = user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")
        
        try:
            user_role = UserRole(role)
        except ValueError:
            user_role = UserRole.PARTICIPANT
        
        user = User(
            id=0,
            name=name,
            email=email,
            password_hash=self._hash_password(password),
            role=user_role,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        saved_user = user_repository.add(user)
        
        print(f"DEBUG [UserService]: Зарегистрирован пользователь ID: {saved_user.id}")
        print(f"DEBUG [UserService]: Всего пользователей: {len(user_repository.get_all())}")
        
        return saved_user
    
    def update_profile(self, user_id: int, **kwargs) -> User:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        if 'name' in kwargs:
            user.name = kwargs['name']
        
        if 'email' in kwargs:
            if not validate_email(kwargs['email']):
                raise ValueError("Неверный формат email")
            existing_user = user_repository.get_by_email(kwargs['email'])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Пользователь с таким email уже существует")
            user.email = kwargs['email']
        
        if 'password' in kwargs:
            if not validate_password(kwargs['password']):
                raise ValueError("Пароль должен содержать минимум 6 символов")
            user.password_hash = self._hash_password(kwargs['password'])
        
        user.updated_at = datetime.now()
        return user_repository.update(user)
    
    def create_group(self, user_id: int, name: str, description: str) -> Group:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        group = Group(
            id=0,
            name=name,
            description=description,
            created_at=datetime.now(),
            organizer_id=user_id,
            members=[user]
        )
        
        return group_repository.add(group)