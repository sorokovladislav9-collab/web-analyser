-- Схема базы данных для системы анализа веб-ресурсов
-- MySQL 8.0+

-- Создание базы данных
CREATE DATABASE IF NOT EXISTS web_analytics 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE web_analytics;

-- Пользователи системы
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'analyst', 'viewer') DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Веб-ресурсы для анализа
CREATE TABLE websites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(2048) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_url (url(255)),
    INDEX idx_category (category)
);

-- Анализ веб-ресурсов
CREATE TABLE analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    website_id INT NOT NULL,
    user_id INT NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    error_message TEXT,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_website_date (website_id, analysis_date),
    INDEX idx_status (status)
);

-- SEO метрики
CREATE TABLE seo_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    title VARCHAR(255),
    meta_description VARCHAR(500),
    h1_count INT DEFAULT 0,
    h2_count INT DEFAULT 0,
    internal_links INT DEFAULT 0,
    external_links INT DEFAULT 0,
    word_count INT DEFAULT 0,
    images_count INT DEFAULT 0,
    images_without_alt INT DEFAULT 0,
    score DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Метрики производительности
CREATE TABLE performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    load_time_ms INT DEFAULT 0,
    first_contentful_paint_ms INT DEFAULT 0,
    largest_contentful_paint_ms INT DEFAULT 0,
    cumulative_layout_shift DECIMAL(10,8) DEFAULT 0.00000000,
    first_input_delay_ms INT DEFAULT 0,
    time_to_interactive_ms INT DEFAULT 0,
    total_page_size_kb INT DEFAULT 0,
    requests_count INT DEFAULT 0,
    performance_score DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Метрики доступности (accessibility)
CREATE TABLE accessibility_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    alt_text_missing INT DEFAULT 0,
    aria_labels_missing INT DEFAULT 0,
    color_contrast_issues INT DEFAULT 0,
    keyboard_navigation_issues INT DEFAULT 0,
    form_labels_missing INT DEFAULT 0,
    accessibility_score DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Метрики безопасности
CREATE TABLE security_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    has_https BOOLEAN DEFAULT FALSE,
    has_security_headers BOOLEAN DEFAULT FALSE,
    vulnerable_libraries INT DEFAULT 0,
    mixed_content_issues INT DEFAULT 0,
    security_score DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- UX метрики
CREATE TABLE ux_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    mobile_friendly BOOLEAN DEFAULT FALSE,
    responsive_design BOOLEAN DEFAULT FALSE,
    readable_font_sizes BOOLEAN DEFAULT FALSE,
    clear_navigation BOOLEAN DEFAULT FALSE,
    ux_score DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Отчеты
CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    report_type ENUM('html', 'pdf', 'json') NOT NULL,
    file_path VARCHAR(500),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Сравнения веб-ресурсов
CREATE TABLE comparisons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Связь сравнений с веб-ресурсами
CREATE TABLE comparison_websites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comparison_id INT NOT NULL,
    website_id INT NOT NULL,
    FOREIGN KEY (comparison_id) REFERENCES comparisons(id) ON DELETE CASCADE,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE,
    UNIQUE KEY unique_comparison_website (comparison_id, website_id)
);

-- API ключи пользователей
CREATE TABLE api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Логирование действий
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Вставка администратора по умолчанию
INSERT INTO users (username, email, password_hash, role) VALUES 
('admin', 'admin@example.com', 'pbkdf2:sha256:260000$salt$hash', 'admin');
