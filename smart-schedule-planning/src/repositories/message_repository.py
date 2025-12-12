from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.interfaces import IMessageRepository
from src.domain.entities import Message, MessageType

class MessageRepository(IMessageRepository):
    def __init__(self):
        self._messages: Dict[int, Message] = {}
        self._next_id = 1
    
    def add(self, message: Message) -> Message:
        message.id = self._next_id
        message.sent_at = datetime.now()
        self._messages[message.id] = message
        self._next_id += 1
        return message
    
    def get_by_id(self, message_id: int) -> Optional[Message]:
        return self._messages.get(message_id)
    
    def get_user_messages(self, user_id: int) -> List[Message]:
        return [message for message in self._messages.values() 
                if message.user_id == user_id]
    
    def get_unread_messages(self, user_id: int) -> List[Message]:
        return [message for message in self._messages.values() 
                if message.user_id == user_id and not message.is_read]
    
    def mark_as_read(self, message_id: int) -> bool:
        if message_id in self._messages:
            self._messages[message_id].is_read = True
            return True
        return False
    
    def delete(self, message_id: int) -> bool:
        if message_id in self._messages:
            del self._messages[message_id]
            return True
        return False
