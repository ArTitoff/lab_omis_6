# src/controllers/report_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
from src.services.calendar_service import CalendarService
# Импортируем ЕДИНЫЕ экземпляры репозиториев
from src.repositories import task_repository, event_repository, user_repository

report_bp = Blueprint('report', __name__, url_prefix='/reports')

# Используем единые экземпляры и создаем сервис
calendar_service = CalendarService()

@report_bp.route('/')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('reports.html')

@report_bp.route('/productivity')
def productivity():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    try:
        start_date = datetime.fromisoformat(start_str) if start_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_str) if end_str else datetime.now()
        
        data = calendar_service.generate_occupancy_chart(user_id, start_date, end_date)
        
        # Анализ продуктивности
        tasks = task_repository.get_user_tasks(user_id)
        completed = sum(1 for t in tasks if t.status.value == 'завершена')
        in_progress = sum(1 for t in tasks if t.status.value == 'в работе')
        new_tasks = sum(1 for t in tasks if t.status.value == 'новая')
        
        response = {
            'success': True,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'stats': {
                'total': len(tasks),
                'completed': completed,
                'in_progress': in_progress,
                'new': new_tasks,
                'completion_rate': round((completed / len(tasks)) * 100, 1) if tasks else 0
            },
            'occupancy_data': data
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400