"""
Модуль для генерации отчетов
"""
import os
import json
from datetime import datetime
from jinja2 import Template
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Класс для генерации отчетов"""
    
    def __init__(self):
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_report(self, analysis, report_type='html') -> str:
        """
        Генерация отчета
        
        Args:
            analysis: Объект анализа из базы данных
            report_type: Тип отчета ('html', 'pdf', 'json')
            
        Returns:
            Путь к сгенерированному файлу
        """
        try:
            logger.info(f"Генерация {report_type} отчета для анализа {analysis.id}")
            
            # Сбор данных для отчета
            report_data = self._collect_report_data(analysis)
            
            if report_type == 'html':
                return self._generate_html_report(report_data)
            elif report_type == 'pdf':
                return self._generate_pdf_report(report_data)
            elif report_type == 'json':
                return self._generate_json_report(report_data)
            else:
                raise ValueError(f"Неподдерживаемый тип отчета: {report_type}")
        
        except Exception as e:
            logger.error(f"Ошибка при генерации отчета: {e}")
            raise
    
    def _collect_report_data(self, analysis) -> dict:
        """Сбор данных для отчета"""
        data = {
            'analysis': {
                'id': analysis.id,
                'status': analysis.status,
                'analysis_date': analysis.analysis_date.strftime('%d.%m.%Y %H:%M:%S'),
                'error_message': analysis.error_message
            },
            'website': {
                'id': analysis.website.id,
                'url': analysis.website.url,
                'name': analysis.website.name,
                'description': analysis.website.description,
                'category': analysis.website.category
            },
            'metrics': {},
            'summary': {},
            'recommendations': [],
            'generated_at': datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        }
        
        # Собираем метрики
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
        
        # Генерируем сводку и рекомендации
        data['summary'] = self._generate_summary(data['metrics'])
        data['recommendations'] = self._generate_recommendations(data['metrics'])
        
        return data
    
    def _generate_html_report(self, data: dict) -> str:
        """Генерация HTML отчета"""
        template_str = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет анализа {{ website.name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .metric-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .score { font-size: 24px; font-weight: bold; }
        .score.excellent { color: #28a745; }
        .score.good { color: #17a2b8; }
        .score.fair { color: #ffc107; }
        .score.poor { color: #dc3545; }
        .recommendations { background-color: #f8f9fa; padding: 20px; border-radius: 8px; }
        .recommendation-item { margin-bottom: 10px; padding-left: 20px; position: relative; }
        .recommendation-item:before { content: "•"; position: absolute; left: 0; color: #007bff; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Отчет анализа веб-ресурса</h1>
        <h2>{{ website.name }}</h2>
        <p><strong>URL:</strong> {{ website.url }}</p>
        <p><strong>Дата анализа:</strong> {{ analysis.analysis_date }}</p>
        <p><strong>Дата генерации отчета:</strong> {{ generated_at }}</p>
    </div>

    {% if website.description %}
    <div class="section">
        <h3>Описание</h3>
        <p>{{ website.description }}</p>
    </div>
    {% endif %}

    <div class="section">
        <h3>Общая оценка</h3>
        <div class="metric-card">
            <div class="score {{ summary.overall_score_class }}">{{ summary.overall_score }}/100</div>
            <p>{{ summary.overall_assessment }}</p>
        </div>
    </div>

    <div class="section">
        <h3>Метрики по категориям</h3>
        
        {% if metrics.seo %}
        <div class="metric-card">
            <h4>SEO оптимизация</h4>
            <div class="score {{ metrics.seo.score_class }}">{{ "%.1f"|format(metrics.seo.score) }}/100</div>
            <ul>
                <li>Заголовок: {{ metrics.seo.title or 'Отсутствует' }}</li>
                <li>Количество слов: {{ metrics.seo.word_count }}</li>
                <li>Внутренних ссылок: {{ metrics.seo.internal_links }}</li>
                <li>Внешних ссылок: {{ metrics.seo.external_links }}</li>
                <li>Изображений без alt: {{ metrics.seo.images_without_alt }}</li>
            </ul>
        </div>
        {% endif %}

        {% if metrics.performance %}
        <div class="metric-card">
            <h4>Производительность</h4>
            <div class="score {{ metrics.performance.performance_score_class }}">{{ "%.1f"|format(metrics.performance.performance_score) }}/100</div>
            <ul>
                <li>Время загрузки: {{ metrics.performance.load_time_ms }} мс</li>
                <li>First Contentful Paint: {{ metrics.performance.first_contentful_paint_ms }} мс</li>
                <li>Largest Contentful Paint: {{ metrics.performance.largest_contentful_paint_ms }} мс</li>
                <li>Размер страницы: {{ metrics.performance.total_page_size_kb }} КБ</li>
                <li>Количество запросов: {{ metrics.performance.requests_count }}</li>
            </ul>
        </div>
        {% endif %}

        {% if metrics.accessibility %}
        <div class="metric-card">
            <h4>Доступность</h4>
            <div class="score {{ metrics.accessibility.accessibility_score_class }}">{{ "%.1f"|format(metrics.accessibility.accessibility_score) }}/100</div>
            <ul>
                <li>Изображений без alt-текста: {{ metrics.accessibility.alt_text_missing }}</li>
                <li>Отсутствующих ARIA-меток: {{ metrics.accessibility.aria_labels_missing }}</li>
                <li>Проблем с контрастностью: {{ metrics.accessibility.color_contrast_issues }}</li>
                <li>Проблем с навигацией: {{ metrics.accessibility.keyboard_navigation_issues }}</li>
            </ul>
        </div>
        {% endif %}

        {% if metrics.security %}
        <div class="metric-card">
            <h4>Безопасность</h4>
            <div class="score {{ metrics.security.security_score_class }}">{{ "%.1f"|format(metrics.security.security_score) }}/100</div>
            <ul>
                <li>HTTPS: {{ 'Да' if metrics.security.has_https else 'Нет' }}</li>
                <li>Заголовки безопасности: {{ 'Да' if metrics.security.has_security_headers else 'Нет' }}</li>
                <li>Уязвимых библиотек: {{ metrics.security.vulnerable_libraries }}</li>
                <li>Проблем со смешанным контентом: {{ metrics.security.mixed_content_issues }}</li>
            </ul>
        </div>
        {% endif %}

        {% if metrics.ux %}
        <div class="metric-card">
            <h4>Пользовательский опыт (UX)</h4>
            <div class="score {{ metrics.ux.ux_score_class }}">{{ "%.1f"|format(metrics.ux.ux_score) }}/100</div>
            <ul>
                <li>Мобильная адаптация: {{ 'Да' if metrics.ux.mobile_friendly else 'Нет' }}</li>
                <li>Адаптивный дизайн: {{ 'Да' if metrics.ux.responsive_design else 'Нет' }}</li>
                <li>Читаемость шрифтов: {{ 'Да' if metrics.ux.readable_font_sizes else 'Нет' }}</li>
                <li>Четкая навигация: {{ 'Да' if metrics.ux.clear_navigation else 'Нет' }}</li>
            </ul>
        </div>
        {% endif %}
    </div>

    {% if recommendations %}
    <div class="section">
        <h3>Рекомендации по улучшению</h3>
        <div class="recommendations">
            {% for recommendation in recommendations %}
            <div class="recommendation-item">{{ recommendation }}</div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="footer">
        <p>Отчет сгенерирован системой анализа веб-ресурсов</p>
        <p>{{ generated_at }}</p>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        html_content = template.render(**data)
        
        # Сохранение HTML файла
        filename = f"report_{data['analysis']['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML отчет сохранен: {filepath}")
        return filepath
    
    def _generate_pdf_report(self, data: dict) -> str:
        """Генерация PDF отчета"""
        filename = f"report_{data['analysis']['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Центрирование
        )
        
        story.append(Paragraph("Отчет анализа веб-ресурса", title_style))
        story.append(Paragraph(data['website']['name'], styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Основная информация
        info_data = [
            ['URL:', data['website']['url']],
            ['Дата анализа:', data['analysis']['analysis_date']],
            ['Дата генерации:', data['generated_at']]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Общая оценка
        story.append(Paragraph("Общая оценка", styles['Heading2']))
        overall_score = data['summary']['overall_score']
        score_text = f"{overall_score}/100 - {data['summary']['overall_assessment']}"
        story.append(Paragraph(score_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Метрики
        story.append(Paragraph("Метрики по категориям", styles['Heading2']))
        
        for category, metrics in data['metrics'].items():
            story.append(Paragraph(category.title(), styles['Heading3']))
            
            score = metrics.get('score', 0) or metrics.get(f'{category}_score', 0)
            story.append(Paragraph(f"Оценка: {score}/100", styles['Normal']))
            
            # Добавляем ключевые метрики
            if category == 'seo':
                metrics_text = f"""
                Заголовок: {metrics.get('title', 'Отсутствует')}
                Количество слов: {metrics.get('word_count', 0)}
                Внутренних ссылок: {metrics.get('internal_links', 0)}
                Внешних ссылок: {metrics.get('external_links', 0)}
                """
            elif category == 'performance':
                metrics_text = f"""
                Время загрузки: {metrics.get('load_time_ms', 0)} мс
                First Contentful Paint: {metrics.get('first_contentful_paint_ms', 0)} мс
                Размер страницы: {metrics.get('total_page_size_kb', 0)} КБ
                Количество запросов: {metrics.get('requests_count', 0)}
                """
            else:
                metrics_text = "Метрики доступны в полной версии отчета"
            
            story.append(Paragraph(metrics_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Рекомендации
        if data.get('recommendations'):
            story.append(PageBreak())
            story.append(Paragraph("Рекомендации по улучшению", styles['Heading2']))
            
            for recommendation in data['recommendations']:
                story.append(Paragraph(f"• {recommendation}", styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Построение PDF
        doc.build(story)
        
        logger.info(f"PDF отчет сохранен: {filepath}")
        return filepath
    
    def _generate_json_report(self, data: dict) -> str:
        """Генерация JSON отчета"""
        filename = f"report_{data['analysis']['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Преобразование datetime в строки для JSON
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=json_serializer)
        
        logger.info(f"JSON отчет сохранен: {filepath}")
        return filepath
    
    def _generate_summary(self, metrics: dict) -> dict:
        """Генерация сводки"""
        scores = []
        
        for category, metric_data in metrics.items():
            if isinstance(metric_data, dict):
                score = metric_data.get('score', 0)
                if score:
                    scores.append(score)
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Определение класса и оценки
        if overall_score >= 90:
            score_class = 'excellent'
            assessment = 'Отлично'
        elif overall_score >= 75:
            score_class = 'good'
            assessment = 'Хорошо'
        elif overall_score >= 60:
            score_class = 'fair'
            assessment = 'Удовлетворительно'
        else:
            score_class = 'poor'
            assessment = 'Требует улучшения'
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_score_class': score_class,
            'overall_assessment': assessment,
            'categories_analyzed': len(metrics)
        }
    
    def _generate_recommendations(self, metrics: dict) -> list:
        """Генерация рекомендаций"""
        recommendations = []
        
        # SEO рекомендации
        if metrics.get('seo'):
            seo = metrics['seo']
            if not seo.get('title'):
                recommendations.append("Добавьте заголовок страницы (title)")
            if seo.get('images_without_alt', 0) > 0:
                recommendations.append(f"Добавьте alt-тексты для {seo.get('images_without_alt')} изображений")
            if seo.get('word_count', 0) < 300:
                recommendations.append("Увеличьте объем текстового контента")
        
        # Производительность
        if metrics.get('performance'):
            perf = metrics['performance']
            if perf.get('load_time_ms', 0) > 3000:
                recommendations.append("Оптимизируйте время загрузки страницы")
            if perf.get('total_page_size_kb', 0) > 2000:
                recommendations.append("Сократите размер страницы")
        
        # Доступность
        if metrics.get('accessibility'):
            access = metrics['accessibility']
            if access.get('alt_text_missing', 0) > 0:
                recommendations.append("Добавьте alt-тексты для изображений")
            if access.get('color_contrast_issues', 0) > 0:
                recommendations.append("Улучшите контрастность цветов")
        
        # Безопасность
        if metrics.get('security'):
            security = metrics['security']
            if not security.get('has_https'):
                recommendations.append("Включите HTTPS")
            if not security.get('has_security_headers'):
                recommendations.append("Настройте заголовки безопасности")
        
        # UX
        if metrics.get('ux'):
            ux = metrics['ux']
            if not ux.get('mobile_friendly'):
                recommendations.append("Оптимизируйте сайт для мобильных устройств")
            if not ux.get('responsive_design'):
                recommendations.append("Сделайте дизайн адаптивным")
        
        return recommendations
    
    def generate_comparison_report(self, comparison_data: dict, report_type='html') -> str:
        """
        Генерация сравнительного отчета
        
        Args:
            comparison_data: Данные сравнительного анализа
            report_type: Тип отчета ('html', 'pdf', 'json')
            
        Returns:
            Путь к сгенерированному файлу
        """
        try:
            logger.info(f"Генерация сравнительного {report_type} отчета для {comparison_data.get('websites_count', 0)} сайтов")
            
            if report_type == 'html':
                return self._generate_comparison_html_report(comparison_data)
            elif report_type == 'pdf':
                return self._generate_comparison_pdf_report(comparison_data)
            elif report_type == 'json':
                return self._generate_comparison_json_report(comparison_data)
            else:
                raise ValueError(f"Неподдерживаемый тип отчета: {report_type}")
        
        except Exception as e:
            logger.error(f"Ошибка при генерации сравнительного отчета: {e}")
            raise
    
    def _generate_comparison_html_report(self, data: dict) -> str:
        """Генерация HTML сравнительного отчета"""
        template_str = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сравнительный анализ веб-ресурсов</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .ranking-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .ranking-table th, .ranking-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .ranking-table th { background-color: #f2f2f2; font-weight: bold; }
        .ranking-table tr:nth-child(even) { background-color: #f9f9f9; }
        .rank-1 { background-color: #ffd700; font-weight: bold; }
        .rank-2 { background-color: #c0c0c0; }
        .rank-3 { background-color: #cd7f32; }
        .score { font-weight: bold; }
        .score.high { color: #28a745; }
        .score.medium { color: #ffc107; }
        .score.low { color: #dc3545; }
        .chart-placeholder { 
            border: 2px dashed #ddd; 
            height: 300px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin: 20px 0; 
            background-color: #f8f9fa; 
        }
        .recommendations { background-color: #f8f9fa; padding: 20px; border-radius: 8px; }
        .recommendation-item { margin-bottom: 10px; padding-left: 20px; position: relative; }
        .recommendation-item:before { content: "•"; position: absolute; left: 0; color: #007bff; }
        .statistics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Сравнительный анализ веб-ресурсов</h1>
        <p><strong>Количество сайтов:</strong> {{ websites_count }}</p>
        <p><strong>Дата генерации:</strong> {{ generated_at }}</p>
    </div>

    <div class="section">
        <h3>Общий рейтинг сайтов</h3>
        <table class="ranking-table">
            <thead>
                <tr>
                    <th>Место</th>
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
                {% for rank, site_id, url, score in rankings.overall %}
                <tr class="{% if rank == 1 %}rank-1{% elif rank == 2 %}rank-2{% elif rank == 3 %}rank-3{% endif %}">
                    <td>{{ rank }}</td>
                    <td>{{ url }}</td>
                    <td class="score {% if score >= 80 %}high{% elif score >= 60 %}medium{% else %}low{% endif %}">{{ "%.1f"|format(score) }}</td>
                    <td>{{ overall_scores[site_id].seo_score }}</td>
                    <td>{{ overall_scores[site_id].performance_score }}</td>
                    <td>{{ overall_scores[site_id].security_score }}</td>
                    <td>{{ overall_scores[site_id].accessibility_score }}</td>
                    <td>{{ overall_scores[site_id].ux_score }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h3>Статистика по категориям</h3>
        <div class="statistics-grid">
            <div class="stat-card">
                <div class="stat-value">{{ "%.1f"|format(overall_scores.values() | map(attribute='overall_score') | list | average) }}</div>
                <div>Средний общий балл</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ seo_comparison.statistics.average_score | round(1) }}</div>
                <div>Средний SEO балл</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ performance_comparison.statistics.average_score | round(1) }}</div>
                <div>Средняя производительность</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ security_comparison.statistics.https_adoption | round(1) }}%</div>
                <div>Использование HTTPS</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h3>SEO сравнение</h3>
        <table class="ranking-table">
            <thead>
                <tr>
                    <th>Место</th>
                    <th>Сайт</th>
                    <th>SEO балл</th>
                    <th>Заголовок</th>
                    <th>Контент</th>
                    <th>Ссылки</th>
                    <th>Изображения</th>
                </tr>
            </thead>
            <tbody>
                {% for rank, site_id, url, score in rankings.seo %}
                <tr>
                    <td>{{ rank }}</td>
                    <td>{{ url }}</td>
                    <td class="score {% if score >= 80 %}high{% elif score >= 60 %}medium{% else %}low{% endif %}">{{ score }}</td>
                    <td>{{ seo_comparison.metrics[site_id].title_score }}</td>
                    <td>{{ seo_comparison.metrics[site_id].content_score }}</td>
                    <td>{{ seo_comparison.metrics[site_id].links_score }}</td>
                    <td>{{ seo_comparison.metrics[site_id].images_score }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h3>Производительность</h3>
        <table class="ranking-table">
            <thead>
                <tr>
                    <th>Место</th>
                    <th>Сайт</th>
                    <th>Балл</th>
                    <th>Время загрузки</th>
                    <th>Размер страницы</th>
                </tr>
            </thead>
            <tbody>
                {% for rank, site_id, url, score in rankings.performance %}
                <tr>
                    <td>{{ rank }}</td>
                    <td>{{ url }}</td>
                    <td class="score {% if score >= 80 %}high{% elif score >= 60 %}medium{% else %}low{% endif %}">{{ score }}</td>
                    <td>{{ performance_comparison.metrics[site_id].load_time }} мс</td>
                    <td>{{ (performance_comparison.metrics[site_id].page_size / 1024 / 1024) | round(2) }} МБ</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h3>Безопасность</h3>
        <table class="ranking-table">
            <thead>
                <tr>
                    <th>Место</th>
                    <th>Сайт</th>
                    <th>Балл</th>
                    <th>HTTPS</th>
                    <th>Заголовки безопасности</th>
                </tr>
            </thead>
            <tbody>
                {% for rank, site_id, url, score in rankings.security %}
                <tr>
                    <td>{{ rank }}</td>
                    <td>{{ url }}</td>
                    <td class="score {% if score >= 80 %}high{% elif score >= 60 %}medium{% else %}low{% endif %}">{{ score }}</td>
                    <td>{{ 'Да' if security_comparison.metrics[site_id].has_https else 'Нет' }}</td>
                    <td>{{ security_comparison.metrics[site_id].security_headers_count }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    {% if recommendations %}
    <div class="section">
        <h3>Общие рекомендации</h3>
        <div class="recommendations">
            {% for recommendation in recommendations %}
            <div class="recommendation-item">{{ recommendation }}</div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="footer">
        <p>Сравнительный отчет сгенерирован системой анализа веб-ресурсов</p>
        <p>{{ generated_at }}</p>
    </div>
</body>
</html>
        """
        
        # Добавляем данные для шаблона
        data['generated_at'] = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        template = Template(template_str)
        html_content = template.render(**data)
        
        # Сохранение HTML файла
        filename = f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Сравнительный HTML отчет сохранен: {filepath}")
        return filepath
    
    def _generate_comparison_pdf_report(self, data: dict) -> str:
        """Генерация PDF сравнительного отчета"""
        filename = f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        
        story.append(Paragraph("Сравнительный анализ веб-ресурсов", title_style))
        story.append(Paragraph(f"Количество сайтов: {data.get('websites_count', 0)}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Общий рейтинг
        story.append(Paragraph("Общий рейтинг сайтов", styles['Heading2']))
        
        rankings_data = [['Место', 'Сайт', 'Общий балл']]
        for rank, site_id, url, score in data.get('rankings', {}).get('overall', []):
            rankings_data.append([str(rank), url, f"{score:.1f}"])
        
        rankings_table = Table(rankings_data)
        rankings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(rankings_table)
        story.append(Spacer(1, 20))
        
        # Статистика
        story.append(Paragraph("Статистика по категориям", styles['Heading2']))
        
        overall_scores = data.get('overall_scores', {})
        if overall_scores:
            scores = [metrics['overall_score'] for metrics in overall_scores.values()]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            stats_text = f"""
            Средний общий балл: {avg_score:.1f}
            Средний SEO балл: {data.get('seo_comparison', {}).get('statistics', {}).get('average_score', 0):.1f}
            Средняя производительность: {data.get('performance_comparison', {}).get('statistics', {}).get('average_score', 0):.1f}
            Использование HTTPS: {data.get('security_comparison', {}).get('statistics', {}).get('https_adoption', 0):.1f}%
            """
            
            story.append(Paragraph(stats_text, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Рекомендации
        if data.get('recommendations'):
            story.append(Paragraph("Общие рекомендации", styles['Heading2']))
            for recommendation in data['recommendations']:
                story.append(Paragraph(f"• {recommendation}", styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Построение PDF
        doc.build(story)
        
        logger.info(f"Сравнительный PDF отчет сохранен: {filepath}")
        return filepath
    
    def _generate_comparison_json_report(self, data: dict) -> str:
        """Генерация JSON сравнительного отчета"""
        filename = f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Добавляем метаданные
        data['generated_at'] = datetime.now().isoformat()
        data['report_type'] = 'comparison'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Сравнительный JSON отчет сохранен: {filepath}")
        return filepath
