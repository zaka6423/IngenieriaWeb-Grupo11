# exit on error
#!/bin/bash
set -o errexit

gunicorn config.wsgi:application