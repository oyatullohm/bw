
import os
from pathlib import Path
import environ
BASE_DIR = Path(__file__).resolve().parent.parent

from .local_db_ import LOCAL_DATABASE , LOGGING
env = environ.Env()
env.read_env()
DEBUG = env.bool('DEBUG')
SECRET_KEY = env.str('SECRET_KEY')
SECURE_BROWSER_XSS_FILTER = env.bool('SECURE_BROWSER_XSS_FILTER')
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF =env.bool('SECURE_CONTENT_TYPE_NOSNIFF')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT')
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE')
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE')
ALLOWED_HOSTS = env.str('ALLOWED_HOSTS', default='').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'main',
    'food',
    'app',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', )
}


# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'ROTATE_REFRESH_TOKENS': False,
#     'BLACKLIST_AFTER_ROTATION': True,
#     'AUTH_HEADER_TYPES': ('Bearer',),  # Token yuborishda 'Bearer' oldindan keladi
# }

    # 'rest_framework_simplejwt',
    # 'cachalot',

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # Redis server manzili
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 3600,
    }
}
# CACHALOT_TIMEOUT = 60  # 1 soat
# CACHALOT_ENABLED = True



# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
# }

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR / 'template')],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = LOCAL_DATABASE

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

TIME_ZONE ='Asia/Tashkent'
LANGUAGE_CODE = 'uz'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# MODELTRANSLATION_DEFAULT_LANGUAGE = 'uz'
# MODELTRANSLATION_FALLBACK_LANGUAGES = ('uz', 'ru')
# LANGUAGE_COOKIE_NAME = 'django_language'  
# SESSION_COOKIE_AGE = 1209600  # Sessiya muddati (bu yerda 2 hafta)
# LANGUAGE_COOKIE_AGE = 1209600  # Til cookie muddati (bu yerda 2 hafta)

gettext = lambda s:s
LANGUAGES = (
    ('uz',gettext("Uzbek")),
    ('uzb',gettext("Узбек")),
    ('en',gettext("English")),
    ('ru',gettext("Russian")),
)

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)
LOGIN_URL = '/login/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join('static')
STATICFILES_DIRS = (
     os.path.join(BASE_DIR / "staticfiles"),
)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'main.Teacher'
LOGGING = LOGGING
# LOGGING = {
#     'version':1,
#     'handlers':{
#          'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': 'debug.log'
#         },
#         'console':{'class':'logging.StreamHandler'}
#     },
#     'loggers':{
#         'django.db.backends':{
#             'handlers':['file'],
#             'level':'DEBUG'
#                     }
#                }
# }