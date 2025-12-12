# src/services/task_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.domain.interfaces import ITaskService
from src.domain.entities import Task, TaskPriority, TaskStatus
from src.repositories import task_repository, user_repository

class TaskService(ITaskService):
    def __init__(self):
        pass
    
    def create_task(self, user_id: int, title: str, description: str, deadline: datetime,
                   duration: int, priority: str, schedule_id: Optional[int] = None) -> Task:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        try:
            task_priority = TaskPriority(priority)
        except ValueError:
            task_priority = TaskPriority.MEDIUM
        
        task = Task(
            id=0,
            title=title,
            description=description,
            deadline=deadline,
            start_time=None,
            end_time=None,
            duration=duration,
            priority=task_priority,
            status=TaskStatus.NEW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            creator_id=user_id,
            schedule_id=schedule_id,
            assigned_users=[user_id]
        )
        
        return task_repository.add(task)
    
    def update_task(self, task_id: int, **kwargs) -> Task:
        task = task_repository.get_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")
        
        if 'title' in kwargs:
            task.title = kwargs['title']
        
        if 'description' in kwargs:
            task.description = kwargs['description']
        
        if 'deadline' in kwargs:
            task.deadline = kwargs['deadline']
        
        if 'duration' in kwargs:
            task.duration = kwargs['duration']
        
        if 'priority' in kwargs:
            try:
                task.priority = TaskPriority(kwargs['priority'])
            except ValueError:
                pass
        
        if 'status' in kwargs:
            try:
                task.status = TaskStatus(kwargs['status'])
            except ValueError:
                pass
        
        if 'start_time' in kwargs:
            task.start_time = kwargs['start_time']
        
        if 'end_time' in kwargs:
            task.end_time = kwargs['end_time']
        
        task.updated_at = datetime.now()
        return task_repository.update(task)
    
    def complete_task(self, task_id: int) -> Task:
        task = task_repository.get_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")
        
        task.status = TaskStatus.COMPLETED
        task.end_time = datetime.now()
        if not task.start_time:
            task.start_time = datetime.now()
        
        task.updated_at = datetime.now()
        return task_repository.update(task)
    
    def get_user_tasks(self, user_id: int, status: Optional[str] = None) -> List[Task]:
        tasks = task_repository.get_user_tasks(user_id)
        
        if status:
            try:
                task_status = TaskStatus(status)
                tasks = [task for task in tasks if task.status == task_status]
            except ValueError:
                pass
        
        return tasks
    
    def create_task_with_time(self, user_id: int, title: str, description: str,
                         deadline: datetime, start_time: datetime, end_time: datetime,
                         duration: int, priority: str, schedule_id: Optional[int] = None) -> Task:
        """Создать задачу с указанием времени начала и окончания"""
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        try:
            task_priority = TaskPriority(priority)
        except ValueError:
            task_priority = TaskPriority.MEDIUM
        
        task = Task(
            id=0,
            title=title,
            description=description,
            deadline=deadline,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            priority=task_priority,
            status=TaskStatus.NEW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            creator_id=user_id,
            schedule_id=schedule_id,
            assigned_users=[user_id]
        )
        
        return task_repository.add(task)