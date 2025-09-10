# 🚀 Configuración de Cloudinary para Comedores Comunitarios

## 📋 Requisitos Previos

1. **Cuenta de Cloudinary** (gratuita en [cloudinary.com](https://cloudinary.com))
2. **Credenciales de API** de tu cuenta de Cloudinary

## 🔑 Configuración de Variables de Entorno

### **PASO 1: Crear archivo .env**

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=tu_cloud_name_aqui
CLOUDINARY_API_KEY=tu_api_key_aqui
CLOUDINARY_API_SECRET=tu_api_secret_aqui

# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-w8%qh2%u=*u7@j-l&ibzl-7e=gwjs)8*qo0r4n)_*4w5yy(c59

# Database (local development)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@comedorescomunitarios.com
```

### **PASO 2: Obtener credenciales de Cloudinary**

1. Ve a [cloudinary.com](https://cloudinary.com) y crea una cuenta
2. En tu dashboard, ve a **Settings** → **Access Keys**
3. Copia:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

### **PASO 3: Reemplazar en .env**

```bash
CLOUDINARY_CLOUD_NAME=mi_cloud_name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

## ✅ Verificación

### **1. Verificar que Django funcione:**
```bash
python manage.py check
```

### **2. Verificar que el servidor funcione:**
```bash
python manage.py runserver
```

### **3. Mensajes esperados:**
- ✅ **"Usando Cloudinary para almacenamiento de imágenes"** = Configuración correcta
- ⚠️ **"Usando almacenamiento local"** = Falta archivo .env o credenciales

## 🌐 Configuración en Render.com

### **Variables de entorno en Render:**
```
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
RENDER_EXTERNAL_HOSTNAME=tu_dominio.onrender.com
```

## 🔧 Solución de Problemas

### **Error: "Cannot use ImageField because Pillow is not installed"**
```bash
pip install Pillow
```

### **Error: "No module named 'cloudinary_storage'"**
```bash
pip install django-cloudinary-storage
```

### **Error: "No module named 'python-dotenv'"**
```bash
pip install python-dotenv
```

## 📱 Funcionalidades

### **Con Cloudinary configurado:**
- ✅ **Imágenes se suben a la nube**
- ✅ **Accesibles desde cualquier lugar**
- ✅ **Optimización automática**
- ✅ **CDN global**

### **Sin Cloudinary (fallback):**
- ✅ **Imágenes se guardan localmente**
- ✅ **Funciona para desarrollo**
- ⚠️ **Solo accesible desde tu PC**

## 🚀 Deploy

1. **Subir código al repo** (sin .env)
2. **Configurar variables en Render**
3. **Deploy automático**
4. **Imágenes funcionarán en Cloudinary**

---

**¿Necesitas ayuda?** Revisa que:
- El archivo `.env` esté en la raíz del proyecto
- Las credenciales de Cloudinary sean correctas
- Todas las dependencias estén instaladas
