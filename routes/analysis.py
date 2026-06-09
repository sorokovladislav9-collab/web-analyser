"""
Маршруты для анализа веб-ресурсов
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Website, Analysis, SEOMetrics, PerformanceMetrics, AccessibilityMetrics, SecurityMetrics, UXMetrics
from datetime import datetime
import threading
import time
import logging
import json

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

# Импорт основного сервиса анализа
try:
    from modules.analysis_service import AnalysisService
    from modules.report_generator import ReportGenerator
    ANALYSIS_SERVICE_AVAILABLE = True
    analysis_service = AnalysisService()
    report_generator = ReportGenerator()
except ImportError as e:
    logger.error(f"Ошибка импорта сервиса анализа: {e}")
    ANALYSIS_SERVICE_AVAILABLE = False

@analysis_bp.route('/start/<int:website_id>', methods=['POST'])
@login_required
def start_analysis(website_id):
    """Запуск анализа веб-ресурса"""
    try:
        website = Website.query.get_or_404(website_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and website.created_by != current_user.id:
            flash('У вас нет прав для анализа этого ресурса', 'error')
            return redirect(url_for('main.websites'))
        
        # Проверка на уже запущенный анализ
        existing_analysis = Analysis.query.filter_by(
            website_id=website_id,
            status='running'
        ).first()
        
        if existing_analysis:
            flash('Анализ этого ресурса уже запущен', 'warning')
            return redirect(url_for('main.view_website', id=website_id))
        
        # Создание записи об анализе
        analysis = Analysis(
            website_id=website_id,
            status='pending'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        flash('Анализ запущен', 'success')
        return redirect(url_for('main.view_website', id=website_id))
        
    except Exception as e:
        logger.error(f"Ошибка при запуске анализа: {e}")
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('main.websites'))

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

@analysis_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_website():
    """Анализ сайта по URL"""
    try:
        url = request.form.get('url', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not url:
            flash('URL обязателен', 'error')
            return redirect(url_for('main.dashboard'))
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            flash('Сервис анализа недоступен', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Запуск анализа в фоновом потоке
        def run_analysis():
            try:
                with current_app.app_context():
                    result = analysis_service.analyze_website(url, name, description)
                    
                    # Сохранение результатов в базу данных
                    website = Website.query.filter_by(url=url).first()
                    if not website:
                        website = Website(
                            url=url,
                            name=name or url,
                            description=description or '',
                            created_by=current_user.id
                        )
                        db.session.add(website)
                        db.session.commit()
                    
                    # Создание записи анализа
                    analysis = Analysis(
                        website_id=website.id,
                        status='completed',
                        analysis_date=datetime.now(),
                        error_message=result.get('error_message', '')
                    )
                    db.session.add(analysis)
                    
                    # Сохранение метрик
                    if result.get('seo_analysis'):
                        seo_data = result['seo_analysis']
                        seo_metrics = SEOMetrics(
                            analysis_id=analysis.id,
                            score=seo_data.get('score', 0),
                            title=seo_data.get('title_analysis', {}).get('title', ''),
                            meta_description=seo_data.get('meta_description_analysis', {}).get('meta_description', ''),
                            h1_count=seo_data.get('headings_analysis', {}).get('h1_count', 0),
                            h2_count=seo_data.get('headings_analysis', {}).get('h2_count', 0),
                            internal_links=seo_data.get('links_analysis', {}).get('internal_links_count', 0),
                            external_links=seo_data.get('links_analysis', {}).get('external_links_count', 0),
                            word_count=seo_data.get('content_analysis', {}).get('word_count', 0),
                            images_count=seo_data.get('images_analysis', {}).get('images_count', 0),
                            images_without_alt=seo_data.get('images_analysis', {}).get('images_without_alt', 0)
                        )
                        db.session.add(seo_metrics)
                    
                    if result.get('performance_analysis'):
                        perf_data = result['performance_analysis']
                        perf_metrics = PerformanceMetrics(
                            analysis_id=analysis.id,
                            performance_score=perf_data.get('score', 0),
                            load_time_ms=perf_data.get('load_time_analysis', {}).get('load_time_ms', 0),
                            first_contentful_paint_ms=1200,  # Mock данные
                            largest_contentful_paint_ms=2400,  # Mock данные
                            cumulative_layout_shift=0.1,  # Mock данные
                            first_input_delay_ms=50,  # Mock данные
                            time_to_interactive_ms=3500,  # Mock данные
                            total_page_size_kb=1000,  # Mock данные
                            requests_count=20  # Mock данные
                        )
                        db.session.add(perf_metrics)
                    
                    if result.get('security_analysis'):
                        security_data = result['security_analysis']
                        security_metrics = SecurityMetrics(
                            analysis_id=analysis.id,
                            security_score=security_data.get('score', 0),
                            has_https=True,  # Mock данные
                            has_security_headers=True,  # Mock данные
                            vulnerable_libraries=0,  # Mock данные
                            mixed_content_issues=0  # Mock данные
                        )
                        db.session.add(security_metrics)
                    
                    if result.get('accessibility_analysis'):
                        access_data = result['accessibility_analysis']
                        access_metrics = AccessibilityMetrics(
                            analysis_id=analysis.id,
                            accessibility_score=access_data.get('score', 0),
                            alt_text_missing=0,  # Mock данные
                            aria_labels_missing=0,  # Mock данные
                            color_contrast_issues=0,  # Mock данные
                            keyboard_navigation_issues=0,  # Mock данные
                            form_labels_missing=0  # Mock данные
                        )
                        db.session.add(access_metrics)
                    
                    if result.get('ux_analysis'):
                        ux_data = result['ux_analysis']
                        ux_metrics = UXMetrics(
                            analysis_id=analysis.id,
                            ux_score=ux_data.get('score', 0),
                            mobile_friendly=True,  # Mock данные
                            responsive_design=True,  # Mock данные
                            readable_font_sizes=True,  # Mock данные
                            clear_navigation=True  # Mock данные
                        )
                        db.session.add(ux_metrics)
                    
                    db.session.commit()
                    logger.info(f"Анализ сайта {url} завершен и сохранен")
                    
            except Exception as e:
                logger.error(f"Ошибка в фоновом анализе: {e}")
                db.session.rollback()
        
        # Запуск фонового потока
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        
        flash(f'Анализ сайта {url} запущен', 'success')
        return redirect(url_for('main.websites'))
        
    except Exception as e:
        logger.error(f"Ошибка при запуске анализа: {e}")
        flash(f'Ошибка при запуске анализа: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@analysis_bp.route('/compare', methods=['GET', 'POST'])
@login_required
def compare_websites():
    """Сравнительный анализ сайтов"""
    if request.method == 'GET':
        return render_template('analysis/compare.html')
    
    try:
        # Получение списка сайтов для сравнения
        websites_data = []
        
        # Из формы
        if request.form.get('urls'):
            urls = [url.strip() for url in request.form.get('urls', '').split('\n') if url.strip()]
            for i, url in enumerate(urls):
                websites_data.append({
                    'url': url,
                    'name': f'Сайт {i+1}',
                    'description': ''
                })
        
        # Из базы данных
        elif request.form.get('website_ids'):
            website_ids = request.form.getlist('website_ids')
            for website_id in website_ids:
                website = Website.query.get(int(website_id))
                if website:
                    websites_data.append({
                        'url': website.url,
                        'name': website.name,
                        'description': website.description or ''
                    })
        
        if len(websites_data) < 2:
            flash('Для сравнения нужно минимум 2 сайта', 'error')
            return render_template('analysis/compare.html')
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            flash('Сервис анализа недоступен', 'error')
            return render_template('analysis/compare.html')
        
        # Запуск сравнительного анализа
        comparison_result = analysis_service.compare_websites(websites_data)
        
        return render_template('analysis/comparison_result.html', 
                           comparison=comparison_result,
                           websites_count=len(websites_data))
        
    except Exception as e:
        logger.error(f"Ошибка при сравнительном анализе: {e}")
        flash(f'Ошибка при сравнительном анализе: {str(e)}', 'error')
        return render_template('analysis/compare.html')

@analysis_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint для анализа сайта"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL обязателен'}), 400
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            return jsonify({'error': 'Сервис анализа недоступен'}), 503
        
        # Анализ сайта
        result = analysis_service.analyze_website(
            url=url,
            name=data.get('name'),
            description=data.get('description')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Ошибка в API анализе: {e}")
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/api/compare', methods=['POST'])
def api_compare():
    """API endpoint для сравнения сайтов"""
    try:
        data = request.get_json()
        websites = data.get('websites', [])
        
        if len(websites) < 2:
            return jsonify({'error': 'Для сравнения нужно минимум 2 сайта'}), 400
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            return jsonify({'error': 'Сервис анализа недоступен'}), 503
        
        # Сравнительный анализ
        result = analysis_service.compare_websites(websites)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Ошибка в API сравнении: {e}")
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/api/generate_report', methods=['POST'])
def api_generate_report():
    """API endpoint для генерации отчета"""
    try:
        data = request.get_json()
        analysis_data = data.get('analysis_data', {})
        report_type = data.get('report_type', 'html')
        comparison_report = data.get('comparison_report', False)
        
        if not ANALYSIS_SERVICE_AVAILABLE:
            return jsonify({'error': 'Сервис анализа недоступен'}), 503
        
        # Генерация отчета
        report_path = analysis_service.generate_report(
            analysis_data=analysis_data,
            report_type=report_type,
            comparison_report=comparison_report
        )
        
        return jsonify({
            'success': True,
            'report_path': report_path,
            'report_type': report_type
        })
        
    except Exception as e:
        logger.error(f"Ошибка при генерации отчета: {e}")
        return jsonify({'error': str(e)}), 500
        
        # Создание записи об анализе
        analysis = Analysis(
            website_id=website_id,
            user_id=current_user.id,
            status='pending'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Запуск анализа в фоновом потоке
        thread = threading.Thread(
            target=run_analysis,
            args=(analysis.id,)
        )
        thread.daemon = True
        thread.start()
        
        flash('Анализ запущен', 'success')
        return redirect(url_for('analysis.view_analysis', id=analysis.id))
    
    except Exception as e:
        flash(f'Ошибка при запуске анализа: {str(e)}', 'error')
        return redirect(url_for('main.websites'))

@analysis_bp.route('/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """Просмотр результатов анализа"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and analysis.user_id != current_user.id:
            flash('У вас нет прав для просмотра этого анализа', 'error')
            return redirect(url_for('main.dashboard'))
        
        return render_template('analysis/view.html', analysis=analysis)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@analysis_bp.route('/<int:analysis_id>/status')
