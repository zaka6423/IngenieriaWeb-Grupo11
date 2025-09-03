// Modo oscuro
let darkMode = localStorage.getItem('darkMode') === 'true';

function toggleDarkMode() {
    darkMode = !darkMode;
    localStorage.setItem('darkMode', darkMode);
    applyDarkMode();
}

function applyDarkMode() {
    const body = document.body;
    const toggle = document.getElementById('darkModeToggle');
    const icon = toggle.querySelector('i');
    
    if (darkMode) {
        body.style.backgroundColor = '#1a1a1a';
        body.style.color = '#ffffff';
        body.classList.add('dark-mode');
        icon.className = 'fas fa-sun me-1';
        toggle.innerHTML = '<i class="fas fa-sun me-1"></i>Modo claro';
    } else {
        body.style.backgroundColor = '';
        body.style.color = '';
        body.classList.remove('dark-mode');
        icon.className = 'fas fa-moon me-1';
        toggle.innerHTML = '<i class="fas fa-moon me-1"></i>Modo oscuro';
    }
}

// Aplicar modo oscuro al cargar
document.addEventListener('DOMContentLoaded', () => {
    applyDarkMode();
    
    // Event listener para el toggle
    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);
});
