#!/usr/bin/env bash
# Generic build script for any platform
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Prep static files
mkdir -p staticfiles
python manage.py collectstatic --no-input --clear

# Database migrations
python manage.py migrate

# Import your 100+ dishes automatically
echo "==> Restoring your 100+ dishes..."
python manage.py loaddata menu_data.json
python manage.py loaddata tables_data.json

# Regenerate any broken or missing QR codes automatically
echo "==> Regenerating table QR codes..."
python manage.py regenerate_qrs

# Master User Setup (detected from environment or defaults)
python manage.py shell -c "
import os
from django.contrib.auth.models import User
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'==> Superuser [{username}] created!')
else:
    print(f'==> User [{username}] already exists.')
"