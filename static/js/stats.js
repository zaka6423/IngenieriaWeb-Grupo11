function showStats() {
    // Buscar elementos con data-counter (nuevo formato)
    const dataCounters = document.querySelectorAll('[data-counter]');
    
    dataCounters.forEach((counter) => {
        const target = parseInt(counter.getAttribute('data-counter'));
        
        if (target > 0) {
            animateCounter(counter, target);
        } else {
            counter.textContent = '0';
        }
    });
    
    // Buscar elementos con clase counter (formato anterior)
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach((counter) => {
        const target = parseInt(counter.getAttribute('data-target'));
        
        if (target > 0) {
            animateCounter(counter, target);
        } else {
            counter.textContent = '0';
        }
    });
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 50; // 50 pasos para la animación
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 30); // 30ms entre cada paso
}

// Función para inicializar contadores con Intersection Observer
function initCountersWithObserver() {
    const counters = document.querySelectorAll('[data-counter], .counter');
    
    if (counters.length === 0) {
        return;
    }
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-counter') || counter.getAttribute('data-target'));
                
                if (target > 0) {
                    animateCounter(counter, target);
                    observer.unobserve(counter);
                }
            }
        });
    }, {
        threshold: 0.5,
        rootMargin: '0px 0px -50px 0px'
    });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    showStats();
    initCountersWithObserver();
});

window.addEventListener('load', function() {
    showStats();
});
