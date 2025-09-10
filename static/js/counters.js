// Contador animado para estadísticas
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    }
    
    updateCounter();
}

// Función para inicializar contadores
function initCounters() {
    const counters = document.querySelectorAll('.counter');
    
    if (counters.length > 0) {
        // Crear observador para cada contador
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-target'));
                    
                    if (target > 0) {
                        animateCounter(counter, target);
                        observer.unobserve(counter);
                    }
                }
            });
        }, {
            threshold: 0.5, // Activar cuando el 50% del elemento sea visible
            rootMargin: '0px 0px -50px 0px' // Activar un poco antes
        });
        
        // Observar cada contador
        counters.forEach(counter => {
            observer.observe(counter);
        });
        
        console.log(`🔢 ${counters.length} contadores encontrados y observando...`);
    } else {
        console.log('⚠️ No se encontraron contadores en la página');
    }
}

// Inicializar contadores cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCounters);
} else {
    // Si el DOM ya está cargado, ejecutar inmediatamente
    initCounters();
}

// También ejecutar después de un pequeño delay para asegurar que todo esté renderizado
setTimeout(initCounters, 100);
