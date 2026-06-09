"""
Пакет модулей для анализа веб-ресурсов
"""

from .data_collector import DataCollector
from .seo_analyzer import SEOAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from .accessibility_analyzer import AccessibilityAnalyzer
from .security_analyzer import SecurityAnalyzer
from .ux_analyzer import UXAnalyzer
from .report_generator import ReportGenerator

__all__ = [
    'DataCollector',
    'SEOAnalyzer', 
    'PerformanceAnalyzer',
    'AccessibilityAnalyzer',
    'SecurityAnalyzer',
    'UXAnalyzer',
    'ReportGenerator'
]
