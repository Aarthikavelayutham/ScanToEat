from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#@jr1e7-vs-*kqnqa^t&khep)nldh6jfg2!wb2%(@1du)i1%1h')

# Deployment-agnostic Security & Host Settings
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Allowed Hosts: Localhost + common cloud subdomains for zero-config deployment
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '.up.railway.app', '.onrender.com', '.herokuapp.com', '.vercel.app']
PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN') or os.environ.get('RENDER_EXTERNAL_HOSTNAME') or os.environ.get('PUBLIC_DOMAIN')
if PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(PUBLIC_DOMAIN)

# Site URL for QR codes: prioritizes environment, then detected domain, then localhost
SITE_URL = os.environ.get('SITE_URL')
if not SITE_URL:
    if PUBLIC_DOMAIN:
        SITE_URL = f'https://{PUBLIC_DOMAIN}'
    elif os.environ.get('RAILWAY_STATIC_URL'):
        SITE_URL = os.environ.get('RAILWAY_STATIC_URL')
    else:
        SITE_URL = 'http://localhost:8000'

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic', # Essential for cross-platform static serving
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx',
    'menu',
    'orders',
    'tables',
    'kitchen',
    'analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scantoeat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scantoeat.wsgi.application'

# Database: Detects DATABASE_URL on any platform
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# CSRF: Auto-detects and adds common origins
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
if PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{PUBLIC_DOMAIN}")
CSRF_TRUSTED_ORIGINS.extend(['https://*.railway.app', 'https://*.up.railway.app', 'https://*.onrender.com'])

# HTTPS/Proxy Settings: Universal for common cloud proxies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

# Redirects
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Universal Storage Config for all platforms
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'