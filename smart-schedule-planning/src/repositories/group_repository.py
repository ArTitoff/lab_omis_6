from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.interfaces import IGroupRepository
from src.domain.entities import Group

class GroupRepository(IGroupRepository):
    def __init__(self):
        self._groups: Dict[int, Group] = {}
        self._next_id = 1
    
    def add(self, group: Group) -> Group:
        group.id = self._next_id
        group.created_at = datetime.now()
        self._groups[group.id] = group
        self._next_id += 1
        return group
    
    def get_by_id(self, group_id: int) -> Optional[Group]:
        return self._groups.get(group_id)
    
    def get_all(self) -> List[Group]:
        return list(self._groups.values())
    
    def get_user_groups(self, user_id: int) -> List[Group]:
        return [group for group in self._groups.values() 
                if group.organizer_id == user_id or 
                any(member.id == user_id for member in group.members)]
    
    def update(self, group: Group) -> Group:
        if group.id in self._groups:
            self._groups[group.id] = group
        return group
    
    def delete(self, group_id: int) -> bool:
        if group_id in self._groups:
            del self._groups[group_id]
            return True
        return False
