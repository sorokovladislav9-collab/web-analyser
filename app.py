"""
Основное приложение Flask для системы анализа веб-ресурсов
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

# Импорт конфигурации и моделей
from config.config import config
from models import db, User, Website, Analysis, SEOMetrics, PerformanceMetrics, AccessibilityMetrics, SecurityMetrics, UXMetrics, Report, Comparison

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Фабрика приложения"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Инициализация расширений
    db.init_app(app)
    
    # Настройка Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Настройка миграций
    migrate = Migrate(app, db)
    
    # Регистрация Blueprintов
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.main import main_bp
    from routes.analysis_routes import analysis_bp
    from routes.reports import reports_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

def init_db(app):
    """Инициализация базы данных"""
    with app.app_context():
        try:
            # Создание таблиц
            db.create_all()
            
            # Создание администратора по умолчанию
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role='admin'
                )
                admin.set_password('admin123')  # Изменить в продакшене!
                db.session.add(admin)
                db.session.commit()
                logger.info("Создан администратор по умолчанию")
            
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {e}")
            raise

if __name__ == '__main__':
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app = create_app(config_name)
    
    # Инициализация БД при первом запуске
    if not os.path.exists('app.db'):
        init_db(app)
    
    # Запуск приложения
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
