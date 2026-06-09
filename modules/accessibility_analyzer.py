"""
Модуль для анализа доступности веб-ресурсов
"""
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class AccessibilityAnalyzer:
    """Класс для анализа доступности"""
    
    def __init__(self):
        pass
        
    def analyze(self, data: Dict) -> Dict:
        """
        Основной метод анализа доступности
        
        Args:
            data: Словарь с данными о веб-ресурсе от DataCollector
            
        Returns:
            Словарь с результатами анализа доступности
        """
        try:
            logger.info(f"Начинаю анализ доступности для URL: {data.get('url')}")
            
            results = {
                'images_accessibility': self._analyze_images_accessibility(data),
                'forms_accessibility': self._analyze_forms_accessibility(data),
                'headings_accessibility': self._analyze_headings_accessibility(data),
                'links_accessibility': self._analyze_links_accessibility(data),
                'color_contrast': self._analyze_color_contrast(data),
                'keyboard_navigation': self._analyze_keyboard_navigation(data),
                'aria_usage': self._analyze_aria_usage(data),
                'score': 0,
                'recommendations': []
            }
            
            # Расчет общего балла
            results['score'] = self._calculate_accessibility_score(results)
            
            # Генерация рекомендаций
            results['recommendations'] = self._generate_recommendations(results)
            
            logger.info(f"Анализ доступности завершен для URL: {data.get('url')}")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при анализе доступности: {e}")
            return self._get_empty_results()
    
    def _analyze_images_accessibility(self, data: Dict) -> Dict:
        """Анализ доступности изображений"""
        images = data.get('images', [])
        
        analysis = {
            'total_images': len(images),
            'images_with_alt': sum(1 for img in images if img.get('has_alt')),
            'images_without_alt': sum(1 for img in images if not img.get('has_alt')),
            'images_with_meaningful_alt': 0,
            'decorative_images': 0,
            'complex_images_without_longdesc': 0,
            'score': 0
        }
        
        # Анализ качества alt-текстов
        for img in images:
            alt = img.get('alt', '').strip()
            if alt:
                # Проверяем на осмысленный alt-текст (не просто "image" или "photo")
                if len(alt) > 3 and alt.lower() not in ['image', 'photo', 'картинка', 'фото']:
                    analysis['images_with_meaningful_alt'] += 1
                elif alt == '' or alt.lower() in ['image', 'photo', 'картинка', 'фото']:
                    analysis['decorative_images'] += 1
        
        # Проверка на сложные изображения без longdesc (упрощенная)
        complex_images = sum(1 for img in images 
                           if img.get('width') and int(img.get('width', 0)) > 500)
        analysis['complex_images_without_longdesc'] = complex_images
        
        # Расчет балла
        if len(images) > 0:
            alt_percentage = (analysis['images_with_alt'] / len(images)) * 100
            meaningful_alt_percentage = (analysis['images_with_meaningful_alt'] / len(images)) * 100
            
            if alt_percentage >= 90:
                analysis['score'] += 50
            elif alt_percentage >= 70:
                analysis['score'] += 30
            elif alt_percentage >= 50:
                analysis['score'] += 15
            
            if meaningful_alt_percentage >= 80:
                analysis['score'] += 30
            elif meaningful_alt_percentage >= 60:
                analysis['score'] += 20
            elif meaningful_alt_percentage >= 40:
                analysis['score'] += 10
            
            # Штраф за сложные изображения без описания
            if analysis['complex_images_without_longdesc'] == 0:
                analysis['score'] += 20
            else:
                analysis['score'] -= min(analysis['complex_images_without_longdesc'] * 5, 20)
        else:
            analysis['score'] = 100  # Нет изображений - нет проблем
        
        analysis['score'] = max(0, min(100, analysis['score']))
        
        return analysis
    
    def _analyze_forms_accessibility(self, data: Dict) -> Dict:
        """Анализ доступности форм"""
        html = data.get('html', '')
        soup = data.get('soup')
        
        if not soup:
            return {'score': 50, 'forms_count': 0}
        
        forms = soup.find_all('form')
        
        analysis = {
            'forms_count': len(forms),
            'inputs_with_labels': 0,
            'inputs_without_labels': 0,
            'forms_with_fieldsets': 0,
            'inputs_with_placeholders': 0,
            'submit_buttons': 0,
            'score': 0
        }
        
        for form in forms:
            # Проверяем наличие fieldset
            if form.find('fieldset'):
                analysis['forms_with_fieldsets'] += 1
            
            # Анализируем поля ввода
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            for input_elem in inputs:
                input_type = input_elem.get('type', '')
                
                # Пропускаем скрытые поля и кнопки
                if input_type in ['hidden', 'submit', 'button', 'reset']:
                    if input_type in ['submit', 'button']:
                        analysis['submit_buttons'] += 1
                    continue
                
                # Проверяем наличие label
                label_id = input_elem.get('id')
                has_label = False
                
                if label_id:
                    label = soup.find('label', {'for': label_id})
                    if label:
                        has_label = True
                
                # Проверяем aria-label
                aria_label = input_elem.get('aria-label')
                if aria_label:
                    has_label = True
                
                # Проверяем placeholder
                placeholder = input_elem.get('placeholder')
                if placeholder:
                    analysis['inputs_with_placeholders'] += 1
                
                if has_label:
                    analysis['inputs_with_labels'] += 1
                else:
                    analysis['inputs_without_labels'] += 1
        
        # Расчет балла
        if len(forms) > 0:
            total_inputs = analysis['inputs_with_labels'] + analysis['inputs_without_labels']
            
            if total_inputs > 0:
                label_percentage = (analysis['inputs_with_labels'] / total_inputs) * 100
                
                if label_percentage >= 90:
                    analysis['score'] += 40
                elif label_percentage >= 70:
                    analysis['score'] += 25
                elif label_percentage >= 50:
                    analysis['score'] += 10
                
                # Дополнительные баллы за fieldset
                if analysis['forms_with_fieldsets'] == len(forms):
                    analysis['score'] += 30
                elif analysis['forms_with_fieldsets'] > 0:
                    analysis['score'] += 15
                
                # Баллы за кнопки отправки
                if analysis['submit_buttons'] >= len(forms):
                    analysis['score'] += 30
                elif analysis['submit_buttons'] > 0:
                    analysis['score'] += 15
        else:
            analysis['score'] = 100  # Нет форм - нет проблем
        
        analysis['score'] = max(0, min(100, analysis['score']))
        
        return analysis
    
    def _analyze_headings_accessibility(self, data: Dict) -> Dict:
        """Анализ доступности заголовков"""
        soup = data.get('soup')
        
        if not soup:
            return {'score': 50}
        
        headings = []
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            for tag in h_tags:
                headings.append({
                    'level': i,
                    'text': tag.get_text().strip(),
                    'has_text': bool(tag.get_text().strip())
                })
        
        analysis = {
            'total_headings': len(headings),
            'headings_with_text': sum(1 for h in headings if h['has_text']),
            'proper_hierarchy': True,
            'has_h1': False,
            'multiple_h1': False,
            'skipped_levels': [],
            'score': 0
        }
        
        # Проверка на H1
        h1_count = sum(1 for h in headings if h['level'] == 1)
        analysis['has_h1'] = h1_count > 0
        analysis['multiple_h1'] = h1_count > 1
        
        # Проверка иерархии
        if headings:
            prev_level = 0
            for heading in headings:
                current_level = heading['level']
                
                # Проверяем на пропуск уровней (например, H1 -> H3)
                if prev_level > 0 and current_level > prev_level + 1:
                    analysis['proper_hierarchy'] = False
                    analysis['skipped_levels'].append(f"H{prev_level} -> H{current_level}")
                
                prev_level = current_level
        
        # Расчет балла
        if analysis['has_h1'] and not analysis['multiple_h1']:
            analysis['score'] += 30
        elif analysis['has_h1']:
            analysis['score'] += 15
        
        if analysis['proper_hierarchy']:
            analysis['score'] += 40
        else:
            analysis['score'] -= len(analysis['skipped_levels']) * 10
        
        # Баллы за осмысленные тексты заголовков
        if len(headings) > 0:
            text_percentage = (analysis['headings_with_text'] / len(headings)) * 100
            if text_percentage >= 90:
                analysis['score'] += 30
            elif text_percentage >= 70:
                analysis['score'] += 20
            elif text_percentage >= 50:
                analysis['score'] += 10
        else:
            analysis['score'] = 50  # Нет заголовков - средний балл
        
        analysis['score'] = max(0, min(100, analysis['score']))
        
        return analysis
    
    def _analyze_links_accessibility(self, data: Dict) -> Dict:
        """Анализ доступности ссылок"""
        links = data.get('links', {})
        
        analysis = {
            'total_links': links.get('total', 0),
            'links_with_text': 0,
            'links_without_text': 0,
            'links_with_meaningful_text': 0,
            'links_with_title': 0,
            'ambiguous_links': 0,
            'score': 0
        }
        
        for link_list in [links.get('internal', []), links.get('external', [])]:
            for link in link_list:
                text = link.get('text', '').strip()
                
                if text:
                    analysis['links_with_text'] += 1
                    
                    # Проверяем на осмысленный текст
                    if (len(text) > 2 and 
                        text.lower() not in ['здесь', 'тут', 'click', 'here', 'click here', 'подробнее']):
                        analysis['links_with_meaningful_text'] += 1
                    else:
                        analysis['ambiguous_links'] += 1
                else:
                    analysis['links_without_text'] += 1
        
        # Расчет балла
        if analysis['total_links'] > 0:
            text_percentage = (analysis['links_with_text'] / analysis['total_links']) * 100
            meaningful_percentage = (analysis['links_with_meaningful_text'] / analysis['total_links']) * 100
            
            if text_percentage >= 95:
                analysis['score'] += 40
            elif text_percentage >= 85:
                analysis['score'] += 25
            elif text_percentage >= 70:
                analysis['score'] += 10
            
            if meaningful_percentage >= 90:
                analysis['score'] += 40
            elif meaningful_percentage >= 75:
                analysis['score'] += 25
            elif meaningful_percentage >= 60:
                analysis['score'] += 10
            
            # Штраф за неоднозначные ссылки
            if analysis['ambiguous_links'] == 0:
                analysis['score'] += 20
            else:
                analysis['score'] -= min(analysis['ambiguous_links'] * 5, 20)
        else:
            analysis['score'] = 100  # Нет ссылок - нет проблем
        
        analysis['score'] = max(0, min(100, analysis['score']))
        
        return analysis
    
    def _analyze_color_contrast(self, data: Dict) -> Dict:
        """Анализ цветового контраста (упрощенный)"""
        # В реальном приложении здесь будет анализ CSS и расчет контрастности
        return {
            'has_sufficient_contrast': True,  # Заглушка
            'contrast_issues': 0,
            'score': 85  # Заглушка
        }
    
    def _analyze_keyboard_navigation(self, data: Dict) -> Dict:
        """Анализ навигации с клавиатуры (упрощенный)"""
        html = data.get('html', '')
        
        analysis = {
            'has_skip_links': 'skip' in html.lower() or 'пропустить' in html.lower(),
            'has_focus_indicators': ':focus' in html or 'outline' in html,
            'tab_index_issues': 0,
            'keyboard_accessible': True,
            'score': 0
        }
        
        # Расчет балла (упрощенный)
        score = 60  # Базовый балл
        
        if analysis['has_skip_links']:
            score += 20
        
        if analysis['has_focus_indicators']:
            score += 20
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_aria_usage(self, data: Dict) -> Dict:
        """Анализ использования ARIA"""
        html = data.get('html', '')
        
        analysis = {
            'has_aria_labels': 'aria-label' in html,
            'has_aria_describedby': 'aria-describedby' in html,
            'has_aria_roles': 'role=' in html,
            'has_landmarks': False,
            'aria_issues': 0,
            'score': 0
        }
        
        # Проверка на ARIA ландмарки
        landmarks = ['banner', 'navigation', 'main', 'complementary', 'contentinfo', 'search', 'form']
        analysis['has_landmarks'] = any(f'role="{landmark}"' in html for landmark in landmarks)
        
        # Расчет балла
        score = 40  # Базовый балл
        
        if analysis['has_aria_labels']:
            score += 20
        
        if analysis['has_aria_describedby']:
            score += 15
        
        if analysis['has_landmarks']:
            score += 25
        
        analysis['score'] = score
        
        return analysis
    
    def _calculate_accessibility_score(self, results: Dict) -> float:
        """Расчет общего балла доступности"""
        total_score = 0
        max_score = 0
        
        # Вес каждого аспекта
        weights = {
            'images_accessibility': 0.2,
            'forms_accessibility': 0.15,
            'headings_accessibility': 0.15,
            'links_accessibility': 0.15,
            'color_contrast': 0.15,
            'keyboard_navigation': 0.1,
            'aria_usage': 0.1
        }
        
        for aspect, weight in weights.items():
            if aspect in results:
                score = results[aspect].get('score', 0)
                total_score += score * weight
                max_score += 100 * weight
        
        return min(total_score, 100)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Генерация рекомендаций по улучшению доступности"""
        recommendations = []
        
        # Рекомендации по изображениям
        images = results.get('images_accessibility', {})
        if images.get('images_without_alt', 0) > 0:
            recommendations.append(f"Добавьте alt-тексты для {images.get('images_without_alt')} изображений")
        
        # Рекомендации по формам
        forms = results.get('forms_accessibility', {})
        if forms.get('inputs_without_labels', 0) > 0:
            recommendations.append(f"Добавьте label для {forms.get('inputs_without_labels')} полей формы")
        
        # Рекомендации по заголовкам
        headings = results.get('headings_accessibility', {})
        if not headings.get('proper_hierarchy'):
            recommendations.append("Исправьте иерархию заголовков (не пропускайте уровни)")
        
        if headings.get('multiple_h1'):
            recommendations.append("Используйте только один заголовок H1 на странице")
        
        # Рекомендации по ссылкам
        links = results.get('links_accessibility', {})
        if links.get('ambiguous_links', 0) > 0:
            recommendations.append("Замените неоднозначные тексты ссылок на более описательные")
        
        # Рекомендации по навигации
        keyboard = results.get('keyboard_navigation', {})
        if not keyboard.get('has_skip_links'):
            recommendations.append("Добавьте ссылку для пропуска навигации")
        
        # Рекомендации по ARIA
        aria = results.get('aria_usage', {})
        if not aria.get('has_landmarks'):
            recommendations.append("Используйте ARIA ландмарки для улучшения навигации")
        
        return recommendations
    
    def _get_empty_results(self) -> Dict:
        """Возвращает пустые результаты анализа в случае ошибки"""
        return {
            'images_accessibility': {'score': 0},
            'forms_accessibility': {'score': 0},
            'headings_accessibility': {'score': 0},
            'links_accessibility': {'score': 0},
            'color_contrast': {'score': 0},
            'keyboard_navigation': {'score': 0},
            'aria_usage': {'score': 0},
            'score': 0,
            'recommendations': ['Не удалось выполнить анализ доступности']
        }
