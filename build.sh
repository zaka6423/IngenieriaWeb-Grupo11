# exit on error
set -o errexit

# install project dependencies
uv sync

# make sure django has all the things it needs to run
cd $(dirname $(find . | grep manage.py$))
uv run ./manage.py collectstatic --no-input
uv run ./manage.py migrate
export DJANGO_SUPERUSER_PASSWORD=admin123
uv run ./manage.py createsuperuser --username admin --email "zacariasapoca@gmail.com" --noinput || true
