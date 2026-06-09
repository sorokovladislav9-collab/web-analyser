"""
Роуты для анализа веб-ресурсов
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from modules.analysis_service import AnalysisService
import logging

logger = logging.getLogger(__name__)

# Создаем Blueprint для анализа
analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')

try:
    analysis_service = AnalysisService()
    ANALYSIS_SERVICE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Ошибка импорта AnalysisService: {e}")
    analysis_service = None
    ANALYSIS_SERVICE_AVAILABLE = False

@analysis_bp.route('/quick-analyze', methods=['GET', 'POST'])
def quick_analyze():
    """Быстрый анализ сайта без регистрации"""
    if request.method == 'GET':
        return render_template('analysis/quick_analyze.html')
    
    try:
        url = request.form.get('url', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not url:
            flash('URL обязателен', 'error')
            return render_template('analysis/quick_analyze.html')
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            flash('Сервис анализа недоступен', 'error')
            return render_template('analysis/quick_analyze.html')
        
        # Прямой анализ без сохранения в базу
        result = analysis_service.analyze_website(url, name, description)
        
        return render_template('analysis/simple_result.html', 
                           analysis=result,
                           url=url,
                           name=name)
        
    except Exception as e:
        logger.error(f"Ошибка при быстром анализе: {e}")
        flash(f'Ошибка при анализе: {str(e)}', 'error')
        return render_template('analysis/quick_analyze.html')

@analysis_bp.route('/start-analysis/<int:website_id>', methods=['POST'])
@login_required
def start_analysis(website_id):
    """Запуск анализа для существующего сайта"""
    try:
        from models import Website, Analysis, db, SEOMetrics, PerformanceMetrics, AccessibilityMetrics, SecurityMetrics, UXMetrics
        from datetime import datetime
        
        website = Website.query.get_or_404(website_id)
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            flash('Сервис анализа недоступен', 'error')
            return redirect(url_for('main.websites'))
        
        # Анализ существующего сайта
        result = analysis_service.analyze_website(website.url, website.name, website.description)
        
        # Сохраняем результаты анализа в базу данных
        analysis = Analysis(
            website_id=website.id,
            user_id=current_user.id,
            status='completed',
            analysis_date=datetime.now()
        )
        
        db.session.add(analysis)
        db.session.flush()  # Получаем ID анализа
        
        # Извлекаем баллы из результатов анализа
        seo_score = result.get('seo_analysis', {}).get('score', 0)
        performance_score = result.get('performance_analysis', {}).get('score', 0)
        security_score = result.get('security_analysis', {}).get('score', 0)
        accessibility_score = result.get('accessibility_analysis', {}).get('score', 0)
        ux_score = result.get('ux_analysis', {}).get('score', 0)
        
        # Создаем SEO метрики
        seo_metrics = SEOMetrics(
            analysis_id=analysis.id,
            score=seo_score
        )
        
        # Создаем метрики производительности
        performance_metrics = PerformanceMetrics(
            analysis_id=analysis.id,
            performance_score=performance_score
        )
        
        # Создаем метрики доступности
        accessibility_metrics = AccessibilityMetrics(
            analysis_id=analysis.id,
            accessibility_score=accessibility_score
        )
        
        # Создаем метрики безопасности
        security_metrics = SecurityMetrics(
            analysis_id=analysis.id,
            security_score=security_score
        )
        
        # Создаем UX метрики
        ux_metrics = UXMetrics(
            analysis_id=analysis.id,
            ux_score=ux_score
        )
        
        db.session.add_all([seo_metrics, performance_metrics, accessibility_metrics, security_metrics, ux_metrics])
        db.session.commit()
        
        flash('Анализ успешно завершен', 'success')
        return redirect(url_for('main.view_analysis', analysis_id=analysis.id))
        
    except Exception as e:
        logger.error(f"Ошибка при запуске анализа: {e}")
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('main.websites'))

@analysis_bp.route('/analyze-website/<int:website_id>', methods=['GET', 'POST'])
@login_required
def analyze_website_start(website_id):
    """Запуск анализа для существующего сайта"""
    try:
        from models import Website, Analysis, db, SEOMetrics, PerformanceMetrics, AccessibilityMetrics, SecurityMetrics, UXMetrics
        from datetime import datetime
        
        website = Website.query.get_or_404(website_id)
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            flash('Сервис анализа недоступен', 'error')
            return redirect(url_for('main.websites'))
        
        # Анализ существующего сайта
        result = analysis_service.analyze_website(website.url, website.name, website.description)
        
        # Сохраняем результаты анализа в базу данных
        analysis = Analysis(
            website_id=website.id,
            user_id=current_user.id,
            status='completed',
            analysis_date=datetime.now()
        )
        
        db.session.add(analysis)
        db.session.flush()  # Получаем ID анализа
        
        # Извлекаем баллы из результатов анализа
        seo_score = result.get('seo_analysis', {}).get('score', 0)
        performance_score = result.get('performance_analysis', {}).get('score', 0)
        security_score = result.get('security_analysis', {}).get('score', 0)
        accessibility_score = result.get('accessibility_analysis', {}).get('score', 0)
        ux_score = result.get('ux_analysis', {}).get('score', 0)
        
        # Создаем SEO метрики
        seo_metrics = SEOMetrics(
            analysis_id=analysis.id,
            score=seo_score
        )
        
        # Создаем метрики производительности
        performance_metrics = PerformanceMetrics(
            analysis_id=analysis.id,
            performance_score=performance_score
        )
        
        # Создаем метрики доступности
        accessibility_metrics = AccessibilityMetrics(
            analysis_id=analysis.id,
            accessibility_score=accessibility_score
        )
        
        # Создаем метрики безопасности
        security_metrics = SecurityMetrics(
            analysis_id=analysis.id,
            security_score=security_score
        )
        
        # Создаем UX метрики
        ux_metrics = UXMetrics(
            analysis_id=analysis.id,
            ux_score=ux_score
        )
        
        db.session.add_all([seo_metrics, performance_metrics, accessibility_metrics, security_metrics, ux_metrics])
        db.session.commit()
        
        flash('Анализ успешно завершен', 'success')
        return redirect(url_for('main.view_analysis', analysis_id=analysis.id))
        
    except Exception as e:
        logger.error(f"Ошибка при запуске анализа: {e}")
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('main.websites'))

@analysis_bp.route('/compare-websites', methods=['GET', 'POST'])
@login_required
def compare_websites():
    """Страница сравнения сайтов"""
    if request.method == 'GET':
        # Получаем сайты из базы данных для выбора
        from models import Website
        if current_user.is_admin():
            websites = Website.query.all()
        else:
            websites = Website.query.filter_by(created_by=current_user.id).all()
        return render_template('analysis/compare.html', websites=websites)
    
    try:
        websites = []
        
        # Отладочное логирование
        logger.info(f"Получены данные формы: {list(request.form.keys())}")
        logger.info(f"website_ids: {request.form.getlist('website_ids')}")
        logger.info(f"urls: {request.form.get('urls', '')}")
        
        # Получаем выбранные сайты из базы данных
        website_ids = request.form.getlist('website_ids')
        if website_ids:
            from models import Website
            for website_id in website_ids:
                website = Website.query.get(website_id)
                if website:
                    websites.append({
                        'id': website.id,
                        'url': website.url,
                        'name': website.name
                    })
        
        # Получаем URL из формы (для ручного ввода)
        urls_text = request.form.get('urls', '').strip()
        if urls_text:
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            
            for i, url in enumerate(urls, 1):
                websites.append({
                    'id': f'new_{i}',
                    'url': url,
                    'name': f'Сайт {i}'
                })
        
        logger.info(f"Всего сайтов для сравнения: {len(websites)}")
        
        if len(websites) < 2:
            flash('Выберите как минимум 2 сайта для сравнения', 'error')
            # Получаем сайты для отображения в списке
            from models import Website
            if current_user.is_admin():
                all_websites = Website.query.all()
            else:
                all_websites = Website.query.filter_by(created_by=current_user.id).all()
            return render_template('analysis/compare.html', websites=all_websites)
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            flash('Сервис анализа недоступен', 'error')
            # Получаем сайты для отображения в списке
            from models import Website
            if current_user.is_admin():
                all_websites = Website.query.all()
            else:
                all_websites = Website.query.filter_by(created_by=current_user.id).all()
            return render_template('analysis/compare.html', websites=all_websites)
        
        # Сравнительный анализ
        print(f"DEBUG: Начинаем сравнение {len(websites)} сайтов: {websites}")
        result = analysis_service.compare_websites(websites)
        print(f"DEBUG: Результат сравнения: {result}")
        
        return render_template('analysis/comparison_result.html', 
                           comparison=result)
        
    except Exception as e:
        logger.error(f"Ошибка при сравнительном анализе: {e}")
        flash(f'Ошибка при сравнении: {str(e)}', 'error')
        # Получаем сайты для отображения в списке
        from models import Website
        if current_user.is_admin():
            all_websites = Website.query.all()
        else:
            all_websites = Website.query.filter_by(created_by=current_user.id).all()
        return render_template('analysis/compare.html', websites=all_websites)

@analysis_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API для анализа сайта"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL обязателен'
            }), 400
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Сервис анализа недоступен'
            }), 503
        
        result = analysis_service.analyze_website(url, name, description)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Ошибка API анализа: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/compare', methods=['POST'])
def api_compare():
    """API для сравнения сайтов"""
    try:
        data = request.get_json()
        websites = data.get('websites', [])
        
        if not websites:
            return jsonify({
                'success': False,
                'error': 'Список сайтов обязателен'
            }), 400
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Сервис анализа недоступен'
            }), 503
        
        result = analysis_service.compare_websites(websites)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Ошибка API сравнения: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/generate_report', methods=['POST'])
def api_generate_report():
    """API для генерации отчета"""
    try:
        data = request.get_json()
        analysis_data = data.get('analysis_data')
        report_type = data.get('report_type', 'html')
        comparison_report = data.get('comparison_report', False)
        
        if not analysis_data:
            return jsonify({
                'success': False,
                'error': 'Данные анализа обязательны'
            }), 400
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Сервис анализа недоступен'
            }), 503
        
        from modules.report_generator import ReportGenerator
        
        report_generator = ReportGenerator()
        report_path = report_generator.generate_report(
            analysis_data, 
            report_type, 
            comparison_report=comparison_report
        )
        
        return jsonify({
            'success': True,
            'report_path': report_path
        })
        
    except Exception as e:
        logger.error(f"Ошибка API генерации отчета: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
