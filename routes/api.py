"""
REST API маршруты
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Website, Analysis, SEOMetrics, PerformanceMetrics, AccessibilityMetrics, SecurityMetrics, UXMetrics, User, Comparison
from datetime import datetime
import json

api_bp = Blueprint('api', __name__)

def api_response(data=None, error=None, status_code=200):
    """Форматирование API ответа"""
    response = {
        'success': error is None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code

@api_bp.route('/websites', methods=['GET'])
@login_required
def get_websites():
    """Получение списка веб-ресурсов"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        query = Website.query
        
        # Фильтрация для обычных пользователей
        if not current_user.is_admin():
            query = query.filter_by(created_by=current_user.id)
        
        # Поиск
        search = request.args.get('search')
        if search:
            query = query.filter(
                Website.name.contains(search) | 
                Website.url.contains(search)
            )
        
        # Пагинация
        websites = query.paginate(page=page, per_page=per_page, error_out=False)
        
        data = {
            'websites': [{
                'id': w.id,
                'url': w.url,
                'name': w.name,
                'description': w.description,
                'category': w.category,
                'created_at': w.created_at.isoformat(),
                'updated_at': w.updated_at.isoformat()
            } for w in websites.items],
            'pagination': {
                'page': websites.page,
                'pages': websites.pages,
                'per_page': websites.per_page,
                'total': websites.total,
                'has_next': websites.has_next,
                'has_prev': websites.has_prev
            }
        }
        
        return api_response(data=data)
    
    except Exception as e:
        return api_response(error=str(e), status_code=500)

@api_bp.route('/websites', methods=['POST'])
@login_required
def create_website():
    """Создание нового веб-ресурса"""
    try:
        data = request.get_json()
        
        if not data or not data.get('url') or not data.get('name'):
            return api_response(error='URL и название обязательны', status_code=400)
        
        # Проверка дублирования
        existing = Website.query.filter_by(url=data['url']).first()
        if existing:
            return api_response(error='Веб-ресурс с таким URL уже существует', status_code=409)
        
        website = Website(
            url=data['url'],
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', ''),
            created_by=current_user.id
        )
        
        db.session.add(website)
        db.session.commit()
        
        result = {
            'id': website.id,
            'url': website.url,
            'name': website.name,
            'description': website.description,
            'category': website.category,
            'created_at': website.created_at.isoformat()
        }
        
        return api_response(data=result, status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status_code=500)

