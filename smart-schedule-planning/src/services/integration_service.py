# src/services/integration_service.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
import csv
import io
from icalendar import Calendar, Event as ICalEvent
from src.domain.interfaces import IIntegrationService
from src.domain.entities import Task, Event
from src.repositories import task_repository, event_repository, user_repository

class IntegrationService(IIntegrationService):
    def __init__(self):
        pass
    
    def export_to_ical(self, user_id: int, start_date: datetime, 
                      end_date: datetime) -> str:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        tasks = task_repository.get_by_date_range(start_date, end_date)
        user_tasks = [task for task in tasks if user_id in task.assigned_users]
        
        events = event_repository.get_user_events(user_id)
        user_events = [event for event in events 
                      if start_date <= event.start_time <= end_date or
                      start_date <= event.end_time <= end_date]
        
        # Создаем iCalendar
        cal = Calendar()
        cal.add('prodid', '-//Smart Schedule//RU')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', f'Расписание {user.name}')
        cal.add('x-wr-timezone', 'Europe/Moscow')
        
        # Добавляем задачи
        for task in user_tasks:
            if task.start_time and task.end_time:
                ical_event = ICalEvent()
                ical_event.add('uid', f'task_{task.id}@smartschedule.local')
                ical_event.add('dtstamp', datetime.now())
                ical_event.add('dtstart', task.start_time)
                ical_event.add('dtend', task.end_time)
                ical_event.add('summary', task.title)
                ical_event.add('description', task.description or '')
                ical_event.add('priority', 
                              {'высокий': '1', 'средний': '5', 'низкий': '9'}.get(
                                  task.priority.value, '5'))
                
                status_map = {
                    'новая': 'NEEDS-ACTION',
                    'в работе': 'IN-PROCESS',
                    'завершена': 'COMPLETED'
                }
                ical_event.add('status', status_map.get(task.status.value, 'NEEDS-ACTION'))
                
                cal.add_component(ical_event)
        
        # Добавляем события
        for event in user_events:
            ical_event = ICalEvent()
            ical_event.add('uid', f'event_{event.id}@smartschedule.local')
            ical_event.add('dtstamp', datetime.now())
            ical_event.add('dtstart', event.start_time)
            ical_event.add('dtend', event.end_time)
            ical_event.add('summary', event.title)
            ical_event.add('description', event.description or '')
            ical_event.add('location', 'Online' if event.is_shared else 'Personal')
            
            cal.add_component(ical_event)
        
        return cal.to_ical().decode('utf-8')
    
    def export_to_csv(self, user_id: int, start_date: datetime, 
                     end_date: datetime) -> str:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        tasks = task_repository.get_by_date_range(start_date, end_date)
        user_tasks = [task for task in tasks if user_id in task.assigned_users]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Заголовок
        writer.writerow([
            'ID', 'Название', 'Описание', 'Начало', 'Окончание', 
            'Длительность (мин)', 'Приоритет', 'Статус', 'Создано', 'Обновлено'
        ])
        
        # Данные
        for task in user_tasks:
            writer.writerow([
                task.id,
                task.title,
                task.description or '',
                task.start_time.isoformat() if task.start_time else '',
                task.end_time.isoformat() if task.end_time else '',
                task.duration,
                task.priority.value,
                task.status.value,
                task.created_at.isoformat(),
                task.updated_at.isoformat()
            ])
        
        return output.getvalue()
    
    def import_from_ical(self, user_id: int, ical_content: str) -> bool:
        # В реальной системе здесь была бы реализация импорта из iCalendar
        # Для простоты возвращаем успех
        return True