from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.interfaces import ITaskRepository
from src.domain.entities import Task, TaskPriority, TaskStatus

class TaskRepository(ITaskRepository):
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
    
    def add(self, task: Task) -> Task:
        task.id = self._next_id
        task.created_at = datetime.now()
        task.updated_at = datetime.now()
        self._tasks[task.id] = task
        self._next_id += 1
        return task
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)
    
    def get_user_tasks(self, user_id: int) -> List[Task]:
        return [task for task in self._tasks.values() 
                if task.creator_id == user_id or user_id in task.assigned_users]
    
    def get_schedule_tasks(self, schedule_id: int) -> List[Task]:
        return [task for task in self._tasks.values() 
                if task.schedule_id == schedule_id]
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        result = []
        for task in self._tasks.values():
            if task.start_time and task.end_time:
                if start_date <= task.start_time <= end_date or \
                   start_date <= task.end_time <= end_date or \
                   (task.start_time <= start_date and task.end_time >= end_date):
                    result.append(task)
        return result
    
    def update(self, task: Task) -> Task:
        if task.id in self._tasks:
            task.updated_at = datetime.now()
            self._tasks[task.id] = task
        return task
    
    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
