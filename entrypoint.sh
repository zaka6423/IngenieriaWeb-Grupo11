#!/usr/bin/env bash
set -e

# Asegura que exista /data (lo montamos como volumen)
mkdir -p /data

# Aplica migraciones (idempotente)
python manage.py migrate --noinput

# Recolecta estáticos (si usás STATIC_ROOT)
# Si no usás estáticos locales, podés comentar esta línea
python manage.py collectstatic --noinput || true

# Arranca el servidor de desarrollo en 0.0.0.0:8000
python manage.py runserver 0.0.0.0:8000