@api_bp.route('/websites/<int:website_id>', methods=['GET'])
@login_required
def get_website(website_id):
    """Получение информации о веб-ресурсе"""
    try:
        website = Website.query.get_or_404(website_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and website.created_by != current_user.id:
            return api_response(error='Доступ запрещен', status_code=403)
        
        # Получение последнего анализа
        latest_analysis = website.get_latest_analysis()
        
        data = {
            'id': website.id,
            'url': website.url,
            'name': website.name,
            'description': website.description,
            'category': website.category,
            'created_at': website.created_at.isoformat(),
            'updated_at': website.updated_at.isoformat(),
            'latest_analysis': {
                'id': latest_analysis.id,
                'status': latest_analysis.status,
                'analysis_date': latest_analysis.analysis_date.isoformat()
            } if latest_analysis else None
        }
        
        return api_response(data=data)
    
    except Exception as e:
        return api_response(error=str(e), status_code=500)

@api_bp.route('/websites/<int:website_id>', methods=['PUT'])
@login_required
def update_website(website_id):
    """Обновление веб-ресурса"""
    try:
        website = Website.query.get_or_404(website_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and website.created_by != current_user.id:
            return api_response(error='Доступ запрещен', status_code=403)
        
        data = request.get_json()
        
        if data.get('url'):
            website.url = data['url']
        if data.get('name'):
            website.name = data['name']
        if 'description' in data:
            website.description = data['description']
        if 'category' in data:
            website.category = data['category']
        
        db.session.commit()
        
        result = {
            'id': website.id,
            'url': website.url,
            'name': website.name,
            'description': website.description,
            'category': website.category,
            'updated_at': website.updated_at.isoformat()
        }
        
        return api_response(data=result)
    
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status_code=500)

@api_bp.route('/websites/<int:website_id>', methods=['DELETE'])
@login_required
def delete_website(website_id):
    """Удаление веб-ресурса"""
    try:
        website = Website.query.get_or_404(website_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and website.created_by != current_user.id:
            return api_response(error='Доступ запрещен', status_code=403)
        
        db.session.delete(website)
        db.session.commit()
        
        return api_response(data={'message': 'Веб-ресурс удален'})
    
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status_code=500)

@api_bp.route('/analyses', methods=['GET'])
@login_required
def get_analyses():
    """Получение списка анализов"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status_filter = request.args.get('status')
        website_id = request.args.get('website_id', type=int)
        
        query = Analysis.query
        
        # Фильтрация для обычных пользователей
        if not current_user.is_admin():
            query = query.filter_by(user_id=current_user.id)
        
        # Применение фильтров
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if website_id:
            query = query.filter_by(website_id=website_id)
        
        # Пагинация
        analyses = query.order_by(Analysis.analysis_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        data = {
            'analyses': [{
                'id': a.id,
                'website_id': a.website_id,
                'website_name': a.website.name,
                'status': a.status,
                'analysis_date': a.analysis_date.isoformat(),
                'error_message': a.error_message
            } for a in analyses.items],
            'pagination': {
                'page': analyses.page,
                'pages': analyses.pages,
                'per_page': analyses.per_page,
                'total': analyses.total,
                'has_next': analyses.has_next,
                'has_prev': analyses.has_prev
            }
        }
        
        return api_response(data=data)
    
    except Exception as e:
        return api_response(error=str(e), status_code=500)

@api_bp.route('/analyses/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id):
    """Получение детальной информации об анализе"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and analysis.user_id != current_user.id:
            return api_response(error='Доступ запрещен', status_code=403)
        
        # Собираем все метрики
        metrics = {}
        
        if analysis.seo_metrics:
            metrics['seo'] = {
                'title': analysis.seo_metrics.title,
                'meta_description': analysis.seo_metrics.meta_description,
                'h1_count': analysis.seo_metrics.h1_count,
                'h2_count': analysis.seo_metrics.h2_count,
                'internal_links': analysis.seo_metrics.internal_links,
                'external_links': analysis.seo_metrics.external_links,
                'word_count': analysis.seo_metrics.word_count,
                'images_count': analysis.seo_metrics.images_count,
                'images_without_alt': analysis.seo_metrics.images_without_alt,
                'score': float(analysis.seo_metrics.score)
            }
        
        if analysis.performance_metrics:
            metrics['performance'] = {
                'load_time_ms': analysis.performance_metrics.load_time_ms,
                'first_contentful_paint_ms': analysis.performance_metrics.first_contentful_paint_ms,
                'largest_contentful_paint_ms': analysis.performance_metrics.largest_contentful_paint_ms,
                'cumulative_layout_shift': float(analysis.performance_metrics.cumulative_layout_shift),
                'first_input_delay_ms': analysis.performance_metrics.first_input_delay_ms,
                'time_to_interactive_ms': analysis.performance_metrics.time_to_interactive_ms,
                'total_page_size_kb': analysis.performance_metrics.total_page_size_kb,
                'requests_count': analysis.performance_metrics.requests_count,
                'performance_score': float(analysis.performance_metrics.performance_score)
            }
        
        if analysis.accessibility_metrics:
            metrics['accessibility'] = {
                'alt_text_missing': analysis.accessibility_metrics.alt_text_missing,
                'aria_labels_missing': analysis.accessibility_metrics.aria_labels_missing,
                'color_contrast_issues': analysis.accessibility_metrics.color_contrast_issues,
                'keyboard_navigation_issues': analysis.accessibility_metrics.keyboard_navigation_issues,
                'form_labels_missing': analysis.accessibility_metrics.form_labels_missing,
                'accessibility_score': float(analysis.accessibility_metrics.accessibility_score)
            }
        
        if analysis.security_metrics:
            metrics['security'] = {
                'has_https': analysis.security_metrics.has_https,
                'has_security_headers': analysis.security_metrics.has_security_headers,
                'vulnerable_libraries': analysis.security_metrics.vulnerable_libraries,
                'mixed_content_issues': analysis.security_metrics.mixed_content_issues,
                'security_score': float(analysis.security_metrics.security_score)
            }
        
        if analysis.ux_metrics:
            metrics['ux'] = {
                'mobile_friendly': analysis.ux_metrics.mobile_friendly,
                'responsive_design': analysis.ux_metrics.responsive_design,
                'readable_font_sizes': analysis.ux_metrics.readable_font_sizes,
                'clear_navigation': analysis.ux_metrics.clear_navigation,
                'ux_score': float(analysis.ux_metrics.ux_score)
            }
        
        data = {
            'id': analysis.id,
            'website': {
                'id': analysis.website.id,
                'url': analysis.website.url,
                'name': analysis.website.name
            },
            'status': analysis.status,
            'analysis_date': analysis.analysis_date.isoformat(),
            'error_message': analysis.error_message,
            'metrics': metrics
        }
        
        return api_response(data=data)
    
    except Exception as e:
        return api_response(error=str(e), status_code=500)

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Получение статистики"""
    try:
        # Базовая статистика
        if current_user.is_admin():
            stats = {
                'total_websites': Website.query.count(),
                'total_analyses': Analysis.query.count(),
                'total_users': User.query.count(),
                'completed_analyses': Analysis.query.filter_by(status='completed').count(),
                'pending_analyses': Analysis.query.filter_by(status='pending').count(),
                'failed_analyses': Analysis.query.filter_by(status='failed').count()
            }
        else:
            stats = {
                'user_websites': Website.query.filter_by(created_by=current_user.id).count(),
                'user_analyses': Analysis.query.filter_by(user_id=current_user.id).count(),
                'completed_analyses': Analysis.query.filter_by(
                    user_id=current_user.id, 
                    status='completed'
                ).count(),
                'pending_analyses': Analysis.query.filter_by(
                    user_id=current_user.id, 
                    status='pending'
                ).count(),
                'failed_analyses': Analysis.query.filter_by(
                    user_id=current_user.id, 
                    status='failed'
                ).count()
            }
        
        return api_response(data=stats)
    
    except Exception as e:
        return api_response(error=str(e), status_code=500)
