# src/controllers/planning_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
from src.services.planning_service import PlanningService
# Импортируем ЕДИНЫЕ экземпляры репозиториев
from src.repositories import task_repository, user_repository, group_repository

planning_bp = Blueprint('planning', __name__, url_prefix='/planning')

# Создаем экземпляр сервиса БЕЗ аргументов
planning_service = PlanningService()

@planning_bp.route('/collaborative')
def collaborative():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('collaborative.html')

@planning_bp.route('/find-slots', methods=['POST'])
def find_slots():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    duration = request.json.get('duration', type=int)
    start_str = request.json.get('start_date')
    end_str = request.json.get('end_date')
    
    try:
        start_date = datetime.fromisoformat(start_str) if start_str else datetime.now()
        end_date = datetime.fromisoformat(end_str) if end_str else datetime.now() + timedelta(days=7)
        
        slots = planning_service.find_free_slots(user_id, duration, start_date, end_date)
        return jsonify({'success': True, 'slots': slots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/check-conflicts', methods=['POST'])
def check_conflicts():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    start_str = request.json.get('start_time')
    end_str = request.json.get('end_time')
    
    try:
        start_time = datetime.fromisoformat(start_str) if start_str else datetime.now()
        end_time = datetime.fromisoformat(end_str) if end_str else datetime.now() + timedelta(hours=1)
        
        conflicts = planning_service.check_conflicts(user_id, start_time, end_time)
        return jsonify({'success': True, 'conflicts': conflicts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/group-analysis', methods=['POST'])
def group_analysis():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    group_id = request.json.get('group_id', type=int)
    duration = request.json.get('duration', type=int)
    
    try:
        slots = planning_service.analyze_group_schedule(group_id, duration)
        return jsonify({'success': True, 'slots': slots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
@planning_bp.route('/create-group', methods=['POST'])
def create_group():
    """Создать группу для совместной работы"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    try:
        name = request.json.get('name')
        description = request.json.get('description', '')
        is_public = request.json.get('is_public', False)
        max_members = request.json.get('max_members', 10)
        
        if not name:
            return jsonify({'success': False, 'error': 'Название группы обязательно'}), 400
        
        result = planning_service.create_collaborative_group(
            user_id, name, description, is_public, max_members
        )
        
        return jsonify({'success': True, **result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/join-group', methods=['POST'])
def join_group():
    """Присоединиться к группе"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    try:
        group_id = request.json.get('group_id', type=int)
        
        if not group_id:
            return jsonify({'success': False, 'error': 'ID группы обязателен'}), 400
        
        result = planning_service.join_group(user_id, group_id)
        
        return jsonify({'success': True, **result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/leave-group', methods=['POST'])
def leave_group():
    """Покинуть группу"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    try:
        group_id = request.json.get('group_id', type=int)
        
        if not group_id:
            return jsonify({'success': False, 'error': 'ID группы обязателен'}), 400
        
        result = planning_service.leave_group(user_id, group_id)
        
        return jsonify({'success': True, **result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/my-groups')
def my_groups():
    """Получить мои группы"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    try:
        groups = planning_service.get_user_groups(user_id)
        return jsonify({'success': True, 'groups': groups})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/common-slots', methods=['POST'])
def get_common_slots():
    """Найти общее время для группы"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    group_id = request.json.get('group_id', type=int)
    duration = request.json.get('duration', 60)
    
    try:
        slots = planning_service.find_common_slots(group_id, duration)
        return jsonify({'success': True, 'slots': slots})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/group-tasks/<int:group_id>')
def group_tasks(group_id):
    """Получить задачи группы"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    try:
        from src.repositories import group_repository, schedule_repository, task_repository
        
        group = group_repository.get_by_id(group_id)
        if not group:
            return jsonify({'success': False, 'error': 'Группа не найдена'}), 404
        
        # Проверяем, состоит ли пользователь в группе
        if not any(member.id == user_id for member in group.members):
            return jsonify({'success': False, 'error': 'Доступ запрещен'}), 403
        
        # Получаем задачи из расписания группы
        tasks = []
        if group.schedule:
            tasks = task_repository.get_schedule_tasks(group.schedule.id)
        
        return jsonify({
            'success': True,
            'group': group.to_dict(),
            'tasks': [task.to_dict() for task in tasks]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
@planning_bp.route('/api/create-group', methods=['POST'])
def api_create_group():
    """API для создания группы"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'success': False, 'error': 'Название группы обязательно'}), 400
        
        result = planning_service.create_group(user_id, name, description)
        return jsonify({'success': True, **result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@planning_bp.route('/api/my-groups')
def api_my_groups():
    """Получить группы пользователя"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    try:
        groups = group_repository.get_user_groups(user_id)
        return jsonify({
            'success': True, 
            'groups': [group.to_dict() for group in groups]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400