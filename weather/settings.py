"""
Django settings for weather project.
"""

from pathlib import Path

from weather.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = settings.secret_key
DEBUG = settings.debug
ALLOWED_HOSTS = settings.allowed_hosts_list

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main.apps.MainConfig",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "django_celery_beat",
    "django_celery_results",
    "django_filters",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "weather.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "mainapp/build"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "weather.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": settings.db_engine,
        "NAME": settings.db_name,
        "USER": settings.db_user,
        "PASSWORD": settings.db_password,
        "HOST": settings.db_host,
        "PORT": settings.db_port,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
_build_dir = BASE_DIR / "mainapp/build"
STATICFILES_DIRS = (_build_dir,) if _build_dir.exists() else ()

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_TIMEZONE = "Europe/Moscow"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = settings.celery_broker_url
CELERY_RESULT_BACKEND = settings.celery_broker_url

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Weather API",
    "DESCRIPTION": "Historical weather data from rp5.ru weather stations",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

WEATHER_PARSER = {
    "DELETE_CSV_FILES": False,
    "MIN_DELAY_BETWEEN_REQUESTS": 1,
    "MAX_DELAY_BETWEEN_REQUESTS": 3,
    "COUNT_REQUESTS_FOR_ONE_SESSION": 100,
    "CSV_DELIMITER": settings.csv_delimiter,
    "STATIC_DATA_PATH": settings.static_data_path,
}

CSV_DELIMITER = settings.csv_delimiter
STATIC_DATA_PATH = BASE_DIR / settings.static_data_path

WHITENOISE_USE_FINDERS = DEBUG
