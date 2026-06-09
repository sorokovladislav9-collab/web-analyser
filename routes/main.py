"""
Основные маршруты приложения
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Website, Analysis, User, Comparison
from sqlalchemy import desc, func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница"""
    # Статистика для главной страницы
    stats = {
        'total_websites': Website.query.count(),
        'total_analyses': Analysis.query.count(),
        'total_users': User.query.count(),
        'recent_analyses': Analysis.query.order_by(desc(Analysis.analysis_date)).limit(5).all()
    }
    
    return render_template('index.html', stats=stats)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Панель управления"""
    # Получаем веб-ресурсы пользователя
    user_websites = Website.query.filter_by(created_by=current_user.id).all()
    
    # Последние анализы пользователя
    recent_analyses = db.session.query(Analysis, Website).join(Website).filter(
        Analysis.user_id == current_user.id
    ).order_by(desc(Analysis.analysis_date)).limit(10).all()
    
    # Статистика
    stats = {
        'user_websites': len(user_websites),
        'total_analyses': Analysis.query.filter_by(user_id=current_user.id).count(),
        'completed_analyses': Analysis.query.filter_by(
            user_id=current_user.id, 
            status='completed'
        ).count(),
        'comparisons': Comparison.query.filter_by(user_id=current_user.id).count()
    }
    
    return render_template('dashboard.html', 
                         websites=user_websites,
                         recent_analyses=recent_analyses,
                         stats=stats)

@main_bp.route('/start-analysis/<int:website_id>', methods=['GET', 'POST'])
@login_required
def start_analysis(website_id):
    """Запуск анализа для существующего сайта"""
    try:
        from models import Website
        
        website = Website.query.get_or_404(website_id)
        
        # Перенаправление на новый роут анализа
        return redirect(url_for('analysis.analyze_website_start', website_id=website_id))
        
    except Exception as e:
        logger.error(f"Ошибка при запуске анализа: {e}")
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('main.websites'))

@main_bp.route('/websites')
@login_required
def websites():
    """Список веб-ресурсов"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Фильтрация
    category_filter = request.args.get('category')
    search = request.args.get('search')
    
    query = Website.query
    
    # Показываем все ресурсы для админа, иначе только свои
    if not current_user.is_admin():
        query = query.filter_by(created_by=current_user.id)
    
    # Применяем фильтры
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    if search:
        query = query.filter(
            Website.name.contains(search) | 
            Website.url.contains(search) |
            Website.description.contains(search)
        )
    
    # Пагинация
    websites = query.order_by(desc(Website.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Получаем уникальные категории для фильтра
    categories = db.session.query(Website.category).filter(
        Website.category.isnot(None)
    ).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('websites.html', 
                         websites=websites,
                         categories=categories,
                         current_category=category_filter,
                         current_search=search)

@main_bp.route('/website/add', methods=['GET', 'POST'])
@login_required
def add_website():
    """Добавление веб-ресурса"""
    if request.method == 'POST':
        url = request.form.get('url')
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        
        if not url or not name:
            flash('URL и название обязательны', 'error')
            return render_template('add_website.html')
        
        # Проверка дублирования
        existing = Website.query.filter_by(url=url).first()
        if existing:
            flash('Веб-ресурс с таким URL уже существует', 'error')
            return render_template('add_website.html')
        
        # Создание веб-ресурса
        website = Website(
            url=url,
            name=name,
            description=description,
            category=category,
            created_by=current_user.id
        )
        
        db.session.add(website)
        db.session.commit()
        
        flash('Веб-ресурс успешно добавлен', 'success')
        return redirect(url_for('main.websites'))
    
    return render_template('add_website.html')

@main_bp.route('/website/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_website(id):
    """Редактирование веб-ресурса"""
    website = Website.query.get_or_404(id)
    
    # Проверка прав доступа
    if not current_user.is_admin() and website.created_by != current_user.id:
        flash('У вас нет прав для редактирования этого ресурса', 'error')
        return redirect(url_for('main.websites'))
    
    if request.method == 'POST':
        website.url = request.form.get('url')
        website.name = request.form.get('name')
        website.description = request.form.get('description')
        website.category = request.form.get('category')
        
        db.session.commit()
        flash('Веб-ресурс успешно обновлен', 'success')
        return redirect(url_for('main.websites'))
    
    return render_template('edit_website.html', website=website)

@main_bp.route('/website/<int:id>/delete', methods=['POST'])
@login_required
def delete_website(id):
    """Удаление веб-ресурса"""
    website = Website.query.get_or_404(id)
    
    # Проверка прав доступа
    if not current_user.is_admin() and website.created_by != current_user.id:
        flash('У вас нет прав для удаления этого ресурса', 'error')
        return redirect(url_for('main.websites'))
    
    db.session.delete(website)
    db.session.commit()
    flash('Веб-ресурс успешно удален', 'success')
    return redirect(url_for('main.websites'))

@main_bp.route('/comparisons')
@login_required
def comparisons():
    """Список сравнений"""
    comparisons = Comparison.query.filter_by(user_id=current_user.id).order_by(
        desc(Comparison.created_at)
    ).all()
    
    return render_template('comparisons.html', comparisons=comparisons)

@main_bp.route('/comparison/add', methods=['GET', 'POST'])
@login_required
def add_comparison():
    """Создание сравнения"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        website_ids = request.form.getlist('websites')
        
        if not name or not website_ids:
            flash('Название и хотя бы один веб-ресурс обязательны', 'error')
            return _render_comparison_form()
        
        # Создание сравнения
        comparison = Comparison(
            name=name,
            description=description,
            user_id=current_user.id
        )
        
        # Добавление веб-ресурсов
        for website_id in website_ids:
            website = Website.query.get(website_id)
            if website:
                comparison.websites.append(website)
        
        db.session.add(comparison)
        db.session.commit()
        
        flash('Сравнение успешно создано', 'success')
        return redirect(url_for('main.comparisons'))
    
    return _render_comparison_form()

def _render_comparison_form():
    """Вспомогательная функция для формы сравнения"""
    # Получаем веб-ресурсы пользователя
    if current_user.is_admin():
        websites = Website.query.all()
    else:
        websites = Website.query.filter_by(created_by=current_user.id).all()
    
    return render_template('add_comparison.html', websites=websites)

@main_bp.route('/comparison/<int:id>')
@login_required
def view_comparison(id):
    """Просмотр сравнения"""
    comparison = Comparison.query.get_or_404(id)
    
    # Проверка прав доступа
    if comparison.user_id != current_user.id and not current_user.is_admin():
        flash('У вас нет прав для просмотра этого сравнения', 'error')
        return redirect(url_for('main.comparisons'))
    
    # Получаем последние анализы для каждого веб-ресурса
    websites_data = []
    for website in comparison.websites:
        latest_analysis = website.get_latest_analysis()
        websites_data.append({
            'website': website,
            'analysis': latest_analysis
        })
    
    return render_template('view_comparison.html', 
                         comparison=comparison,
                         websites_data=websites_data)

@main_bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """Просмотр анализа"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Проверка прав доступа
    if analysis.user_id != current_user.id and not current_user.is_admin():
        flash('У вас нет прав для просмотра этого анализа', 'error')
        return redirect(url_for('main.websites'))
    
    # Получаем связанный веб-ресурс
    website = Website.query.get(analysis.website_id)
    
    # Получаем баллы из связанных таблиц
    seo_score = analysis.seo_metrics.score if analysis.seo_metrics else 0
    performance_score = analysis.performance_metrics.performance_score if analysis.performance_metrics else 0
    security_score = analysis.security_metrics.security_score if analysis.security_metrics else 0
    accessibility_score = analysis.accessibility_metrics.accessibility_score if analysis.accessibility_metrics else 0
    ux_score = analysis.ux_metrics.ux_score if analysis.ux_metrics else 0
    
    # Вычисляем общий балл
    overall_score = (seo_score + performance_score + security_score + accessibility_score + ux_score) / 5
    
    # Получаем предыдущий анализ для сравнения
    previous_analysis = website.get_previous_analysis(analysis.id)
    
    # Данные для сравнения с предыдущим анализом
    comparison = None
    if previous_analysis:
        prev_seo_score = previous_analysis.seo_metrics.score if previous_analysis.seo_metrics else 0
        prev_performance_score = previous_analysis.performance_metrics.performance_score if previous_analysis.performance_metrics else 0
        prev_security_score = previous_analysis.security_metrics.security_score if previous_analysis.security_metrics else 0
        prev_accessibility_score = previous_analysis.accessibility_metrics.accessibility_score if previous_analysis.accessibility_metrics else 0
        prev_ux_score = previous_analysis.ux_metrics.ux_score if previous_analysis.ux_metrics else 0
        prev_overall_score = (prev_seo_score + prev_performance_score + prev_security_score + prev_accessibility_score + prev_ux_score) / 5
        
        comparison = {
            'has_previous': True,
            'previous_analysis_date': previous_analysis.analysis_date,
            'seo_change': seo_score - prev_seo_score,
            'performance_change': performance_score - prev_performance_score,
            'security_change': security_score - prev_security_score,
            'accessibility_change': accessibility_score - prev_accessibility_score,
            'ux_change': ux_score - prev_ux_score,
            'overall_change': overall_score - prev_overall_score,
            'seo_improved': seo_score > prev_seo_score,
            'performance_improved': performance_score > prev_performance_score,
            'security_improved': security_score > prev_security_score,
            'accessibility_improved': accessibility_score > prev_accessibility_score,
            'ux_improved': ux_score > prev_ux_score,
            'overall_improved': overall_score > prev_overall_score
        }
    else:
        comparison = {
            'has_previous': False
        }
    
    return render_template('view_analysis.html', 
                         analysis=analysis,
                         website=website,
                         overall_score=overall_score,
                         seo_score=seo_score,
                         performance_score=performance_score,
                         security_score=security_score,
                         accessibility_score=accessibility_score,
                         ux_score=ux_score,
                         comparison=comparison)

@main_bp.route('/website/<int:website_id>')
@login_required
def view_website(website_id):
    """Просмотр детальной информации о сайте"""
    website = Website.query.get_or_404(website_id)
    
    # Проверка прав доступа
    if not current_user.is_admin() and website.created_by != current_user.id:
        flash('У вас нет прав для просмотра этого сайта', 'error')
        return redirect(url_for('main.websites'))
    
    # Получаем последний анализ
    latest_analysis = website.get_latest_analysis()
    
    return render_template('view_website.html', 
                         website=website,
                         latest_analysis=latest_analysis)
