// Funcionalidades JavaScript personalizadas para Comedores Comunitarios

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar todas las funcionalidades
    initAnimations();
    initFormValidation();
    initInteractiveElements();
    
});

// Animaciones y efectos visuales
function initAnimations() {
    
    // Animación de contador para estadísticas
    const statsNumbers = document.querySelectorAll('.stats-number');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalNumber = parseInt(target.textContent.replace(/\D/g, ''));
                animateCounter(target, 0, finalNumber, 2000);
                observer.unobserve(target);
            }
        });
    }, observerOptions);
    
    statsNumbers.forEach(number => {
        observer.observe(number);
    });
    
    // Animación de aparición de elementos
    const animatedElements = document.querySelectorAll('.card, .feature-icon, .btn');
    
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'all 0.6s ease';
        animationObserver.observe(element);
    });
}

// Función para animar contadores
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    const originalText = element.textContent;
    const suffix = originalText.replace(/\d/g, '');
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * easeOutQuart(progress));
        element.textContent = current + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Función de easing para animaciones suaves
function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

// Validación de formularios
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
        
        // Validación en tiempo real
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

// Validar campo individual
function validateField(field) {
    const isValid = field.checkValidity();
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
}

// Elementos interactivos
function initInteractiveElements() {
    
    // Botones de favorito
    const favoriteButtons = document.querySelectorAll('.btn-outline-primary');
    favoriteButtons.forEach(button => {
        if (button.textContent.includes('Favorito')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                toggleFavorite(this);
            });
        }
    });
    
    // Tooltips personalizados
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
    
    // Botones de acción con efectos
    const actionButtons = document.querySelectorAll('.btn-action');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });
}

// Función para alternar favorito
function toggleFavorite(button) {
    const icon = button.querySelector('i');
    const isFavorited = button.classList.contains('active');
    
    if (isFavorited) {
        button.classList.remove('active');
        icon.className = 'fas fa-heart';
        button.innerHTML = '<i class="fas fa-heart me-1"></i>Favorito';
        showNotification('Removido de favoritos', 'info');
    } else {
        button.classList.add('active');
        icon.className = 'fas fa-heart text-danger';
        button.innerHTML = '<i class="fas fa-heart me-1 text-danger"></i>Favorito';
        showNotification('Agregado a favoritos', 'success');
    }
}

// Función para mostrar tooltip
function showTooltip(event) {
    const tooltipText = event.target.getAttribute('data-tooltip');
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-custom-text';
    tooltip.textContent = tooltipText;
    tooltip.style.cssText = `
        position: absolute;
        background: var(--text-dark);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
}

// Función para ocultar tooltip
function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip-custom-text');
    tooltips.forEach(tooltip => tooltip.remove());
}

// Efecto de ondulación para botones
function createRippleEffect(event, button) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    `;
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// Sistema de notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
        ${message}
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Obtener icono para notificación
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Exportar funciones para uso global
window.ComedoresApp = {
    showNotification,
    toggleFavorite,
    createRippleEffect
};