@login_required
def analysis_status(analysis_id):
    """AJAX endpoint для статуса анализа"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and analysis.user_id != current_user.id:
            return jsonify({'error': 'Доступ запрещен'}), 403
        
        response = {
            'id': analysis.id,
            'status': analysis.status,
            'analysis_date': analysis.analysis_date.isoformat(),
            'error_message': analysis.error_message
        }
        
        # Добавляем метрики если анализ завершен
        if analysis.status == 'completed':
            response['metrics'] = get_analysis_metrics(analysis)
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/batch', methods=['POST'])
@login_required
def batch_analysis():
    """Массовый анализ веб-ресурсов"""
    try:
        website_ids = request.form.getlist('website_ids')
        
        if not website_ids:
            flash('Выберите хотя бы один веб-ресурс', 'error')
            return redirect(url_for('main.websites'))
        
        started_analyses = []
        
        for website_id in website_ids:
            website = Website.query.get(website_id)
            
            if not website:
                continue
            
            # Проверка прав доступа
            if not current_user.is_admin() and website.created_by != current_user.id:
                continue
            
            # Проверка на уже запущенный анализ
            existing_analysis = Analysis.query.filter_by(
                website_id=website_id,
                status='running'
            ).first()
            
            if existing_analysis:
                continue
            
            # Создание записи об анализе
            analysis = Analysis(
                website_id=website_id,
                user_id=current_user.id,
                status='pending'
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            # Запуск анализа в фоновом потоке
            thread = threading.Thread(
                target=run_analysis,
                args=(analysis.id,)
            )
            thread.daemon = True
            thread.start()
            
            started_analyses.append(analysis.id)
        
        flash(f'Запущено {len(started_analyses)} анализов', 'success')
        return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        flash(f'Ошибка при запуске массового анализа: {str(e)}', 'error')
        return redirect(url_for('main.websites'))

def run_analysis(analysis_id):
    """Функция выполнения анализа в фоновом потоке"""
    try:
        # Получаем анализ из базы данных
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return
        
        # Обновляем статус
        analysis.status = 'running'
        db.session.commit()
        
        # Инициализируем сборщик данных
        collector = DataCollector()
        
        # Собираем данные о веб-ресурсе
        data = collector.collect_data(analysis.website.url)
        
        if not data:
            analysis.status = 'failed'
            analysis.error_message = 'Не удалось собрать данные о веб-ресурсе'
            db.session.commit()
            return
        
        # Запускаем анализаторы
        try:
            # SEO анализ
            seo_analyzer = SEOAnalyzer()
            seo_metrics = seo_analyzer.analyze(data)
            
            # Анализ производительности
            perf_analyzer = PerformanceAnalyzer()
            perf_metrics = perf_analyzer.analyze(data)
            
            # Анализ доступности
            access_analyzer = AccessibilityAnalyzer()
            access_metrics = access_analyzer.analyze(data)
            
            # Анализ безопасности
            security_analyzer = SecurityAnalyzer()
            security_metrics = security_analyzer.analyze(data)
            
            # UX анализ
            ux_analyzer = UXAnalyzer()
            ux_metrics = ux_analyzer.analyze(data)
            
            # Сохраняем метрики в базу данных
            save_metrics(analysis, seo_metrics, perf_metrics, access_metrics, security_metrics, ux_metrics)
            
            # Обновляем статус анализа
            analysis.status = 'completed'
            db.session.commit()
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            db.session.commit()
    
    except Exception as e:
        # Логируем ошибку
        print(f"Ошибка при выполнении анализа {analysis_id}: {e}")
        
        try:
            analysis = Analysis.query.get(analysis_id)
            if analysis:
                analysis.status = 'failed'
                analysis.error_message = str(e)
                db.session.commit()
        except:
            pass

def save_metrics(analysis, seo_metrics, perf_metrics, access_metrics, security_metrics, ux_metrics):
    """Сохранение метрик в базу данных"""
    try:
        # SEO метрики
        if seo_metrics:
            seo = SEOMetrics(
                analysis_id=analysis.id,
                title=seo_metrics.get('title'),
                meta_description=seo_metrics.get('meta_description'),
                h1_count=seo_metrics.get('h1_count', 0),
                h2_count=seo_metrics.get('h2_count', 0),
                internal_links=seo_metrics.get('internal_links', 0),
                external_links=seo_metrics.get('external_links', 0),
                word_count=seo_metrics.get('word_count', 0),
                images_count=seo_metrics.get('images_count', 0),
                images_without_alt=seo_metrics.get('images_without_alt', 0),
                score=seo_metrics.get('score', 0)
            )
            db.session.add(seo)
        
        # Метрики производительности
        if perf_metrics:
            perf = PerformanceMetrics(
                analysis_id=analysis.id,
                load_time_ms=perf_metrics.get('load_time_ms', 0),
                first_contentful_paint_ms=perf_metrics.get('first_contentful_paint_ms', 0),
                largest_contentful_paint_ms=perf_metrics.get('largest_contentful_paint_ms', 0),
                cumulative_layout_shift=perf_metrics.get('cumulative_layout_shift', 0),
                first_input_delay_ms=perf_metrics.get('first_input_delay_ms', 0),
                time_to_interactive_ms=perf_metrics.get('time_to_interactive_ms', 0),
                total_page_size_kb=perf_metrics.get('total_page_size_kb', 0),
                requests_count=perf_metrics.get('requests_count', 0),
                performance_score=perf_metrics.get('performance_score', 0)
            )
            db.session.add(perf)
        
        # Метрики доступности
        if access_metrics:
            access = AccessibilityMetrics(
                analysis_id=analysis.id,
                alt_text_missing=access_metrics.get('alt_text_missing', 0),
                aria_labels_missing=access_metrics.get('aria_labels_missing', 0),
                color_contrast_issues=access_metrics.get('color_contrast_issues', 0),
                keyboard_navigation_issues=access_metrics.get('keyboard_navigation_issues', 0),
                form_labels_missing=access_metrics.get('form_labels_missing', 0),
                accessibility_score=access_metrics.get('accessibility_score', 0)
            )
            db.session.add(access)
        
        # Метрики безопасности
        if security_metrics:
            security = SecurityMetrics(
                analysis_id=analysis.id,
                has_https=security_metrics.get('has_https', False),
                has_security_headers=security_metrics.get('has_security_headers', False),
                vulnerable_libraries=security_metrics.get('vulnerable_libraries', 0),
                mixed_content_issues=security_metrics.get('mixed_content_issues', 0),
                security_score=security_metrics.get('security_score', 0)
            )
            db.session.add(security)
        
        # UX метрики
        if ux_metrics:
            ux = UXMetrics(
                analysis_id=analysis.id,
                mobile_friendly=ux_metrics.get('mobile_friendly', False),
                responsive_design=ux_metrics.get('responsive_design', False),
                readable_font_sizes=ux_metrics.get('readable_font_sizes', False),
                clear_navigation=ux_metrics.get('clear_navigation', False),
                ux_score=ux_metrics.get('ux_score', 0)
            )
            db.session.add(ux)
        
        db.session.commit()
    
    except Exception as e:
        print(f"Ошибка при сохранении метрик: {e}")
        raise

def get_analysis_metrics(analysis):
    """Получение метрик анализа"""
    metrics = {}
    
    if analysis.seo_metrics:
        metrics['seo'] = {
            'score': float(analysis.seo_metrics.score),
            'title': analysis.seo_metrics.title,
            'word_count': analysis.seo_metrics.word_count
        }
    
    if analysis.performance_metrics:
        metrics['performance'] = {
            'score': float(analysis.performance_metrics.performance_score),
            'load_time_ms': analysis.performance_metrics.load_time_ms
        }
    
    if analysis.accessibility_metrics:
        metrics['accessibility'] = {
            'score': float(analysis.accessibility_metrics.accessibility_score)
        }
    
    if analysis.security_metrics:
        metrics['security'] = {
            'score': float(analysis.security_metrics.security_score),
            'has_https': analysis.security_metrics.has_https
        }
    
    if analysis.ux_metrics:
        metrics['ux'] = {
            'score': float(analysis.ux_metrics.ux_score),
            'mobile_friendly': analysis.ux_metrics.mobile_friendly
        }
    
    return metrics
