"""
Модели данных SQLAlchemy
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'analyst', 'viewer', name='user_role'), default='viewer')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Отношения
    websites = db.relationship('Website', backref='creator', lazy=True)
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    comparisons = db.relationship('Comparison', backref='user', lazy=True)
    api_keys = db.relationship('ApiKey', backref='user', lazy=True)
    
    def set_password(self, password):
        """Установка пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Проверка прав администратора"""
        return self.role == 'admin'
    
    def can_analyze(self):
        """Проверка прав на анализ"""
        return self.role in ['admin', 'analyst']

class Website(db.Model):
    """Модель веб-ресурса"""
    __tablename__ = 'websites'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Отношения
    analyses = db.relationship('Analysis', backref='website', lazy=True, cascade='all, delete-orphan')
    
    def get_latest_analysis(self):
        """Получить последний анализ"""
        return Analysis.query.filter_by(website_id=self.id).order_by(Analysis.analysis_date.desc()).first()
    
    def get_previous_analysis(self, current_analysis_id):
        """Получить предыдущий анализ перед указанным"""
        return Analysis.query.filter(
            Analysis.website_id == self.id,
            Analysis.id < current_analysis_id
        ).order_by(Analysis.analysis_date.desc()).first()

class Analysis(db.Model):
    """Модель анализа веб-ресурса"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed', name='analysis_status'), default='pending')
    error_message = db.Column(db.Text)
    
    # Отношения с метриками
    seo_metrics = db.relationship('SEOMetrics', backref='analysis', uselist=False, cascade='all, delete-orphan')
    performance_metrics = db.relationship('PerformanceMetrics', backref='analysis', uselist=False, cascade='all, delete-orphan')
    accessibility_metrics = db.relationship('AccessibilityMetrics', backref='analysis', uselist=False, cascade='all, delete-orphan')
    security_metrics = db.relationship('SecurityMetrics', backref='analysis', uselist=False, cascade='all, delete-orphan')
    ux_metrics = db.relationship('UXMetrics', backref='analysis', uselist=False, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='analysis', lazy=True, cascade='all, delete-orphan')

class SEOMetrics(db.Model):
    """SEO метрики"""
    __tablename__ = 'seo_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    h1_count = db.Column(db.Integer, default=0)
    h2_count = db.Column(db.Integer, default=0)
    internal_links = db.Column(db.Integer, default=0)
    external_links = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    images_count = db.Column(db.Integer, default=0)
    images_without_alt = db.Column(db.Integer, default=0)
    score = db.Column(db.Numeric(5, 2), default=0.00)

class PerformanceMetrics(db.Model):
    """Метрики производительности"""
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    load_time_ms = db.Column(db.Integer, default=0)
    first_contentful_paint_ms = db.Column(db.Integer, default=0)
    largest_contentful_paint_ms = db.Column(db.Integer, default=0)
    cumulative_layout_shift = db.Column(db.Numeric(10, 8), default=0.00000000)
    first_input_delay_ms = db.Column(db.Integer, default=0)
    time_to_interactive_ms = db.Column(db.Integer, default=0)
    total_page_size_kb = db.Column(db.Integer, default=0)
    requests_count = db.Column(db.Integer, default=0)
    performance_score = db.Column(db.Numeric(5, 2), default=0.00)

class AccessibilityMetrics(db.Model):
    """Метрики доступности"""
    __tablename__ = 'accessibility_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    alt_text_missing = db.Column(db.Integer, default=0)
    aria_labels_missing = db.Column(db.Integer, default=0)
    color_contrast_issues = db.Column(db.Integer, default=0)
    keyboard_navigation_issues = db.Column(db.Integer, default=0)
    form_labels_missing = db.Column(db.Integer, default=0)
    accessibility_score = db.Column(db.Numeric(5, 2), default=0.00)

class SecurityMetrics(db.Model):
    """Метрики безопасности"""
    __tablename__ = 'security_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    has_https = db.Column(db.Boolean, default=False)
    has_security_headers = db.Column(db.Boolean, default=False)
    vulnerable_libraries = db.Column(db.Integer, default=0)
    mixed_content_issues = db.Column(db.Integer, default=0)
    security_score = db.Column(db.Numeric(5, 2), default=0.00)

class UXMetrics(db.Model):
    """UX метрики"""
    __tablename__ = 'ux_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    mobile_friendly = db.Column(db.Boolean, default=False)
    responsive_design = db.Column(db.Boolean, default=False)
    readable_font_sizes = db.Column(db.Boolean, default=False)
    clear_navigation = db.Column(db.Boolean, default=False)
    ux_score = db.Column(db.Numeric(5, 2), default=0.00)

class Report(db.Model):
    """Отчеты"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    report_type = db.Column(db.Enum('html', 'pdf', 'docx', 'xlsx', 'json', name='report_type'), nullable=False)
    file_path = db.Column(db.String(500))
    generated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

class Comparison(db.Model):
    """Сравнения веб-ресурсов"""
    __tablename__ = 'comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    description = db.Column(db.Text)
    
    # Отношения
    websites = db.relationship('Website', secondary='comparison_websites', backref='comparisons')

# Таблица связи для сравнений
comparison_websites = db.Table('comparison_websites',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('comparison_id', db.Integer, db.ForeignKey('comparisons.id'), nullable=False),
    db.Column('website_id', db.Integer, db.ForeignKey('websites.id'), nullable=False)
)

class ApiKey(db.Model):
    """API ключи"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    permissions = db.Column(db.JSON)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    last_used = db.Column(db.TIMESTAMP)
    is_active = db.Column(db.Boolean, default=True)

class AuditLog(db.Model):
    """Логирование действий"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
