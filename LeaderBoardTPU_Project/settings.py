from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные из .env
load_dotenv(BASE_DIR / '.env')

# ============================================================
# БЕЗОПАСНОСТЬ
# ============================================================
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')


# ============================================================
# ПРИЛОЖЕНИЯ
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'LeaderBoard.apps.LeaderboardConfig',
    
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',
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

ROOT_URLCONF = 'LeaderBoardTPU_Project.urls'

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

WSGI_APPLICATION = 'LeaderBoardTPU_Project.wsgi.application'


# ============================================================
# БАЗА ДАННЫХ
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'


# ============================================================
# CORS
# ============================================================
CORS_ORIGIN_ALLOW_ALL = os.getenv('CORS_ORIGIN_ALLOW_ALL', 'False') == 'True'


# ============================================================
# DRF
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # Добавляем пагинацию
    'DEFAULT_PAGINATION_CLASS': 'LeaderBoard.common.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 50,
    # Добавляем обработчик ошибок
    'EXCEPTION_HANDLER': 'LeaderBoard.common.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'LeaderBoard TPU API',
    'DESCRIPTION': 'API системы рейтинга студентов ИШИТР ТПУ',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'auth', 'description': 'Аутентификация и профиль пользователя'},
        {'name': 'students', 'description': 'Студенты'},
        {'name': 'projects', 'description': 'Проекты'},
        {'name': 'teams', 'description': 'Команды'},
        {'name': 'leaderboard', 'description': 'Рейтинги'},
        {'name': 'activity', 'description': 'Активность'},
    ],
}


# ============================================================
# JWT
# ============================================================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}


# ============================================================
# CELERY
# ============================================================
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Europe/Moscow')
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ============================================================
# ИНТЕГРАЦИИ С ВНЕШНИМИ API
# ============================================================

# API ТПУ
TPU_API_BASE_URL = os.getenv('TPU_API_BASE_URL', 'https://tpu.community.design/dev/api')
TPU_CLIENT_ID = os.getenv('TPU_CLIENT_ID', '')
TPU_CLIENT_SECRET = os.getenv('TPU_CLIENT_SECRET', '')
TPU_API_MOCK_MODE = os.getenv('TPU_API_MOCK_MODE', 'False') == 'True'
TPU_API_MOCK_PATH = Path(BASE_DIR) / 'mocks' / 'tpu'

# API Витрины
VITRINA_API_BASE_URL = os.getenv('VITRINA_API_BASE_URL', 'https://tpu.community.design/dev/api')
VITRINA_CLIENT_ID = os.getenv('VITRINA_CLIENT_ID', '')
VITRINA_CLIENT_SECRET = os.getenv('VITRINA_CLIENT_SECRET', '')
VITRINA_API_MOCK_MODE = os.getenv('VITRINA_API_MOCK_MODE', 'False') == 'True'
VITRINA_API_MOCK_PATH = Path(BASE_DIR) / 'mocks' / 'vitrina'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# REDIS CACHE (для маппинга tpu_user_id → login)
# ============================================================================

# Хост Redis: 'redis' в Docker, 'localhost' локально
REDIS_CACHE_HOST = os.getenv('REDIS_CACHE_HOST', 'redis')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{REDIS_CACHE_HOST}:6379/1',  # БД 1 (БД 0 у Celery)
        'TIMEOUT': 60 * 60 * 24,  # TTL по умолчанию: 24 часа
    }
}

# Настройки кеша маппинга tpu_user_id → login
TPU_USER_CACHE_TTL = int(os.getenv('TPU_USER_CACHE_TTL', 60 * 60 * 24))  # 24 часа
TPU_USER_CACHE_PREFIX = 'tpu_user_to_login'
