// ===== EFECTOS VISUALES AVANZADOS =====

// Función para aplicar gradientes dinámicos según la hora
function applyDynamicGradients() {
    const hour = new Date().getHours();
    const elements = document.querySelectorAll('.dynamic-gradient');
    
    elements.forEach(element => {
        // Remover clases anteriores
        element.classList.remove('morning', 'afternoon', 'evening', 'night');
        
        // Aplicar clase según la hora
        if (hour >= 6 && hour < 12) {
            element.classList.add('morning');
        } else if (hour >= 12 && hour < 17) {
            element.classList.add('afternoon');
        } else if (hour >= 17 && hour < 21) {
            element.classList.add('evening');
        } else {
            element.classList.add('night');
        }
    });
}

// Función para inicializar efectos de entrada
function initEntryEffects() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = Math.random() * 0.5 + 's';
                entry.target.classList.add('fade-in-up');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Observar elementos con clases de animación
    document.querySelectorAll('.slide-in-left, .slide-in-right, .slide-in-up').forEach(el => {
        observer.observe(el);
    });
}

// Función para crear efecto parallax en scroll
function initParallaxEffect() {
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax-bg');
        
        parallaxElements.forEach(element => {
            const speed = 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
}

// Función para efectos de partículas
function initParticleEffect() {
    const particleContainers = document.querySelectorAll('.particle-effect');
    
    particleContainers.forEach(container => {
        // Crear partículas adicionales
        for (let i = 0; i < 5; i++) {
            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.style.cssText = `
                position: absolute;
                width: 4px;
                height: 4px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: float ${3 + Math.random() * 4}s ease-in-out infinite;
                animation-delay: ${Math.random() * 2}s;
            `;
            container.appendChild(particle);
        }
    });
}

// Función para efectos de hover avanzados
function initAdvancedHoverEffects() {
    // Efecto de tilt en cards
    document.querySelectorAll('.hover-tilt').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
        });
    });
}

// Función para efectos de glow pulsante
function initPulseGlow() {
    const glowElements = document.querySelectorAll('.pulse-glow');
    
    glowElements.forEach(element => {
        setInterval(() => {
            element.style.boxShadow = `0 0 ${20 + Math.random() * 20}px rgba(255, 107, 53, ${0.4 + Math.random() * 0.4})`;
        }, 2000);
    });
}

// Función para crear efecto de ondas
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
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
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Función para inicializar efectos de ripple
function initRippleEffects() {
    document.querySelectorAll('.btn-primary-custom, .btn-secondary-custom').forEach(button => {
        button.addEventListener('click', (e) => {
            createRippleEffect(button, e);
        });
    });
}

// Función para efectos de typing
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Función para inicializar efectos de typing
function initTypeWriterEffects() {
    const typeElements = document.querySelectorAll('[data-typewriter]');
    
    typeElements.forEach(element => {
        const text = element.getAttribute('data-typewriter');
        const speed = parseInt(element.getAttribute('data-speed')) || 100;
        
        setTimeout(() => {
            typeWriter(element, text, speed);
        }, 1000);
    });
}

// Función para efectos de contador animado
function animateCounter(element, target, duration = 2000) {
    console.log('Animando contador:', element, 'Target:', target);
    
    if (!target || target === 0) {
        element.textContent = '0';
        return;
    }
    
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        element.textContent = Math.floor(current);
        
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        }
    }, 16);
}

// Función para inicializar contadores animados
function initAnimatedCounters() {
    console.log('Inicializando contadores animados...');
    const counters = document.querySelectorAll('[data-counter]');
    console.log('Contadores encontrados:', counters.length);
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-counter'));
        console.log('Contador:', counter, 'Target:', target);
        
        if (target && target > 0) {
            // Animar inmediatamente para debug
            setTimeout(() => {
                animateCounter(counter, target);
            }, 1000);
        }
    });
}

// Función principal de inicialización
function initVisualEffects() {
    // Aplicar gradientes dinámicos
    applyDynamicGradients();
    
    // Inicializar efectos de entrada
    initEntryEffects();
    
    // Inicializar efecto parallax
    initParallaxEffect();
    
    // Inicializar efectos de partículas
    initParticleEffect();
    
    // Inicializar efectos de hover avanzados
    initAdvancedHoverEffects();
    
    // Inicializar efectos de glow pulsante
    initPulseGlow();
    
    // Inicializar efectos de ripple
    initRippleEffects();
    
    // Inicializar efectos de typing
    initTypeWriterEffects();
    
    // Inicializar contadores animados
    initAnimatedCounters();
    
    console.log('🎨 Efectos visuales avanzados inicializados');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initVisualEffects);

// Actualizar gradientes cada hora
setInterval(applyDynamicGradients, 3600000); // 1 hora
