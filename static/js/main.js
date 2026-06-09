// Основной JavaScript файл для системы анализа веб-ресурсов

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация тултипов
    initializeTooltips();
    
    // Инициализация всплывающих окон
    initializePopovers();
    
    // Автоматическое скрытие алертов
    initializeAutoHideAlerts();
    
    // Инициализация форм
    initializeForms();
});

// Инициализация Bootstrap тултипов
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Инициализация Bootstrap поповеров
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Автоматическое скрытие алертов через 5 секунд
function initializeAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Инициализация форм
function initializeForms() {
    // Валидация форм
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Функция для обновления статуса анализа
function updateAnalysisStatus(analysisId) {
    fetch(`/api/analyses/${analysisId}/status`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const statusElement = document.querySelector(`[data-analysis-id="${analysisId}"] .status-badge`);
                const progressBar = document.querySelector(`[data-analysis-id="${analysisId}"] .progress-bar`);
                
                if (statusElement) {
                    statusElement.className = `badge bg-${getStatusColor(data.status)}`;
                    statusElement.textContent = getStatusText(data.status);
                }
                
                if (progressBar && data.status === 'running') {
                    progressBar.style.width = '50%';
                    progressBar.setAttribute('aria-valuenow', '50');
                } else if (progressBar && data.status === 'completed') {
                    progressBar.style.width = '100%';
                    progressBar.setAttribute('aria-valuenow', '100');
                }
                
                // Если анализ завершился, обновляем страницу через 2 секунды
                if (data.status === 'completed' || data.status === 'failed') {
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка обновления статуса:', error);
        });
}

// Получение цвета статуса
function getStatusColor(status) {
    const colors = {
        'pending': 'secondary',
        'running': 'primary',
        'completed': 'success',
        'failed': 'danger'
    };
    return colors[status] || 'secondary';
}

// Получение текста статуса
function getStatusText(status) {
    const texts = {
        'pending': 'В очереди',
        'running': 'Выполняется',
        'completed': 'Завершен',
        'failed': 'Ошибка'
    };
    return texts[status] || status;
}

// Функция для массового выбора
function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.item-checkbox');
    checkboxes.forEach(function(item) {
        item.checked = checkbox.checked;
    });
    updateSelectedCount();
}

// Обновление счетчика выбранных элементов
function updateSelectedCount() {
    const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
    const countElement = document.getElementById('selected-count');
    if (countElement) {
        countElement.textContent = checkedBoxes.length;
    }
    
    // Показываем/скрываем кнопки массовых действий
    const actionButtons = document.getElementById('bulk-actions');
    if (actionButtons) {
        if (checkedBoxes.length > 0) {
            actionButtons.style.display = 'block';
        } else {
            actionButtons.style.display = 'none';
        }
    }
}

// Функция для подтверждения действия
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Функция для копирования текста в буфер обмена
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Скопировано в буфер обмена', 'success');
    }).catch(function(err) {
        console.error('Ошибка копирования:', err);
        showToast('Ошибка копирования', 'error');
    });
}

// Показать уведомление (toast)
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Удаляем элемент после скрытия
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Создание контейнера для уведомлений
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Функция для форматирования даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Функция для форматирования размера файла
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Функция для форматирования времени
function formatDuration(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
        return `${hours}ч ${minutes % 60}м ${seconds % 60}с`;
    } else if (minutes > 0) {
        return `${minutes}м ${seconds % 60}с`;
    } else {
        return `${seconds}с`;
    }
}

// Функция для debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Функция для поиска с debounce
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value;
            performSearch(query);
        }, 300));
    }
}

// Выполнение поиска
function performSearch(query) {
    // Здесь можно реализовать AJAX поиск
    console.log('Поиск:', query);
}

// Инициализация графиков Chart.js
function initializeCharts() {
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(function(element) {
        const chartType = element.dataset.chart;
        const chartData = JSON.parse(element.dataset.chartData);
        
        new Chart(element, {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    });
}

// Экспорт функций для использования в других скриптах
window.WebAnalytics = {
    updateAnalysisStatus,
    toggleSelectAll,
    updateSelectedCount,
    confirmAction,
    copyToClipboard,
    showToast,
    formatDate,
    formatFileSize,
    formatDuration,
    initializeSearch,
    initializeCharts
};
