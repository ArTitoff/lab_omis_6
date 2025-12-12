# src/services/calendar_service.py
from typing import List, Dict, Any
from datetime import datetime, timedelta, date
from calendar import monthrange
from src.repositories import task_repository, event_repository, user_repository

class CalendarService:
    def __init__(self):
        pass
    
    def get_month_view(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """
        Создает данные для отображения календаря месяца
        Возвращает массив из 42 дней (6 недель)
        """
        # Получаем задачи пользователя
        tasks = task_repository.get_user_tasks(user_id)
        events = event_repository.get_user_events(user_id)
        
        # Получаем первый и последний день месяца
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        # Находим понедельник первой недели календаря
        # weekday(): 0=понедельник, 6=воскресенье
        days_from_prev_month = first_day.weekday()  # сколько дней из предыдущего месяца показать
        calendar_start = first_day - timedelta(days=days_from_prev_month)
        
        # Создаем массив из 42 дней (6 недель)
        calendar_days = []
        current_date = calendar_start
        
        for i in range(42):
            # Проверяем, относится ли день к текущему месяцу
            is_current_month = current_date.month == month and current_date.year == year
            
            # Находим задачи на этот день
            day_tasks = []
            for task in tasks:
                if task.start_time and task.start_time.date() == current_date:
                    day_tasks.append({
                        'id': task.id,
                        'title': task.title,
                        'priority': task.priority,
                        'start_time': task.start_time.isoformat() if task.start_time else None,
                        'end_time': task.end_time.isoformat() if task.end_time else None,
                    })
            
            # Находим события на этот день
            day_events = []
            for event in events:
                if event.start_time.date() == current_date:
                    day_events.append({
                        'id': event.id,
                        'title': event.title,
                        'start_time': event.start_time.isoformat(),
                        'end_time': event.end_time.isoformat(),
                    })
            
            calendar_days.append({
                'date': current_date.isoformat(),
                'day': current_date.day,
                'month': current_date.month,
                'year': current_date.year,
                'is_current_month': is_current_month,
                'tasks': day_tasks,
                'events': day_events,
                'task_count': len(day_tasks),
                'event_count': len(day_events),
                'is_today': current_date == date.today()
            })
            
            current_date += timedelta(days=1)
        
        return {
            'year': year,
            'month': month,
            'month_name': first_day.strftime('%B'),
            'days': calendar_days,
            'first_day': first_day.isoformat(),
            'last_day': last_day.isoformat(),
            'today': date.today().isoformat()
        }
    
    def get_day_view(self, user_id: int, date_obj: datetime) -> Dict[str, Any]:
        """Данные для просмотра дня"""
        tasks = task_repository.get_user_tasks(user_id)
        events = event_repository.get_user_events(user_id)
        
        day_tasks = []
        day_events = []
        
        for task in tasks:
            if task.start_time and task.start_time.date() == date_obj.date():
                day_tasks.append(task.to_dict())
        
        for event in events:
            if event.start_time.date() == date_obj.date():
                day_events.append(event.to_dict())
        
        return {
            'date': date_obj.isoformat(),
            'tasks': day_tasks,
            'events': day_events,
            'total_tasks': len(day_tasks),
            'total_events': len(day_events)
        }