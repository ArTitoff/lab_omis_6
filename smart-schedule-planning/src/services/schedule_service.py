# src/services/schedule_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.interfaces import IScheduleService
from src.domain.entities import Schedule, Task
from src.repositories import schedule_repository, task_repository, user_repository

class ScheduleService(IScheduleService):
    def __init__(self):
        pass
    
    def create_schedule(self, user_id: int, title: str, is_shared: bool = False) -> Schedule:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        schedule = Schedule(
            id=0,
            title=title,
            created_at=datetime.now(),
            owner_id=user_id,
            is_shared=is_shared
        )
        
        return schedule_repository.add(schedule)
    
    def add_task_to_schedule(self, schedule_id: int, task_id: int) -> bool:
        schedule = schedule_repository.get_by_id(schedule_id)
        task = task_repository.get_by_id(task_id)
        
        if not schedule or not task:
            return False
        
        task.schedule_id = schedule_id
        task_repository.update(task)
        
        return True
    
    def remove_task_from_schedule(self, schedule_id: int, task_id: int) -> bool:
        schedule = schedule_repository.get_by_id(schedule_id)
        task = task_repository.get_by_id(task_id)
        
        if not schedule or not task:
            return False
        
        task.schedule_id = None
        task_repository.update(task)
        
        return True
    
    def get_schedule_with_tasks(self, schedule_id: int) -> Dict[str, Any]:
        schedule = schedule_repository.get_by_id(schedule_id)
        if not schedule:
            raise ValueError("Расписание не найдено")
        
        tasks = task_repository.get_schedule_tasks(schedule_id)
        
        return {
            'schedule': schedule.to_dict(),
            'tasks': [task.to_dict() for task in tasks]
        }