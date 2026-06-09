"""
Модуль для сбора данных о веб-ресурсах
"""
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class DataCollector:
    """Класс для сбора данных о веб-ресурсах"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        
    def collect_data(self, url: str) -> Optional[Dict]:
        """
        Основной метод сбора данных
        
        Args:
            url: URL веб-ресурса для анализа
            
        Returns:
            Словарь с собранными данными или None в случае ошибки
        """
        try:
            logger.info(f"Начинаю сбор данных для URL: {url}")
            
            # Нормализация URL
            normalized_url = self._normalize_url(url)
            
            # Получение HTML контента
            response = self._fetch_page(normalized_url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Сбор различных типов данных
            data = {
                'url': normalized_url,
                'original_url': url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds() * 1000,  # в миллисекундах
                'content_length': len(response.content),
                'content_type': response.headers.get('content-type', ''),
                'headers': dict(response.headers),
                'html': response.text,
                'soup': soup,
                
                # Базовая информация
                'title': self._get_title(soup),
                'meta_description': self._get_meta_description(soup),
                'meta_keywords': self._get_meta_keywords(soup),
                'h1_tags': self._get_h1_tags(soup),
                'h2_tags': self._get_h2_tags(soup),
                'links': self._get_links(soup, normalized_url),
                'images': self._get_images(soup, normalized_url),
                'text_content': self._get_text_content(soup),
                'word_count': 0,
                
                # Техническая информация
                'has_https': normalized_url.startswith('https://'),
                'security_headers': self._check_security_headers(response.headers),
                'page_size': len(response.content),
                'load_time': response.elapsed.total_seconds() * 1000,
                
                # Дополнительные метаданные
                'canonical_url': self._get_canonical_url(soup, normalized_url),
                'language': self._get_language(soup),
                'favicon': self._get_favicon(soup, normalized_url),
                
                # Временные метки
                'collected_at': time.time()
            }
            
            # Подсчет слов
            data['word_count'] = len(data['text_content'].split())
            
            logger.info(f"Данные успешно собраны для URL: {url}")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при сборе данных для URL {url}: {e}")
            return None
    
    def _normalize_url(self, url: str) -> str:
        """Нормализация URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        """Получение страницы с обработкой ошибок"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при загрузке страницы {url}: {e}")
            return None
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Получение заголовка страницы"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Получение мета-описания"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Альтернативный поиск
        meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        return meta_desc.get('content', '').strip() if meta_desc else ''
    
    def _get_meta_keywords(self, soup: BeautifulSoup) -> str:
        """Получение ключевых слов"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else ''
    
    def _get_h1_tags(self, soup: BeautifulSoup) -> List[str]:
        """Получение H1 тегов"""
        h1_tags = soup.find_all('h1')
        return [tag.get_text().strip() for tag in h1_tags]
    
    def _get_h2_tags(self, soup: BeautifulSoup) -> List[str]:
        """Получение H2 тегов"""
        h2_tags = soup.find_all('h2')
        return [tag.get_text().strip() for tag in h2_tags]
    
    def _get_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Получение информации о ссылках"""
        links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            href = link['href']
            text = link.get_text().strip()
            
            # Пропускаем якоря и javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Преобразуем относительные ссылки в абсолютные
            absolute_url = urljoin(base_url, href)
            
            link_domain = urlparse(absolute_url).netloc
            
            link_info = {
                'url': absolute_url,
                'text': text,
                'is_internal': link_domain == base_domain,
                'has_text': bool(text.strip())
            }
            
            if link_domain == base_domain:
                internal_links.append(link_info)
            else:
                external_links.append(link_info)
        
        return {
            'internal': internal_links,
            'external': external_links,
            'total_internal': len(internal_links),
            'total_external': len(external_links),
            'total': len(links)
        }
    
    def _get_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Получение информации об изображениях"""
        images = soup.find_all('img')
        
        image_data = []
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # Преобразуем относительные ссылки в абсолютные
            if src:
                absolute_src = urljoin(base_url, src)
            else:
                absolute_src = ''
            
            image_info = {
                'src': absolute_src,
                'alt': alt,
                'has_alt': bool(alt.strip()),
                'width': img.get('width'),
                'height': img.get('height'),
                'title': img.get('title', '')
            }
            
            image_data.append(image_info)
        
        return image_data
    
    def _get_text_content(self, soup: BeautifulSoup) -> str:
        """Получение текстового содержимого"""
        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Получаем текст
        text = soup.get_text()
        
        # Очищаем от лишних пробелов и переносов
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _check_security_headers(self, headers: Dict) -> Dict:
        """Проверка заголовков безопасности"""
        security_headers = {
            'strict-transport-security': headers.get('Strict-Transport-Security'),
            'content-security-policy': headers.get('Content-Security-Policy'),
            'x-frame-options': headers.get('X-Frame-Options'),
            'x-content-type-options': headers.get('X-Content-Type-Options'),
            'x-xss-protection': headers.get('X-XSS-Protection'),
            'referrer-policy': headers.get('Referrer-Policy')
        }
        
        # Проверяем наличие заголовков
        has_security_headers = any(value is not None for value in security_headers.values())
        
        return {
            'headers': security_headers,
            'has_security_headers': has_security_headers,
            'score': self._calculate_security_score(security_headers)
        }
    
    def _calculate_security_score(self, security_headers: Dict) -> float:
        """Расчет оценки безопасности на основе заголовков"""
        score = 0
        max_score = len(security_headers)
        
        for header, value in security_headers.items():
            if value:
                score += 1
        
        return (score / max_score) * 100 if max_score > 0 else 0
    
    def _get_canonical_url(self, soup: BeautifulSoup, base_url: str) -> str:
        """Получение канонического URL"""
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            return urljoin(base_url, canonical['href'])
        return base_url
    
    def _get_language(self, soup: BeautifulSoup) -> str:
        """Определение языка страницы"""
        # Из HTML тега
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        # Из мета-тега
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta_lang:
            return meta_lang.get('content', '')
        
        return ''
    
    def _get_favicon(self, soup: BeautifulSoup, base_url: str) -> str:
        """Получение favicon"""
        # Ищем link rel="icon"
        favicon = soup.find('link', rel='icon')
        if favicon and favicon.get('href'):
            return urljoin(base_url, favicon['href'])
        
        # Ищем link rel="shortcut icon"
        favicon = soup.find('link', rel='shortcut icon')
        if favicon and favicon.get('href'):
            return urljoin(base_url, favicon['href'])
        
        # Возвращаем стандартный путь
        return urljoin(base_url, '/favicon.ico')
    
    def get_page_speed_metrics(self, url: str) -> Optional[Dict]:
        """
        Получение метрик производительности (заглушка)
        
        В реальном приложении здесь будет интеграция с Google PageSpeed API
        """
        # Mock данные для демонстрации
        return {
            'performance_score': 85,
            'first_contentful_paint': 1200,
            'largest_contentful_paint': 2400,
            'cumulative_layout_shift': 0.1,
            'first_input_delay': 50,
            'time_to_interactive': 3500,
            'total_blocking_time': 300
        }
    
    def get_accessibility_metrics(self, url: str) -> Optional[Dict]:
        """
        Получение метрик доступности (заглушка)
        
        В реальном приложении здесь будет интеграция с axe-core или similar
        """
        # Mock данные для демонстрации
        return {
            'accessibility_score': 75,
            'alt_text_missing': 3,
            'aria_labels_missing': 2,
            'color_contrast_issues': 1,
            'keyboard_navigation_issues': 0,
            'form_labels_missing': 1
        }
