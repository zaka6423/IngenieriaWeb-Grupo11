// Modo oscuro mejorado - Compatible con Edge y otros navegadores
let darkMode = localStorage.getItem('darkMode') === 'true';

function toggleDarkMode() {
    darkMode = !darkMode;
    localStorage.setItem('darkMode', darkMode);
    applyDarkMode();
}

function applyDarkMode() {
    const body = document.body;
    const toggle = document.getElementById('darkModeToggle');
    
    if (!toggle) return; // Verificar que el elemento existe
    
    const icon = toggle.querySelector('i');
    
    if (darkMode) {
        // Aplicar clase dark-mode al body
        body.classList.add('dark-mode');
        
        // Actualizar el botón toggle
        if (icon) {
            icon.className = 'fas fa-sun me-1';
        }
        toggle.innerHTML = '<i class="fas fa-sun me-1"></i>Modo claro';
        
        // Aplicar estilos específicos para Edge usando variables CSS
        body.style.setProperty('background-color', 'var(--dm-bg-primary)', 'important');
        body.style.setProperty('color', 'var(--dm-text-primary)', 'important');
        
    } else {
        // Remover clase dark-mode del body
        body.classList.remove('dark-mode');
        
        // Actualizar el botón toggle
        if (icon) {
            icon.className = 'fas fa-moon me-1';
        }
        toggle.innerHTML = '<i class="fas fa-moon me-1"></i>Modo oscuro';
        
        // Remover estilos inline
        body.style.removeProperty('background-color');
        body.style.removeProperty('color');
    }
}

// Aplicar modo oscuro al cargar
document.addEventListener('DOMContentLoaded', () => {
    // Esperar un poco para asegurar que todos los elementos estén cargados
    setTimeout(() => {
        applyDarkMode();
        
        // Event listener para el toggle
        const toggle = document.getElementById('darkModeToggle');
        if (toggle) {
            toggle.addEventListener('click', toggleDarkMode);
        }
    }, 100);
});

// También aplicar cuando la página esté completamente cargada
window.addEventListener('load', () => {
    applyDarkMode();
});
