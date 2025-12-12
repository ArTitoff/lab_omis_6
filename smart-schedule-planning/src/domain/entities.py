from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class UserRole(Enum):
    PARTICIPANT = "участник"
    ORGANIZER = "организатор"
    ADMIN = "администратор"

class TaskPriority(Enum):
    LOW = "низкий"
    MEDIUM = "средний"
    HIGH = "высокий"

class TaskStatus(Enum):
    NEW = "новая"
    IN_PROGRESS = "в работе"
    COMPLETED = "завершена"

class MessageType(Enum):
    TASK_REMINDER = "напоминание_о_задаче"
    DEADLINE = "дедлайн"
    SCHEDULE_CHANGE = "изменение_расписания"
    GROUP_INVITE = "приглашение_в_группу"
    SYSTEM = "системное"

@dataclass
class User:
    id: int
    name: str
    email: str
    password_hash: str
    role: UserRole
    created_at: datetime
    updated_at: datetime
    groups: List['Group'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
@dataclass
class Group:
    id: int
    name: str
    description: str
    created_at: datetime
    organizer_id: int
    members: List[User] = field(default_factory=list)
    schedule: Optional['Schedule'] = None
    is_public: bool = False
    invite_code: Optional[str] = None
    max_members: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'organizer_id': self.organizer_id,
            'member_count': len(self.members),
            'created_at': self.created_at.isoformat()
        }

@dataclass
class Schedule:
    id: int
    title: str
    created_at: datetime
    owner_id: int
    is_shared: bool
    group_id: Optional[int] = None
    tasks: List['Task'] = field(default_factory=list)
    events: List['Event'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'owner_id': self.owner_id,
            'group_id': self.group_id,
            'is_shared': self.is_shared,
            'task_count': len(self.tasks),
            'event_count': len(self.events),
            'created_at': self.created_at.isoformat()
        }

@dataclass
class Task:
    id: int
    title: str
    description: str
    deadline: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: int  # в минутах
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    creator_id: int
    schedule_id: Optional[int] = None
    assigned_users: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'priority': self.priority.value,
            'status': self.status.value,
            'creator_id': self.creator_id,
            'schedule_id': self.schedule_id,
            'assigned_users': self.assigned_users,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Event:
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    owner_id: int
    is_shared: bool
    created_at: datetime
    participants: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'owner_id': self.owner_id,
            'is_shared': self.is_shared,
            'participants': self.participants,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class Message:
    id: int
    text: str
    sent_at: datetime
    message_type: MessageType
    user_id: int
    is_read: bool = False
    related_entity_id: Optional[int] = None
    related_entity_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'text': self.text,
            'sent_at': self.sent_at.isoformat(),
            'message_type': self.message_type.value,
            'user_id': self.user_id,
            'is_read': self.is_read,
            'related_entity_id': self.related_entity_id,
            'related_entity_type': self.related_entity_type
        }
