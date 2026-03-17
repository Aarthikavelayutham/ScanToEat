#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
mkdir -p staticfiles
mkdir -p staticfiles/admin
python manage.py collectstatic --no-input --clear
python manage.py migrate
python manage.py shell -c "
import os
from django.contrib.auth.models import User
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
print('Superuser ready')
"