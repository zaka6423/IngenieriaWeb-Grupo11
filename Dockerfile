# ---- Build/runtime base ----
FROM python:3.12-slim

# Evita archivos .pyc y hace logging sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema mínimas (agregá otras si tu proyecto las requiere)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements primero para aprovechar la cache de Docker
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el proyecto
COPY . /app

# Creamos el directorio de datos (se montará como volumen desde el host)
RUN mkdir -p /data
VOLUME ["/data"]

# Exponemos el puerto de la app
EXPOSE 8000

# Entrypoint: migra, collectstatic y arranca el server
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Usuario no-root (opcional)
# RUN useradd -ms /bin/bash app && chown -R app:app /app /data
# USER app

# Comando por defecto
CMD ["/entrypoint.sh"]