from pathlib import Path
import os
import dj_database_url
import dropbox
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")


DEBUG = os.environ.get('DEBUG', 'False') == 'True'

CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS]

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:8000').split(',')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS]

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]


AUTH_USER_MODEL = 'account.Account'

SWEETIFY_SWEETALERT_LIBRARY = 'sweetalert2'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'account',
    'payments',
    'sweetify',
    'corsheaders',
    'bootstrap_modal_forms',
]

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', '')
MPESA_ENV = os.environ.get('MPESA_ENV', 'sandbox')
MPESA_CALLBACK_BASE_URL = os.environ.get('MPESA_CALLBACK_BASE_URL', '').rstrip('/')
MPESA_CALLBACK_SECRET = os.environ.get('MPESA_CALLBACK_SECRET', '')
MPESA_ALLOWED_IPS = [
    ip.strip()
    for ip in os.environ.get('MPESA_ALLOWED_IPS', '').split(',')
    if ip.strip()
]

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False') == 'True'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'



DATABASE_URL = os.environ.get('DATABASE_URL')
DB_NAME = os.environ.get('DB_NAME')

if DATABASE_URL:
    # Use DATABASE_URL if provided (e.g. production on Render/Neon)
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
elif DB_NAME:
    # Fallback to discrete PostgreSQL environment variables (common in cPanel deployments)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    # Safe default for local development: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }





AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    "main/static",
    os.path.join(BASE_DIR, 'images'),
]

CREATE_SUPERUSER = os.environ.get("CREATE_SUPERUSER") == "1"


OTP = False
OTP_EMAIL = os.environ.get('OTP_EMAIL', 'youremail@gmail.com')
OTP_PASSWORD = os.environ.get('OTP_PASSWORD', 'yourpassword')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ SECURITY SETTINGS ============
# SSL/HTTPS Configuration
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),  # unsafe-inline for Django admin
    'style-src': ("'self'", "'unsafe-inline'"),
    'img-src': ("'self'", "data:", "https:"),
}

# HSTS (HTTP Strict Transport Security)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_HSTS_SECONDS = 0

# Session and CSRF Configuration
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Login Redirect
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
