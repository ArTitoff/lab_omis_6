# src/utils/filters.py
from datetime import datetime

def datetime_format(value, format='%d.%m.%Y %H:%M'):
    """Фильтр для форматирования даты в шаблонах"""
    if not value:
        return ''
    
    if isinstance(value, str):
        try:
            # Пытаемся разобрать строку даты
            if 'T' in value:
                # ISO формат: 2025-12-11T23:06:14
                if value.endswith('Z'):
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    # Добавляем секунды если их нет
                    if ':' in value and value.count(':') == 1:
                        value = value + ':00'
                    value = datetime.fromisoformat(value)
            else:
                # Простой формат: 2025-12-11
                value = datetime.strptime(value, '%Y-%m-%d')
        except Exception as e:
            print(f"Ошибка форматирования даты {value}: {e}")
            return value
    
    if isinstance(value, datetime):
        return value.strftime(format)
    
    return str(value)

def truncate(text, length=100, suffix='...'):
    """Обрезать текст до указанной длины"""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length] + suffix

def register_filters(app):
    """Регистрация всех фильтров в приложении Flask"""
    app.jinja_env.filters['datetime_format'] = datetime_format
    app.jinja_env.filters['truncate'] = truncate