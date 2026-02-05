"""
Django settings for EduTutor project.

This is a reusable Django project template with configurable authentication features.
"""

import os
from datetime import timedelta
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    # Set casting and default values
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    AUTH_METHOD=(str, 'JWT'),
    ENABLE_PASSWORD_RESET=(bool, True),
    ENABLE_PROFILE_EDIT=(bool, True),
    OTP_EXPIRY_MINUTES=(int, 10),
    OTP_LENGTH=(int, 4),
    JWT_ACCESS_TOKEN_LIFETIME=(int, 60),
    JWT_REFRESH_TOKEN_LIFETIME=(int, 7),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:3000', 'http://127.0.0.1:3000']),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
    LANGUAGE_CODE=(str, 'en-us'),
    TIME_ZONE=(str, 'UTC'),
    DJANGO_LOG_LEVEL=(str, 'INFO'),
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


# =============================================================================
# AUTHENTICATION FEATURES CONFIGURATION
# =============================================================================

AUTH_FEATURES = {
    # Authentication method: "JWT" or "SESSION"
    "AUTH_METHOD": env.str('AUTH_METHOD'),
    
    # Enable/disable password reset functionality
    "ENABLE_PASSWORD_RESET": env.bool('ENABLE_PASSWORD_RESET'),
    
    # Enable/disable profile editing functionality
    "ENABLE_PROFILE_EDIT": env.bool('ENABLE_PROFILE_EDIT'),
    
    # OTP expiry time in minutes
    "OTP_EXPIRY_MINUTES": env.int('OTP_EXPIRY_MINUTES'),
    
    # OTP length
    "OTP_LENGTH": 4,
}

AUTH_USER_MODEL='core_auth.User'

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    
    # Local apps
    'core_auth',
    'Profile',
    'utilities',
    'academics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'EduTutor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'EduTutor.wsgi.application'


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Default: SQLite for development
# For production, use PostgreSQL via environment variables

DATABASES = {
    'default': {
        'ENGINE': env.str('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': env.str('DATABASE_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': env.str('DATABASE_USER', default=''),
        'PASSWORD': env.str('DATABASE_PASSWORD', default=''),
        'HOST': env.str('DATABASE_HOST', default=''),
        'PORT': env.str('DATABASE_PORT', default=''),
    }
}


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =============================================================================
# CUSTOM USER MODEL
# =============================================================================

AUTH_USER_MODEL = 'core_auth.User'


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = env.str('LANGUAGE_CODE')

TIME_ZONE = env.str('TIME_ZONE')

USE_I18N = True

USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'core_auth.exceptions.custom_exception_handler',
}

# Configure authentication based on AUTH_FEATURES
if AUTH_FEATURES.get('AUTH_METHOD') == 'JWT':
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
else:
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
        'rest_framework.authentication.SessionAuthentication',
    ]


# =============================================================================
# DRF SPECTACULAR CONFIGURATION
# =============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'EduTutor API',
    'DESCRIPTION': """Complete API documentation for EduTutor authentication system.
    
## Features
- User Registration and Authentication
- JWT Token Management
- Profile Management
- Email Verification
- OTP-based verification

## Authentication
Most endpoints require authentication. Use the `/api/auth/login/` endpoint to obtain JWT tokens.
Then include the access token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```
    """,
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api',
    'CONTACT': {
        'email': 'contact@edututor.local'
    },
    'LICENSE': {
        'name': 'MIT License'
    },
    # Automatic tag discovery and organization
    'TAGS': None,  # Set to None to auto-discover tags from views
    'SORT_OPERATIONS': True,  # Sort operations alphabetically
    'SORT_OPERATION_PARAMETERS': True,  # Sort parameters alphabetically
    'ENUM_NAME_OVERRIDES': {},
    'PREPROCESSING_HOOKS': [],
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
    ],
    # Group operations by tags automatically
    'SCHEMA_COERCE_METHOD_NAMES': {},
    'CAMELIZE_NAMES': False,
    'SERVERS': [],
    # Show all endpoints in Swagger UI
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,  # Enable search filter
        'tagsSorter': 'alpha',  # Sort tags alphabetically
        'operationsSorter': 'alpha',  # Sort operations alphabetically
        'docExpansion': 'list',  # Expand/collapse operations
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
    },
}


# =============================================================================
# SIMPLE JWT CONFIGURATION
# =============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME')),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_TOKEN_LIFETIME')),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# =============================================================================
# CORS CONFIGURATION
# =============================================================================

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

CORS_ALLOW_CREDENTIALS = True


# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

EMAIL_BACKEND = env.str(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)

EMAIL_HOST = env.str('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='noreply@example.com')


# =============================================================================
# CELERY CONFIGURATION
# =============================================================================

# Celery settings
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Celery task settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Celery beat schedule (for periodic tasks)
CELERY_BEAT_SCHEDULE = {
    # Add periodic tasks here if needed
    # Example:
    # 'clean-up-old-otps': {
    #     'task': 'core_auth.tasks.cleanup_expired_otps',
    #     'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    # },
}


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env.str('DJANGO_LOG_LEVEL'),
            'propagate': False,
        },
        'core_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Ensure logs directory exists
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(BASE_DIR / 'static', exist_ok=True)
os.makedirs(BASE_DIR / 'media', exist_ok=True)
