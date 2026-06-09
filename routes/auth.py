"""
Маршруты аутентификации
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, AuditLog
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Пожалуйста, введите имя пользователя и пароль', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            
            # Логирование входа
            log = AuditLog(
                user_id=user.id,
                action='login',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details={'remember': remember}
            )
            db.session.add(log)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        consent = request.form.get('consent')
        
        # Валидация
        if not all([username, email, password, confirm_password]):
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('auth/register.html')
        
        if not consent:
            flash('Необходимо согласие на обработку личных данных', 'error')
            return render_template('auth/register.html')
        
        # Проверка существования пользователя
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('auth/register.html')
        
        # Создание пользователя
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Логирование регистрации
        log = AuditLog(
            user_id=user.id,
            action='register',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    # Логирование выхода
    log = AuditLog(
        user_id=current_user.id,
        action='logout',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Профиль пользователя"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Редактирование профиля"""
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Валидация email
        if not email:
            flash('Email обязателен', 'error')
            return render_template('auth/edit_profile.html', user=current_user)
        
        # Проверка изменения email
        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Этот email уже используется', 'error')
                return render_template('auth/edit_profile.html', user=current_user)
            current_user.email = email
        
        # Изменение пароля
        if new_password:
            if not current_password or not current_user.check_password(current_password):
                flash('Неверный текущий пароль', 'error')
                return render_template('auth/edit_profile.html', user=current_user)
            
            if new_password != confirm_password:
                flash('Новые пароли не совпадают', 'error')
                return render_template('auth/edit_profile.html', user=current_user)
            
            if len(new_password) < 6:
                flash('Пароль должен содержать минимум 6 символов', 'error')
                return render_template('auth/edit_profile.html', user=current_user)
            
            current_user.set_password(new_password)
            flash('Пароль успешно изменен', 'success')
        
        db.session.commit()
        
        # Логирование изменения профиля
        log = AuditLog(
            user_id=current_user.id,
            action='profile_edit',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={'email_changed': email != current_user.email}
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=current_user)
