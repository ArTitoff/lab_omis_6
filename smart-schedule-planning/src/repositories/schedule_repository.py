from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.interfaces import IScheduleRepository
from src.domain.entities import Schedule

class ScheduleRepository(IScheduleRepository):
    def __init__(self):
        self._schedules: Dict[int, Schedule] = {}
        self._next_id = 1
    
    def add(self, schedule: Schedule) -> Schedule:
        schedule.id = self._next_id
        schedule.created_at = datetime.now()
        self._schedules[schedule.id] = schedule
        self._next_id += 1
        return schedule
    
    def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        return self._schedules.get(schedule_id)
    
    def get_user_schedules(self, user_id: int) -> List[Schedule]:
        return [schedule for schedule in self._schedules.values() 
                if schedule.owner_id == user_id or schedule.is_shared]
    
    def get_group_schedule(self, group_id: int) -> Optional[Schedule]:
        for schedule in self._schedules.values():
            if schedule.group_id == group_id:
                return schedule
        return None
    
    def update(self, schedule: Schedule) -> Schedule:
        if schedule.id in self._schedules:
            self._schedules[schedule.id] = schedule
        return schedule
    
    def delete(self, schedule_id: int) -> bool:
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False
