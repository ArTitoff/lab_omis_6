# src/repositories/__init__.py
from .user_repository import UserRepository
from .task_repository import TaskRepository
from .event_repository import EventRepository
from .group_repository import GroupRepository
from .schedule_repository import ScheduleRepository
from .message_repository import MessageRepository

# Создаем ЕДИНЫЕ экземпляры репозиториев
user_repository = UserRepository()
task_repository = TaskRepository()
event_repository = EventRepository()
group_repository = GroupRepository()
schedule_repository = ScheduleRepository()
message_repository = MessageRepository()

__all__ = [
    'user_repository',
    'task_repository',
    'event_repository', 
    'group_repository',
    'schedule_repository',
    'message_repository',
    'UserRepository',
    'TaskRepository',
    'EventRepository',
    'GroupRepository', 
    'ScheduleRepository',
    'MessageRepository'
]