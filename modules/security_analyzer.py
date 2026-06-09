"""
Модуль для анализа безопасности веб-ресурсов
"""
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Класс для анализа безопасности"""
    
    def __init__(self):
        self.security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Referrer-Policy'
        ]
        
    def analyze(self, data: Dict) -> Dict:
        """
        Основной метод анализа безопасности
        
        Args:
            data: Словарь с данными о веб-ресурсе от DataCollector
            
        Returns:
            Словарь с результатами анализа безопасности
        """
        try:
            logger.info(f"Начинаю анализ безопасности для URL: {data.get('url')}")
            
            results = {
                'https_analysis': self._analyze_https(data),
                'security_headers_analysis': self._analyze_security_headers(data),
                'content_security': self._analyze_content_security(data),
                'vulnerabilities': self._analyze_vulnerabilities(data),
                'mixed_content': self._analyze_mixed_content(data),
                'privacy_analysis': self._analyze_privacy(data),
                'score': 0,
                'recommendations': []
            }
            
            # Расчет общего балла
            results['score'] = self._calculate_security_score(results)
            
            # Генерация рекомендаций
            results['recommendations'] = self._generate_recommendations(results)
            
            logger.info(f"Анализ безопасности завершен для URL: {data.get('url')}")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при анализе безопасности: {e}")
            return self._get_empty_results()
    
    def _analyze_https(self, data: Dict) -> Dict:
        """Анализ HTTPS"""
        url = data.get('url', '')
        headers = data.get('headers', {})
        
        analysis = {
            'has_https': url.startswith('https://'),
            'redirects_to_https': False,
            'certificate_valid': True,  # Заглушка
            'protocol_version': 'TLS 1.2+',  # Заглушка
            'score': 0
        }
        
        # Базовый балл за HTTPS
        if analysis['has_https']:
            analysis['score'] = 50
            
            # Дополнительные баллы за заголовки HSTS
            if 'Strict-Transport-Security' in headers:
                analysis['score'] += 30
            
            # Проверка на редирект с HTTP
            if not url.startswith('https://'):
                analysis['redirects_to_https'] = True
                analysis['score'] += 20
        else:
            analysis['score'] = 0
        
        return analysis
    
    def _analyze_security_headers(self, data: Dict) -> Dict:
        """Анализ заголовков безопасности"""
        headers = data.get('headers', {})
        
        analysis = {
            'present_headers': [],
            'missing_headers': [],
            'header_scores': {},
            'total_headers': len(self.security_headers),
            'present_count': 0,
            'score': 0
        }
        
        # Проверяем каждый заголовок
        for header in self.security_headers:
            if header in headers:
                analysis['present_headers'].append(header)
                analysis['present_count'] += 1
                
                # Оцениваем качество заголовка
                header_score = self._evaluate_header_quality(header, headers[header])
                analysis['header_scores'][header] = header_score
            else:
                analysis['missing_headers'].append(header)
                analysis['header_scores'][header] = 0
        
        # Расчет общего балла
        if analysis['total_headers'] > 0:
            header_percentage = (analysis['present_count'] / analysis['total_headers']) * 100
            analysis['score'] = header_percentage
        
        return analysis
    
    def _analyze_content_security(self, data: Dict) -> Dict:
        """Анализ безопасности контента"""
        html = data.get('html', '')
        headers = data.get('headers', {})
        
        analysis = {
            'has_csp': 'Content-Security-Policy' in headers,
            'csp_policy': headers.get('Content-Security-Policy', ''),
            'has_inline_scripts': '<script>' in html and not 'nonce=' in html,
            'has_inline_styles': '<style>' in html and not 'nonce=' in html,
            'has_eval': 'eval(' in html,
            'has_document_write': 'document.write(' in html,
            'score': 0
        }
        
        # Расчет балла
        score = 0
        
        if analysis['has_csp']:
            score += 40
            
            # Дополнительные баллы за строгую политику
            if analysis['csp_policy']:
                if "default-src 'self'" in analysis['csp_policy']:
                    score += 20
                if "script-src 'self'" in analysis['csp_policy']:
                    score += 15
                if "style-src 'self'" in analysis['csp_policy']:
                    score += 15
                if "object-src 'none'" in analysis['csp_policy']:
                    score += 10
        
        # Штрафы за небезопасные практики
        if not analysis['has_inline_scripts']:
            score += 10
        else:
            score -= 10
        
        if not analysis['has_inline_styles']:
            score += 5
        else:
            score -= 5
        
        if not analysis['has_eval']:
            score += 10
        else:
            score -= 15
        
        if not analysis['has_document_write']:
            score += 5
        else:
            score -= 10
        
        analysis['score'] = max(0, min(100, score))
        
        return analysis
    
    def _analyze_vulnerabilities(self, data: Dict) -> Dict:
        """Анализ уязвимостей (упрощенный)"""
        html = data.get('html', '')
        headers = data.get('headers', {})
        
        analysis = {
            'sql_injection_risk': self._check_sql_injection_risk(html),
            'xss_risk': self._check_xss_risk(html),
            'csrf_risk': not 'SameSite' in headers.get('Set-Cookie', ''),
            'directory_traversal_risk': self._check_directory_traversal_risk(html),
            'file_inclusion_risk': self._check_file_inclusion_risk(html),
            'vulnerable_libraries': 0,  # Заглушка
            'score': 0
        }
        
        # Расчет балла
        score = 100
        
        # Штрафы за риски
        if analysis['sql_injection_risk']:
            score -= 20
        
        if analysis['xss_risk']:
            score -= 25
        
        if analysis['csrf_risk']:
            score -= 15
        
        if analysis['directory_traversal_risk']:
            score -= 15
        
        if analysis['file_inclusion_risk']:
            score -= 15
        
        if analysis['vulnerable_libraries'] > 0:
            score -= min(analysis['vulnerable_libraries'] * 10, 30)
        
        analysis['score'] = max(0, score)
        
        return analysis
    
    def _analyze_mixed_content(self, data: Dict) -> Dict:
        """Анализ смешанного контента"""
        html = data.get('html', '')
        url = data.get('url', '')
        
        analysis = {
            'has_https': url.startswith('https://'),
            'http_resources': 0,
            'https_resources': 0,
            'mixed_content_issues': 0,
            'insecure_forms': 0,
            'insecure_iframes': 0,
            'score': 0
        }
        
        if analysis['has_https']:
            # Ищем HTTP ресурсы в HTTPS странице
            http_patterns = [
                r'http://[^"\'\s]+',
                r'src=["\']http://',
                r'href=["\']http://',
                r'action=["\']http://'
            ]
            
            for pattern in http_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                analysis['http_resources'] += len(matches)
            
            # Проверяем формы
            form_matches = re.findall(r'action=["\']http://', html, re.IGNORECASE)
            analysis['insecure_forms'] = len(form_matches)
            
            # Проверяем iframe
            iframe_matches = re.findall(r'<iframe[^>]*src=["\']http://', html, re.IGNORECASE)
            analysis['insecure_iframes'] = len(iframe_matches)
            
            analysis['mixed_content_issues'] = (
                analysis['http_resources'] + 
                analysis['insecure_forms'] + 
                analysis['insecure_iframes']
            )
            
            # Расчет балла
            if analysis['mixed_content_issues'] == 0:
                analysis['score'] = 100
            elif analysis['mixed_content_issues'] <= 5:
                analysis['score'] = 70
            elif analysis['mixed_content_issues'] <= 10:
                analysis['score'] = 40
            else:
                analysis['score'] = 20
        else:
            analysis['score'] = 50  # HTTP страница - средний балл
        
        return analysis
    
    def _analyze_privacy(self, data: Dict) -> Dict:
        """Анализ приватности"""
        html = data.get('html', '')
        headers = data.get('headers', {})
        
        analysis = {
            'has_tracking_scripts': self._check_tracking_scripts(html),
            'has_cookies': 'Set-Cookie' in headers or 'cookie' in html.lower(),
            'has_privacy_policy': self._check_privacy_policy(html),
            'has_gdpr_compliance': self._check_gdpr_compliance(html),
            'third_party_requests': 0,  # Заглушка
            'score': 0
        }
        
        # Расчет балла
        score = 50  # Базовый балл
        
        if analysis['has_privacy_policy']:
            score += 20
        
        if analysis['has_gdpr_compliance']:
            score += 20
        
        if not analysis['has_tracking_scripts']:
            score += 10
        
        if analysis['third_party_requests'] <= 5:
            score += 10
        
        analysis['score'] = min(100, score)
        
        return analysis
    
    def _evaluate_header_quality(self, header: str, value: str) -> int:
        """Оценка качества заголовка безопасности"""
        if not value:
            return 0
        
        score = 0
        
        if header == 'Strict-Transport-Security':
            if 'max-age=' in value:
                score += 50
                if 'includeSubDomains' in value:
                    score += 30
                if 'preload' in value:
                    score += 20
        
        elif header == 'Content-Security-Policy':
            if 'default-src' in value:
                score += 30
            if 'script-src' in value:
                score += 25
            if 'style-src' in value:
                score += 25
            if 'object-src' in value:
                score += 20
        
        elif header == 'X-Frame-Options':
            if value in ['DENY', 'SAMEORIGIN']:
                score = 100
        
        elif header == 'X-Content-Type-Options':
            if value == 'nosniff':
                score = 100
        
        elif header == 'X-XSS-Protection':
            if '1; mode=block' in value:
                score = 100
            elif value == '1':
                score = 50
        
        elif header == 'Referrer-Policy':
            if value in ['strict-origin-when-cross-origin', 'no-referrer', 'same-origin']:
                score = 100
        
        return score
    
    def _check_sql_injection_risk(self, html: str) -> bool:
        """Проверка риска SQL-инъекций (упрощенная)"""
        # Ищем признаки уязвимого кода
        patterns = [
            r'\$_GET\[.*\]',
            r'\$_POST\[.*\]',
            r'\$_REQUEST\[.*\]',
            r'mysql_query.*\$\w+',
            r'SELECT.*FROM.*WHERE.*\$\w+'
        ]
        
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_xss_risk(self, html: str) -> bool:
        """Проверка риска XSS (упрощенная)"""
        # Ищем признаки уязвимого кода
        patterns = [
            r'innerHTML.*\$\w+',
            r'outerHTML.*\$\w+',
            r'document\.write.*\$\w+',
            r'eval.*\$\w+',
            r'echo.*\$\w+',
            r'print.*\$\w+'
        ]
        
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_directory_traversal_risk(self, html: str) -> bool:
        """Проверка риска directory traversal"""
        patterns = [
            r'\.\./.*\.\.',
            r'file_get_contents.*\$\w+',
            r'fopen.*\$\w+',
            r'readfile.*\$\w+'
        ]
        
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_file_inclusion_risk(self, html: str) -> bool:
        """Проверка риска file inclusion"""
        patterns = [
            r'include.*\$\w+',
            r'require.*\$\w+',
            r'include_once.*\$\w+',
            r'require_once.*\$\w+'
        ]
        
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        return False
    
    def _check_tracking_scripts(self, html: str) -> bool:
        """Проверка на отслеживающие скрипты"""
        tracking_domains = [
            'google-analytics',
            'googletagmanager',
            'facebook.net',
            'doubleclick',
            'googlesyndication'
        ]
        
        for domain in tracking_domains:
            if domain in html.lower():
                return True
        
        return False
    
    def _check_privacy_policy(self, html: str) -> bool:
        """Проверка наличия политики конфиденциальности"""
        policy_indicators = [
            'privacy policy',
            'политика конфиденциальности',
            'privacy',
            'конфиденциальность'
        ]
        
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in policy_indicators)
    
    def _check_gdpr_compliance(self, html: str) -> bool:
        """Проверка соответствия GDPR"""
        gdpr_indicators = [
            'gdpr',
            'cookie consent',
            'согласие на cookies',
            'персональные данные'
        ]
        
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in gdpr_indicators)
    
    def _calculate_security_score(self, results: Dict) -> float:
        """Расчет общего балла безопасности"""
        total_score = 0
        max_score = 0
        
        # Вес каждого аспекта
        weights = {
            'https_analysis': 0.25,
            'security_headers_analysis': 0.25,
            'content_security': 0.2,
            'vulnerabilities': 0.15,
            'mixed_content': 0.1,
            'privacy_analysis': 0.05
        }
        
        for aspect, weight in weights.items():
            if aspect in results:
                score = results[aspect].get('score', 0)
                total_score += score * weight
                max_score += 100 * weight
        
        return min(total_score, 100)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Генерация рекомендаций по улучшению безопасности"""
        recommendations = []
        
        # Рекомендации по HTTPS
        https = results.get('https_analysis', {})
        if not https.get('has_https'):
            recommendations.append("Включите HTTPS для шифрования данных")
        
        # Рекомендации по заголовкам
        headers = results.get('security_headers_analysis', {})
        missing_headers = headers.get('missing_headers', [])
        for header in missing_headers:
            recommendations.append(f"Добавьте заголовок безопасности: {header}")
        
        # Рекомендации по CSP
        csp = results.get('content_security', {})
        if not csp.get('has_csp'):
            recommendations.append("Настройте Content Security Policy (CSP)")
        
        # Рекомендации по уязвимостям
        vulns = results.get('vulnerabilities', {})
        if vulns.get('xss_risk'):
            recommendations.append("Устраните уязвимости XSS")
        
        if vulns.get('sql_injection_risk'):
            recommendations.append("Устраните уязвимости SQL-инъекций")
        
        # Рекомендации по смешанному контенту
        mixed = results.get('mixed_content', {})
        if mixed.get('mixed_content_issues', 0) > 0:
            recommendations.append("Исправьте проблемы смешанного контента")
        
        return recommendations
    
    def _get_empty_results(self) -> Dict:
        """Возвращает пустые результаты анализа в случае ошибки"""
        return {
            'https_analysis': {'score': 0},
            'security_headers_analysis': {'score': 0},
            'content_security': {'score': 0},
            'vulnerabilities': {'score': 0},
            'mixed_content': {'score': 0},
            'privacy_analysis': {'score': 0},
            'score': 0,
            'recommendations': ['Не удалось выполнить анализ безопасности']
        }
