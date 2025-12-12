import re
from datetime import datetime
from typing import Optional

def validate_email(email: str) -> bool:
    """Проверяет валидность email адреса."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """Проверяет валидность пароля."""
    return len(password) >= 6

def validate_date(date_str: str, format: str = '%Y-%m-%d') -> Optional[datetime]:
    """Проверяет и парсит дату из строки."""
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        return None

def validate_time(time_str: str) -> Optional[datetime]:
    """Проверяет и парсит время из строки."""
    try:
        return datetime.strptime(time_str, '%H:%M')
    except ValueError:
        return None

def validate_duration(duration: int) -> bool:
    """Проверяет валидность продолжительности (в минутах)."""
    return 0 < duration <= 24 * 60  # Максимум 24 часа
