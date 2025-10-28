"""
Django settings for config project.

Generado con compatibilidad para:
- Desarrollo local (SQLite, media local, email consola si no hay credenciales)
- Render.com (Whitenoise, ALLOWED_HOSTS dinámico, DB por DATABASE_URL)
- Cloudinary (opcional, no rompe si no está configurado)
- Envío de email real por SMTP si hay credenciales (sino consola)
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# --Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad / Core
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-w8%qh2%u=*u7@j-l&ibzl-7e=gwjs)8*qo0r4n)_*4w5yy(c59')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    "comedorescomunitarios.onrender.com",
    "localhost",
    "127.0.0.1",
    "[::1]"
]

# Application definition

# En el caso de que usemos cookies
# CSRF_TRUSTED_ORIGINS = [
#     "https://comedorescomunitarios.onrender.com",
# ]

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'core',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de mensajes
MESSAGE_TAGS = {
    10: 'debug',
    20: 'info',
    25: 'success',
    30: 'warning',
    40: 'error',
}

ROOT_URLCONF = 'config.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # <- acá apuntamos a /templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.email_verification_status',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- Base de datos
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# --- Base de datos ---
# En Docker, la base se guarda en /data/db.sqlite3 (volumen persistente)
# En desarrollo local, se guarda en db.sqlite3 en la raíz del proyecto
# Si existe DATABASE_URL (Render u otro servicio), se usa esa en lugar de SQLite.

DATABASES = {
    "default": dj_database_url.config(default="sqlite:///db.sqlite3")
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# --- I18N / TZ
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Static & Media (imagenes)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data/media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'                 # dónde redirige login_required
LOGIN_REDIRECT_URL = 'core:privada' # a dónde ir si no hay "next"
LOGOUT_REDIRECT_URL = 'core:home'

# Configuración de Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# --- Verificación de correo electrónico
# Tiempo que el código es válido (en minutos)
VERIFICATION_WINDOW_MINUTES = int(os.getenv("VERIFICATION_WINDOW_MINUTES", "15"))

# Máximo de intentos permitidos antes de regenerar código
VERIFICATION_MAX_TRIES = int(os.getenv("VERIFICATION_MAX_TRIES", "5"))

# Configuración de email
INSTALLED_APPS += ["anymail"]

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

ANYMAIL = {
    "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
}

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@example.com")

# --- Auth redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'core:privada'
LOGOUT_REDIRECT_URL = 'core:home'

# Cloudinary Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Configuración de almacenamiento
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    # Usar Cloudinary si las credenciales están disponibles
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage'
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'
        }
    }
    print("Using Cloudinary for image storage")
else:
    # Usar almacenamiento local si no hay credenciales de Cloudinary
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage'
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'
        }
    }
    print("Using local storage (create .env file with Cloudinary credentials)")

# code needed to deploy in Render.com:
if 'RENDER' in os.environ:
    # Validación de variables de entorno críticas
    RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    print("Using Render.com settings")
    DEBUG = False
    if not RENDER_HOSTNAME:
        print("RENDER_EXTERNAL_HOSTNAME no está definido. Usando 'comedorescomunitarios.onrender.com' como fallback.")
        ALLOWED_HOSTS = ["comedorescomunitarios.onrender.com"]
    else:
        ALLOWED_HOSTS = [RENDER_HOSTNAME]
    if not os.environ.get('DATABASE_URL'):
        print("DATABASE_URL no está definido. Usando SQLite por defecto.")
    else:
        DATABASES = {'default': dj_database_url.config(conn_max_age=600)}
    MIDDLEWARE.insert(MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,
                      'whitenoise.middleware.WhiteNoiseMiddleware')
    MEDIA_URL= "/media/"
    # Cloudinary obligatorio en producción
    if os.getenv('CLOUDINARY_CLOUD_NAME') and os.getenv('CLOUDINARY_API_KEY') and os.getenv('CLOUDINARY_API_SECRET'):
        STORAGES = {
            "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
            "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
        }
        print("Cloudinary activado para almacenamiento de imágenes")
    else:
        raise Exception("Cloudinary no configurado. Debes definir CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET en las variables de entorno.")
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    print(f"DATABASES: {DATABASES}")
    print(f"STORAGES: {STORAGES}")

# Configuración básica de logging para producción
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# settings.py
INSTALLED_APPS += [
    'haystack',
]

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': BASE_DIR / 'whoosh_index',
    },
}
