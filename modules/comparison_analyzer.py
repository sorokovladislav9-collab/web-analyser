"""
Модуль для сравнительного анализа веб-ресурсов
"""
import logging
from typing import Dict, List, Optional, Tuple
import statistics

logger = logging.getLogger(__name__)

class ComparisonAnalyzer:
    """Класс для сравнительного анализа веб-ресурсов"""
    
    def __init__(self):
        pass
        
    def compare_websites(self, websites_data: List[Dict]) -> Dict:
        """
        Основной метод сравнения веб-ресурсов
        
        Args:
            websites_data: Список словарей с данными о веб-ресурсах и их анализе
            
        Returns:
            Словарь с результатами сравнения
        """
        try:
            logger.info(f"Начинаю сравнительный анализ {len(websites_data)} веб-ресурсов")
            
            if len(websites_data) < 2:
                return self._get_error_result("Для сравнения нужно минимум 2 веб-ресурса")
            
            results = {
                'websites_count': len(websites_data),
                'websites': [data.get('url', 'Unknown') for data in websites_data],
                'seo_comparison': self._compare_seo(websites_data),
                'performance_comparison': self._compare_performance(websites_data),
                'security_comparison': self._compare_security(websites_data),
                'accessibility_comparison': self._compare_accessibility(websites_data),
                'ux_comparison': self._compare_ux(websites_data),
                'overall_scores': self._calculate_overall_scores(websites_data),
                'rankings': {},
                'recommendations': []
            }
            
            # Расчет рейтингов
            results['rankings'] = self._calculate_rankings(results)
            
            # Генерация общих рекомендаций
            results['recommendations'] = self._generate_comparison_recommendations(results)
            
            logger.info("Сравнительный анализ завершен")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при сравнительном анализе: {e}")
            return self._get_error_result(str(e))
    
    def _compare_seo(self, websites_data: List[Dict]) -> Dict:
        """Сравнение SEO показателей"""
        seo_metrics = {}
        
        # Собираем SEO метрики для каждого сайта
        for i, data in enumerate(websites_data):
            seo_analysis = data.get('seo_analysis', {})
            
            seo_metrics[f'site_{i+1}'] = {
                'url': data.get('url', ''),
                'overall_score': seo_analysis.get('score', 0),
                'title_score': seo_analysis.get('title_analysis', {}).get('score', 0),
                'meta_description_score': seo_analysis.get('meta_description_analysis', {}).get('score', 0),
                'headings_score': seo_analysis.get('headings_analysis', {}).get('score', 0),
                'content_score': seo_analysis.get('content_analysis', {}).get('score', 0),
                'links_score': seo_analysis.get('links_analysis', {}).get('score', 0),
                'images_score': seo_analysis.get('images_analysis', {}).get('score', 0),
                'technical_score': seo_analysis.get('technical_seo', {}).get('score', 0)
            }
        
        # Расчет статистики
        scores = [metrics['overall_score'] for metrics in seo_metrics.values()]
        
        comparison = {
            'metrics': seo_metrics,
            'statistics': {
                'average_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'std_deviation': statistics.stdev(scores) if len(scores) > 1 else 0
            },
            'best_practices': self._analyze_seo_best_practices(seo_metrics),
            'improvement_areas': self._analyze_seo_improvement_areas(seo_metrics)
        }
        
        return comparison
    
    def _compare_performance(self, websites_data: List[Dict]) -> Dict:
        """Сравнение производительности"""
        perf_metrics = {}
        
        for i, data in enumerate(websites_data):
            perf_analysis = data.get('performance_analysis', {})
            
            perf_metrics[f'site_{i+1}'] = {
                'url': data.get('url', ''),
                'overall_score': perf_analysis.get('score', 0),
                'load_time': data.get('load_time', 0),
                'page_size': data.get('page_size', 0),
                'load_time_score': perf_analysis.get('load_time_analysis', {}).get('score', 0),
                'page_size_score': perf_analysis.get('page_size_analysis', {}).get('score', 0),
                'content_score': perf_analysis.get('content_analysis', {}).get('score', 0),
                'network_score': perf_analysis.get('network_analysis', {}).get('score', 0)
            }
        
        # Расчет статистики
        scores = [metrics['overall_score'] for metrics in perf_metrics.values()]
        load_times = [metrics['load_time'] for metrics in perf_metrics.values()]
        page_sizes = [metrics['page_size'] for metrics in perf_metrics.values()]
        
        comparison = {
            'metrics': perf_metrics,
            'statistics': {
                'average_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'average_load_time': statistics.mean(load_times) if load_times else 0,
                'fastest_load_time': min(load_times) if load_times else 0,
                'slowest_load_time': max(load_times) if load_times else 0,
                'average_page_size': statistics.mean(page_sizes) if page_sizes else 0,
                'smallest_page_size': min(page_sizes) if page_sizes else 0,
                'largest_page_size': max(page_sizes) if page_sizes else 0
            },
            'performance_leader': self._find_performance_leader(perf_metrics),
            'optimization_opportunities': self._find_performance_opportunities(perf_metrics)
        }
        
        return comparison
    
    def _compare_security(self, websites_data: List[Dict]) -> Dict:
        """Сравнение безопасности"""
        security_metrics = {}
        
        for i, data in enumerate(websites_data):
            security_analysis = data.get('security_analysis', {})
            security_headers = data.get('security_headers', {})
            
            security_metrics[f'site_{i+1}'] = {
                'url': data.get('url', ''),
                'overall_score': security_analysis.get('score', 0),
                'has_https': data.get('has_https', False),
                'security_headers_count': len([h for h in security_headers.get('headers', {}).values() if h]),
                'ssl_score': security_analysis.get('ssl_analysis', {}).get('score', 0),
                'headers_score': security_analysis.get('headers_analysis', {}).get('score', 0),
                'vulnerabilities_score': security_analysis.get('vulnerabilities_analysis', {}).get('score', 0)
            }
        
        # Расчет статистики
        scores = [metrics['overall_score'] for metrics in security_metrics.values()]
        https_count = sum(1 for metrics in security_metrics.values() if metrics['has_https'])
        
        comparison = {
            'metrics': security_metrics,
            'statistics': {
                'average_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'https_adoption': (https_count / len(security_metrics) * 100) if security_metrics else 0
            },
            'security_leader': self._find_security_leader(security_metrics),
            'common_issues': self._find_common_security_issues(security_metrics)
        }
        
        return comparison
    
    def _compare_accessibility(self, websites_data: List[Dict]) -> Dict:
        """Сравнение доступности"""
        accessibility_metrics = {}
        
        for i, data in enumerate(websites_data):
            accessibility_analysis = data.get('accessibility_analysis', {})
            
            accessibility_metrics[f'site_{i+1}'] = {
                'url': data.get('url', ''),
                'overall_score': accessibility_analysis.get('score', 0),
                'alt_text_score': accessibility_analysis.get('images_analysis', {}).get('score', 0),
                'aria_score': accessibility_analysis.get('aria_analysis', {}).get('score', 0),
                'keyboard_score': accessibility_analysis.get('keyboard_analysis', {}).get('score', 0),
                'contrast_score': accessibility_analysis.get('contrast_analysis', {}).get('score', 0),
                'forms_score': accessibility_analysis.get('forms_analysis', {}).get('score', 0)
            }
        
        # Расчет статистики
        scores = [metrics['overall_score'] for metrics in accessibility_metrics.values()]
        
        comparison = {
            'metrics': accessibility_metrics,
            'statistics': {
                'average_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0
            },
            'accessibility_leader': self._find_accessibility_leader(accessibility_metrics),
            'improvement_priorities': self._find_accessibility_priorities(accessibility_metrics)
        }
        
        return comparison
    
    def _compare_ux(self, websites_data: List[Dict]) -> Dict:
        """Сравнение UX показателей"""
        ux_metrics = {}
        
        for i, data in enumerate(websites_data):
            ux_analysis = data.get('ux_analysis', {})
            
            ux_metrics[f'site_{i+1}'] = {
                'url': data.get('url', ''),
                'overall_score': ux_analysis.get('score', 0),
                'navigation_score': ux_analysis.get('navigation_analysis', {}).get('score', 0),
                'mobile_score': ux_analysis.get('mobile_analysis', {}).get('score', 0),
                'content_structure_score': ux_analysis.get('content_structure_analysis', {}).get('score', 0),
                'usability_score': ux_analysis.get('usability_analysis', {}).get('score', 0),
                'design_score': ux_analysis.get('design_analysis', {}).get('score', 0)
            }
        
        # Расчет статистики
        scores = [metrics['overall_score'] for metrics in ux_metrics.values()]
        
        comparison = {
            'metrics': ux_metrics,
            'statistics': {
                'average_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0
            },
            'ux_leader': self._find_ux_leader(ux_metrics),
            'user_experience_insights': self._analyze_ux_insights(ux_metrics)
        }
        
        return comparison
    
    def _calculate_overall_scores(self, websites_data: List[Dict]) -> Dict:
        """Расчет общих баллов для каждого сайта"""
        overall_scores = {}
        
        for i, data in enumerate(websites_data):
            seo_score = data.get('seo_analysis', {}).get('score', 0)
            perf_score = data.get('performance_analysis', {}).get('score', 0)
            security_score = data.get('security_analysis', {}).get('score', 0)
            accessibility_score = data.get('accessibility_analysis', {}).get('score', 0)
            ux_score = data.get('ux_analysis', {}).get('score', 0)
            
            # Веса для каждого аспекта
            overall_score = (
                seo_score * 0.25 +
                perf_score * 0.25 +
                security_score * 0.20 +
                accessibility_score * 0.15 +
                ux_score * 0.15
            )
            
            overall_scores[f'site_{i+1}'] = {
                'url': data.get('url', ''),
                'overall_score': round(overall_score, 2),
                'seo_score': seo_score,
                'performance_score': perf_score,
                'security_score': security_score,
                'accessibility_score': accessibility_score,
                'ux_score': ux_score,
                'strengths': self._identify_strengths(seo_score, perf_score, security_score, accessibility_score, ux_score),
                'weaknesses': self._identify_weaknesses(seo_score, perf_score, security_score, accessibility_score, ux_score)
            }
        
        return overall_scores
    
    def _calculate_rankings(self, results: Dict) -> Dict:
        """Расчет рейтингов сайтов по разным категориям"""
        rankings = {}
        
        # Рейтинг по общему баллу
        overall_scores = results.get('overall_scores', {})
        sorted_overall = sorted(overall_scores.items(), key=lambda x: x[1]['overall_score'], reverse=True)
        rankings['overall'] = [(rank + 1, site_id, metrics['url'], metrics['overall_score']) for rank, (site_id, metrics) in enumerate(sorted_overall)]
        
        # Рейтинг по SEO
        seo_scores = [(site_id, metrics['seo_score']) for site_id, metrics in overall_scores.items()]
        seo_scores.sort(key=lambda x: x[1], reverse=True)
        rankings['seo'] = [(rank + 1, site_id, overall_scores[site_id]['url'], score) for rank, (site_id, score) in enumerate(seo_scores)]
        
        # Рейтинг по производительности
        perf_scores = [(site_id, metrics['performance_score']) for site_id, metrics in overall_scores.items()]
        perf_scores.sort(key=lambda x: x[1], reverse=True)
        rankings['performance'] = [(rank + 1, site_id, overall_scores[site_id]['url'], score) for rank, (site_id, score) in enumerate(perf_scores)]
        
        # Рейтинг по безопасности
        security_scores = [(site_id, metrics['security_score']) for site_id, metrics in overall_scores.items()]
        security_scores.sort(key=lambda x: x[1], reverse=True)
        rankings['security'] = [(rank + 1, site_id, overall_scores[site_id]['url'], score) for rank, (site_id, score) in enumerate(security_scores)]
        
        # Рейтинг по доступности
        accessibility_scores = [(site_id, metrics['accessibility_score']) for site_id, metrics in overall_scores.items()]
        accessibility_scores.sort(key=lambda x: x[1], reverse=True)
        rankings['accessibility'] = [(rank + 1, site_id, overall_scores[site_id]['url'], score) for rank, (site_id, score) in enumerate(accessibility_scores)]
        
        # Рейтинг по UX
        ux_scores = [(site_id, metrics['ux_score']) for site_id, metrics in overall_scores.items()]
        ux_scores.sort(key=lambda x: x[1], reverse=True)
        rankings['ux'] = [(rank + 1, site_id, overall_scores[site_id]['url'], score) for rank, (site_id, score) in enumerate(ux_scores)]
        
        return rankings
    
    def _identify_strengths(self, seo_score: float, perf_score: float, security_score: float, 
                          accessibility_score: float, ux_score: float) -> List[str]:
        """Определение сильных сторон сайта"""
        strengths = []
        scores = {
            'SEO': seo_score,
            'Производительность': perf_score,
            'Безопасность': security_score,
            'Доступность': accessibility_score,
            'UX': ux_score
        }
        
        for category, score in scores.items():
            if score >= 80:
                strengths.append(category)
            elif score >= 60:
                strengths.append(f"{category} (хороший уровень)")
        
        return strengths
    
    def _identify_weaknesses(self, seo_score: float, perf_score: float, security_score: float,
                           accessibility_score: float, ux_score: float) -> List[str]:
        """Определение слабых сторон сайта"""
        weaknesses = []
        scores = {
            'SEO': seo_score,
            'Производительность': perf_score,
            'Безопасность': security_score,
            'Доступность': accessibility_score,
            'UX': ux_score
        }
        
        for category, score in scores.items():
            if score < 40:
                weaknesses.append(category)
            elif score < 60:
                weaknesses.append(f"{category} (требует улучшения)")
        
        return weaknesses
    
    def _find_performance_leader(self, metrics: Dict) -> Dict:
        """Нахождение лидера по производительности"""
        best_site = max(metrics.items(), key=lambda x: x[1]['overall_score'])
        return {
            'site_id': best_site[0],
            'url': best_site[1]['url'],
            'score': best_site[1]['overall_score'],
            'load_time': best_site[1]['load_time'],
            'page_size': best_site[1]['page_size']
        }
    
    def _find_security_leader(self, metrics: Dict) -> Dict:
        """Нахождение лидера по безопасности"""
        best_site = max(metrics.items(), key=lambda x: x[1]['overall_score'])
        return {
            'site_id': best_site[0],
            'url': best_site[1]['url'],
            'score': best_site[1]['overall_score'],
            'has_https': best_site[1]['has_https']
        }
    
    def _find_accessibility_leader(self, metrics: Dict) -> Dict:
        """Нахождение лидера по доступности"""
        best_site = max(metrics.items(), key=lambda x: x[1]['overall_score'])
        return {
            'site_id': best_site[0],
            'url': best_site[1]['url'],
            'score': best_site[1]['overall_score']
        }
    
    def _find_ux_leader(self, metrics: Dict) -> Dict:
        """Нахождение лидера по UX"""
        best_site = max(metrics.items(), key=lambda x: x[1]['overall_score'])
        return {
            'site_id': best_site[0],
            'url': best_site[1]['url'],
            'score': best_site[1]['overall_score']
        }
    
    def _analyze_seo_best_practices(self, metrics: Dict) -> List[str]:
        """Анализ лучших SEO практик среди сайтов"""
        best_practices = []
        
        # Проверяем, какие сайты хорошо оптимизированы
        good_seo_sites = [site_id for site_id, data in metrics.items() if data['overall_score'] >= 70]
        
        if len(good_seo_sites) > 0:
            best_practices.append(f"{len(good_seo_sites)} сайтов имеют хорошую SEO оптимизацию")
        
        # Анализируем конкретные метрики
        avg_title_score = statistics.mean([data['title_score'] for data in metrics.values()])
        if avg_title_score >= 70:
            best_practices.append("Хорошая оптимизация заголовков")
        
        avg_content_score = statistics.mean([data['content_score'] for data in metrics.values()])
        if avg_content_score >= 70:
            best_practices.append("Качественный контент")
        
        return best_practices
    
    def _analyze_seo_improvement_areas(self, metrics: Dict) -> List[str]:
        """Анализ областей для улучшения SEO"""
        improvement_areas = []
        
        # Находим общие проблемы
        avg_title_score = statistics.mean([data['title_score'] for data in metrics.values()])
        if avg_title_score < 50:
            improvement_areas.append("Оптимизация заголовков")
        
        avg_meta_score = statistics.mean([data['meta_description_score'] for data in metrics.values()])
        if avg_meta_score < 50:
            improvement_areas.append("Мета-описания")
        
        avg_images_score = statistics.mean([data['images_score'] for data in metrics.values()])
        if avg_images_score < 50:
            improvement_areas.append("Alt-тексты для изображений")
        
        return improvement_areas
    
    def _find_performance_opportunities(self, metrics: Dict) -> List[str]:
        """Нахождение возможностей для улучшения производительности"""
        opportunities = []
        
        avg_load_time = statistics.mean([data['load_time'] for data in metrics.values()])
        if avg_load_time > 3000:
            opportunities.append("Оптимизация времени загрузки")
        
        avg_page_size = statistics.mean([data['page_size'] for data in metrics.values()])
        if avg_page_size > 3 * 1024 * 1024:  # 3MB
            opportunities.append("Сжатие изображений и контента")
        
        return opportunities
    
    def _find_common_security_issues(self, metrics: Dict) -> List[str]:
        """Нахождение общих проблем безопасности"""
        issues = []
        
        https_count = sum(1 for data in metrics.values() if data['has_https'])
        if https_count < len(metrics):
            issues.append(f"{len(metrics) - https_count} сайтов не используют HTTPS")
        
        avg_headers_count = statistics.mean([data['security_headers_count'] for data in metrics.values()])
        if avg_headers_count < 3:
            issues.append("Недостаточно заголовков безопасности")
        
        return issues
    
    def _find_accessibility_priorities(self, metrics: Dict) -> List[str]:
        """Нахождение приоритетов для улучшения доступности"""
        priorities = []
        
        avg_alt_score = statistics.mean([data['alt_text_score'] for data in metrics.values()])
        if avg_alt_score < 50:
            priorities.append("Добавление alt-текстов к изображениям")
        
        avg_contrast_score = statistics.mean([data['contrast_score'] for data in metrics.values()])
        if avg_contrast_score < 50:
            priorities.append("Улучшение контрастности цветов")
        
        return priorities
    
    def _analyze_ux_insights(self, metrics: Dict) -> List[str]:
        """Анализ UX инсайтов"""
        insights = []
        
        avg_mobile_score = statistics.mean([data['mobile_score'] for data in metrics.values()])
        if avg_mobile_score < 60:
            insights.append("Улучшение мобильной версии")
        
        avg_navigation_score = statistics.mean([data['navigation_score'] for data in metrics.values()])
        if avg_navigation_score < 60:
            insights.append("Улучшение навигации")
        
        return insights
    
    def _generate_comparison_recommendations(self, results: Dict) -> List[str]:
        """Генерация общих рекомендаций по результатам сравнения"""
        recommendations = []
        
        # Анализ лидеров и отстающих
        overall_scores = results.get('overall_scores', {})
        if overall_scores:
            scores = [metrics['overall_score'] for metrics in overall_scores.values()]
            avg_score = statistics.mean(scores)
            
            if avg_score < 60:
                recommendations.append("Общий уровень оптимизации сайтов требует улучшения")
            elif avg_score < 80:
                recommendations.append("Хороший уровень оптимизации, но есть возможности для улучшения")
            else:
                recommendations.append("Отличный уровень оптимизации сайтов")
        
        # Рекомендации по конкретным аспектам
        seo_comparison = results.get('seo_comparison', {})
        if seo_comparison.get('statistics', {}).get('average_score', 0) < 60:
            recommendations.append("Обратить внимание на SEO оптимизацию")
        
        perf_comparison = results.get('performance_comparison', {})
        if perf_comparison.get('statistics', {}).get('average_score', 0) < 60:
            recommendations.append("Оптимизировать производительность сайтов")
        
        security_comparison = results.get('security_comparison', {})
        if security_comparison.get('statistics', {}).get('https_adoption', 0) < 100:
            recommendations.append("Внедрить HTTPS на всех сайтах")
        
        return recommendations
    
    def _get_error_result(self, error_message: str) -> Dict:
        """Возвращает результат в случае ошибки"""
        return {
            'error': True,
            'message': error_message,
            'websites_count': 0,
            'websites': [],
            'seo_comparison': {},
            'performance_comparison': {},
            'security_comparison': {},
            'accessibility_comparison': {},
            'ux_comparison': {},
            'overall_scores': {},
            'rankings': {},
            'recommendations': [f'Ошибка: {error_message}']
        }
