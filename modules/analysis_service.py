"""
Основной сервис анализа веб-ресурсов
Интегрирует все модули анализа в единую систему
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .data_collector import DataCollector
from .seo_analyzer import SEOAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from .security_analyzer import SecurityAnalyzer
from .accessibility_analyzer import AccessibilityAnalyzer
from .ux_analyzer import UXAnalyzer
from .comparison_analyzer import ComparisonAnalyzer
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class AnalysisService:
    """Основной сервис анализа веб-ресурсов"""
    
    def __init__(self):
        self.data_collector = DataCollector()
        self.seo_analyzer = SEOAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.accessibility_analyzer = AccessibilityAnalyzer()
        self.ux_analyzer = UXAnalyzer()
        self.comparison_analyzer = ComparisonAnalyzer()
        self.report_generator = ReportGenerator()
    
    def analyze_website(self, url: str, name: str = None, description: str = None) -> Dict:
        """
        Полный анализ веб-ресурса
        
        Args:
            url: URL веб-ресурса
            name: Название сайта (опционально)
            description: Описание сайта (опционально)
            
        Returns:
            Словарь с результатами анализа
        """
        try:
            logger.info(f"Начинаю полный анализ веб-ресурса: {url}")
            start_time = datetime.now()
            
            # 1. Сбор данных
            raw_data = self.data_collector.collect_data(url)
            if not raw_data:
                return self._get_error_result(f"Не удалось собрать данные для URL: {url}")
            
            # 2. Анализ по всем категориям
            analysis_results = {
                'url': url,
                'name': name or url,
                'description': description or '',
                'analysis_date': start_time.isoformat(),
                'data_collection': raw_data,
                
                # Результаты анализа
                'seo_analysis': self.seo_analyzer.analyze(raw_data),
                'performance_analysis': self.performance_analyzer.analyze(raw_data),
                'security_analysis': self.security_analyzer.analyze(raw_data),
                'accessibility_analysis': self.accessibility_analyzer.analyze(raw_data),
                'ux_analysis': self.ux_analyzer.analyze(raw_data),
                
                # Общие метрики
                'overall_score': 0,
                'analysis_duration': 0,
                'status': 'completed',
                'recommendations': []
            }
            
            # 3. Расчет общего балла
            analysis_results['overall_score'] = self._calculate_overall_score(analysis_results)
            
            # 4. Генерация общих рекомендаций
            analysis_results['recommendations'] = self._generate_overall_recommendations(analysis_results)
            
            # 5. Расчет времени анализа
            end_time = datetime.now()
            analysis_results['analysis_duration'] = (end_time - start_time).total_seconds()
            
            logger.info(f"Анализ завершен за {analysis_results['analysis_duration']:.2f} сек. Общий балл: {analysis_results['overall_score']}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Ошибка при анализе веб-ресурса {url}: {e}")
            return self._get_error_result(str(e))
    
    def analyze_multiple_websites(self, websites: List[Dict]) -> Dict:
        """
        Анализ нескольких веб-ресурсов
        
        Args:
            websites: Список словарей с данными о сайтах [{'url': '', 'name': '', 'description': ''}, ...]
            
        Returns:
            Словарь с результатами анализа всех сайтов
        """
        try:
            logger.info(f"Начинаю анализ {len(websites)} веб-ресурсов")
            start_time = datetime.now()
            
            results = {
                'websites_count': len(websites),
                'analysis_date': start_time.isoformat(),
                'websites': [],
                'summary': {},
                'status': 'in_progress'
            }
            
            # Анализ каждого сайта
            for website_data in websites:
                url = website_data.get('url')
                name = website_data.get('name')
                description = website_data.get('description')
                
                logger.info(f"Анализ сайта: {url}")
                site_analysis = self.analyze_website(url, name, description)
                logger.info(f"Результат анализа сайта {url}: {site_analysis}")
                results['websites'].append(site_analysis)
            
            # Генерация сводки
            results['summary'] = self._generate_multi_site_summary(results['websites'])
            results['status'] = 'completed'
            
            # Расчет общего времени
            end_time = datetime.now()
            results['total_duration'] = (end_time - start_time).total_seconds()
            
            logger.info(f"Анализ {len(websites)} сайтов завершен за {results['total_duration']:.2f} сек")
            
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при анализе нескольких сайтов: {e}")
            return self._get_error_result(str(e))
    
    def compare_websites(self, websites: List[Dict]) -> Dict:
        """
        Сравнительный анализ веб-ресурсов
        
        Args:
            websites: Список словарей с данными о сайтах для сравнения
            
        Returns:
            Словарь с результатами сравнения
        """
        try:
            logger.info(f"Начинаю сравнительный анализ {len(websites)} веб-ресурсов")
            logger.info(f"Сайты для сравнения: {websites}")
            
            # Сначала анализируем все сайты
            analysis_results = self.analyze_multiple_websites(websites)
            
            logger.info(f"Результаты анализа: {analysis_results}")
            
            if analysis_results.get('status') != 'completed':
                return analysis_results
            
            # Затем сравниваем результаты
            comparison_results = self.comparison_analyzer.compare_websites(analysis_results['websites'])
            
            logger.info(f"Результаты сравнения: {comparison_results}")
            
            # Добавляем метаданные
            comparison_results['analysis_date'] = analysis_results['analysis_date']
            comparison_results['total_duration'] = analysis_results['total_duration']
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Ошибка при сравнительном анализе: {e}")
            return self._get_error_result(str(e))
    
    def generate_report(self, analysis_data: Dict, report_type: str = 'html', 
                       comparison_report: bool = False) -> str:
        """
        Генерация отчета
        
        Args:
            analysis_data: Данные анализа
            report_type: Тип отчета ('html', 'pdf', 'json')
            comparison_report: Флаг сравнительного отчета
            
        Returns:
            Путь к сгенерированному файлу отчета
        """
        try:
            if comparison_report:
                return self.report_generator.generate_comparison_report(analysis_data, report_type)
            else:
                # Создаем объект анализа для одиночного отчета
                mock_analysis = self._create_mock_analysis_object(analysis_data)
                return self.report_generator.generate_report(mock_analysis, report_type)
                
        except Exception as e:
            logger.error(f"Ошибка при генерации отчета: {e}")
            raise
    
    def _calculate_overall_score(self, analysis_results: Dict) -> float:
        """Расчет общего балла на основе всех категорий анализа"""
        scores = {
            'seo': analysis_results.get('seo_analysis', {}).get('score', 0),
            'performance': analysis_results.get('performance_analysis', {}).get('score', 0),
            'security': analysis_results.get('security_analysis', {}).get('score', 0),
            'accessibility': analysis_results.get('accessibility_analysis', {}).get('score', 0),
            'ux': analysis_results.get('ux_analysis', {}).get('score', 0)
        }
        
        # Веса для каждой категории
        weights = {
            'seo': 0.25,
            'performance': 0.25,
            'security': 0.20,
            'accessibility': 0.15,
            'ux': 0.15
        }
        
        overall_score = sum(scores[category] * weights[category] for category in scores)
        return round(overall_score, 2)
    
    def _generate_overall_recommendations(self, analysis_results: Dict) -> List[str]:
        """Генерация общих рекомендаций на основе всех категорий"""
        recommendations = []
        
        # Собираем рекомендации из всех категорий
        categories = {
            'seo': analysis_results.get('seo_analysis', {}).get('recommendations', []),
            'performance': analysis_results.get('performance_analysis', {}).get('recommendations', []),
            'security': analysis_results.get('security_analysis', {}).get('recommendations', []),
            'accessibility': analysis_results.get('accessibility_analysis', {}).get('recommendations', []),
            'ux': analysis_results.get('ux_analysis', {}).get('recommendations', [])
        }
        
        # Приоритезация рекомендаций
        priority_recommendations = []
        
        # Критические проблемы (безопасность)
        if categories['security']:
            priority_recommendations.extend([f"Безопасность: {rec}" for rec in categories['security'][:2]])
        
        # Важные проблемы (производительность)
        if categories['performance']:
            priority_recommendations.extend([f"Производительность: {rec}" for rec in categories['performance'][:2]])
        
        # SEO рекомендации
        if categories['seo']:
            priority_recommendations.extend([f"SEO: {rec}" for rec in categories['seo'][:2]])
        
        # Остальные рекомендации
        for category, recs in categories.items():
            if category not in ['security', 'performance', 'seo']:
                priority_recommendations.extend([f"{category.title()}: {rec}" for rec in recs[:1]])
        
        # Удаляем дубликаты и ограничиваем количество
        unique_recommendations = list(dict.fromkeys(priority_recommendations))
        recommendations = unique_recommendations[:10]  # Максимум 10 рекомендаций
        
        return recommendations
    
    def _generate_multi_site_summary(self, websites_analyses: List[Dict]) -> Dict:
        """Генерация сводки по нескольким сайтам"""
        if not websites_analyses:
            return {}
        
        total_sites = len(websites_analyses)
        scores = [site.get('overall_score', 0) for site in websites_analyses]
        
        summary = {
            'total_sites': total_sites,
            'average_score': sum(scores) / total_sites if scores else 0,
            'min_score': min(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'successful_analyses': sum(1 for site in websites_analyses if site.get('status') == 'completed'),
            'failed_analyses': sum(1 for site in websites_analyses if site.get('status') != 'completed'),
            'categories_summary': {}
        }
        
        # Сводка по категориям
        categories = ['seo', 'performance', 'security', 'accessibility', 'ux']
        for category in categories:
            category_scores = []
            for site in websites_analyses:
                analysis = site.get(f'{category}_analysis', {})
                if analysis:
                    category_scores.append(analysis.get('score', 0))
            
            if category_scores:
                summary['categories_summary'][category] = {
                    'average': sum(category_scores) / len(category_scores),
                    'min': min(category_scores),
                    'max': max(category_scores)
                }
        
        return summary
    
    def _create_mock_analysis_object(self, analysis_data: Dict):
        """Создание мок-объекта анализа для генератора отчетов"""
        class MockAnalysis:
            def __init__(self, data):
                self.id = data.get('url', '').replace('.', '_').replace('/', '_')
                self.status = data.get('status', 'completed')
                self.analysis_date = datetime.fromisoformat(data.get('analysis_date', datetime.now().isoformat()))
                self.error_message = data.get('error_message', '')
                
                # Мок-объект для сайта
                self.website = MockWebsite(data)
                
                # Мок-объекты для метрик
                self.seo_metrics = MockMetrics(data.get('seo_analysis', {}))
                self.performance_metrics = MockMetrics(data.get('performance_analysis', {}))
                self.accessibility_metrics = MockMetrics(data.get('accessibility_analysis', {}))
                self.security_metrics = MockMetrics(data.get('security_analysis', {}))
                self.ux_metrics = MockMetrics(data.get('ux_analysis', {}))
        
        class MockWebsite:
            def __init__(self, data):
                self.id = data.get('url', '').replace('.', '_').replace('/', '_')
                self.url = data.get('url', '')
                self.name = data.get('name', '')
                self.description = data.get('description', '')
                self.category = 'general'
        
        class MockMetrics:
            def __init__(self, analysis_data):
                for key, value in analysis_data.items():
                    setattr(self, key, value)
        
        return MockAnalysis(analysis_data)
    
    def _get_error_result(self, error_message: str) -> Dict:
        """Возвращает результат в случае ошибки"""
        return {
            'status': 'error',
            'error_message': error_message,
            'url': '',
            'name': '',
            'description': '',
            'analysis_date': datetime.now().isoformat(),
            'overall_score': 0,
            'analysis_duration': 0,
            'seo_analysis': {'score': 0, 'recommendations': []},
            'performance_analysis': {'score': 0, 'recommendations': []},
            'security_analysis': {'score': 0, 'recommendations': []},
            'accessibility_analysis': {'score': 0, 'recommendations': []},
            'ux_analysis': {'score': 0, 'recommendations': []},
            'recommendations': [f'Ошибка анализа: {error_message}']
        }
