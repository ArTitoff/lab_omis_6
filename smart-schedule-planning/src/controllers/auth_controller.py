# src/controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.user_service import UserService
from src.repositories import user_repository  # Импортируем единый репозиторий

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Создаем единый экземпляр UserService
user_service = UserService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Аутентификация через UserService
            user = user_service.authenticate(email, password)
            if user:
                # Сохраняем данные в сессии
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                session['user_role'] = user.role.value
                
                # Дебаг-вывод
                print(f"DEBUG [Auth]: Успешный вход. ID: {user.id}, Email: {user.email}")
                print(f"DEBUG [Auth]: Пароль хеш: {user.password_hash}")
                print(f"DEBUG [Auth]: Всего пользователей в системе: {len(user_repository.get_all())}")
                
                flash('Успешный вход в систему!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Неверный email или пароль', 'error')
        except Exception as e:
            flash(f'Ошибка при входе: {str(e)}', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Проверка совпадения паролей
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        
        try:
            # Регистрация через UserService
            user = user_service.register(name, email, password)
            
            # Дебаг-вывод
            print(f"DEBUG [Auth]: Успешная регистрация. ID: {user.id}, Email: {user.email}")
            print(f"DEBUG [Auth]: Пароль хеш: {user.password_hash}")
            print(f"DEBUG [Auth]: Все пользователи: {[u.id for u in user_repository.get_all()]}")
            
            flash('Регистрация успешна! Теперь войдите в систему.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Выход из системы"""
    # Дебаг-вывод
    print(f"DEBUG [Auth]: Выход. ID пользователя: {session.get('user_id')}")
    
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))