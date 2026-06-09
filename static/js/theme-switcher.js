// Переключатель тем для улучшения доступности
document.addEventListener('DOMContentLoaded', function() {
    // Создаем переключатель тем
    const themeSwitcher = document.createElement('div');
    themeSwitcher.className = 'theme-switcher position-fixed top-0 end-0 p-3';
    themeSwitcher.style.zIndex = '9999';
    themeSwitcher.innerHTML = `
        <div class="btn-group" role="group">
            <button type="button" class="btn btn-sm btn-outline-light" id="light-theme" title="Светлая тема">
                <i class="fas fa-sun"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-light" id="dark-theme" title="Темная тема">
                <i class="fas fa-moon"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-light" id="high-contrast-theme" title="Высокая контрастность">
                <i class="fas fa-adjust"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(themeSwitcher);
    
    // Функция переключения темы
    function switchTheme(themeName) {
        const cssLinks = document.querySelectorAll('link[href*="css"]');
        
        cssLinks.forEach(link => {
            if (link.href.includes('css/')) {
                link.href = `/static/css/${themeName}-style.css`;
            }
        });
        
        // Сохраняем выбор в localStorage
        localStorage.setItem('preferred-theme', themeName);
        
        // Обновляем активную кнопку
        document.querySelectorAll('.theme-switcher button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`${themeName}-theme`).classList.add('active');
    }
    
    // Восстанавливаем сохраненную тему
    const savedTheme = localStorage.getItem('preferred-theme') || 'high-contrast';
    switchTheme(savedTheme);
    
    // Обработчики событий
    document.getElementById('light-theme').addEventListener('click', () => switchTheme('improved'));
    document.getElementById('dark-theme').addEventListener('click', () => switchTheme('dark'));
    document.getElementById('high-contrast-theme').addEventListener('click', () => switchTheme('high-contrast'));
    
    // Добавляем стили для переключателя
    const style = document.createElement('style');
    style.textContent = `
        .theme-switcher {
            background: rgba(0,0,0,0.8);
            border-radius: 0 0 0.5rem 0.5rem;
        }
        
        .theme-switcher button.active {
            background: #0066cc !important;
            border-color: #0066cc !important;
            color: white !important;
        }
        
        .theme-switcher button:hover {
            transform: scale(1.1);
        }
        
        .theme-switcher button {
            transition: all 0.3s ease;
            margin: 0 0.25rem;
        }
        
        /* Стили для темной темы */
        @media (prefers-color-scheme: dark) {
            .theme-switcher {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
            }
        }
    `;
    document.head.appendChild(style);
    
    // Показываем/скрываем переключатель при наведении
    let hideTimeout;
    themeSwitcher.addEventListener('mouseenter', () => {
        clearTimeout(hideTimeout);
        themeSwitcher.style.opacity = '1';
    });
    
    themeSwitcher.addEventListener('mouseleave', () => {
        hideTimeout = setTimeout(() => {
            themeSwitcher.style.opacity = '0.7';
        }, 2000);
    });
    
    // Изначально делаем переключатель полупрозрачным
    themeSwitcher.style.opacity = '0.7';
    
    // Горячие клавиши для переключения тем
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    switchTheme('improved');
                    break;
                case '2':
                    e.preventDefault();
                    switchTheme('dark');
                    break;
                case '3':
                    e.preventDefault();
                    switchTheme('high-contrast');
                    break;
            }
        }
    });
    
    // Добавляем подсказку о горячих клавишах
    const helpText = document.createElement('div');
    helpText.className = 'theme-help text-muted small mt-2';
    helpText.innerHTML = '<i class="fas fa-keyboard me-1"></i> Ctrl+1: Светлая | Ctrl+2: Темная | Ctrl+3: Высокая контрастность';
    themeSwitcher.appendChild(helpText);
});
