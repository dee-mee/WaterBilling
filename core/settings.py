from pathlib import Path
import os
import dj_database_url
import dropbox

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY', default='django-insecure-u@d=el-b)c#y)02ne71+k&^8m0xu%y(77(7=#p2+3gn3m##bl^')


DEBUG = 'RENDER' not in os.environ

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'https://*.onrender.com']

CORS_ALLOWED_ORIGINS = ['http://localhost:8000', 'https://*.onrender.com']

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'waterbilling-r92q.onrender.com', '.onrender.com']


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
    'sweetify',
    'corsheaders',
    'bootstrap_modal_forms',
]

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

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

if DATABASE_URL:
    # Use DATABASE_URL if provided (e.g. production on Render/Neon)
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
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
OTP_EMAIL = "youremail@gmail.com"
OTP_PASSWORD = "yourpassword"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
