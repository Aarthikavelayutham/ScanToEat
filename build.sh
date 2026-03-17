#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
mkdir -p staticfiles
mkdir -p staticfiles/admin
python manage.py collectstatic --no-input --clear
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print('Superuser ready')
"