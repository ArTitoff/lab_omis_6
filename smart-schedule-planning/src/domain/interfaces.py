from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

# Интерфейсы репозиториев
class IUserRepository(ABC):
    @abstractmethod
    def add(self, user: 'User') -> 'User':
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional['User']:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional['User']:
        pass
    
    @abstractmethod
    def get_all(self) -> List['User']:
        pass
    
    @abstractmethod
    def update(self, user: 'User') -> 'User':
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

class IGroupRepository(ABC):
    @abstractmethod
    def add(self, group: 'Group') -> 'Group':
        pass
    
    @abstractmethod
    def get_by_id(self, group_id: int) -> Optional['Group']:
        pass
    
    @abstractmethod
    def get_all(self) -> List['Group']:
        pass
    
    @abstractmethod
    def get_user_groups(self, user_id: int) -> List['Group']:
        pass
    
    @abstractmethod
    def update(self, group: 'Group') -> 'Group':
        pass
    
    @abstractmethod
    def delete(self, group_id: int) -> bool:
        pass

class IScheduleRepository(ABC):
    @abstractmethod
    def add(self, schedule: 'Schedule') -> 'Schedule':
        pass
    
    @abstractmethod
    def get_by_id(self, schedule_id: int) -> Optional['Schedule']:
        pass
    
    @abstractmethod
    def get_user_schedules(self, user_id: int) -> List['Schedule']:
        pass
    
    @abstractmethod
    def get_group_schedule(self, group_id: int) -> Optional['Schedule']:
        pass
    
    @abstractmethod
    def update(self, schedule: 'Schedule') -> 'Schedule':
        pass
    
    @abstractmethod
    def delete(self, schedule_id: int) -> bool:
        pass

class ITaskRepository(ABC):
    @abstractmethod
    def add(self, task: 'Task') -> 'Task':
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional['Task']:
        pass
    
    @abstractmethod
    def get_user_tasks(self, user_id: int) -> List['Task']:
        pass
    
    @abstractmethod
    def get_schedule_tasks(self, schedule_id: int) -> List['Task']:
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List['Task']:
        pass
    
    @abstractmethod
    def update(self, task: 'Task') -> 'Task':
        pass
    
    @abstractmethod
    def delete(self, task_id: int) -> bool:
        pass

class IEventRepository(ABC):
    @abstractmethod
    def add(self, event: 'Event') -> 'Event':
        pass
    
    @abstractmethod
    def get_by_id(self, event_id: int) -> Optional['Event']:
        pass
    
    @abstractmethod
    def get_user_events(self, user_id: int) -> List['Event']:
        pass
    
    @abstractmethod
    def get_shared_events(self) -> List['Event']:
        pass
    
    @abstractmethod
    def update(self, event: 'Event') -> 'Event':
        pass
    
    @abstractmethod
    def delete(self, event_id: int) -> bool:
        pass

class IMessageRepository(ABC):
    @abstractmethod
    def add(self, message: 'Message') -> 'Message':
        pass
    
    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional['Message']:
        pass
    
    @abstractmethod
    def get_user_messages(self, user_id: int) -> List['Message']:
        pass
    
    @abstractmethod
    def get_unread_messages(self, user_id: int) -> List['Message']:
        pass
    
    @abstractmethod
    def mark_as_read(self, message_id: int) -> bool:
        pass
    
    @abstractmethod
    def delete(self, message_id: int) -> bool:
        pass

# Интерфейсы сервисов
class IUserService(ABC):
    @abstractmethod
    def authenticate(self, email: str, password: str) -> Optional['User']:
        pass
    
    @abstractmethod
    def register(self, name: str, email: str, password: str, role: str) -> 'User':
        pass
    
    @abstractmethod
    def update_profile(self, user_id: int, **kwargs) -> 'User':
        pass
    
    @abstractmethod
    def create_group(self, user_id: int, name: str, description: str) -> 'Group':
        pass

class ITaskService(ABC):
    @abstractmethod
    def create_task(self, user_id: int, title: str, description: str, deadline: datetime,
                   duration: int, priority: str, schedule_id: Optional[int] = None) -> 'Task':
        pass
    
    @abstractmethod
    def update_task(self, task_id: int, **kwargs) -> 'Task':
        pass
    
    @abstractmethod
    def complete_task(self, task_id: int) -> 'Task':
        pass
    
    @abstractmethod
    def get_user_tasks(self, user_id: int, status: Optional[str] = None) -> List['Task']:
        pass

class IScheduleService(ABC):
    @abstractmethod
    def create_schedule(self, user_id: int, title: str, is_shared: bool = False) -> 'Schedule':
        pass
    
    @abstractmethod
    def add_task_to_schedule(self, schedule_id: int, task_id: int) -> bool:
        pass
    
    @abstractmethod
    def remove_task_from_schedule(self, schedule_id: int, task_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_schedule_with_tasks(self, schedule_id: int) -> Dict[str, Any]:
        pass

class ICalendarService(ABC):
    @abstractmethod
    def get_day_view(self, user_id: int, date: datetime) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_week_view(self, user_id: int, start_date: datetime) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_month_view(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def generate_occupancy_chart(self, user_id: int, start_date: datetime, 
                               end_date: datetime) -> Dict[str, Any]:
        pass

class IPlanningService(ABC):
    @abstractmethod
    def find_free_slots(self, user_id: int, duration: int, 
                       start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def check_conflicts(self, user_id: int, start_time: datetime, 
                       end_time: datetime) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def suggest_optimal_time(self, user_id: int, task_duration: int, 
                           priority: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def analyze_group_schedule(self, group_id: int, duration: int) -> List[Dict[str, Any]]:
        pass

class INotificationService(ABC):
    @abstractmethod
    def send_task_reminder(self, task_id: int, hours_before: int) -> bool:
        pass
    
    @abstractmethod
    def send_deadline_notification(self, task_id: int) -> bool:
        pass
    
    @abstractmethod
    def send_schedule_change_notification(self, schedule_id: int, 
                                        user_ids: List[int]) -> bool:
        pass
    
    @abstractmethod
    def get_user_notifications(self, user_id: int) -> List['Message']:
        pass

class IIntegrationService(ABC):
    @abstractmethod
    def export_to_ical(self, user_id: int, start_date: datetime, 
                      end_date: datetime) -> str:
        pass
    
    @abstractmethod
    def export_to_csv(self, user_id: int, start_date: datetime, 
                     end_date: datetime) -> str:
        pass
    
    @abstractmethod
    def import_from_ical(self, user_id: int, ical_content: str) -> bool:
        pass
