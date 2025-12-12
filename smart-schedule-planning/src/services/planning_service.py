# src/services/planning_service.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.domain.interfaces import IPlanningService
from src.domain.entities import Task, TaskPriority, Group
from src.repositories import task_repository, user_repository, group_repository


class PlanningService(IPlanningService):
    def __init__(self):
        pass
    
    def find_free_slots(self, user_id: int, duration: int, 
                       start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        tasks = task_repository.get_user_tasks(user_id)
        
        # Фильтруем задачи в заданном диапазоне
        relevant_tasks = []
        for task in tasks:
            if task.start_time and task.end_time:
                if start_date <= task.start_time <= end_date or \
                   start_date <= task.end_time <= end_date or \
                   (task.start_time <= start_date and task.end_time >= end_date):
                    relevant_tasks.append(task)
        
        # Сортируем задачи по времени начала
        relevant_tasks.sort(key=lambda x: x.start_time)
        
        free_slots = []
        current_time = start_date
        
        # Рабочие часы (предполагаем 9:00-18:00)
        work_start_hour = 9
        work_end_hour = 18
        
        while current_time < end_date:
            # Проверяем, рабочий ли это час
            if work_start_hour <= current_time.hour < work_end_hour:
                slot_end = current_time + timedelta(minutes=duration)
                
                # Проверяем конфликты
                has_conflict = False
                for task in relevant_tasks:
                    if task.start_time < slot_end and task.end_time > current_time:
                        has_conflict = True
                        current_time = task.end_time
                        break
                
                if not has_conflict and slot_end <= end_date:
                    free_slots.append({
                        'start_time': current_time.isoformat(),
                        'end_time': slot_end.isoformat(),
                        'duration_minutes': duration
                    })
                    current_time = slot_end
                elif not has_conflict:
                    break
            else:
                # Переходим к следующему рабочему дню
                next_day = current_time + timedelta(days=1)
                current_time = datetime(next_day.year, next_day.month, next_day.day, 
                                       work_start_hour, 0, 0)
        
        return free_slots[:3]  # Возвращаем первые 3 слота
    
    def check_conflicts(self, user_id: int, start_time: datetime, 
                       end_time: datetime) -> List[Dict[str, Any]]:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        tasks = task_repository.get_user_tasks(user_id)
        
        conflicts = []
        for task in tasks:
            if task.start_time and task.end_time:
                if task.start_time < end_time and task.end_time > start_time:
                    conflicts.append({
                        'task_id': task.id,
                        'task_title': task.title,
                        'conflict_start': max(task.start_time, start_time).isoformat(),
                        'conflict_end': min(task.end_time, end_time).isoformat(),
                        'duration': (min(task.end_time, end_time) - 
                                    max(task.start_time, start_time)).total_seconds() / 60
                    })
        
        return conflicts
    
    
    def analyze_group_schedule(self, group_id: int, duration: int) -> List[Dict[str, Any]]:
        group = group_repository.get_by_id(group_id)
        if not group:
            raise ValueError("Группа не найдена")
        
        common_slots = []
        
        # Простой алгоритм поиска общего времени
        now = datetime.now()
        for day_offset in [0, 1, 2]:
            for hour in [10, 14, 16]:  # 10:00, 14:00, 16:00
                start_time = datetime(now.year, now.month, now.day + day_offset, 
                                    hour, 0, 0)
                end_time = start_time + timedelta(minutes=duration)
                
                # Проверяем доступность для всех участников
                available_members = []
                for member in group.members:
                    conflicts = self.check_conflicts(member.id, start_time, end_time)
                    if not conflicts:
                        available_members.append(member.id)
                
                if len(available_members) >= len(group.members) * 0.7:  # 70% участников
                    common_slots.append({
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'available_members': len(available_members),
                        'total_members': len(group.members),
                        'score': int((len(available_members) / len(group.members)) * 100)
                    })
            
            if len(common_slots) >= 3:
                break
        
        return common_slots[:3]
    

    def suggest_optimal_time(self, user_id: int, task_duration: int, 
                           priority: str) -> List[Dict[str, Any]]:
        """Предложить оптимальное время для задачи"""
        print(f"PlanningService.suggest_optimal_time вызван: user_id={user_id}, duration={task_duration}, priority={priority}")
        
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        try:
            task_priority = TaskPriority(priority)
        except ValueError:
            task_priority = TaskPriority.MEDIUM
        
        # Для демонстрации возвращаем фиктивные данные
        now = datetime.now()
        suggestions = []
        
        # Генерируем предложения на ближайшие 3 дня
        for day_offset in [0, 1, 2]:  # сегодня, завтра, послезавтра
            for hour in [10, 14, 16]:  # утреннее, дневное, вечернее время
                start_time = datetime(now.year, now.month, now.day + day_offset, hour, 0, 0)
                end_time = start_time + timedelta(minutes=task_duration)
                
                # Проверяем, что время в будущем
                if start_time > now:
                    suggestions.append({
                        'date': start_time.strftime('%Y-%m-%d'),
                        'start_time': start_time.strftime('%H:%M'),
                        'end_time': end_time.strftime('%H:%M'),
                        'duration': task_duration,
                        'score': 90 - day_offset * 10,  # чем раньше, тем лучше
                        'reason': 'Оптимальное время на основе продуктивности'
                    })
        
        # Если нет предложений (например, если все времена в прошлом)
        if not suggestions:
            tomorrow = datetime(now.year, now.month, now.day + 1, 14, 0, 0)
            suggestions.append({
                'date': tomorrow.strftime('%Y-%m-%d'),
                'start_time': '14:00',
                'end_time': (tomorrow + timedelta(minutes=task_duration)).strftime('%H:%M'),
                'duration': task_duration,
                'score': 80,
                'reason': 'Запасной вариант на завтра'
            })
        
        return suggestions[:3]  # Возвращаем максимум 3 предложения
    
    def create_collaborative_group(self, user_id: int, name: str, description: str = "", 
                                   is_public: bool = False, max_members: int = 10) -> Dict[str, Any]:
        """Создать группу для совместной работы"""
        from src.repositories import group_repository, user_repository
        
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Создаем группу
        group = group_repository.Group(
            id=0,
            name=name,
            description=description,
            created_at=datetime.now(),
            organizer_id=user_id,
            members=[user],
            is_public=is_public,
            max_members=max_members
        )
        
        # Создаем расписание для группы
        from src.services.schedule_service import ScheduleService
        schedule_service = ScheduleService()
        schedule = schedule_service.create_schedule(
            user_id=user_id,
            title=f"Расписание группы '{name}'",
            is_shared=True
        )
        
        group.schedule = schedule
        
        saved_group = group_repository.add(group)
        
        return {
            'group': saved_group.to_dict(),
            'schedule': schedule.to_dict(),
            'message': 'Группа успешно создана'
        }
    
    def join_group(self, user_id: int, group_id: int) -> Dict[str, Any]:
        """Присоединиться к группе"""
        from src.repositories import group_repository, user_repository
        
        group = group_repository.get_by_id(group_id)
        if not group:
            raise ValueError("Группа не найдена")
        
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Проверяем ограничения
        if len(group.members) >= group.max_members:
            raise ValueError(f"Группа переполнена (максимум {group.max_members} участников)")
        
        # Проверяем, не состоит ли уже пользователь в группе
        if any(member.id == user_id for member in group.members):
            raise ValueError("Вы уже состоите в этой группе")
        
        # Добавляем пользователя
        group.members.append(user)
        group_repository.update(group)
        
        return {
            'group': group.to_dict(),
            'user': user.to_dict(),
            'message': f'Вы присоединились к группе "{group.name}"'
        }
    
    def leave_group(self, user_id: int, group_id: int) -> Dict[str, Any]:
        """Покинуть группу"""
        from src.repositories import group_repository
        
        group = group_repository.get_by_id(group_id)
        if not group:
            raise ValueError("Группа не найдена")
        
        # Нельзя покинуть группу, если ты организатор
        if group.organizer_id == user_id:
            raise ValueError("Организатор не может покинуть группу. Передайте управление другому участнику.")
        
        # Удаляем пользователя из участников
        group.members = [member for member in group.members if member.id != user_id]
        group_repository.update(group)
        
        return {
            'group': group.to_dict(),
            'message': f'Вы покинули группу "{group.name}"'
        }
    
    def find_common_slots(self, group_id: int, duration: int) -> List[Dict[str, Any]]:
        """Найти общее свободное время для группы"""
        from src.repositories import group_repository
        
        group = group_repository.get_by_id(group_id)
        if not group:
            raise ValueError("Группа не найдена")
        
        if len(group.members) < 2:
            return []
        
        # Собираем всех задачи всех участников
        all_slots = []
        for member in group.members:
            # Ищем свободные слоты для каждого участника на ближайшие 3 дня
            start_date = datetime.now()
            end_date = start_date + timedelta(days=3)
            
            member_slots = self.find_free_slots(member.id, duration, start_date, end_date)
            
            # Преобразуем времена в datetime для сравнения
            for slot in member_slots:
                try:
                    start_time = datetime.fromisoformat(slot['start_time'])
                    end_time = datetime.fromisoformat(slot['end_time'])
                    
                    all_slots.append({
                        'member_id': member.id,
                        'member_name': member.name,
                        'start_time': start_time,
                        'end_time': end_time
                    })
                except:
                    continue
        
        # Находим пересечения временных слотов
        common_slots = []
        if all_slots:
            # Берем времена первого участника как базовые
            first_member_slots = [s for s in all_slots if s['member_id'] == group.members[0].id]
            
            for base_slot in first_member_slots:
                start_time = base_slot['start_time']
                end_time = base_slot['end_time']
                
                # Проверяем, доступно ли это время для других участников
                available_for_all = True
                for member in group.members[1:]:
                    member_available = False
                    member_slots = [s for s in all_slots if s['member_id'] == member.id]
                    
                    for slot in member_slots:
                        if (slot['start_time'] <= start_time and slot['end_time'] >= end_time) or \
                           (abs((slot['start_time'] - start_time).total_seconds()) < 3600):  # в пределах часа
                            member_available = True
                            break
                    
                    if not member_available:
                        available_for_all = False
                        break
                
                if available_for_all:
                    common_slots.append({
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'date': start_time.strftime('%Y-%m-%d'),
                        'time': start_time.strftime('%H:%M'),
                        'duration': duration,
                        'available_members': len(group.members),
                        'score': 100
                    })
        
        # Если нет точных совпадений, ищем хотя бы для 70% участников
        if not common_slots:
            for base_slot in first_member_slots:
                start_time = base_slot['start_time']
                end_time = base_slot['end_time']
                
                available_count = 1  # Первый участник точно доступен
                for member in group.members[1:]:
                    member_slots = [s for s in all_slots if s['member_id'] == member.id]
                    
                    for slot in member_slots:
                        if (slot['start_time'] <= start_time and slot['end_time'] >= end_time) or \
                           (abs((slot['start_time'] - start_time).total_seconds()) < 7200):  # в пределах 2 часов
                            available_count += 1
                            break
                
                if available_count >= len(group.members) * 0.7:  # Доступно для 70% участников
                    common_slots.append({
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'date': start_time.strftime('%Y-%m-%d'),
                        'time': start_time.strftime('%H:%M'),
                        'duration': duration,
                        'available_members': available_count,
                        'total_members': len(group.members),
                        'score': int((available_count / len(group.members)) * 100)
                    })
        
        return common_slots[:5]  # Возвращаем максимум 5 вариантов
    
    def get_user_groups(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все группы пользователя"""
        from src.repositories import group_repository
        
        all_groups = group_repository.get_all()
        user_groups = []
        
        for group in all_groups:
            if any(member.id == user_id for member in group.members):
                user_groups.append(group.to_dict())
        
        return user_groups
    
    def create_group(self, user_id: int, name: str, description: str = "", 
                     is_public: bool = False) -> Dict[str, Any]:
        """Создать группу для совместной работы"""
        from src.services.schedule_service import ScheduleService
        
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Создаем группу
        group = Group(
            id=0,
            name=name,
            description=description,
            created_at=datetime.now(),
            organizer_id=user_id,
            members=[user],
            is_public=is_public,
            invite_code=f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}" if is_public else None
        )
        
        # Создаем расписание для группы
        schedule_service = ScheduleService()
        schedule = schedule_service.create_schedule(
            user_id=user_id,
            title=f"Расписание группы '{name}'",
            is_shared=True
        )
        
        group.schedule = schedule
        saved_group = group_repository.add(group)
        
        return {
            'group': saved_group.to_dict(),
            'schedule': schedule.to_dict(),
            'message': 'Группа успешно создана'
        }