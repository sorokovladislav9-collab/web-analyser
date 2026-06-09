"""
Тесты основного приложения Flask
"""
import pytest
from flask import Flask
from app import create_app, init_db
from models import db, User, Website
from config.config import TestingConfig

@pytest.fixture
def app():
    """Создание тестового приложения"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
        # Создаем тестового пользователя
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        yield app
        
        db.drop_all()

@pytest.fixture
def client(app):
    """Создание тестового клиента"""
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Аутентифицированный клиент"""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    return client

class TestBasicRoutes:
    """Тесты основных маршрутов"""
    
    def test_index_page(self, client):
        """Тест главной страницы"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Система анализа веб-ресурсов' in response.data
    
    def test_dashboard_redirect(self, client):
        """Тест редиректа дашборда для неавторизованного пользователя"""
        response = client.get('/dashboard')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_dashboard_authenticated(self, auth_client):
        """Тест дашборда для авторизованного пользователя"""
        response = auth_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Дашборд' in response.data

class TestAuthentication:
    """Тесты аутентификации"""
    
    def test_login_page(self, client):
        """Тест страницы входа"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Вход в систему' in response.data
    
    def test_login_valid(self, client):
        """Тест входа с валидными данными"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        assert response.status_code == 302
        assert '/dashboard' in response.location
    
    def test_login_invalid(self, client):
        """Тест входа с невалидными данными"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        assert b'Неверное имя пользователя или пароль' in response.data
    
    def test_register_page(self, client):
        """Тест страницы регистрации"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Регистрация' in response.data
    
    def test_register_valid(self, client):
        """Тест регистрации с валидными данными"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass',
            'confirm_password': 'newpass'
        })
        assert response.status_code == 302
        
        # Проверяем, что пользователь создан
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
    
    def test_register_invalid_passwords(self, client):
        """Тест регистрации с несовпадающими паролями"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass',
            'confirm_password': 'different'
        })
        assert response.status_code == 200
        assert b'Пароли не совпадают' in response.data
    
    def test_logout(self, auth_client):
        """Тест выхода"""
        response = auth_client.get('/auth/logout')
        assert response.status_code == 302
        assert '/auth/login' in response.location

class TestWebsiteManagement:
    """Тесты управления веб-ресурсами"""
    
    def test_websites_page_unauthorized(self, client):
        """Тест страницы веб-ресурсов для неавторизованного пользователя"""
        response = client.get('/websites')
        assert response.status_code == 302
    
    def test_websites_page_authorized(self, auth_client):
        """Тест страницы веб-ресурсов для авторизованного пользователя"""
        response = auth_client.get('/websites')
        assert response.status_code == 200
        assert b'Веб-ресурсы' in response.data
    
    def test_add_website_page(self, auth_client):
        """Тест страницы добавления веб-ресурса"""
        response = auth_client.get('/website/add')
        assert response.status_code == 200
        assert b'Добавление веб-ресурса' in response.data
    
    def test_add_website_valid(self, auth_client):
        """Тест добавления валидного веб-ресурса"""
        response = auth_client.post('/website/add', data={
            'url': 'https://example.com',
            'name': 'Example Site',
            'category': 'blog',
            'description': 'Test website'
        })
        assert response.status_code == 302
        assert '/websites' in response.location
        
        # Проверяем, что ресурс создан
        website = Website.query.filter_by(url='https://example.com').first()
        assert website is not None
        assert website.name == 'Example Site'
    
    def test_add_website_invalid_url(self, auth_client):
        """Тест добавления веб-ресурса с невалидным URL"""
        response = auth_client.post('/website/add', data={
            'url': 'invalid-url',
            'name': 'Invalid Site'
        })
        assert response.status_code == 200
        # Форма должна вернуться с ошибкой

class TestAPI:
    """Тесты API"""
    
    def test_api_websites_unauthorized(self, client):
        """Тест API веб-ресурсов без авторизации"""
        response = client.get('/api/websites')
        assert response.status_code == 302
    
    def test_api_websites_authorized(self, auth_client):
        """Тест API веб-ресурсов с авторизацией"""
        response = auth_client.get('/api/websites')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'websites' in data['data']
    
    def test_api_create_website(self, auth_client):
        """Тест API создания веб-ресурса"""
        response = auth_client.post('/api/websites', json={
            'url': 'https://api-test.com',
            'name': 'API Test Site',
            'category': 'test'
        })
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['url'] == 'https://api-test.com'
    
    def test_api_stats(self, auth_client):
        """Тест API статистики"""
        response = auth_client.get('/api/stats')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data

class TestModels:
    """Тесты моделей данных"""
    
    def test_user_model(self, app):
        """Тест модели пользователя"""
        with app.app_context():
            user = User(username='modeltest', email='model@test.com')
            user.set_password('testpass')
            
            assert user.username == 'modeltest'
            assert user.email == 'model@test.com'
            assert user.check_password('testpass') is True
            assert user.check_password('wrongpass') is False
            assert user.is_admin() is False
    
    def test_website_model(self, app):
        """Тест модели веб-ресурса"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            website = Website(
                url='https://modeltest.com',
                name='Model Test',
                created_by=user.id
            )
            
            assert website.url == 'https://modeltest.com'
            assert website.name == 'Model Test'
            assert website.created_by == user.id

class TestErrorHandlers:
    """Тесты обработчиков ошибок"""
    
    def test_404_error(self, client):
        """Тест 404 ошибки"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'Страница не найдена' in response.data
    
    def test_500_error(self, app):
        """Тест 500 ошибки"""
        with app.test_client() as client:
            # Создаем ситуацию, которая вызовет 500 ошибку
            with app.app_context():
                # Удаляем все таблицы для вызова ошибки базы данных
                db.drop_all()
                
                response = client.get('/dashboard')
                assert response.status_code == 500

if __name__ == '__main__':
    pytest.main([__file__])
