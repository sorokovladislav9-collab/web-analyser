"""
Модуль для анализа пользовательского опыта (UX)
"""
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class UXAnalyzer:
    """Класс для анализа UX"""
    
    def __init__(self):
        pass
        
    def analyze(self, data: Dict) -> Dict:
        """
        Основной метод анализа UX
        
        Args:
            data: Словарь с данными о веб-ресурсе от DataCollector
            
        Returns:
            Словарь с результатами анализа UX
        """
        try:
            logger.info(f"Начинаю UX анализ для URL: {data.get('url')}")
            
            results = {
                'mobile_friendly': self._analyze_mobile_friendly(data),
                'responsive_design': self._analyze_responsive_design(data),
                'navigation_analysis': self._analyze_navigation(data),
                'readability_analysis': self._analyze_readability(data),
                'content_structure': self._analyze_content_structure(data),
                'interaction_design': self._analyze_interaction_design(data),
                'performance_ux': self._analyze_performance_ux(data),
                'score': 0,
                'recommendations': []
            }
            
            # Расчет общего балла
            results['score'] = self._calculate_ux_score(results)
            
            # Генерация рекомендаций
            results['recommendations'] = self._generate_recommendations(results)
            
            logger.info(f"UX анализ завершен для URL: {data.get('url')}")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при UX анализе: {e}")
            return self._get_empty_results()
    
    def _analyze_mobile_friendly(self, data: Dict) -> Dict:
        """Анализ мобильной дружественности"""
        html = data.get('html', '')
        headers = data.get('headers', {})
        
        analysis = {
            'has_viewport': 'viewport' in html.lower(),
            'has_responsive_meta': self._check_responsive_meta(html),
            'has_touch_friendly_elements': self._check_touch_friendly_elements(html),
            'has_mobile_optimized_images': self._check_mobile_images(html),
            'font_size_appropriate': self._check_font_sizes(html),
            'has_zoom_disabled': 'user-scalable=no' in html.lower(),
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['has_viewport']:
            score += 25
        
        if analysis['has_responsive_meta']:
            score += 20
        
        if analysis['has_touch_friendly_elements']:
            score += 20
        
        if analysis['has_mobile_optimized_images']:
            score += 15
        
        if analysis['font_size_appropriate']:
            score += 15
        
        # Штраф за отключенный zoom
        if not analysis['has_zoom_disabled']:
            score += 5
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_responsive_design(self, data: Dict) -> Dict:
        """Анализ адаптивного дизайна"""
        html = data.get('html', '')
        
        analysis = {
            'has_media_queries': '@media' in html,
            'has_flexbox': 'display: flex' in html or 'flex:' in html,
            'has_grid': 'display: grid' in html or 'grid:' in html,
            'has_responsive_images': self._check_responsive_images(html),
            'has_fluid_layouts': self._check_fluid_layouts(html),
            'breakpoints_count': self._count_breakpoints(html),
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['has_media_queries']:
            score += 30
        
        if analysis['has_flexbox']:
            score += 20
        
        if analysis['has_grid']:
            score += 15
        
        if analysis['has_responsive_images']:
            score += 15
        
        if analysis['has_fluid_layouts']:
            score += 10
        
        # Дополнительные баллы за несколько breakpoints
        if analysis['breakpoints_count'] >= 3:
            score += 10
        elif analysis['breakpoints_count'] >= 2:
            score += 5
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_navigation(self, data: Dict) -> Dict:
        """Анализ навигации"""
        html = data.get('html', '')
        soup = data.get('soup')
        
        if not soup:
            return {'score': 50}
        
        analysis = {
            'has_main_navigation': self._has_main_navigation(soup),
            'has_breadcrumb': self._has_breadcrumb(soup),
            'has_search': self._has_search(soup),
            'navigation_consistency': self._check_navigation_consistency(soup),
            'has_skip_links': self._has_skip_links(html),
            'menu_depth': self._calculate_menu_depth(soup),
            'has_footer_navigation': self._has_footer_navigation(soup),
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['has_main_navigation']:
            score += 25
        
        if analysis['has_breadcrumb']:
            score += 15
        
        if analysis['has_search']:
            score += 15
        
        if analysis['navigation_consistency']:
            score += 15
        
        if analysis['has_skip_links']:
            score += 10
        
        if analysis['has_footer_navigation']:
            score += 10
        
        # Баллы за оптимальную глубину меню
        if 2 <= analysis['menu_depth'] <= 4:
            score += 10
        elif analysis['menu_depth'] == 1:
            score += 5
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_readability(self, data: Dict) -> Dict:
        """Анализ читаемости контента"""
        html = data.get('html', '')
        text_content = data.get('text_content', '')
        word_count = data.get('word_count', 0)
        
        analysis = {
            'has_sufficient_contrast': True,  # Заглушка
            'font_size_readable': self._check_font_sizes(html),
            'line_height_appropriate': self._check_line_height(html),
            'paragraph_length_good': self._check_paragraph_length(text_content),
            'sentence_length_good': self._check_sentence_length(text_content),
            'has_headings_structure': self._check_heading_structure(html),
            'readability_score': self._calculate_readability(text_content),
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['font_size_readable']:
            score += 20
        
        if analysis['line_height_appropriate']:
            score += 15
        
        if analysis['paragraph_length_good']:
            score += 15
        
        if analysis['sentence_length_good']:
            score += 15
        
        if analysis['has_headings_structure']:
            score += 15
        
        if analysis['readability_score'] >= 60:
            score += 20
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_content_structure(self, data: Dict) -> Dict:
        """Анализ структуры контента"""
        html = data.get('html', '')
        soup = data.get('soup')
        
        if not soup:
            return {'score': 50}
        
        analysis = {
            'has_clear_hierarchy': self._has_clear_hierarchy(soup),
            'has_content_sections': self._has_content_sections(soup),
            'has_sidebar': self._has_sidebar(soup),
            'has_footer': self._has_footer(soup),
            'content_above_fold': self._check_content_above_fold(html),
            'has_call_to_action': self._has_call_to_action(soup),
            'content_to_html_ratio': self._calculate_content_ratio(html),
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['has_clear_hierarchy']:
            score += 20
        
        if analysis['has_content_sections']:
            score += 15
        
        if analysis['has_sidebar']:
            score += 10
        
        if analysis['has_footer']:
            score += 10
        
        if analysis['content_above_fold']:
            score += 20
        
        if analysis['has_call_to_action']:
            score += 15
        
        # Баллы за соотношение контента
        if analysis['content_to_html_ratio'] >= 0.15:
            score += 10
        elif analysis['content_to_html_ratio'] >= 0.1:
            score += 5
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_interaction_design(self, data: Dict) -> Dict:
        """Анализ интерактивного дизайна"""
        html = data.get('html', '')
        
        analysis = {
            'has_hover_states': self._has_hover_states(html),
            'has_focus_states': self._has_focus_states(html),
            'has_loading_indicators': self._has_loading_indicators(html),
            'has_error_messages': self._has_error_messages(html),
            'has_success_messages': self._has_success_messages(html),
            'has_tooltips': self._has_tooltips(html),
            'interactive_elements_count': self._count_interactive_elements(html),
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['has_hover_states']:
            score += 20
        
        if analysis['has_focus_states']:
            score += 20
        
        if analysis['has_loading_indicators']:
            score += 15
        
        if analysis['has_error_messages']:
            score += 15
        
        if analysis['has_success_messages']:
            score += 10
        
        if analysis['has_tooltips']:
            score += 10
        
        # Баллы за количество интерактивных элементов
        if 5 <= analysis['interactive_elements_count'] <= 20:
            score += 10
        elif analysis['interactive_elements_count'] > 0:
            score += 5
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_performance_ux(self, data: Dict) -> Dict:
        """Анализ производительности с точки зрения UX"""
        load_time = data.get('load_time', 0)
        
        analysis = {
            'load_time_acceptable': load_time <= 3000,
            'load_time_fast': load_time <= 1500,
            'has_lazy_loading': 'loading="lazy"' in data.get('html', ''),
            'has_progressive_enhancement': self._has_progressive_enhancement(data.get('html', '')),
            'has_offline_support': False,  # Заглушка
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['load_time_fast']:
            score += 40
        elif analysis['load_time_acceptable']:
            score += 25
        
        if analysis['has_lazy_loading']:
            score += 20
        
        if analysis['has_progressive_enhancement']:
            score += 20
        
        if analysis['has_offline_support']:
            score += 20
        
        analysis['score'] = score
        
        return analysis
    
    def _check_responsive_meta(self, html: str) -> bool:
        """Проверка адаптивных мета-тегов"""
        patterns = [
            r'width=device-width',
            r'initial-scale=1',
            r'maximum-scale=1'
        ]
        
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_touch_friendly_elements(self, html: str) -> bool:
        """Проверка touch-friendly элементов"""
        # Ищем признаки адаптации для touch
        touch_indicators = [
            'touch-action',
            '-webkit-tap-highlight',
            'cursor: pointer',
            'ontouchstart'
        ]
        
        for indicator in touch_indicators:
            if indicator in html.lower():
                return True
        
        return False
    
    def _check_mobile_images(self, html: str) -> bool:
        """Проверка оптимизации изображений для мобильных"""
        patterns = [
            r'srcset',
            r'sizes',
            r'picture',
            r'<img.*loading="lazy"'
        ]
        
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_font_sizes(self, html: str) -> bool:
        """Проверка размеров шрифтов"""
        # Ищем признаки адекватных размеров шрифтов
        font_patterns = [
            r'font-size:\s*[1-2]\d+px',
            r'font-size:\s*[1-2]\d+rem',
            r'font-size:\s*[1-2]\d+em'
        ]
        
        for pattern in font_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_responsive_images(self, html: str) -> bool:
        """Проверка адаптивных изображений"""
        return ('srcset' in html) or ('picture' in html) or ('sizes' in html)
    
    def _check_fluid_layouts(self, html: str) -> bool:
        """Проверка fluid layouts"""
        fluid_indicators = [
            'max-width:',
            'width:100%',
            'flex:',
            'grid-template-columns: repeat('
        ]
        
        for indicator in fluid_indicators:
            if indicator in html.lower():
                return True
        
        return False
    
    def _count_breakpoints(self, html: str) -> int:
        """Подсчет breakpoints"""
        media_queries = re.findall(r'@media[^{]+', html, re.IGNORECASE)
        return len(media_queries)
    
    def _has_main_navigation(self, soup) -> bool:
        """Проверка наличия основной навигации"""
        nav_selectors = ['nav', '[role="navigation"', '.nav', '#nav', '.navigation', '#navigation']
        
        for selector in nav_selectors:
            if soup.select_one(selector):
                return True
        
        return False
    
    def _has_breadcrumb(self, soup) -> bool:
        """Проверка наличия хлебных крошек"""
        breadcrumb_selectors = [
            '.breadcrumb', '#breadcrumb', 
            '[aria-label="breadcrumb"]',
            '.breadcrumbs', '#breadcrumbs'
        ]
        
        for selector in breadcrumb_selectors:
            if soup.select_one(selector):
                return True
        
        return False
    
    def _has_search(self, soup) -> bool:
        """Проверка наличия поиска"""
        search_selectors = [
            'input[type="search"]',
            '.search', '#search',
            '[role="search"]'
        ]
        
        for selector in search_selectors:
            if soup.select_one(selector):
                return True
        
        return False
    
    def _check_navigation_consistency(self, soup) -> bool:
        """Проверка консистентности навигации"""
        # Упрощенная проверка
        nav = soup.find('nav') or soup.select_one('[role="navigation"]')
        if nav:
            links = nav.find_all('a')
            return len(links) >= 3 and len(links) <= 10
        
        return False
    
    def _has_skip_links(self, html: str) -> bool:
        """Проверка skip links"""
        return ('skip' in html.lower() and 'href=' in html.lower())
    
    def _calculate_menu_depth(self, soup) -> int:
        """Расчет глубины меню"""
        nav = soup.find('nav') or soup.select_one('[role="navigation"]')
        if not nav:
            return 0
        
        max_depth = 0
        
        def calculate_depth(element, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            for child in element.find_all(['ul', 'ol']):
                calculate_depth(child, current_depth + 1)
        
        calculate_depth(nav)
        return max_depth
    
    def _has_footer_navigation(self, soup) -> bool:
        """Проверка навигации в футере"""
        footer = soup.find('footer')
        if footer:
            links = footer.find_all('a')
            return len(links) > 0
        
        return False
    
    def _check_line_height(self, html: str) -> bool:
        """Проверка межстрочного интервала"""
        patterns = [
            r'line-height:\s*1\.[4-6]',
            r'line-height:\s*1\.[4-6]em',
            r'line-height:\s*1\.[4-6]rem'
        ]
        
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_paragraph_length(self, text: str) -> bool:
        """Проверка длины абзацев"""
        paragraphs = text.split('\n\n')
        if not paragraphs:
            return True
        
        avg_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
        return 20 <= avg_length <= 100
    
    def _check_sentence_length(self, text: str) -> bool:
        """Проверка длины предложений"""
        sentences = text.split('.')
        if not sentences:
            return True
        
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        return 10 <= avg_length <= 25
    
    def _check_heading_structure(self, html: str) -> bool:
        """Проверка структуры заголовков"""
        return ('<h1' in html) and ('<h2' in html)
    
    def _calculate_readability(self, text: str) -> float:
        """Расчет читаемости (упрощенный)"""
        if not text:
            return 0
        
        sentences = text.split('.')
        words = text.split()
        
        if len(sentences) == 0:
            return 0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Упрощенная формула
        if avg_words_per_sentence <= 15:
            return 80
        elif avg_words_per_sentence <= 20:
            return 60
        elif avg_words_per_sentence <= 25:
            return 40
        else:
            return 20
    
    def _has_clear_hierarchy(self, soup) -> bool:
        """Проверка четкой иерархии"""
        has_h1 = bool(soup.find('h1'))
        has_h2 = bool(soup.find('h2'))
        return has_h1 and has_h2
    
    def _has_content_sections(self, soup) -> bool:
        """Проверка секций контента"""
        sections = soup.find_all(['section', 'article', 'main'])
        return len(sections) > 0
    
    def _has_sidebar(self, soup) -> bool:
        """Проверка наличия сайдбара"""
        sidebar_selectors = [
            '.sidebar', '#sidebar',
            '.aside', '#aside',
            '[role="complementary"]'
        ]
        
        for selector in sidebar_selectors:
            if soup.select_one(selector):
                return True
        
        return False
    
    def _has_footer(self, soup) -> bool:
        """Проверка наличия футера"""
        return bool(soup.find('footer'))
    
    def _check_content_above_fold(self, html: str) -> bool:
        """Проверка контента выше сгиба"""
        # Упрощенная проверка - ищем контент в начале HTML
        first_part = html[:2000]  # Первые 2KB
        
        # Ищем признаки контента
        content_indicators = ['<p>', '<h1', '<h2', '<main', '<article']
        
        for indicator in content_indicators:
            if indicator in first_part:
                return True
        
        return False
    
    def _has_call_to_action(self, soup) -> bool:
        """Проверка наличия призыва к действию"""
        cta_texts = ['купить', 'заказать', 'регистрация', 'подписаться', 'узнать больше']
        
        for text in cta_texts:
            if soup.find(string=re.compile(text, re.IGNORECASE)):
                return True
        
        return False
    
    def _calculate_content_ratio(self, html: str) -> float:
        """Расчет соотношения контента к HTML"""
        # Упрощенная проверка
        text_content = re.sub(r'<[^>]+>', ' ', html)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if len(html) == 0:
            return 0
        
        return len(text_content) / len(html)
    
    def _has_hover_states(self, html: str) -> bool:
        """Проверка hover состояний"""
        return ':hover' in html
    
    def _has_focus_states(self, html: str) -> bool:
        """Проверка focus состояний"""
        return ':focus' in html
    
    def _has_loading_indicators(self, html: str) -> bool:
        """Проверка индикаторов загрузки"""
        loading_indicators = ['loading', 'spinner', 'progress', 'loader']
        
        for indicator in loading_indicators:
            if indicator in html.lower():
                return True
        
        return False
    
    def _has_error_messages(self, html: str) -> bool:
        """Проверка сообщений об ошибках"""
        error_indicators = ['error', 'alert', 'danger', 'warning']
        
        for indicator in error_indicators:
            if f'class="{indicator}' in html or f"class='{indicator}'" in html:
                return True
        
        return False
    
    def _has_success_messages(self, html: str) -> bool:
        """Проверка сообщений об успехе"""
        success_indicators = ['success', 'done', 'complete', 'ok']
        
        for indicator in success_indicators:
            if f'class="{indicator}' in html or f"class='{indicator}'" in html:
                return True
        
        return False
    
    def _has_tooltips(self, html: str) -> bool:
        """Проверка всплывающих подсказок"""
        tooltip_indicators = ['tooltip', 'title=', 'data-tooltip']
        
        for indicator in tooltip_indicators:
            if indicator in html.lower():
                return True
        
        return False
    
    def _count_interactive_elements(self, html: str) -> int:
        """Подсчет интерактивных элементов"""
        interactive_tags = ['button', 'input', 'select', 'textarea', 'a']
        
        count = 0
        for tag in interactive_tags:
            count += len(re.findall(f'<{tag}', html, re.IGNORECASE))
        
        return count
    
    def _has_progressive_enhancement(self, html: str) -> bool:
        """Проверка прогрессивного улучшения"""
        pe_indicators = ['<noscript>', 'no-js', 'modernizr']
        
        for indicator in pe_indicators:
            if indicator in html.lower():
                return True
        
        return False
    
    def _calculate_ux_score(self, results: Dict) -> float:
        """Расчет общего UX балла"""
        total_score = 0
        max_score = 0
        
        # Вес каждого аспекта
        weights = {
            'mobile_friendly': 0.2,
            'responsive_design': 0.15,
            'navigation_analysis': 0.15,
            'readability_analysis': 0.15,
            'content_structure': 0.15,
            'interaction_design': 0.1,
            'performance_ux': 0.1
        }
        
        for aspect, weight in weights.items():
            if aspect in results:
                score = results[aspect].get('score', 0)
                total_score += score * weight
                max_score += 100 * weight
        
        return min(total_score, 100)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Генерация рекомендаций по улучшению UX"""
        recommendations = []
        
        # Рекомендации по мобильной дружественности
        mobile = results.get('mobile_friendly', {})
        if not mobile.get('has_viewport'):
            recommendations.append("Добавьте viewport meta-тег для мобильных устройств")
        
        if not mobile.get('font_size_appropriate'):
            recommendations.append("Увеличьте размер шрифта для мобильных устройств")
        
        # Рекомендации по адаптивному дизайну
        responsive = results.get('responsive_design', {})
        if not responsive.get('has_media_queries'):
            recommendations.append("Добавьте media queries для адаптивного дизайна")
        
        # Рекомендации по навигации
        navigation = results.get('navigation_analysis', {})
        if not navigation.get('has_main_navigation'):
            recommendations.append("Добавьте основную навигацию")
        
        if not navigation.get('has_search'):
            recommendations.append("Добавьте поиск по сайту")
        
        # Рекомендации по читаемости
        readability = results.get('readability_analysis', {})
        if readability.get('readability_score', 0) < 60:
            recommendations.append("Улучшите читаемость контента")
        
        # Рекомендации по структуре
        structure = results.get('content_structure', {})
        if not structure.get('has_call_to_action'):
            recommendations.append("Добавите призыв к действию")
        
        return recommendations
    
    def _get_empty_results(self) -> Dict:
        """Возвращает пустые результаты анализа в случае ошибки"""
        return {
            'mobile_friendly': {'score': 0},
            'responsive_design': {'score': 0},
            'navigation_analysis': {'score': 0},
            'readability_analysis': {'score': 0},
            'content_structure': {'score': 0},
            'interaction_design': {'score': 0},
            'performance_ux': {'score': 0},
            'score': 0,
            'recommendations': ['Не удалось выполнить UX анализ']
        }
