# src/services/notification_service.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.domain.interfaces import INotificationService
from src.domain.entities import Message, MessageType, Task, TaskStatus
from src.repositories import message_repository, task_repository, user_repository

class NotificationService(INotificationService):
    def __init__(self):
        pass
    
    def send_task_reminder(self, task_id: int, hours_before: int) -> bool:
        task = task_repository.get_by_id(task_id)
        if not task or not task.deadline:
            return False
        
        reminder_time = task.deadline - timedelta(hours=hours_before)
        
        for user_id in task.assigned_users:
            message = Message(
                id=0,
                text=f"Напоминание: задача '{task.title}' через {hours_before} часа(ов)",
                sent_at=reminder_time,
                message_type=MessageType.TASK_REMINDER,
                user_id=user_id,
                is_read=False,
                related_entity_id=task_id,
                related_entity_type='task'
            )
            message_repository.add(message)
        
        return True
    
    def send_deadline_notification(self, task_id: int) -> bool:
        task = task_repository.get_by_id(task_id)
        if not task or not task.deadline:
            return False
        
        for user_id in task.assigned_users:
            message = Message(
                id=0,
                text=f"СРОЧНО: дедлайн задачи '{task.title}' сегодня!",
                sent_at=datetime.now(),
                message_type=MessageType.DEADLINE,
                user_id=user_id,
                is_read=False,
                related_entity_id=task_id,
                related_entity_type='task'
            )
            message_repository.add(message)
        
        return True
    
    def send_schedule_change_notification(self, schedule_id: int, 
                                        user_ids: List[int]) -> bool:
        for user_id in user_ids:
            message = Message(
                id=0,
                text=f"Изменения в расписании #{schedule_id}",
                sent_at=datetime.now(),
                message_type=MessageType.SCHEDULE_CHANGE,
                user_id=user_id,
                is_read=False,
                related_entity_id=schedule_id,
                related_entity_type='schedule'
            )
            message_repository.add(message)
        
        return True
    
    def get_user_notifications(self, user_id: int) -> List[Message]:
        user = user_repository.get_by_id(user_id)
        if not user:
            return []
        
        messages = message_repository.get_user_messages(user_id)
        
        # Помечаем сообщения о дедлайнах, если задачи уже выполнены
        for message in messages:
            if (message.message_type == MessageType.DEADLINE and 
                message.related_entity_id and 
                message.related_entity_type == 'task'):
                task = task_repository.get_by_id(message.related_entity_id)
                if task and task.status == TaskStatus.COMPLETED:
                    message.is_read = True
        
        return messages
    
    def check_upcoming_deadlines(self):
        """Проверяет приближающиеся дедлайны и отправляет уведомления"""
        now = datetime.now()
        tasks = task_repository.get_all()
        
        for task in tasks:
            if task.status != TaskStatus.COMPLETED and task.deadline:
                time_to_deadline = task.deadline - now
                
                # Если дедлайн через 24 часа
                if timedelta(hours=0) < time_to_deadline <= timedelta(hours=24):
                    self.send_deadline_notification(task.id)
                
                # Если дедлайн через 1 час
                elif timedelta(minutes=0) < time_to_deadline <= timedelta(hours=1):
                    urgent_message = Message(
                        id=0,
                        text=f"СРОЧНО: дедлайн задачи '{task.title}' через 1 час!",
                        sent_at=datetime.now(),
                        message_type=MessageType.DEADLINE,
                        user_id=task.creator_id,
                        is_read=False,
                        related_entity_id=task.id,
                        related_entity_type='task'
                    )
                    message_repository.add(urgent_message)