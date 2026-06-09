"""
Маршруты для генерации отчетов
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, Response
from flask_login import login_required, current_user
from models import db, Analysis, Report, Website
from datetime import datetime
import os
import json
import io

reports_bp = Blueprint('reports', __name__)

# Импорт генераторов отчетов
from modules.report_generator import ReportGenerator

@reports_bp.route('/generate/<int:analysis_id>/<format>')
@login_required
def generate_report(analysis_id, format):
    """Генерация отчета для анализа в указанном формате"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and analysis.user_id != current_user.id:
            flash('У вас нет прав для генерации отчета по этому анализу', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Проверка статуса анализа
        if analysis.status != 'completed':
            flash('Отчет можно сгенерировать только для завершенного анализа', 'error')
            return redirect(url_for('main.view_analysis', analysis_id=analysis_id))
        
        # Получаем связанный веб-ресурс
        website = Website.query.get(analysis.website_id)
        
        # Получаем метрики
        seo_score = analysis.seo_metrics.score if analysis.seo_metrics else 0
        performance_score = analysis.performance_metrics.performance_score if analysis.performance_metrics else 0
        security_score = analysis.security_metrics.security_score if analysis.security_metrics else 0
        accessibility_score = analysis.accessibility_metrics.accessibility_score if analysis.accessibility_metrics else 0
        ux_score = analysis.ux_metrics.ux_score if analysis.ux_metrics else 0
        overall_score = (seo_score + performance_score + security_score + accessibility_score + ux_score) / 5
        
        # Подготовка данных для отчета
        report_data = {
            'website': {
                'name': website.name,
                'url': website.url,
                'description': website.description
            },
            'analysis': {
                'date': analysis.analysis_date.strftime('%d.%m.%Y %H:%M'),
                'overall_score': overall_score,
                'seo_score': seo_score,
                'performance_score': performance_score,
                'security_score': security_score,
                'accessibility_score': accessibility_score,
                'ux_score': ux_score
            }
        }
        
        # Генерация отчета в зависимости от формата
        if format == 'txt':
            return _generate_pdf_report(report_data, analysis_id)
        elif format == 'docx':
            return _generate_docx_report(report_data, analysis_id)
        elif format == 'xlsx':
            return _generate_xlsx_report(report_data, analysis_id)
        elif format == 'html':
            return _generate_html_report(report_data, analysis_id)
        elif format == 'json':
            return _generate_json_report(report_data, analysis_id)
        else:
            flash('Неподдерживаемый формат отчета', 'error')
            return redirect(url_for('main.view_analysis', analysis_id=analysis_id))
        
    except Exception as e:
        flash(f'Ошибка при генерации отчета: {str(e)}', 'error')
        return redirect(url_for('main.view_analysis', analysis_id=analysis_id))

def _generate_pdf_report(report_data, analysis_id):
    """Генерация PDF отчета"""
    try:
        # Создаем отчет в базе данных
        report = Report(
            analysis_id=analysis_id,
            report_type='pdf'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Генерируем простой текстовый контент (как заглушку для PDF)
        pdf_content = f"""
Отчет по анализу сайта: {report_data['website']['name']}
URL: {report_data['website']['url']}
Дата анализа: {report_data['analysis']['date']}

РЕЗУЛЬТАТЫ АНАЛИЗА:
Общий балл: {report_data['analysis']['overall_score']:.1f}/100
SEO балл: {report_data['analysis']['seo_score']:.1f}/100
Производительность: {report_data['analysis']['performance_score']:.1f}/100
Безопасность: {report_data['analysis']['security_score']:.1f}/100
Доступность: {report_data['analysis']['accessibility_score']:.1f}/100
UX: {report_data['analysis']['ux_score']:.1f}/100

Примечание: Для полноценного PDF отчета требуется установить библиотеку reportlab
        """.encode('utf-8')
        
        # Создаем директорию для отчетов если она не существует
        os.makedirs('reports', exist_ok=True)
        
        # Сохраняем путь к файлу
        file_path = f"reports/report_{report.id}.txt"
        report.file_path = file_path
        db.session.commit()
        
        # Создаем файл на диске
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(pdf_content)
        
        # Возвращаем файл для скачивания
        return send_file(
            file_path,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f"report_{report_data['website']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
    except Exception as e:
        flash(f'Ошибка при генерации PDF: {str(e)}', 'error')
        return redirect(url_for('main.view_analysis', analysis_id=analysis_id))

def _generate_docx_report(report_data, analysis_id):
    """Генерация DOCX отчета"""
    try:
        # Создаем отчет в базе данных
        report = Report(
            analysis_id=analysis_id,
            report_type='docx'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Генерируем простой DOCX-подобный контент
        docx_content = f"""
        Отчет по анализу сайта: {report_data['website']['name']}
        URL: {report_data['website']['url']}
        Дата анализа: {report_data['analysis']['date']}
        
        Результаты анализа:
        Общий балл: {report_data['analysis']['overall_score']:.1f}/100
        SEO балл: {report_data['analysis']['seo_score']:.1f}/100
        Производительность: {report_data['analysis']['performance_score']:.1f}/100
        Безопасность: {report_data['analysis']['security_score']:.1f}/100
        Доступность: {report_data['analysis']['accessibility_score']:.1f}/100
        UX: {report_data['analysis']['ux_score']:.1f}/100
        
        Для полноценного DOCX отчета требуется установить библиотеку python-docx
        """.encode('utf-8')
        
        # Создаем директорию для отчетов если она не существует
        os.makedirs('reports', exist_ok=True)
        
        # Сохраняем путь к файлу
        file_path = f"reports/report_{report.id}.docx"
        report.file_path = file_path
        db.session.commit()
        
        # Создаем файл на диске
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(docx_content)
        
        # Возвращаем файл для скачивания
        return send_file(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f"report_{report_data['website']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        )
        
    except Exception as e:
        flash(f'Ошибка при генерации DOCX: {str(e)}', 'error')
        return redirect(url_for('main.view_analysis', analysis_id=analysis_id))

def _generate_xlsx_report(report_data, analysis_id):
    """Генерация XLSX отчета"""
    try:
        # Создаем отчет в базе данных
        report = Report(
            analysis_id=analysis_id,
            report_type='xlsx'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Генерируем простой CSV-подобный контент (как XLSX)
        xlsx_content = f"""
        Отчет по анализу сайта: {report_data['website']['name']}
        URL: {report_data['website']['url']}
        Дата анализа: {report_data['analysis']['date']}
        
        Метрика,Балл
        Общий балл,{report_data['analysis']['overall_score']:.1f}
        SEO балл,{report_data['analysis']['seo_score']:.1f}
        Производительность,{report_data['analysis']['performance_score']:.1f}
        Безопасность,{report_data['analysis']['security_score']:.1f}
        Доступность,{report_data['analysis']['accessibility_score']:.1f}
        UX,{report_data['analysis']['ux_score']:.1f}
        
        Для полноценного XLSX отчета требуется установить библиотеку openpyxl
        """.encode('utf-8')
        
        # Создаем директорию для отчетов если она не существует
        os.makedirs('reports', exist_ok=True)
        
        # Сохраняем путь к файлу
        file_path = f"reports/report_{report.id}.xlsx"
        report.file_path = file_path
        db.session.commit()
        
        # Создаем файл на диске
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xlsx_content)
        
        # Возвращаем файл для скачивания
        return send_file(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"report_{report_data['website']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
    except Exception as e:
        flash(f'Ошибка при генерации XLSX: {str(e)}', 'error')
        return redirect(url_for('main.view_analysis', analysis_id=analysis_id))

def _generate_json_report(report_data, analysis_id):
    """Генерация JSON отчета"""
    try:
        # Создаем отчет в базе данных
        report = Report(
            analysis_id=analysis_id,
            report_type='json'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Конвертируем Decimal в float для JSON сериализации
        json_report_data = {
            'website': report_data['website'],
            'analysis': {
                'date': report_data['analysis']['date'],
                'overall_score': float(report_data['analysis']['overall_score']),
                'seo_score': float(report_data['analysis']['seo_score']),
                'performance_score': float(report_data['analysis']['performance_score']),
                'security_score': float(report_data['analysis']['security_score']),
                'accessibility_score': float(report_data['analysis']['accessibility_score']),
                'ux_score': float(report_data['analysis']['ux_score'])
            }
        }
        
        # Генерируем JSON контент
        json_content = json.dumps(json_report_data, ensure_ascii=False, indent=2)
        
        # Создаем директорию для отчетов если она не существует
        os.makedirs('reports', exist_ok=True)
        
        # Сохраняем путь к файлу
        file_path = f"reports/report_{report.id}.json"
        report.file_path = file_path
        db.session.commit()
        
        # Создаем файл на диске
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
        
        # Возвращаем файл для скачивания
        return send_file(
            file_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=f"report_{report_data['website']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
    except Exception as e:
        flash(f'Ошибка при генерации JSON: {str(e)}', 'error')
        return redirect(url_for('main.view_analysis', analysis_id=analysis_id))

def _generate_html_report(report_data, analysis_id):
    """Генерация HTML отчета"""
    try:
        # Создаем отчет в базе данных
        report = Report(
            analysis_id=analysis_id,
            report_type='html'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Генерируем простой HTML контент
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Отчет по анализу {report_data['website']['name']}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>Отчет по анализу сайта</h1>
                <h2>{report_data['website']['name']}</h2>
                <p><strong>URL:</strong> {report_data['website']['url']}</p>
                <p><strong>Дата анализа:</strong> {report_data['analysis']['date']}</p>
                
                <h3>Результаты анализа</h3>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Общий балл:</strong> {report_data['analysis']['overall_score']:.1f}/100</p>
                        <p><strong>SEO балл:</strong> {report_data['analysis']['seo_score']:.1f}/100</p>
                        <p><strong>Производительность:</strong> {report_data['analysis']['performance_score']:.1f}/100</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Безопасность:</strong> {report_data['analysis']['security_score']:.1f}/100</p>
                        <p><strong>Доступность:</strong> {report_data['analysis']['accessibility_score']:.1f}/100</p>
                        <p><strong>UX:</strong> {report_data['analysis']['ux_score']:.1f}/100</p>
                    </div>
                </div>
                
                <div class="mt-4">
                    <p><em>Отчет сгенерирован системой анализа веб-ресурсов</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Создаем директорию для отчетов если она не существует
        os.makedirs('reports', exist_ok=True)
        
        # Сохраняем путь к файлу
        file_path = f"reports/report_{report.id}.html"
        report.file_path = file_path
        db.session.commit()
        
        # Создаем файл на диске
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Возвращаем HTML страницу
        return send_file(
            file_path,
            mimetype='text/html',
            as_attachment=True,
            download_name=f"report_{report_data['website']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
    except Exception as e:
        flash(f'Ошибка при генерации HTML: {str(e)}', 'error')
        return redirect(url_for('main.view_analysis', analysis_id=analysis_id))

@reports_bp.route('/generate_comparison_report', methods=['POST'])
@login_required
def generate_comparison_report():
    """Генерация отчета сравнения"""
    try:
        data = request.get_json()
        comparison_data = data.get('comparison_data')
        format = data.get('format')
        
        if not comparison_data or not format:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
        
        # Подготовка данных для отчета
        report_data = {
            'comparison': comparison_data,
            'websites_count': len(comparison_data.get('overall_scores', {})),
            'analysis_date': comparison_data.get('analysis_date'),
            'total_duration': comparison_data.get('total_duration')
        }
        
        # Генерация отчета в зависимости от формата
        if format == 'txt':
            return _generate_comparison_pdf_report(report_data)
        elif format == 'docx':
            return _generate_comparison_docx_report(report_data)
        elif format == 'xlsx':
            return _generate_comparison_xlsx_report(report_data)
        elif format == 'html':
            return _generate_comparison_html_report(report_data)
        elif format == 'json':
            return _generate_comparison_json_report(report_data)
        else:
            return jsonify({'error': 'Неподдерживаемый формат отчета'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _generate_comparison_pdf_report(report_data):
    """Генерация PDF отчета сравнения"""
    try:
        # Генерируем простой текстовый контент для отчета сравнения
        comparison = report_data['comparison']
        
        pdf_content = f"""
Отчет сравнения веб-ресурсов
Количество сайтов: {report_data['websites_count']}
Дата анализа: {comparison.get('analysis_date', 'N/A')}

РЕЗУЛЬТАТЫ СРАВНЕНИЯ:
"""
        
        # Добавляем данные по каждому сайту
        overall_scores = comparison.get('overall_scores', {})
        for site_id, site_data in overall_scores.items():
            pdf_content += f"""
Сайт: {site_data.get('url', 'N/A')}
Общий балл: {site_data.get('overall_score', 0):.1f}/100
SEO балл: {site_data.get('seo_score', 0):.1f}/100
Производительность: {site_data.get('performance_score', 0):.1f}/100
Безопасность: {site_data.get('security_score', 0):.1f}/100
Доступность: {site_data.get('accessibility_score', 0):.1f}/100
UX: {site_data.get('ux_score', 0):.1f}/100
---
"""
        
        pdf_content += "\nПримечание: Для полноценного PDF отчета требуется установить библиотеку reportlab"
        
        # Возвращаем файл для скачивания как текстовый с правильным расширением
        return send_file(
            io.BytesIO(pdf_content.encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
    except Exception as e:
        return jsonify({'error': f'Ошибка при генерации PDF: {str(e)}'}), 500

def _generate_comparison_docx_report(report_data):
    """Генерация DOCX отчета сравнения"""
    try:
        # Генерируем простой текстовый контент для отчета сравнения
        comparison = report_data['comparison']
        
        docx_content = f"""
Отчет сравнения веб-ресурсов
Количество сайтов: {report_data['websites_count']}
Дата анализа: {comparison.get('analysis_date', 'N/A')}

РЕЗУЛЬТАТЫ СРАВНЕНИЯ:
"""
        
        # Добавляем данные по каждому сайту
        overall_scores = comparison.get('overall_scores', {})
        for site_id, site_data in overall_scores.items():
            docx_content += f"""
Сайт: {site_data.get('url', 'N/A')}
Общий балл: {site_data.get('overall_score', 0):.1f}/100
SEO балл: {site_data.get('seo_score', 0):.1f}/100
Производительность: {site_data.get('performance_score', 0):.1f}/100
Безопасность: {site_data.get('security_score', 0):.1f}/100
Доступность: {site_data.get('accessibility_score', 0):.1f}/100
UX: {site_data.get('ux_score', 0):.1f}/100
---
"""
        
        docx_content += "\nПримечание: Для полноценного DOCX отчета требуется установить библиотеку python-docx"
        
        # Возвращаем файл для скачивания как текстовый
        return send_file(
            io.BytesIO(docx_content.encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
    except Exception as e:
        return jsonify({'error': f'Ошибка при генерации DOCX: {str(e)}'}), 500

def _generate_comparison_xlsx_report(report_data):
    """Генерация XLSX отчета сравнения"""
    try:
        # Генерируем CSV-подобный контент для отчета сравнения
        comparison = report_data['comparison']
        
        xlsx_content = f"""
Отчет сравнения веб-ресурсов
Количество сайтов: {report_data['websites_count']}
Дата анализа: {comparison.get('analysis_date', 'N/A')}

Сайт,Общий балл,SEO балл,Производительность,Безопасность,Доступность,UX
"""
        
        # Добавляем данные по каждому сайту
        overall_scores = comparison.get('overall_scores', {})
        for site_id, site_data in overall_scores.items():
            xlsx_content += f"""
{site_data.get('url', 'N/A')},{site_data.get('overall_score', 0):.1f},{site_data.get('seo_score', 0):.1f},{site_data.get('performance_score', 0):.1f},{site_data.get('security_score', 0):.1f},{site_data.get('accessibility_score', 0):.1f},{site_data.get('ux_score', 0):.1f}
"""
        
        xlsx_content += "\nПримечание: Для полноценного XLSX отчета требуется установить библиотеку openpyxl"
        
        # Возвращаем файл для скачивания как текстовый
        return send_file(
            io.BytesIO(xlsx_content.encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
    except Exception as e:
        
        if report_type not in ['html', 'pdf', 'json']:
            flash('Неподдерживаемый тип отчета', 'error')
            return redirect(url_for('analysis.view_analysis', id=analysis_id))
        
        # Проверка на существующий отчет
        existing_report = Report.query.filter_by(
            analysis_id=analysis_id,
            report_type=report_type
        ).first()
        
        if existing_report and os.path.exists(existing_report.file_path):
            flash('Отчет этого типа уже существует', 'info')
            return redirect(url_for('reports.view_report', id=existing_report.id))
        
        # Генерация отчета
        generator = ReportGenerator()
        file_path = generator.generate_report(analysis, report_type)
        
        if not file_path:
            flash('Ошибка при генерации отчета', 'error')
            return redirect(url_for('analysis.view_analysis', id=analysis_id))
        
        # Сохранение информации об отчете
        report = Report(
            analysis_id=analysis_id,
            report_type=report_type,
            file_path=file_path
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Отчет успешно сгенерирован', 'success')
        return redirect(url_for('reports.view_report', id=report.id))
    
    except Exception as e:
        flash(f'Ошибка при генерации отчета: {str(e)}', 'error')
        return redirect(url_for('analysis.view_analysis', id=analysis_id))

@reports_bp.route('/view/<int:report_id>')
@login_required
def view_report(report_id):
    """Просмотр отчета"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and report.analysis.user_id != current_user.id:
            flash('У вас нет прав для просмотра этого отчета', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Проверка существования файла
        if not os.path.exists(report.file_path):
            flash('Файл отчета не найден', 'error')
            return redirect(url_for('main.dashboard'))
        
        if report.report_type == 'html':
            # Открываем HTML отчет в браузере
            return send_file(report.file_path, mimetype='text/html')
        
        elif report.report_type == 'pdf':
            # Скачиваем PDF отчет
            return send_file(
                report.file_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'report_{report.id}.pdf'
            )
        
        elif report.report_type == 'json':
            # Открываем JSON отчет
            return send_file(report.file_path, mimetype='application/json')
        
        else:
            flash('Неподдерживаемый тип отчета', 'error')
            return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        flash(f'Ошибка при просмотре отчета: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@reports_bp.route('/list')
@login_required
def list_reports():
    """Список отчетов"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        query = Report.query.join(Analysis).join(Website)
        
        # Фильтрация для обычных пользователей
        if not current_user.is_admin():
            query = query.filter(Analysis.user_id == current_user.id)
        
        # Фильтрация по типу отчета
        report_type = request.args.get('type')
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        # Пагинация
        reports = query.order_by(Report.generated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('reports/list.html', reports=reports, current_type=report_type)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@reports_bp.route('/download/<int:report_id>')
@login_required
def download_report(report_id):
    """Скачивание отчета"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and report.analysis.user_id != current_user.id:
            flash('У вас нет прав для скачивания этого отчета', 'error')
            return redirect(url_for('reports.list_reports'))
        
        if not report.file_path or not os.path.exists(report.file_path):
            flash('Файл отчета не найден', 'error')
            return redirect(url_for('reports.list_reports'))
        
        # Определяем MIME тип в зависимости от формата отчета
        if report.report_type == 'txt':
            mimetype = 'text/plain'
        elif report.report_type == 'pdf':
            mimetype = 'application/pdf'
        elif report.report_type == 'docx':
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif report.report_type == 'xlsx':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif report.report_type == 'html':
            mimetype = 'text/html'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(
            report.file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"report_{report.id}_{report.generated_at.strftime('%Y%m%d_%H%M%S')}.{report.report_type}"
        )
    
    except Exception as e:
        flash(f'Ошибка при скачивании отчета: {str(e)}', 'error')
        return redirect(url_for('reports.list_reports'))

@reports_bp.route('/delete/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    """Удаление отчета"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and report.analysis.user_id != current_user.id:
            flash('У вас нет прав для удаления этого отчета', 'error')
            return redirect(url_for('reports.list_reports'))
        
        # Удаление файла
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)
        
        # Удаление записи из базы данных
        db.session.delete(report)
        db.session.commit()
        
        flash('Отчет успешно удален', 'success')
        return redirect(url_for('reports.list_reports'))
    
    except Exception as e:
        flash(f'Ошибка при удалении отчета: {str(e)}', 'error')
        return redirect(url_for('reports.list_reports'))

@reports_bp.route('/compare')
@login_required
def compare_reports():
    """Сравнение отчетов"""
    try:
        analysis_ids = request.args.get('analysis_ids', '').split(',')
        analysis_ids = [int(id) for id in analysis_ids if id.isdigit()]
        
        if len(analysis_ids) < 2:
            flash('Выберите хотя бы два анализа для сравнения', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Получаем анализы
        analyses = Analysis.query.filter(Analysis.id.in_(analysis_ids)).all()
        
        # Проверка прав доступа
        for analysis in analyses:
            if not current_user.is_admin() and analysis.user_id != current_user.id:
                flash('У вас нет прав для просмотра некоторых из выбранных анализов', 'error')
                return redirect(url_for('main.dashboard'))
        
        # Проверка статуса анализов
        for analysis in analyses:
            if analysis.status != 'completed':
                flash('Все анализы должны быть завершены для сравнения', 'error')
                return redirect(url_for('main.dashboard'))
        
        # Формируем данные для сравнения
        comparison_data = []
        
        for analysis in analyses:
            data = {
                'website': {
                    'id': analysis.website.id,
                    'url': analysis.website.url,
                    'name': analysis.website.name
                },
                'analysis_date': analysis.analysis_date.isoformat(),
                'metrics': {}
            }
            
            # Собираем метрики
            if analysis.seo_metrics:
                data['metrics']['seo'] = {
                    'score': float(analysis.seo_metrics.score),
                    'title_length': len(analysis.seo_metrics.title) if analysis.seo_metrics.title else 0,
                    'description_length': len(analysis.seo_metrics.meta_description) if analysis.seo_metrics.meta_description else 0,
                    'h1_count': analysis.seo_metrics.h1_count,
                    'h2_count': analysis.seo_metrics.h2_count,
                    'word_count': analysis.seo_metrics.word_count,
                    'images_count': analysis.seo_metrics.images_count,
                    'images_without_alt': analysis.seo_metrics.images_without_alt
                }
            
            if analysis.performance_metrics:
                data['metrics']['performance'] = {
                    'score': float(analysis.performance_metrics.performance_score),
                    'load_time_ms': analysis.performance_metrics.load_time_ms,
                    'first_contentful_paint_ms': analysis.performance_metrics.first_contentful_paint_ms,
                    'largest_contentful_paint_ms': analysis.performance_metrics.largest_contentful_paint_ms,
                    'total_page_size_kb': analysis.performance_metrics.total_page_size_kb,
                    'requests_count': analysis.performance_metrics.requests_count
                }
            
            if analysis.accessibility_metrics:
                data['metrics']['accessibility'] = {
                    'score': float(analysis.accessibility_metrics.accessibility_score),
                    'alt_text_missing': analysis.accessibility_metrics.alt_text_missing,
                    'aria_labels_missing': analysis.accessibility_metrics.aria_labels_missing,
                    'color_contrast_issues': analysis.accessibility_metrics.color_contrast_issues
                }
            
            if analysis.security_metrics:
                data['metrics']['security'] = {
                    'score': float(analysis.security_metrics.security_score),
                    'has_https': analysis.security_metrics.has_https,
                    'has_security_headers': analysis.security_metrics.has_security_headers,
                    'vulnerable_libraries': analysis.security_metrics.vulnerable_libraries
                }
            
            if analysis.ux_metrics:
                data['metrics']['ux'] = {
                    'score': float(analysis.ux_metrics.ux_score),
                    'mobile_friendly': analysis.ux_metrics.mobile_friendly,
                    'responsive_design': analysis.ux_metrics.responsive_design,
                    'readable_font_sizes': analysis.ux_metrics.readable_font_sizes
                }
            
            comparison_data.append(data)
        
        return render_template('reports/compare.html', analyses=comparison_data)
    
    except Exception as e:
        flash(f'Ошибка при сравнении отчетов: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@reports_bp.route('/export/<int:analysis_id>/<format>')
@login_required
def export_analysis(analysis_id, format):
    """Экспорт данных анализа"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Проверка прав доступа
        if not current_user.is_admin() and analysis.user_id != current_user.id:
            return jsonify({'error': 'Доступ запрещен'}), 403
        
        if format not in ['csv', 'json']:
            return jsonify({'error': 'Неподдерживаемый формат'}), 400
        
        # Получаем данные анализа
        data = get_analysis_export_data(analysis)
        
        if format == 'json':
            # Генерация JSON
            filename = f'analysis_{analysis_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            filepath = os.path.join('exports', filename)
            
            os.makedirs('exports', exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif format == 'csv':
            # Генерация CSV
            import pandas as pd
            
            # Преобразование данных в DataFrame
            df_data = []
            
            # SEO метрики
            if analysis.seo_metrics:
                df_data.append({
                    'category': 'SEO',
                    'metric': 'Score',
                    'value': float(analysis.seo_metrics.score),
                    'unit': 'points'
                })
                df_data.append({
                    'category': 'SEO',
                    'metric': 'Word Count',
                    'value': analysis.seo_metrics.word_count,
                    'unit': 'words'
                })
            
            # Метрики производительности
            if analysis.performance_metrics:
                df_data.append({
                    'category': 'Performance',
                    'metric': 'Score',
                    'value': float(analysis.performance_metrics.performance_score),
                    'unit': 'points'
                })
                df_data.append({
                    'category': 'Performance',
                    'metric': 'Load Time',
                    'value': analysis.performance_metrics.load_time_ms,
                    'unit': 'ms'
                })
            
            # Метрики доступности
            if analysis.accessibility_metrics:
                df_data.append({
                    'category': 'Accessibility',
                    'metric': 'Score',
                    'value': float(analysis.accessibility_metrics.accessibility_score),
                    'unit': 'points'
                })
            
            # Метрики безопасности
            if analysis.security_metrics:
                df_data.append({
                    'category': 'Security',
                    'metric': 'Score',
                    'value': float(analysis.security_metrics.security_score),
                    'unit': 'points'
                })
            
            # UX метрики
            if analysis.ux_metrics:
                df_data.append({
                    'category': 'UX',
                    'metric': 'Score',
                    'value': float(analysis.ux_metrics.ux_score),
                    'unit': 'points'
                })
            
            df = pd.DataFrame(df_data)
            
            filename = f'analysis_{analysis_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            filepath = os.path.join('exports', filename)
            
            os.makedirs('exports', exist_ok=True)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            return send_file(filepath, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_analysis_export_data(analysis):
    """Получение данных анализа для экспорта"""
    data = {
        'website': {
            'id': analysis.website.id,
            'url': analysis.website.url,
            'name': analysis.website.name,
            'description': analysis.website.description,
            'category': analysis.website.category
        },
        'analysis': {
            'id': analysis.id,
            'status': analysis.status,
            'analysis_date': analysis.analysis_date.isoformat(),
            'error_message': analysis.error_message
        },
        'metrics': {}
    }
    
    # Собираем все метрики
    if analysis.seo_metrics:
        data['metrics']['seo'] = {
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
        data['metrics']['performance'] = {
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
        data['metrics']['accessibility'] = {
            'alt_text_missing': analysis.accessibility_metrics.alt_text_missing,
            'aria_labels_missing': analysis.accessibility_metrics.aria_labels_missing,
            'color_contrast_issues': analysis.accessibility_metrics.color_contrast_issues,
            'keyboard_navigation_issues': analysis.accessibility_metrics.keyboard_navigation_issues,
            'form_labels_missing': analysis.accessibility_metrics.form_labels_missing,
            'accessibility_score': float(analysis.accessibility_metrics.accessibility_score)
        }
    
    if analysis.security_metrics:
        data['metrics']['security'] = {
            'has_https': analysis.security_metrics.has_https,
            'has_security_headers': analysis.security_metrics.has_security_headers,
            'vulnerable_libraries': analysis.security_metrics.vulnerable_libraries,
            'mixed_content_issues': analysis.security_metrics.mixed_content_issues,
            'security_score': float(analysis.security_metrics.security_score)
        }
    
    if analysis.ux_metrics:
        data['metrics']['ux'] = {
            'mobile_friendly': analysis.ux_metrics.mobile_friendly,
            'responsive_design': analysis.ux_metrics.responsive_design,
            'readable_font_sizes': analysis.ux_metrics.readable_font_sizes,
            'clear_navigation': analysis.ux_metrics.clear_navigation,
            'ux_score': float(analysis.ux_metrics.ux_score)
        }
    
    return data

def _generate_comparison_html_report(report_data):
    """Генерация HTML отчета сравнения"""
    try:
        # Генерируем HTML контент для отчета сравнения
        comparison = report_data['comparison']
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Отчет сравнения веб-ресурсов</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>Отчет сравнения веб-ресурсов</h1>
                <p><strong>Количество сайтов:</strong> {report_data['websites_count']}</p>
                <p><strong>Дата анализа:</strong> {comparison.get('analysis_date', 'N/A')}</p>
                
                <h3>Результаты сравнения</h3>
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <thead class="table-dark">
                            <tr>
                                <th>Сайт</th>
                                <th>Общий балл</th>
                                <th>SEO</th>
                                <th>Производительность</th>
                                <th>Безопасность</th>
                                <th>Доступность</th>
                                <th>UX</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Добавляем данные по каждому сайту
        overall_scores = comparison.get('overall_scores', {})
        for site_id, site_data in overall_scores.items():
            html_content += f"""
                            <tr>
                                <td>{site_data.get('url', 'N/A')}</td>
                                <td>{site_data.get('overall_score', 0):.1f}</td>
                                <td>{site_data.get('seo_score', 0):.1f}</td>
                                <td>{site_data.get('performance_score', 0):.1f}</td>
                                <td>{site_data.get('security_score', 0):.1f}</td>
                                <td>{site_data.get('accessibility_score', 0):.1f}</td>
                                <td>{site_data.get('ux_score', 0):.1f}</td>
                            </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-4">
                    <p><em>Отчет сгенерирован системой анализа веб-ресурсов</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Возвращаем HTML страницу
        return Response(html_content, mimetype='text/html')
        
    except Exception as e:
        return jsonify({'error': f'Ошибка при генерации HTML: {str(e)}'}), 500

def _generate_comparison_json_report(report_data):
    """Генерация JSON отчета сравнения"""
    try:
        # Конвертируем Decimal в float для JSON сериализации
        comparison = report_data['comparison']
        overall_scores = comparison.get('overall_scores', {})
        
        # Конвертируем все баллы в float
        json_comparison_data = {
            'websites_count': report_data['websites_count'],
            'analysis_date': comparison.get('analysis_date'),
            'websites': []
        }
        
        for site_id, site_data in overall_scores.items():
            json_site_data = {
                'url': site_data.get('url', 'N/A'),
                'overall_score': float(site_data.get('overall_score', 0)),
                'seo_score': float(site_data.get('seo_score', 0)),
                'performance_score': float(site_data.get('performance_score', 0)),
                'security_score': float(site_data.get('security_score', 0)),
                'accessibility_score': float(site_data.get('accessibility_score', 0)),
                'ux_score': float(site_data.get('ux_score', 0))
            }
            json_comparison_data['websites'].append(json_site_data)
        
        # Генерируем JSON контент
        json_content = json.dumps(json_comparison_data, ensure_ascii=False, indent=2)
        
        # Возвращаем файл для скачивания
        return send_file(
            io.BytesIO(json_content.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
    except Exception as e:
        return jsonify({'error': f'Ошибка при генерации JSON: {str(e)}'}), 500
