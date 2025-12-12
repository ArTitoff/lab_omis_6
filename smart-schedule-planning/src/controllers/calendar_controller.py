# src/controllers/calendar_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
from src.services.calendar_service import CalendarService
from src.repositories import task_repository, event_repository, user_repository

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

# Создаем экземпляр сервиса БЕЗ аргументов
calendar_service = CalendarService()

@calendar_bp.route('/')
def calendar_view():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    view = request.args.get('view', 'month')
    date_str = request.args.get('date')
    
    try:
        if date_str:
            current_date = datetime.fromisoformat(date_str)
        else:
            current_date = datetime.now()
        
        if view == 'day':
            data = calendar_service.get_day_view(user_id, current_date)
            return render_template('calendar_day.html', 
                                 **data, 
                                 current_date=current_date,
                                 prev_day=(current_date - timedelta(days=1)).isoformat(),
                                 next_day=(current_date + timedelta(days=1)).isoformat())
        
        elif view == 'week':
            data = calendar_service.get_week_view(user_id, current_date)
            return render_template('calendar_week.html', 
                                 **data, 
                                 current_date=current_date,
                                 prev_week=(current_date - timedelta(days=7)).isoformat(),
                                 next_week=(current_date + timedelta(days=7)).isoformat())
        
        else:  # month
            data = calendar_service.get_month_view(user_id, current_date.year, current_date.month)
            
            # Вычисляем предыдущий и следующий месяц
            if current_date.month == 1:
                prev_month = datetime(current_date.year - 1, 12, 1)
            else:
                prev_month = datetime(current_date.year, current_date.month - 1, 1)
                
            if current_date.month == 12:
                next_month = datetime(current_date.year + 1, 1, 1)
            else:
                next_month = datetime(current_date.year, current_date.month + 1, 1)
            
            return render_template('calendar_month.html', 
                                **data, 
                                current_date=current_date,
                                prev_month=prev_month.isoformat(),
                                next_month=next_month.isoformat())
    
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('dashboard'))
    

@calendar_bp.route('/day/<string:date_str>')
def day_view(date_str):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        date = datetime.fromisoformat(date_str)
        data = calendar_service.get_day_view(user_id, date)
        return jsonify({'success': True, **data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@calendar_bp.route('/week/<string:date_str>')
def week_view(date_str):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        date = datetime.fromisoformat(date_str)
        data = calendar_service.get_week_view(user_id, date)
        return jsonify({'success': True, **data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@calendar_bp.route('/month/<int:year>/<int:month>')
def month_view(year, month):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        data = calendar_service.get_month_view(user_id, year, month)
        return jsonify({'success': True, **data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@calendar_bp.route('/occupancy')
def occupancy_chart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    try:
        start_date = datetime.fromisoformat(start_str) if start_str else datetime.now() - timedelta(days=7)
        end_date = datetime.fromisoformat(end_str) if end_str else datetime.now()
        
        data = calendar_service.generate_occupancy_chart(user_id, start_date, end_date)
        return jsonify({'success': True, **data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400