from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.interfaces import IEventRepository
from src.domain.entities import Event

class EventRepository(IEventRepository):
    def __init__(self):
        self._events: Dict[int, Event] = {}
        self._next_id = 1
    
    def add(self, event: Event) -> Event:
        event.id = self._next_id
        event.created_at = datetime.now()
        self._events[event.id] = event
        self._next_id += 1
        return event
    
    def get_by_id(self, event_id: int) -> Optional[Event]:
        return self._events.get(event_id)
    
    def get_user_events(self, user_id: int) -> List[Event]:
        return [event for event in self._events.values() 
                if event.owner_id == user_id or user_id in event.participants]
    
    def get_shared_events(self) -> List[Event]:
        return [event for event in self._events.values() if event.is_shared]
    
    def update(self, event: Event) -> Event:
        if event.id in self._events:
            self._events[event.id] = event
        return event
    
    def delete(self, event_id: int) -> bool:
        if event_id in self._events:
            del self._events[event_id]
            return True
        return False
