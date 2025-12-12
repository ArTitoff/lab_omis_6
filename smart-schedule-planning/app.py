from flask import Flask, render_template, session, redirect, url_for
from datetime import datetime
import os

# Импорт контроллеров
from src.controllers.auth_controller import auth_bp
from src.controllers.task_controller import task_bp
from src.controllers.calendar_controller import calendar_bp
from src.controllers.planning_controller import planning_bp
from src.controllers.report_controller import report_bp
from src.controllers.settings_controller import settings_bp
from src.utils.filters import register_filters


# После создания app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Регистрируем фильтры ДО регистрации blueprints
register_filters(app)

# Регистрация Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(task_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(planning_bp)
app.register_blueprint(report_bp)
app.register_blueprint(settings_bp)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from src.repositories import user_repository
    from src.services.task_service import TaskService
    from datetime import datetime, timedelta  # Добавьте этот импорт!
    
    user = user_repository.get_by_id(session['user_id'])
    if not user:
        session.clear()
        print('Сессия устарела. Пожалуйста, войдите снова.', 'error')
        return redirect(url_for('auth.login'))
    
    # Получаем статистику задач
    task_service = TaskService()
    tasks = task_service.get_user_tasks(user.id)
    
    stats = {
        'total': len(tasks),
        'completed': len([t for t in tasks if t.status.value == 'завершена']),
        'in_progress': len([t for t in tasks if t.status.value == 'в работе']),
        'new': len([t for t in tasks if t.status.value == 'новая'])
    }
    
    # Ближайшие задачи (следующие 7 дней)
    now = datetime.now()
    week_later = now + timedelta(days=7)
    
    upcoming_tasks = []
    for task in tasks:
        if task.deadline and task.deadline <= week_later:
            task_dict = task.to_dict()
            upcoming_tasks.append(task_dict)
    
    # Сортируем по дедлайну
    upcoming_tasks.sort(key=lambda x: x['deadline'] if x['deadline'] else '9999-12-31')
    
    return render_template('dashboard.html', 
                         user_name=session.get('user_name'),
                         user_email=session.get('user_email'),
                         stats=stats,
                         upcoming_tasks=upcoming_tasks[:5],
                         current_date=now.strftime('%d %B %Y'))


@app.route('/collaborative')
def collaborative():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('collaborative.html')

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('reports.html')

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('notifications.html')

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('settings.html')

@app.route('/data-export')
def data_export():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('data_export.html')

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
