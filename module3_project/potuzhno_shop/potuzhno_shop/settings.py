"""
Django settings for potuzhno_shop project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Змінні оточення: читаємо .env з кореня репозиторію (потрібен для локального
# запуску; у Docker ті самі змінні передає docker-compose).
env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")


# SECURITY WARNING: keep the secret key used in production secret!
# Без DJANGO_SECRET_KEY у .env Django не запуститься — це навмисно.
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# За замовчуванням False — щоб випадково не поїхати в прод з DEBUG=True.
DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# Потрібно лише коли сайт відкривається по HTTPS через reverse-proxy,
# напр. DJANGO_CSRF_TRUSTED_ORIGINS=https://shop.example.com
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# nginx передає X-Forwarded-Proto — так Django знає, що запит прийшов по HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # feature-apps проєкту: кожен = моделі + DRF (serializers, views)
    "apps.catalog.apps.CatalogConfig",
    "apps.reviews.apps.ReviewsConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.contact.apps.ContactConfig",
    # спільне для API: маршрути /api/v1/, permissions, pagination, GraphQL
    "apps.api.apps.ApiConfig",

    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",

    "corsheaders",

    "drf_spectacular",
    "graphene_django",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Vite dev-сервер React живе на іншому origin, тому потрібен CORS.
# У Docker nginx віддає фронтенд і API з одного origin — CORS там не задіяний.
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

ROOT_URLCONF = 'potuzhno_shop.urls'

# Власних HTML-шаблонів більше немає (фронтенд — React), але шаблони потрібні
# адмінці, Browsable API та Swagger — вони беруться з пакетів через APP_DIRS.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'potuzhno_shop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env.int("POSTGRES_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

# Куди `collectstatic` складає статику адмінки/DRF; у Docker цю папку віддає nginx.
STATIC_ROOT = BASE_DIR / "staticfiles"

APPEND_SLASH = True


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [  # OR
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [  # AND
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/hour',
        'user': '600/hour',
        'login': '5/min',
        'register': '10/hour',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "AUTH_HEADER_TYPES": ("Bearer",),  # Authorization: Bearer <token>
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "security": {"handlers": ["console"], "level": "INFO"},
        "contact": {"handlers": ["console"], "level": "INFO"},
    },
}


SPECTACULAR_SETTINGS = {
    "TITLE": "ПОТУЖНО Shop API",
    "DESCRIPTION": "API інтернет-магазину одягу та взуття",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

GRAPHENE = {
    "SCHEMA": "apps.api.schema.schema",
    "MIDDLEWARE": ["graphene_django.debug.DjangoDebugMiddleware"],
}
