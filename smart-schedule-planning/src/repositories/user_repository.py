# src/repositories/user_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.interfaces import IUserRepository
from src.domain.entities import User, UserRole
from src.utils.validators import validate_email, validate_password

class UserRepository(IUserRepository):
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id = 1
    
    def add(self, user: User) -> User:
        user.id = self._next_id
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        self._users[user.id] = user
        self._next_id += 1
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def get_all(self) -> List[User]:
        return list(self._users.values())
    
    def update(self, user: User) -> User:
        if user.id in self._users:
            user.updated_at = datetime.now()
            self._users[user.id] = user
        return user
    
    def delete(self, user_id: int) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False