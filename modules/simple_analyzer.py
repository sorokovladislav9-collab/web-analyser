"""
Упрощенный анализатор для быстрого тестирования
"""
import logging

logger = logging.getLogger(__name__)

class SimpleAnalyzer:
    """Простой анализатор для тестирования"""
    
    def __init__(self):
        pass
    
    def analyze(self, data):
        """Упрощенный анализ"""
        logger.info(f"Запуск упрощенного анализа для {data.get('url', 'неизвестно')}")
        
        # Возвращаем базовые результаты
        return {
            'score': 75.0,
            'recommendations': [
                'Добавьте мета-описание страницы',
                'Оптимизируйте изображения',
                'Проверьте заголовки H1-H6'
            ],
            'details': {
                'title': data.get('title', 'Нет заголовка'),
                'url': data.get('url', ''),
                'load_time': data.get('load_time', 1500),
                'images_count': len(data.get('images', []))
            }
        }
