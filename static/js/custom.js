document.addEventListener('DOMContentLoaded', function() {
    initAnimations();
    initFormValidation();
    initInteractiveElements();
});

function initAnimations() {
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

function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

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

function initInteractiveElements() {
    const favoriteButtons = document.querySelectorAll('.btn-outline-primary');
    favoriteButtons.forEach(button => {
        if (button.textContent.includes('Favorito')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                toggleFavorite(this);
            });
        }
    });
    
    // Event listener para botones de voluntariado
    // EXCLUIR: .btn-donar-modal, .btn-enviar-donacion-modal, .btn-success (verde), botones dentro del modal, botones con "Donar"
    const volunteerButtons = document.querySelectorAll('button:not([disabled]):not(.btn-donar-modal):not(.btn-enviar-donacion-modal):not(.btn-success)');
    volunteerButtons.forEach(button => {
        // Si está dentro de un modal, saltarlo
        if (button.closest('.modal')) {
            return;
        }
        
        const buttonText = button.textContent.trim().toLowerCase();
        
        // VERIFICACIÓN EXPLÍCITA: Saltar cualquier cosa relacionada con donación
        if (buttonText.includes('donar') || buttonText.includes('donación')) {
            return;
        }
        
        // Solo manejar botones de voluntariado
        if (buttonText.includes('voluntario') || buttonText.includes('voluntariado')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                handleVolunteering(this);
            });
        }
    });
    
    // Event listener para botones de compartir
    // EXCLUIR: .btn-donar-modal, .btn-enviar-donacion-modal, .btn-success, botones dentro del modal
    const shareButtons = document.querySelectorAll('button:not([disabled]):not(.btn-donar-modal):not(.btn-enviar-donacion-modal):not(.btn-success)');
    shareButtons.forEach(button => {
        // Si está dentro de un modal, saltarlo
        if (button.closest('.modal')) {
            return;
        }
        
        const buttonText = button.textContent.trim().toLowerCase();
        
        // VERIFICACIÓN EXPLÍCITA: Saltar cualquier cosa relacionada con donación
        if (buttonText.includes('donar') || buttonText.includes('donación')) {
            return;
        }
        
        if (buttonText.includes('compartir')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                handleShare(this);
            });
        }
    });
    
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
    
    const actionButtons = document.querySelectorAll('.btn-action');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });
}

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

function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip-custom-text');
    tooltips.forEach(tooltip => tooltip.remove());
}

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
    
    // Agregar log para debug
    console.log(`📢 NOTIFICACIÓN: [${type.toUpperCase()}] ${message}`);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 10000); // Aumentado a 10 segundos para poder leer
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Función para manejar donaciones
function handleDonation(button) {
    // La funcionalidad de donaciones ya está implementada en el modal
    console.log('Donación manejada desde custom.js');
}

// Función para manejar voluntariado
function handleVolunteering(button) {
    showNotification('Esta funcionalidad estará disponible próximamente. Para ser voluntario, contacta directamente al comedor.', 'info');
}

// Función para manejar compartir
function handleShare(button) {
    if (navigator.share) {
        navigator.share({
            title: 'Comedores Comunitarios',
            text: 'Conoce este comedor comunitario y ayuda a construir una ciudad más solidaria',
            url: window.location.href
        }).then(() => {
            showNotification('¡Gracias por compartir!', 'success');
        }).catch(() => {
            fallbackShare();
        });
    } else {
        fallbackShare();
    }
}

// Función de respaldo para compartir
function fallbackShare() {
    const url = window.location.href;
    const text = 'Conoce este comedor comunitario y ayuda a construir una ciudad más solidaria';
    
    // Crear un modal simple para compartir
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 2rem; border-radius: 15px; max-width: 400px; text-align: center;">
            <h5 style="margin-bottom: 1rem; color: #2C3E50;">Compartir comedor</h5>
            <p style="margin-bottom: 1rem; color: #6c757d;">Copia este enlace para compartir:</p>
            <input type="text" value="${url}" readonly style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 1rem;">
            <div style="display: flex; gap: 0.5rem; justify-content: center;">
                <button onclick="navigator.clipboard.writeText('${url}').then(() => { showNotification('Enlace copiado al portapapeles', 'success'); this.parentElement.parentElement.parentElement.remove(); })" style="background: #FF6B35; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">Copiar</button>
                <button onclick="this.parentElement.parentElement.parentElement.remove()" style="background: #6c757d; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">Cerrar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Exportar funciones para uso global
window.ComedoresApp = {
    showNotification,
    toggleFavorite,
    createRippleEffect,
    handleDonation,
    handleVolunteering,
    handleShare
};
