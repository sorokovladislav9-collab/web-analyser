# Система анализа веб-ресурсов

Комплексная система для сравнительного анализа качественных показателей веб-ресурсов, включающая SEO, производительность, доступность, безопасность и UX анализ.

## Возможности

- **SEO анализ**: мета-теги, заголовки, контент, ссылки, изображения
- **Анализ производительности**: скорость загрузки, Core Web Vitals, оптимизация ресурсов
- **Анализ доступности**: соответствие WCAG, доступность для людей с ограниченными возможностями
- **Анализ безопасности**: HTTPS, заголовки безопасности, уязвимости
- **UX анализ**: мобильная адаптация, удобство использования, навигация
- **Сравнительный анализ**: сравнение нескольких веб-ресурсов
- **Генерация отчетов**: HTML, PDF, JSON форматы
- **REST API**: программный доступ к функциям системы

## Технологический стек

- **Backend**: Python 3.8+, Flask 2.3.3
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **База данных**: MySQL 8.0
- **Тестирование**: pytest
- **CI/CD**: GitHub Actions

## Системные требования

- Python 3.8 или выше
- MySQL 8.0 или выше
- 2GB RAM (минимум)
- 1GB свободного дискового пространства

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/username/web-analytics.git
cd web-analytics
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных MySQL

```sql
-- Создание базы данных
CREATE DATABASE web_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создание пользователя (опционально)
CREATE USER 'web_analytics'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON web_analytics.* TO 'web_analytics'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=web_analytics

# API ключи (опционально)
GOOGLE_PAGESPEED_API_KEY=your_google_api_key
LHCI_API_KEY=your_lhci_api_key
```

### 5. Инициализация базы данных

```bash
# Импорт схемы
mysql -u root -p web_analytics < db/schema.sql

# Запуск приложения с инициализацией
python app.py
```

### 6. Запуск приложения

```bash
python app.py
```

Приложение будет доступно по адресу: http://localhost:5000

## Документация API

### Аутентификация

Все API endpoints требуют аутентификации. Используйте cookie сессии или API ключи.

### Основные endpoints

#### Веб-ресурсы

- `GET /api/websites` - Получение списка веб-ресурсов
- `POST /api/websites` - Создание нового веб-ресурса
- `GET /api/websites/{id}` - Получение информации о веб-ресурсе
- `PUT /api/websites/{id}` - Обновление веб-ресурса
- `DELETE /api/websites/{id}` - Удаление веб-ресурса

#### Анализы

- `GET /api/analyses` - Получение списка анализов
- `GET /api/analyses/{id}` - Получение детальной информации об анализе
- `POST /api/analyses` - Запуск нового анализа

#### Статистика

- `GET /api/stats` - Получение статистики

### Примеры запросов

```bash
# Получение списка веб-ресурсов
curl -X GET http://localhost:5000/api/websites \
  -H "Cookie: session=your_session_cookie"

# Создание нового веб-ресурса
curl -X POST http://localhost:5000/api/websites \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{"url": "https://example.com", "name": "Example Site"}'
```

## Структура проекта

```
web-analytics/
├── app.py                 # Основное приложение Flask
├── requirements.txt       # Зависимости Python
├── config/
│   └── config.py         # Конфигурация приложения
├── models.py              # Модели данных SQLAlchemy
├── routes/                # Маршруты Flask
│   ├── auth.py          # Аутентификация
│   ├── main.py          # Основные страницы
│   ├── api.py           # REST API
│   ├── analysis.py      # Анализ веб-ресурсов
│   └── reports.py       # Генерация отчетов
├── modules/              # Модули анализа
│   ├── data_collector.py
│   ├── seo_analyzer.py
│   ├── performance_analyzer.py
│   ├── accessibility_analyzer.py
│   ├── security_analyzer.py
│   ├── ux_analyzer.py
│   └── report_generator.py
├── templates/            # HTML шаблоны
├── static/              # Статические файлы
│   ├── css/
│   ├── js/
│   └── images/
├── tests/               # Тесты
├── db/                  # Файлы базы данных
│   └── schema.sql
└── .github/workflows/   # CI/CD конфигурации
```

## Тестирование

### Запуск всех тестов

```bash
pytest
```

### Запуск тестов с покрытием кода

```bash
pytest --cov=app --cov=routes --cov=models --cov=modules --cov-report=html
```

### Запуск конкретных тестов

```bash
pytest tests/test_app.py::TestAuthentication
pytest tests/test_app.py::TestAPI
```

## Роли пользователей

- **Admin**: полный доступ ко всем функциям
- **Analyst**: может создавать анализы и просматривать отчеты
- **Viewer**: может только просматривать результаты

## Заглушки и моки

Система использует заглушки для внешних API:

- **Google PageSpeed API**: генерирует mock данные о производительности
- **Lighthouse API**: mock данные для анализа доступности
- **Внешние сервисы**: mock ответы для сетевых запросов

Для подключения реальных API ключей:

1. Получите API ключи у соответствующих провайдеров
2. Добавьте их в переменные окружения
3. Перезапустите приложение

## Разработка

### Установка окружения разработки

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей для разработки
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Форматирование кода

```bash
black .
isort .
```

### Проверка кода

```bash
flake8 .
bandit -r .
```

## Внесение изменений

1. Fork репозитория
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Внесите изменения
4. Запустите тесты (`pytest`)
5. Создайте коммит (`git commit -m 'Add amazing feature'`)
6. Отправьте в ветку (`git push origin feature/amazing-feature`)
7. Создайте Pull Request

## Лицензия

Этот проект лицензирован под MIT License - см. файл LICENSE для деталей.

## Поддержка

- Документация: [Wiki](https://github.com/username/web-analytics/wiki)
- Вопросы: [Issues](https://github.com/username/web-analytics/issues)
- Обсуждения: [Discussions](https://github.com/username/web-analytics/discussions)

## Авторы

- **Ваше Имя** - *Initial work* - [YourUsername](https://github.com/YourUsername)

## Благодарности

- Flask сообществу
- Bootstrap
- Chart.js
- Разработчикам используемых библиотек

## История изменений

### v1.0.0 (2024-03-19)
- Первоначальный выпуск
- Базовый функционал анализа
- REST API
- Система аутентификации
- Генерация отчетов
