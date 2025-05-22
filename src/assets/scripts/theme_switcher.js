// Функция для получения текущей темы
const getTheme = () => {
    if (typeof localStorage !== 'undefined' && localStorage.getItem('theme')) {
        return localStorage.getItem('theme');
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
};

// Функция для установки темы
const applyTheme = (theme) => {
    window.requestAnimationFrame(() => {
        const htmlElement = document.documentElement;
        if (theme === 'light') {
            htmlElement.classList.remove('dark');
        } else {
            htmlElement.classList.add('dark');
        }
        updateIcons(theme);
    });
    // Сохраняем тему в localStorage для будущих сессий, если она еще не сохранена
    // или если она определилась через prefers-color-scheme и localStorage пуст.
    if (typeof localStorage !== 'undefined' && localStorage.getItem('theme') !== theme) {
        localStorage.setItem('theme', theme);
    }
};

const toggleTheme = (currentTheme) => {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(currentTheme);
    return currentTheme;
}

// Функция для обновления иконок
const updateIcons = (theme) => {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const sunIcon = themeToggle.querySelector('.icon-tabler-sun');
        const moonIcon = themeToggle.querySelector('.icon-tabler-moon-stars');

        if (sunIcon instanceof HTMLElement && moonIcon instanceof HTMLElement) {
            if (theme === 'dark') {
                sunIcon.style.display = 'none';
                moonIcon.style.display = 'block';
            } else {
                sunIcon.style.display = 'block';
                moonIcon.style.display = 'none';
            }
        }
    }
};

// Инициализация темы при загрузке скрипта (для предотвращения мигания)
const initialTheme = getTheme();
applyTheme(initialTheme);
// Обновляем иконки сразу после применения темы, но до полного DOMContentLoaded,
// так как кнопка уже может быть в DOM, если скрипт загружен defer
updateIcons(initialTheme);

// Функция для инициализации переключателя темы
export function initializeThemeSwitcher() {
    // Применяем тему еще раз на случай, если localStorage обновился другим скриптом
    let currentTheme = getTheme();
    applyTheme(currentTheme);

    const themeToggle = document.getElementById('theme-toggle');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            currentTheme = toggleTheme(currentTheme);
        });
    }
} 