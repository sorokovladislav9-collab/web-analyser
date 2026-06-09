"""
Модуль для SEO анализа веб-ресурсов
"""
import re
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    """Класс для SEO анализа"""
    
    def __init__(self):
        self.recommendations = []
        
    def analyze(self, data: Dict) -> Dict:
        """
        Основной метод SEO анализа
        
        Args:
            data: Словарь с данными о веб-ресурсе от DataCollector
            
        Returns:
            Словарь с результатами SEO анализа
        """
        try:
            logger.info(f"Начинаю SEO анализ для URL: {data.get('url')}")
            
            results = {
                'title_analysis': self._analyze_title(data),
                'meta_description_analysis': self._analyze_meta_description(data),
                'headings_analysis': self._analyze_headings(data),
                'content_analysis': self._analyze_content(data),
                'links_analysis': self._analyze_links(data),
                'images_analysis': self._analyze_images(data),
                'technical_seo': self._analyze_technical_seo(data),
                'score': 0,
                'recommendations': []
            }
            
            # Расчет общего балла
            results['score'] = self._calculate_seo_score(results)
            
            # Генерация рекомендаций
            results['recommendations'] = self._generate_recommendations(results)
            
            logger.info(f"SEO анализ завершен для URL: {data.get('url')}")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при SEO анализе: {e}")
            return self._get_empty_results()
    
    def _analyze_title(self, data: Dict) -> Dict:
        """Анализ заголовка страницы"""
        title = data.get('title', '')
        
        analysis = {
            'title': title,
            'length': len(title),
            'is_present': bool(title.strip()),
            'optimal_length': 30 <= len(title) <= 60,
            'has_keywords': False,
            'is_unique': True,  # В реальном приложении проверяется against других страниц
            'score': 0
        }
        
        # Проверка оптимальной длины
        if analysis['optimal_length']:
            analysis['score'] += 25
        elif len(title) > 0:
            analysis['score'] += 10
        
        # Проверка наличия заголовка
        if analysis['is_present']:
            analysis['score'] += 25
        
        # Проверка на ключевые слова (упрощенная)
        if self._has_keywords(title):
            analysis['has_keywords'] = True
            analysis['score'] += 25
        
        # Проверка на уникальность (заглушка)
        analysis['score'] += 25
        
        return analysis
    
    def _analyze_meta_description(self, data: Dict) -> Dict:
        """Анализ мета-описания"""
        meta_desc = data.get('meta_description', '')
        
        analysis = {
            'meta_description': meta_desc,
            'length': len(meta_desc),
            'is_present': bool(meta_desc.strip()),
            'optimal_length': 120 <= len(meta_desc) <= 160,
            'has_keywords': False,
            'is_compelling': False,  # Упрощенная проверка
            'score': 0
        }
        
        # Проверка оптимальной длины
        if analysis['optimal_length']:
            analysis['score'] += 30
        elif len(meta_desc) > 0:
            analysis['score'] += 15
        
        # Проверка наличия описания
        if analysis['is_present']:
            analysis['score'] += 30
        
        # Проверка на ключевые слова
        if self._has_keywords(meta_desc):
            analysis['has_keywords'] = True
            analysis['score'] += 20
        
        # Проверка на привлекательность (упрощенная)
        if self._is_compelling_description(meta_desc):
            analysis['is_compelling'] = True
            analysis['score'] += 20
        
        return analysis
    
    def _analyze_headings(self, data: Dict) -> Dict:
        """Анализ заголовков H1-H6"""
        h1_tags = data.get('h1_tags', [])
        h2_tags = data.get('h2_tags', [])
        
        analysis = {
            'h1_count': len(h1_tags),
            'h2_count': len(h2_tags),
            'has_h1': len(h1_tags) > 0,
            'has_multiple_h1': len(h1_tags) > 1,
            'h1_text': h1_tags[0] if h1_tags else '',
            'h1_length': len(h1_tags[0]) if h1_tags else 0,
            'proper_structure': False,
            'score': 0
        }
        
        # Проверка наличия H1
        if analysis['has_h1']:
            analysis['score'] += 30
        
        # Проверка на множественные H1 (негативный фактор)
        if not analysis['has_multiple_h1']:
            analysis['score'] += 20
        
        # Проверка длины H1
        if 20 <= analysis['h1_length'] <= 70:
            analysis['score'] += 20
        
        # Проверка структуры заголовков
        if len(h1_tags) == 1 and len(h2_tags) > 0:
            analysis['proper_structure'] = True
            analysis['score'] += 30
        
        return analysis
    
    def _analyze_content(self, data: Dict) -> Dict:
        """Анализ контента"""
        text_content = data.get('text_content', '')
        word_count = data.get('word_count', 0)
        
        analysis = {
            'word_count': word_count,
            'text_length': len(text_content),
            'has_sufficient_content': word_count >= 300,
            'has_keywords': False,
            'keyword_density': 0,
            'readability_score': 0,  # Упрощенная оценка
            'has_internal_links': False,
            'score': 0
        }
        
        # Проверка достаточного объема контента
        if analysis['has_sufficient_content']:
            analysis['score'] += 25
        elif word_count >= 100:
            analysis['score'] += 10
        
        # Проверка на ключевые слова
        if self._has_keywords(text_content):
            analysis['has_keywords'] = True
            analysis['score'] += 25
        
        # Расчет плотности ключевых слов (упрощенный)
        analysis['keyword_density'] = self._calculate_keyword_density(text_content)
        if 1 <= analysis['keyword_density'] <= 3:
            analysis['score'] += 25
        
        # Оценка читаемости (упрощенная)
        analysis['readability_score'] = self._calculate_readability_score(text_content)
        if analysis['readability_score'] >= 60:
            analysis['score'] += 25
        
        return analysis
    
    def _analyze_links(self, data: Dict) -> Dict:
        """Анализ ссылок"""
        links = data.get('links', {})
        internal_links = links.get('internal', [])
        external_links = links.get('external', [])
        
        analysis = {
            'internal_links_count': len(internal_links),
            'external_links_count': len(external_links),
            'total_links_count': len(internal_links) + len(external_links),
            'has_internal_links': len(internal_links) > 0,
            'has_external_links': len(external_links) > 0,
            'broken_links': 0,  # В реальном приложении проверяется
            'anchor_text_optimization': 0,  # Упрощенная проверка
            'score': 0
        }
        
        # Проверка наличия внутренних ссылок
        if analysis['has_internal_links']:
            analysis['score'] += 30
        
        # Проверка наличия внешних ссылок
        if analysis['has_external_links']:
            analysis['score'] += 20
        
        # Проверка общего количества ссылок
        if 5 <= analysis['total_links_count'] <= 20:
            analysis['score'] += 25
        elif analysis['total_links_count'] > 0:
            analysis['score'] += 10
        
        # Проверка оптимизации анкорного текста (упрощенная)
        good_anchor_texts = sum(1 for link in internal_links if link.get('has_text') and len(link.get('text', '')) > 3)
        if good_anchor_texts / max(len(internal_links), 1) >= 0.7:
            analysis['anchor_text_optimization'] = 70
            analysis['score'] += 25
        
        return analysis
    
    def _analyze_images(self, data: Dict) -> Dict:
        """Анализ изображений"""
        images = data.get('images', [])
        
        analysis = {
            'images_count': len(images),
            'images_with_alt': sum(1 for img in images if img.get('has_alt')),
            'images_without_alt': sum(1 for img in images if not img.get('has_alt')),
            'alt_optimization': 0,
            'has_optimized_images': False,
            'score': 0
        }
        
        if len(images) > 0:
            # Расчет оптимизации alt-текстов
            analysis['alt_optimization'] = (analysis['images_with_alt'] / len(images)) * 100
            
            if analysis['alt_optimization'] >= 80:
                analysis['score'] += 50
            elif analysis['alt_optimization'] >= 50:
                analysis['score'] += 30
            elif analysis['alt_optimization'] > 0:
                analysis['score'] += 10
            
            # Проверка на оптимизацию изображений (упрощенная)
            optimized_images = sum(1 for img in images 
                                 if img.get('width') and img.get('height') and img.get('has_alt'))
            if optimized_images / len(images) >= 0.7:
                analysis['has_optimized_images'] = True
                analysis['score'] += 50
        else:
            # Если нет изображений, это не штрафуется
            analysis['score'] = 50
        
        return analysis
    
    def _analyze_technical_seo(self, data: Dict) -> Dict:
        """Анализ технических SEO аспектов"""
        analysis = {
            'has_canonical': bool(data.get('canonical_url')),
            'has_favicon': bool(data.get('favicon')),
            'has_language': bool(data.get('language')),
            'url_structure': self._analyze_url_structure(data.get('url', '')),
            'has_meta_keywords': bool(data.get('meta_keywords')),
            'score': 0
        }
        
        # Проверка канонического URL
        if analysis['has_canonical']:
            analysis['score'] += 25
        
        # Проверка favicon
        if analysis['has_favicon']:
            analysis['score'] += 15
        
        # Проверка языка
        if analysis['has_language']:
            analysis['score'] += 15
        
        # Проверка структуры URL
        if analysis['url_structure']['is_good']:
            analysis['score'] += 25
        
        # Проверка мета-ключевых слов (устаревший фактор)
        if analysis['has_meta_keywords']:
            analysis['score'] += 10
        
        # Дополнительные 10 баллов за базовые технические требования
        analysis['score'] += 10
        
        return analysis
    
    def _analyze_url_structure(self, url: str) -> Dict:
        """Анализ структуры URL"""
        parsed = urlparse(url)
        path = parsed.path
        
        analysis = {
            'is_https': parsed.scheme == 'https',
            'is_short': len(url) <= 60,
            'has_keywords': self._has_keywords(path),
            'uses_hyphens': '-' in path,
            'no_underscores': '_' not in path,
            'is_good': False
        }
        
        # Оценка качества URL
        score = 0
        if analysis['is_https']:
            score += 1
        if analysis['is_short']:
            score += 1
        if analysis['has_keywords']:
            score += 1
        if analysis['uses_hyphens']:
            score += 1
        if analysis['no_underscores']:
            score += 1
        
        analysis['is_good'] = score >= 3
        
        return analysis
    
    def _has_keywords(self, text: str) -> bool:
        """Упрощенная проверка на наличие ключевых слов"""
        # В реальном приложении здесь будет проверка against списка ключевых слов
        # Для демонстрации проверяем на наличие общих SEO-терминов
        seo_keywords = ['анализ', 'оптимизация', 'продвижение', 'маркетинг', 'сайт', 'веб']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in seo_keywords)
    
    def _is_compelling_description(self, description: str) -> bool:
        """Упрощенная проверка привлекательности описания"""
        # Проверяем на наличие призывов к действию и эмоциональных слов
        call_to_action = ['купить', 'заказать', 'узнать', 'получить', 'скачать']
        emotional_words = ['лучший', 'уникальный', 'профессиональный', 'быстрый', 'качественный']
        
        desc_lower = description.lower()
        has_cta = any(cta in desc_lower for cta in call_to_action)
        has_emotional = any(emotional in desc_lower for emotional in emotional_words)
        
        return has_cta or has_emotional
    
    def _calculate_keyword_density(self, text: str) -> float:
        """Расчет плотности ключевых слов (упрощенный)"""
        words = text.lower().split()
        if len(words) == 0:
            return 0
        
        # Используем упрощенный список ключевых слов
        seo_keywords = ['анализ', 'оптимизация', 'продвижение', 'маркетинг', 'сайт', 'веб']
        keyword_count = sum(1 for word in words if any(keyword in word for keyword in seo_keywords))
        
        return (keyword_count / len(words)) * 100
    
    def _calculate_readability_score(self, text: str) -> float:
        """Расчет оценки читаемости (упрощенный)"""
        if not text:
            return 0
        
        sentences = text.split('.')
        words = text.split()
        
        if len(sentences) == 0:
            return 0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Упрощенная формула: чем короче предложения, тем выше читаемость
        if avg_words_per_sentence <= 15:
            return 80
        elif avg_words_per_sentence <= 20:
            return 60
        elif avg_words_per_sentence <= 25:
            return 40
        else:
            return 20
    
    def _calculate_seo_score(self, results: Dict) -> float:
        """Расчет общего SEO балла"""
        total_score = 0
        max_score = 0
        
        # Вес каждого аспекта
        weights = {
            'title_analysis': 0.2,
            'meta_description_analysis': 0.15,
            'headings_analysis': 0.15,
            'content_analysis': 0.2,
            'links_analysis': 0.15,
            'images_analysis': 0.1,
            'technical_seo': 0.05
        }
        
        for aspect, weight in weights.items():
            if aspect in results:
                total_score += results[aspect]['score'] * weight
                max_score += 100 * weight  # Максимальный балл для каждого аспекта
        
        return min(total_score, 100)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Генерация рекомендаций по улучшению"""
        recommendations = []
        
        # Рекомендации по заголовку
        title = results.get('title_analysis', {})
        if not title.get('is_present'):
            recommendations.append("Добавьте заголовок страницы (title tag)")
        elif not title.get('optimal_length'):
            recommendations.append("Оптимизируйте длину заголовка до 30-60 символов")
        
        # Рекомендации по мета-описанию
        meta_desc = results.get('meta_description_analysis', {})
        if not meta_desc.get('is_present'):
            recommendations.append("Добавьте мета-описание страницы")
        elif not meta_desc.get('optimal_length'):
            recommendations.append("Оптимизируйте длину мета-описания до 120-160 символов")
        
        # Рекомендации по заголовкам
        headings = results.get('headings_analysis', {})
        if not headings.get('has_h1'):
            recommendations.append("Добавьте один заголовок H1 на страницу")
        elif headings.get('has_multiple_h1'):
            recommendations.append("Используйте только один заголовок H1 на страницу")
        
        # Рекомендации по контенту
        content = results.get('content_analysis', {})
        if not content.get('has_sufficient_content'):
            recommendations.append("Увеличьте объем текстового контента до 300+ слов")
        
        # Рекомендации по изображениям
        images = results.get('images_analysis', {})
        if images.get('images_without_alt') > 0:
            recommendations.append(f"Добавьте alt-тексты для {images.get('images_without_alt')} изображений")
        
        # Рекомендации по ссылкам
        links = results.get('links_analysis', {})
        if not links.get('has_internal_links'):
            recommendations.append("Добавьте внутренние ссылки для улучшения навигации")
        
        return recommendations
    
    def _get_empty_results(self) -> Dict:
        """Возвращает пустые результаты анализа в случае ошибки"""
        return {
            'title_analysis': {'score': 0},
            'meta_description_analysis': {'score': 0},
            'headings_analysis': {'score': 0},
            'content_analysis': {'score': 0},
            'links_analysis': {'score': 0},
            'images_analysis': {'score': 0},
            'technical_seo': {'score': 0},
            'score': 0,
            'recommendations': ['Не удалось выполнить SEO анализ']
        }
