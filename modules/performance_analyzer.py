"""
Модуль для анализа производительности веб-ресурсов
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Класс для анализа производительности"""
    
    def __init__(self):
        pass
        
    def analyze(self, data: Dict) -> Dict:
        """
        Основной метод анализа производительности
        
        Args:
            data: Словарь с данными о веб-ресурсе от DataCollector
            
        Returns:
            Словарь с результатами анализа производительности
        """
        try:
            logger.info(f"Начинаю анализ производительности для URL: {data.get('url')}")
            
            results = {
                'load_time_analysis': self._analyze_load_time(data),
                'page_size_analysis': self._analyze_page_size(data),
                'content_analysis': self._analyze_content_performance(data),
                'network_analysis': self._analyze_network_performance(data),
                'core_web_vitals': self._get_core_web_vitals(data),
                'score': 0,
                'recommendations': []
            }
            
            # Расчет общего балла
            results['score'] = self._calculate_performance_score(results)
            
            # Генерация рекомендаций
            results['recommendations'] = self._generate_recommendations(results)
            
            logger.info(f"Анализ производительности завершен для URL: {data.get('url')}")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при анализе производительности: {e}")
            return self._get_empty_results()
    
    def _analyze_load_time(self, data: Dict) -> Dict:
        """Анализ времени загрузки"""
        load_time = data.get('load_time', 0)
        
        analysis = {
            'load_time_ms': load_time,
            'load_time_category': self._categorize_load_time(load_time),
            'is_fast': load_time <= 2000,
            'is_acceptable': load_time <= 4000,
            'score': 0
        }
        
        # Оценка времени загрузки
        if load_time <= 1000:
            analysis['score'] = 100
        elif load_time <= 2000:
            analysis['score'] = 80
        elif load_time <= 3000:
            analysis['score'] = 60
        elif load_time <= 4000:
            analysis['score'] = 40
        else:
            analysis['score'] = 20
        
        return analysis
    
    def _analyze_page_size(self, data: Dict) -> Dict:
        """Анализ размера страницы"""
        page_size = data.get('page_size', 0)
        page_size_mb = page_size / (1024 * 1024)  # Конвертация в МБ
        
        analysis = {
            'page_size_bytes': page_size,
            'page_size_mb': round(page_size_mb, 2),
            'size_category': self._categorize_page_size(page_size_mb),
            'is_optimized': page_size_mb <= 2,
            'is_acceptable': page_size_mb <= 4,
            'score': 0
        }
        
        # Оценка размера страницы
        if page_size_mb <= 1:
            analysis['score'] = 100
        elif page_size_mb <= 2:
            analysis['score'] = 80
        elif page_size_mb <= 3:
            analysis['score'] = 60
        elif page_size_mb <= 4:
            analysis['score'] = 40
        else:
            analysis['score'] = 20
        
        return analysis
    
    def _analyze_content_performance(self, data: Dict) -> Dict:
        """Анализ производительности контента"""
        images = data.get('images', [])
        html_length = len(data.get('html', ''))
        
        analysis = {
            'images_count': len(images),
            'html_size': html_length,
            'has_large_images': False,
            'has_unoptimized_content': False,
            'css_size': self._estimate_css_size(data.get('html', '')),
            'js_size': self._estimate_js_size(data.get('html', '')),
            'score': 0
        }
        
        # Проверка на большие изображения (упрощенная)
        large_images = sum(1 for img in images if img.get('width') and int(img.get('width', 0)) > 2000)
        if large_images > 0:
            analysis['has_large_images'] = True
        
        # Проверка на неоптимизированный контент
        if html_length > 500000:  # 500KB
            analysis['has_unoptimized_content'] = True
        
        # Расчет балла
        score = 100
        
        if analysis['has_large_images']:
            score -= 20
        
        if analysis['has_unoptimized_content']:
            score -= 15
        
        if len(images) > 50:
            score -= 15
        
        if analysis['css_size'] > 100000:  # 100KB
            score -= 10
        
        if analysis['js_size'] > 200000:  # 200KB
            score -= 10
        
        analysis['score'] = max(score, 0)
        
        return analysis
    
    def _analyze_network_performance(self, data: Dict) -> Dict:
        """Анализ сетевой производительности"""
        headers = data.get('headers', {})
        content_type = headers.get('content-type', '')
        
        analysis = {
            'has_compression': self._has_compression(headers),
            'has_caching': self._has_caching_headers(headers),
            'has_keep_alive': self._has_keep_alive(headers),
            'content_type': content_type,
            'is_minified': self._is_content_minified(data.get('html', '')),
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['has_compression']:
            score += 25
        
        if analysis['has_caching']:
            score += 25
        
        if analysis['has_keep_alive']:
            score += 15
        
        if analysis['is_minified']:
            score += 20
        
        # Дополнительные 15 баллов за базовые оптимизации
        score += 15
        
        analysis['score'] = score
        
        return analysis
    
    def _get_core_web_vitals(self, data: Dict) -> Dict:
        """Получение Core Web Vitals (заглушка)"""
        # В реальном приложении здесь будут данные из Lighthouse или PageSpeed
        return {
            'largest_contentful_paint': 2400,  # мс
            'first_input_delay': 50,  # мс
            'cumulative_layout_shift': 0.1,
            'first_contentful_paint': 1200,  # мс
            'time_to_interactive': 3500,  # мс
            'total_blocking_time': 300,  # мс
            'score': 85
        }
    
    def _categorize_load_time(self, load_time: float) -> str:
        """Категоризация времени загрузки"""
        if load_time <= 1000:
            return 'Отличное'
        elif load_time <= 2000:
            return 'Хорошее'
        elif load_time <= 3000:
            return 'Среднее'
        elif load_time <= 4000:
            return 'Медленное'
        else:
            return 'Очень медленное'
    
    def _categorize_page_size(self, size_mb: float) -> str:
        """Категоризация размера страницы"""
        if size_mb <= 1:
            return 'Маленький'
        elif size_mb <= 2:
            return 'Оптимальный'
        elif size_mb <= 4:
            return 'Большой'
        else:
            return 'Очень большой'
    
    def _has_compression(self, headers: Dict) -> bool:
        """Проверка наличия сжатия"""
        encoding = headers.get('content-encoding', '')
        return 'gzip' in encoding or 'br' in encoding or 'deflate' in encoding
    
    def _has_caching_headers(self, headers: Dict) -> bool:
        """Проверка наличия заголовков кеширования"""
        cache_headers = ['cache-control', 'expires', 'etag']
        return any(header in headers for header in cache_headers)
    
    def _has_keep_alive(self, headers: Dict) -> bool:
        """Проверка Keep-Alive"""
        connection = headers.get('connection', '').lower()
        return 'keep-alive' in connection
    
    def _is_content_minified(self, html: str) -> bool:
        """Упрощенная проверка на минификацию"""
        # Проверяем соотношение пробелов и общего размера
        spaces = html.count(' ') + html.count('\n') + html.count('\t')
        ratio = spaces / len(html) if len(html) > 0 else 0
        
        # Если пробелов меньше 10%, считаем контент минифицированным
        return ratio < 0.1
    
    def _estimate_css_size(self, html: str) -> int:
        """Оценка размера CSS (упрощенная)"""
        import re
        css_patterns = re.findall(r'<style[^>]*>.*?</style>', html, re.DOTALL)
        return sum(len(pattern) for pattern in css_patterns)
    
    def _estimate_js_size(self, html: str) -> int:
        """Оценка размера JavaScript (упрощенная)"""
        import re
        js_patterns = re.findall(r'<script[^>]*>.*?</script>', html, re.DOTALL)
        return sum(len(pattern) for pattern in js_patterns)
    
    def _calculate_performance_score(self, results: Dict) -> float:
        """Расчет общего балла производительности"""
        total_score = 0
        max_score = 0
        
        # Вес каждого аспекта
        weights = {
            'load_time_analysis': 0.3,
            'page_size_analysis': 0.2,
            'content_analysis': 0.2,
            'network_analysis': 0.2,
            'core_web_vitals': 0.1
        }
        
        for aspect, weight in weights.items():
            if aspect in results:
                score = results[aspect].get('score', 0)
                total_score += score * weight
                max_score += 100 * weight
        
        return min(total_score, 100)
    
    def _generate_recommendations(self, results: Dict) -> list:
        """Генерация рекомендаций по улучшению производительности"""
        recommendations = []
        
        # Рекомендации по времени загрузки
        load_time = results.get('load_time_analysis', {})
        if load_time.get('load_time_ms', 0) > 3000:
            recommendations.append("Оптимизируйте время загрузки страницы (текущее: {} мс)".format(
                load_time.get('load_time_ms', 0)
            ))
        
        # Рекомендации по размеру страницы
        page_size = results.get('page_size_analysis', {})
        if page_size.get('page_size_mb', 0) > 3:
            recommendations.append("Сократите размер страницы (текущий: {} МБ)".format(
                page_size.get('page_size_mb', 0)
            ))
        
        # Рекомендации по контенту
        content = results.get('content_analysis', {})
        if content.get('has_large_images'):
            recommendations.append("Оптимизируйте размер изображений")
        
        if content.get('images_count', 0) > 50:
            recommendations.append("Уменьшите количество изображений на странице")
        
        # Рекомендации по сети
        network = results.get('network_analysis', {})
        if not network.get('has_compression'):
            recommendations.append("Включите сжатие gzip/brotli")
        
        if not network.get('has_caching'):
            recommendations.append("Настройте заголовки кеширования")
        
        if not network.get('is_minified'):
            recommendations.append("Минифицируйте CSS и JavaScript")
        
        return recommendations
    
    def _get_empty_results(self) -> Dict:
        """Возвращает пустые результаты анализа в случае ошибки"""
        return {
            'load_time_analysis': {'score': 0},
            'page_size_analysis': {'score': 0},
            'content_analysis': {'score': 0},
            'network_analysis': {'score': 0},
            'core_web_vitals': {'score': 0},
            'score': 0,
            'recommendations': ['Не удалось выполнить анализ производительности']
        }
