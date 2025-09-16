// Sistema de mensajes simple y funcional
document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-ocultar mensajes después de 5 segundos (excepto errores y warnings)
    const alerts = document.querySelectorAll('.alert:not(.alert-danger):not(.alert-warning)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Mejorar la experiencia de formularios
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

    // Validación en tiempo real de campos
    const inputs = document.querySelectorAll('input[required], textarea[required], select[required]');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (input.hasAttribute('required') && !input.value.trim()) {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        });

        input.addEventListener('input', function() {
            if (input.classList.contains('is-invalid') && input.value.trim()) {
                input.classList.remove('is-invalid');
            }
        });
    });

    // Mejorar botones de envío
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const form = button.closest('form');
            if (form && form.checkValidity()) {
                // Solo cambiar la apariencia, no deshabilitar el botón
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
                
                // Re-habilitar el botón después de 5 segundos como fallback
                setTimeout(function() {
                    if (button.disabled) {
                        button.disabled = false;
                        button.innerHTML = originalText;
                    }
                }, 5000);
            }
        });
    });
});