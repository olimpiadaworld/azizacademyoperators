import os
from pathlib import Path
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

NODE_ENV = os.getenv('NODE_ENV', 'development').lower()
DEBUG = os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes') if os.getenv('DEBUG') is not None else NODE_ENV != 'production'
SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('DJANGO_SECRET_KEY') or ('dev-only-change-me' if DEBUG else '')


def csv_list(name, default=''):
    return [x.strip().rstrip('/') for x in os.getenv(name, default).split(',') if x.strip()]


if DEBUG:
    ALLOWED_HOSTS = csv_list('ALLOWED_HOSTS', '127.0.0.1,localhost,*')
else:
    ALLOWED_HOSTS = csv_list('ALLOWED_HOSTS', '.up.railway.app')
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
    if railway_domain and railway_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_domain)

CORS_ALLOWED_ORIGINS = csv_list('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173' if DEBUG else '')
CSRF_TRUSTED_ORIGINS = csv_list('CSRF_TRUSTED_ORIGINS') or [x for x in CORS_ALLOWED_ORIGINS if x.startswith('https://') or x.startswith('http://')]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'core.middleware.RequestIdMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.SimpleCorsMiddleware',
    'core.middleware.SimpleRateLimitMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]},
    }
]
WSGI_APPLICATION = 'config.wsgi.application'


def database_from_url(url):
    parsed = urlparse(url)
    engine = 'django.db.backends.postgresql' if parsed.scheme.startswith('postgres') else 'django.db.backends.sqlite3'
    if engine == 'django.db.backends.sqlite3':
        return {'ENGINE': engine, 'NAME': BASE_DIR / 'db.sqlite3'}
    return {
        'ENGINE': engine,
        'NAME': unquote(parsed.path.lstrip('/')),
        'USER': unquote(parsed.username or ''),
        'PASSWORD': unquote(parsed.password or ''),
        'HOST': parsed.hostname or '',
        'PORT': str(parsed.port or 5432),
        'OPTIONS': {'sslmode': 'require'} if os.getenv('DB_SSL_REQUIRE', '').lower() == 'true' else {},
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '60')),
    }

DATABASE_URL = os.getenv('DATABASE_URL', '')
DATABASES = {
    'default': database_from_url(DATABASE_URL) if DATABASE_URL else {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'uz'
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Tashkent')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MIGRATION_MODULES = {'core': None}

DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('MAX_UPLOAD_MB', '10')) * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('MAX_UPLOAD_MB', '10')) * 1024 * 1024

SESSION_COOKIE_SECURE = NODE_ENV == 'production'
CSRF_COOKIE_SECURE = NODE_ENV == 'production'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'false').lower() in ('1', 'true', 'yes')
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = False

JWT_ACCESS_SECRET = os.getenv('JWT_ACCESS_SECRET', 'dev-access-secret')
JWT_REFRESH_SECRET = os.getenv('JWT_REFRESH_SECRET', 'dev-refresh-secret')
ACCESS_TOKEN_EXPIRES_IN = os.getenv('ACCESS_TOKEN_EXPIRES_IN', '30m')
REFRESH_TOKEN_EXPIRES_IN = os.getenv('REFRESH_TOKEN_EXPIRES_IN', '7d')

API_RATE_LIMIT_PER_MINUTE = int(os.getenv('API_RATE_LIMIT_PER_MINUTE', '240'))
AUTH_RATE_LIMIT_PER_15_MINUTES = int(os.getenv('AUTH_RATE_LIMIT_PER_15_MINUTES', '20'))
PUBLIC_LEAD_RATE_LIMIT_PER_MINUTE = int(os.getenv('PUBLIC_LEAD_RATE_LIMIT_PER_MINUTE', '8'))

if NODE_ENV == 'production':
    weak_values = {'', 'dev-only-change-me', 'change-this-local-django-secret', 'dev-access-secret', 'dev-refresh-secret'}
    if SECRET_KEY in weak_values or len(SECRET_KEY) < 40:
        raise RuntimeError('Production uchun SECRET_KEY 40+ belgili random qiymat bo‘lishi shart.')
    if JWT_ACCESS_SECRET in weak_values or len(JWT_ACCESS_SECRET) < 64:
        raise RuntimeError('Production uchun JWT_ACCESS_SECRET 64+ belgili random qiymat bo‘lishi shart.')
    if JWT_REFRESH_SECRET in weak_values or len(JWT_REFRESH_SECRET) < 64 or JWT_REFRESH_SECRET == JWT_ACCESS_SECRET:
        raise RuntimeError('Production uchun JWT_REFRESH_SECRET alohida va 64+ belgili random qiymat bo‘lishi shart.')
    if not CORS_ALLOWED_ORIGINS:
        raise RuntimeError('Production uchun CORS_ALLOWED_ORIGINS ichiga Netlify domenini yozing.')
    if not DATABASE_URL or not DATABASE_URL.startswith(('postgres://', 'postgresql://')):
        raise RuntimeError('Production uchun Railway PostgreSQL DATABASE_URL kerak.')
