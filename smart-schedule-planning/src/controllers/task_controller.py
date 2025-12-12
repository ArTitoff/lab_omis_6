# src/controllers/task_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
from src.services.task_service import TaskService
from src.services.schedule_service import ScheduleService
from src.services.planning_service import PlanningService
from src.repositories import task_repository, user_repository, schedule_repository, group_repository

task_bp = Blueprint('task', __name__, url_prefix='/tasks')

# Создаем экземпляры сервисов БЕЗ аргументов
task_service = TaskService()
schedule_service = ScheduleService()
planning_service = PlanningService()

# ========== РАБОТА С ЗАДАЧАМИ ==========

@task_bp.route('/')
def task_list():
    """Список задач пользователя"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    status_filter = request.args.get('status')
    
    try:
        tasks = task_service.get_user_tasks(user_id, status_filter)
        return render_template('tasks.html', 
                             tasks=[task.to_dict() for task in tasks],
                             status_filter=status_filter)
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('dashboard'))

@task_bp.route('/create', methods=['GET', 'POST'])
def create_task():
    """Создание новой задачи"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        deadline_date = request.form.get('deadline_date')
        deadline_time = request.form.get('deadline_time')
        duration_str = request.form.get('duration')
        priority = request.form.get('priority', 'средний')
        schedule_id_str = request.form.get('schedule_id')
        
        try:
            # Собираем полную дату и время дедлайна
            deadline = None
            if deadline_date and deadline_time:
                try:
                    # Формируем строку вида "2025-12-12T14:00"
                    deadline_str = f"{deadline_date}T{deadline_time}"
                    deadline = datetime.fromisoformat(deadline_str)
                except ValueError as e:
                    flash(f'Некорректный формат даты/времени: {str(e)}', 'error')
                    return render_template('task_create.html', 
                                         schedules=schedule_repository.get_user_schedules(user_id))
            
            # Преобразуем продолжительность
            duration = 60
            if duration_str:
                try:
                    duration = int(duration_str)
                except ValueError:
                    flash('Некорректная продолжительность', 'error')
                    return render_template('task_create.html', 
                                         schedules=schedule_repository.get_user_schedules(user_id))
            
            # Преобразуем ID расписания
            schedule_id = None
            if schedule_id_str:
                try:
                    schedule_id = int(schedule_id_str)
                except ValueError:
                    schedule_id = None
            
            # Вычисляем время начала и окончания
            start_time = None
            end_time = None
            
            if deadline:
                # Если указан дедлайн, время начала = дедлайн - продолжительность
                start_time = deadline - timedelta(minutes=duration)
                end_time = deadline
            
            # Создаем задачу с временем
            task = task_service.create_task_with_time(
                user_id, title, description, 
                deadline, start_time, end_time,
                duration, priority, schedule_id
            )
            
            if schedule_id:
                schedule_service.add_task_to_schedule(schedule_id, task.id)
            
            flash(f'Задача "{title}" создана на {deadline_date} {deadline_time}', 'success')
            return redirect(url_for('task.task_list'))
            
        except Exception as e:
            flash(f'Ошибка при создании задачи: {str(e)}', 'error')
    
    # GET запрос - показываем форму
    schedules = schedule_repository.get_user_schedules(user_id)
    return render_template('task_create.html', 
                         schedules=[s.to_dict() for s in schedules])

