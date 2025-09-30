// ===== VALIDACIONES Y FUNCIONALIDADES PARA PUBLICACIONES =====

document.addEventListener('DOMContentLoaded', function() {
    // Validación de fechas en formularios de publicaciones
    const fechaFinInputs = document.querySelectorAll('input[name="fecha_fin"]');
    
    fechaFinInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fechaFin = new Date(this.value);
            const ahora = new Date();
            
            if (fechaFin <= ahora) {
                this.setCustomValidity('La fecha de fin debe ser posterior a la fecha actual');
                this.classList.add('is-invalid');
                
                // Mostrar mensaje de error
                let errorDiv = this.parentNode.querySelector('.invalid-feedback');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    this.parentNode.appendChild(errorDiv);
                }
                errorDiv.textContent = 'La fecha de fin debe ser posterior a la fecha actual';
            } else {
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                
                // Remover mensaje de error
                const errorDiv = this.parentNode.querySelector('.invalid-feedback');
                if (errorDiv) {
                    errorDiv.remove();
                }
            }
        });
    });
    
    // Validación de formularios antes del envío
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Funcionalidad para agregar/eliminar artículos dinámicamente
    const agregarArticuloBtn = document.getElementById('agregar-articulo');
    if (agregarArticuloBtn) {
        const container = document.getElementById('articulos-container');
        let formCount = parseInt(document.getElementById('id_form-TOTAL_FORMS').value) || 0;
        
        agregarArticuloBtn.addEventListener('click', function() {
            const newForm = document.createElement('div');
            newForm.className = 'col-md-6 form-articulo';
            newForm.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="flex-grow-1 me-2">
                        <input type="text" 
                               name="form-${formCount}-nombre_articulo" 
                               class="form-control" 
                               placeholder="Ej: Leche en polvo 1kg" 
                               maxlength="255" 
                               id="id_form-${formCount}-nombre_articulo"
                               required>
                        <div class="invalid-feedback">
                            Por favor ingresa el nombre del artículo
                        </div>
                    </div>
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="eliminarArticulo(this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(newForm);
            formCount++;
            
            // Actualizar el management form
            document.getElementById('id_form-TOTAL_FORMS').value = formCount;
            
            // Agregar validación al nuevo input
            const newInput = newForm.querySelector('input');
            newInput.addEventListener('blur', function() {
                if (this.value.trim() === '') {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    }
    
    // Funcionalidad para eliminar artículos
    window.eliminarArticulo = function(button) {
        const formArticulo = button.closest('.form-articulo');
        formArticulo.remove();
        
        // Actualizar contador
        const totalForms = document.getElementById('id_form-TOTAL_FORMS');
        if (totalForms) {
            totalForms.value = parseInt(totalForms.value) - 1;
        }
    };
    
    // Auto-submit en filtros para mejor UX
    const filterSelects = document.querySelectorAll('#tipo, #comedor, #barrio, #estado');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Pequeño delay para mejor UX
            setTimeout(() => {
                this.form.submit();
            }, 300);
        });
    });
    
    // Búsqueda con debounce
    const busquedaInput = document.getElementById('busqueda');
    if (busquedaInput) {
        let timeout;
        busquedaInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    this.form.submit();
                }
            }, 500);
        });
    }
    
    // Confirmación para eliminar publicaciones
    const eliminarBtns = document.querySelectorAll('a[href*="eliminar"]');
    eliminarBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que querés eliminar esta publicación? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });
    
    // Mejorar UX de los filtros activos
    const clearFiltersBtn = document.querySelector('a[href*="listar_publicaciones"]');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            // Mostrar loading
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Limpiando...';
            this.style.pointerEvents = 'none';
            
            // Restaurar después de un momento
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.pointerEvents = 'auto';
            }, 1000);
        });
    }
    
    // Animaciones suaves para las cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Validación de campos requeridos en tiempo real
    const requiredInputs = document.querySelectorAll('input[required], textarea[required], select[required]');
    requiredInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.value.trim() !== '') {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });
    
    // Mejorar accesibilidad
    const paginationLinks = document.querySelectorAll('.pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Mostrar indicador de carga
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.style.pointerEvents = 'none';
            
            // Restaurar después de un momento
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.pointerEvents = 'auto';
            }, 1000);
        });
    });
});

// ===== FUNCIONES UTILITARIAS =====

// Función para mostrar notificaciones toast
function mostrarNotificacion(mensaje, tipo = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove después de 5 segundos
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

// Función para formatear fechas
function formatearFecha(fecha) {
    const opciones = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(fecha).toLocaleDateString('es-AR', opciones);
}

// Función para validar email
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Función para validar teléfono argentino
function validarTelefono(telefono) {
    const regex = /^(\+54|54)?[0-9]{10,11}$/;
    return regex.test(telefono.replace(/[\s\-\(\)]/g, ''));
}
