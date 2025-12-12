# src/controllers/settings_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from src.services.user_service import UserService
from src.services.integration_service import IntegrationService
# Импортируем ЕДИНЫЕ экземпляры репозиториев
from src.repositories import user_repository, group_repository, task_repository, event_repository
from datetime import datetime, timedelta
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Используем единые экземпляры репозиториев
# Инициализация сервисов
user_service = UserService()  # Без аргументов!
integration_service = IntegrationService()  # Должен быть без аргументов или с едиными репозиториями

@settings_bp.route('/')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('settings.html')

@settings_bp.route('/profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')
    
    try:
        updates = {}
        if name: updates['name'] = name
        if email: updates['email'] = email
        if password: updates['password'] = password
        
        user = user_service.update_profile(user_id, **updates)
        
        # Обновляем данные в сессии
        session['user_name'] = user.name
        session['user_email'] = user.email
        
        return jsonify({'success': True, 'user': user.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@settings_bp.route('/export/ical', methods=['POST'])
def export_ical():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    start_str = request.json.get('start_date')
    end_str = request.json.get('end_date')
    
    try:
        start_date = datetime.fromisoformat(start_str) if start_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_str) if end_str else datetime.now() + timedelta(days=30)
        
        ical_content = integration_service.export_to_ical(user_id, start_date, end_date)
        
        return jsonify({
            'success': True,
            'content': ical_content,
            'filename': f'schedule_{datetime.now().strftime("%Y%m%d_%H%M%S")}.ics'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@settings_bp.route('/export/csv', methods=['POST'])
def export_csv():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    start_str = request.json.get('start_date')
    end_str = request.json.get('end_date')
    
    try:
        start_date = datetime.fromisoformat(start_str) if start_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_str) if end_str else datetime.now() + timedelta(days=30)
        
        csv_content = integration_service.export_to_csv(user_id, start_date, end_date)
        
        return jsonify({
            'success': True,
            'content': csv_content,
            'filename': f'tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400