@task_bp.route('/<int:task_id>')
def task_detail(task_id):
    """Просмотр деталей задачи"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        task = task_repository.get_by_id(task_id)
        if not task:
            flash('Задача не найдена', 'error')
            return redirect(url_for('task.task_list'))
        
        # Проверяем, что пользователь имеет доступ к задаче
        user_id = session['user_id']
        if task.creator_id != user_id and user_id not in task.assigned_users:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('task.task_list'))
        
        return render_template('task_detail.html', task=task.to_dict())
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('task.task_list'))

@task_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Редактирование задачи"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        task = task_repository.get_by_id(task_id)
        if not task:
            flash('Задача не найдена', 'error')
            return redirect(url_for('task.task_list'))
        
        # Проверяем доступ
        user_id = session['user_id']
        if task.creator_id != user_id and user_id not in task.assigned_users:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('task.task_list'))
        
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            deadline_str = request.form.get('deadline')
            duration_str = request.form.get('duration')
            priority = request.form.get('priority')
            status = request.form.get('status')
            
            updates = {}
            if title: 
                updates['title'] = title
            if description is not None: 
                updates['description'] = description
            
            if deadline_str: 
                try:
                    updates['deadline'] = datetime.fromisoformat(deadline_str)
                except:
                    flash('Некорректный формат даты', 'error')
                    return render_template('task_edit.html', task=task.to_dict())
            
            if duration_str: 
                try:
                    updates['duration'] = int(duration_str)
                except ValueError:
                    flash('Некорректная продолжительность', 'error')
                    return render_template('task_edit.html', task=task.to_dict())
            
            if priority: 
                updates['priority'] = priority
            if status: 
                updates['status'] = status
            
            task = task_service.update_task(task_id, **updates)
            flash('Задача успешно обновлена!', 'success')
            return redirect(url_for('task.task_detail', task_id=task_id))
        
        return render_template('task_edit.html', task=task.to_dict())
    
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('task.task_list'))

@task_bp.route('/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Отметить задачу как выполненную"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    try:
        task = task_service.complete_task(task_id)
        return jsonify({'success': True, 'task': task.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@task_bp.route('/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    """Начать выполнение задачи"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    try:
        updates = {'start_time': datetime.now(), 'status': 'в работе'}
        task = task_service.update_task(task_id, **updates)
        return jsonify({'success': True, 'task': task.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@task_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Удаление задачи"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        success = task_repository.delete(task_id)
        if success:
            flash('Задача успешно удалена', 'success')
        else:
            flash('Задача не найдена', 'error')
    except Exception as e:
        flash(str(e), 'error')
    
    return redirect(url_for('task.task_list'))

# ========== API ДЛЯ DASHBOARD И AJAX ==========

@task_bp.route('/upcoming')
def upcoming_tasks():
    """Получить ближайшие задачи для dashboard"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    try:
        tasks = task_service.get_user_tasks(user_id)
        
        # Ближайшие задачи (с дедлайном в ближайшие 7 дней)
        now = datetime.now()
        week_later = now + timedelta(days=7)
        upcoming = []
        
        for task in tasks:
            if task.deadline and task.deadline <= week_later:
                upcoming.append(task.to_dict())
        
        # Сортируем по дедлайну
        upcoming.sort(key=lambda x: x['deadline'] if x['deadline'] else '9999-12-31')
        
        # Статистика
        stats = {
            'total': len(tasks),
            'completed': len([t for t in tasks if t.status.value == 'завершена']),
            'in_progress': len([t for t in tasks if t.status.value == 'в работе']),
            'new': len([t for t in tasks if t.status.value == 'новая'])
        }
        
        return jsonify({
            'success': True,
            'tasks': upcoming[:5],  # Берем 5 ближайших
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ========== СТАТИСТИКА ==========

@task_bp.route('/stats')
def task_stats():
    """Статистика по задачам"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    try:
        tasks = task_service.get_user_tasks(user_id)
        
        stats = {
            'total': len(tasks),
            'completed': len([t for t in tasks if t.status.value == 'завершена']),
            'in_progress': len([t for t in tasks if t.status.value == 'в работе']),
            'new': len([t for t in tasks if t.status.value == 'новая']),
            
            'by_priority': {
                'высокий': len([t for t in tasks if t.priority.value == 'высокий']),
                'средний': len([t for t in tasks if t.priority.value == 'средний']),
                'низкий': len([t for t in tasks if t.priority.value == 'низкий'])
            }
        }
        
        return jsonify({'success': True, 'stats': stats})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
@task_bp.route('/suggest-time', methods=['POST'])
def suggest_time():
    """Получить предложения по времени для задачи"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    
    print(f"DEBUG: Получаем запрос на подбор времени для user_id={user_id}")
    
    try:
        # Получаем JSON данные
        data = request.get_json()
        print(f"DEBUG: Полученные данные: {data}")
        
        if not data:
            print("DEBUG: Нет данных в запросе")
            return jsonify({'success': False, 'error': 'Нет данных'}), 400
        
        # Безопасное получение данных
        duration_str = data.get('duration', '60')
        priority = data.get('priority', 'средний')
        
        print(f"DEBUG: duration_str={duration_str}, priority={priority}")
        
        try:
            duration = int(duration_str)
        except (ValueError, TypeError):
            print(f"DEBUG: Ошибка преобразования duration: {duration_str}")
            duration = 60
        
        # Проверка допустимых значений
        if duration < 15:
            print(f"DEBUG: Слишком маленькая продолжительность: {duration}")
            return jsonify({'success': False, 'error': 'Продолжительность должна быть не менее 15 минут'}), 400
            
        if priority not in ['низкий', 'средний', 'высокий']:
            print(f"DEBUG: Некорректный приоритет: {priority}, используем 'средний'")
            priority = 'средний'
        
        print(f"DEBUG: Вызываем planning_service.suggest_optimal_time с duration={duration}, priority={priority}")
        
        # Получаем предложения от сервиса планирования
        suggestions = planning_service.suggest_optimal_time(user_id, duration, priority)
        
        print(f"DEBUG: Получено предложений: {len(suggestions)}")
        
        return jsonify({
            'success': True, 
            'suggestions': suggestions,
            'message': f'Найдено {len(suggestions)} предложений'
        })
        
    except ValueError as e:
        print(f"DEBUG: ValueError: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Некорректные данные: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG: Общая ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500