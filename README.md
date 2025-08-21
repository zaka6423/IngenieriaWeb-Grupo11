# Comedores Comunitarios - Frontend

## 🍽️ Descripción

Plataforma web moderna para conectar comedores comunitarios en tu ciudad. El frontend está diseñado con colores cálidos (naranja) y una interfaz atractiva que facilita la conexión entre personas que necesitan ayuda y aquellos que quieren ayudar.

**Estado actual**: Frontend limpio y listo para integrar contenido dinámico desde Django.

## ✨ Características

### 🎨 Diseño Moderno
- **Colores cálidos**: Paleta de naranjas (#FF6B35, #FF8C42, #FFA726)
- **Responsive**: Diseño adaptativo para móviles, tablets y desktop
- **Animaciones suaves**: Efectos visuales atractivos y profesionales
- **Tipografía moderna**: Fuente Poppins para mejor legibilidad

### 🔧 Funcionalidades Implementadas
- **Sistema de autenticación**: Login y registro con validación
- **Dashboard personalizado**: Panel de control para usuarios autenticados
- **Formularios funcionales**: Con validación y estilos modernos
- **Navegación responsive**: Menú adaptativo

### 🛠️ Tecnologías Utilizadas
- **HTML5**: Estructura semántica y accesible
- **CSS3**: Estilos modernos con variables CSS y Flexbox/Grid
- **JavaScript ES6+**: Funcionalidades interactivas básicas
- **Bootstrap 5.3**: Framework CSS para diseño responsive
- **Font Awesome 6.4**: Iconografía profesional
- **Django Templates**: Integración con backend Django

## 📁 Estructura del Proyecto

```
templates/
├── core/
│   ├── base.html          # Template base con navegación y estilos
│   ├── home.html          # Página principal (limpia, lista para contenido dinámico)
│   ├── privada.html       # Dashboard para usuarios autenticados (limpio)
│   └── static/
│       ├── css/
│       │   └── custom.css # Estilos personalizados
│       └── js/
│           └── custom.js  # Funcionalidades JavaScript básicas
└── registration/
    ├── login.html         # Formulario de inicio de sesión (limpio)
    └── registro.html      # Formulario de registro con email (limpio)
```

## 🚀 Instalación y Uso

### Prerrequisitos
- Python 3.8+
- Django 4.0+
- Navegador web moderno

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd IngenieriaWeb-Grupo11
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la base de datos**
   ```bash
   python manage.py migrate
   ```

4. **Crear superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Ejecutar el servidor**
   ```bash
   python manage.py runserver
   ```

6. **Abrir en el navegador**
   ```
   http://localhost:8000
   ```

## 🎯 Páginas Principales

### 🏠 Página de Inicio (`home.html`)
- **Hero Section**: Mensaje principal con llamada a la acción
- **Estadísticas**: Estructura lista para datos dinámicos (actualmente en 0)
- **Características**: Explicación de cómo funciona la plataforma
- **Testimonios**: Sección vacía lista para contenido dinámico
- **Call to Action**: Sección para motivar el registro

### 👤 Dashboard (`privada.html`)
- **Bienvenida personalizada**: Saludo al usuario
- **Estadísticas personales**: Estructura lista para datos dinámicos
- **Comedores cercanos**: Sección vacía lista para contenido dinámico
- **Acciones rápidas**: Botones funcionales
- **Actividad reciente**: Sección vacía lista para contenido dinámico
- **Próximos eventos**: Sección vacía lista para contenido dinámico

### 🔐 Autenticación
- **Login**: Formulario funcional con validación
- **Registro**: Formulario completo con campo de email

## 🎨 Paleta de Colores

```css
:root {
    --primary-orange: #FF6B35;    /* Naranja principal */
    --secondary-orange: #FF8C42;  /* Naranja secundario */
    --warm-orange: #FFA726;       /* Naranja cálido */
    --light-orange: #FFE0B2;      /* Naranja claro */
    --dark-orange: #E65100;       /* Naranja oscuro */
    --text-dark: #2C3E50;         /* Texto oscuro */
    --text-light: #7F8C8D;        /* Texto claro */
    --white: #FFFFFF;             /* Blanco */
    --light-gray: #F8F9FA;        /* Gris claro */
}
```

## 🔧 Funcionalidades JavaScript

### Animaciones
- **Contadores animados**: Estructura lista para datos dinámicos
- **Efectos de aparición**: Elementos que aparecen al hacer scroll
- **Hover effects**: Efectos al pasar el mouse
- **Ripple effect**: Efecto de ondulación en botones

### Interactividad
- **Validación de formularios**: Validación en tiempo real
- **Sistema de favoritos**: Estructura lista para implementar
- **Notificaciones**: Sistema de alertas toast
- **Tooltips**: Sistema de tooltips personalizados

## 📱 Responsive Design

El frontend está optimizado para:
- **Móviles**: 320px - 768px
- **Tablets**: 768px - 1024px
- **Desktop**: 1024px+

### Breakpoints principales
```css
@media (max-width: 768px) {
    /* Estilos para móviles */
}

@media (max-width: 1024px) {
    /* Estilos para tablets */
}
```

## ♿ Accesibilidad

- **Navegación por teclado**: Todos los elementos son accesibles
- **Contraste adecuado**: Cumple con estándares WCAG
- **Textos alternativos**: Imágenes con alt text
- **Reducción de movimiento**: Respeta preferencias del usuario
- **Semántica HTML**: Uso correcto de etiquetas

## 🚀 Próximos Pasos

### Para Desarrolladores
1. **Crear modelos Django** para comedores, usuarios, eventos, etc.
2. **Implementar vistas** para mostrar contenido dinámico
3. **Agregar funcionalidades** como búsqueda, filtros, etc.
4. **Integrar APIs** para geolocalización y mapas
5. **Implementar sistema de notificaciones** en tiempo real

### Áreas Listas para Contenido Dinámico
- ✅ Estructura de estadísticas (actualmente en 0)
- ✅ Sección de comedores cercanos (vacía)
- ✅ Sección de testimonios (vacía)
- ✅ Sección de eventos (vacía)
- ✅ Sección de actividad reciente (vacía)
- ✅ Sistema de favoritos (estructura lista)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Equipo

**Grupo 11** - Ingeniería Web
- Desarrolladores frontend
- Diseñadores UX/UI
- Contribuidores

## 📞 Contacto

Para preguntas o soporte:
- Email: [tu-email@ejemplo.com]
- GitHub: [@tu-usuario]

---

**¡Frontend limpio y listo para desarrollo!** 🚀✨