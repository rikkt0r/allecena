# coding: utf-8
import os
import djcelery
from kombu import Queue, Exchange

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '7pwhm1844^d27suz-#6s-_vt6lp%q1*v!)ndzz*i(4&9-0u*q)'
DEBUG = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
# STATIC_ROOT = os.path.join(BASE_DIR, "static")
ALLOWED_HOSTS = ['allecena.com', 'localhost', '185.5.99.214', '127.0.0.1']
CONN_MAX_AGE = 0  # sqlite..

VERSION = 2.3

DJANGO_LIVE_TEST_SERVER_ADDRESS = 'localhost:8000'

djcelery.setup_loader()
BROKER_URL = "amqp://allecena:allecenaPassword@localhost:5672/allecena"
CELERY_RESULT_BACKEND = 'cache+memcached://127.0.0.1:11211/'
CELERYD_HIJACK_ROOT_LOGGER=False
# djcelery.backends.cache:CacheBackend // djcelery.backends.database:DatabaseBackend
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Warsaw'
CELERY_TASK_RESULT_EXPIRES = 3600
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# For testing
# CELERY_ALWAYS_EAGER = True


CELERY_CREATE_MISSING_QUEUES = True
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('allecena.email', Exchange('allecena.email'), routing_key='email'),
    Queue('allecena.analysis', Exchange('allecena.analysis'), routing_key='analysis'),
    Queue('allecena.triggers', Exchange('allecena.triggers'), routing_key='triggers'),
)
CELERY_ROUTES = {
    'ac_common.tasks.MailTask': {'queue': 'allecena.email', 'routing_key': 'email'},
    'ac_engine.tasks.ComputingTask': {'queue': 'allecena.analysis', 'routing_key': 'analysis'},
    'ac_engine.tasks.TriggerTask': {'queue': 'allecena.triggers', 'routing_key': 'triggers'},
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'rest_framework',
    'ac_common',
    'ac_computing',
    'ac_api',
    'ac_engine',
    'ac_engine_allegro',
    'ac_docs'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-name-bla-bla',
        # 'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        # 'LOCATION': '127.0.0.1:11211',
    }
}

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'temporary_db.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/home/rikkt0r/emails'

ALLECENA_EMAIL = 'no-reply@allecena.com'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('pl', 'Polski'),
    ('en', 'English'),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEST_RUNNER = 'ac_common.testrunner.AcTestRunner'
AUTH_USER_MODEL = 'ac_common.User'
AUTHENTICATION_BACKENDS = ['ac_common.backends.AllecenaAuthenticationBackend', 'ac_common.backends.FacebookAuthenticationBackend']
AUTH_KEY_ADDITION = 'iliketrainz'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'ac_common.drf.IsAuthenticatedAndOwnerPermission'

    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'ac_common.drf.AllecenaTokenAuth'
    ],
    'EXCEPTION_HANDLER': 'ac_common.drf.allecena_exception_handler'
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
        'simple_date': {
            'format': '[%(levelname)s] %(message)s',
            'datefmt': "%Y/%b/%d %H:%M:%S"
        },
        'stats': {
            'format': "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s",
            'datefmt': "%Y/%b/%d %H:%M:%S"
        },
    },
    'handlers': {
        'base': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 100,
            'filename': os.path.join(BASE_DIR, 'logs/log_django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'celery': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 100,
            'filename': os.path.join(BASE_DIR, 'logs/log_celery.log'),
            'formatter': 'simple_date'
        },
        'exception': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 100,
            'filename': os.path.join(BASE_DIR, 'logs/log_exception.log'),
            'formatter': 'verbose'
        },
        'api': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 100,
            'filename': os.path.join(BASE_DIR, 'logs/log_api.log'),
            'formatter': 'simple_date',
        },
        'statistics': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 100,
            'filename': os.path.join(BASE_DIR, 'logs/log_statistics.log'),
            'formatter': 'stats'
        },
    },
    'loggers': {
        # automatic loggers -----------
        'django.request': {
            'handlers': ['exception', 'console'],
            'propagate': False,
            'level': 'ERROR',
        },
        'suds': {
            'handlers': ['console', 'exception'],
            'level': 'ERROR',
            'propagate': True
        },
        'py.warnings': {
            'handlers': ['base', 'console'],
        },
        'django': {
            'handlers': ['base', 'exception', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['celery'],
            'level': 'DEBUG',
            'propagate': True
        },
        # manual loggers -----------
        'exception': {
            'handlers': ['exception', 'console'],
            'propagate': False,
            'level': 'ERROR',
        },
        'api': {
            'handlers': ['api', 'console'],
            'propagate': False,
            'level': 'INFO',
        },
        'statistics': {
            'handlers': ['statistics'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False
        },
    }
}

PROVIDER_ALLEGRO = 0
PROVIDER_EBAY = 1
PROVIDER_ALL = 2

PROVIDERS = (
    (PROVIDER_ALLEGRO, 'allegro'),
    (PROVIDER_EBAY, 'ebay'),
    (PROVIDER_ALL, 'all'),
)
PROVIDERS_KEYS = ('allegro', 'ebay', 'all')

ALLEGRO_SOAP_URL = 'https://webapi.allegro.pl/service.php'
# ALLEGRO_SOAP_WSDL = 'https://webapi.allegro.pl/service.php?wsdl'
# TO SAVE TIME ON SUDS CACHING PROBLEM....
ALLEGRO_SOAP_WSDL = 'file://' + os.path.join(BASE_DIR, 'static', 'allegro.wsdl')

ALLEGRO_VERSION_FILE = os.path.join(BASE_DIR, 'allegro_api.version')
ALLEGRO_SESSION_FILE = os.path.join(BASE_DIR, 'allegro_api.session')
ALLEGRO_VERSION = 0
ALLEGRO_COUNTRY = 1  # country code for poland

from .deploy_settings import ALLEGRO_PASSWORD_HASH, ALLEGRO_KEY, ALLEGRO_LOGIN

EBAY_SOAP_URL = 'register and fill me'
EBAY_SOAP_WSDL = 'file://' + os.path.join(BASE_DIR, 'static', 'ebay.wsdl')
EBAY_VERSION_FILE = os.path.join(BASE_DIR, 'ebay_api.version')
EBAY_SESSION_FILE = os.path.join(BASE_DIR, 'ebay_api.session')
EBAY_PASSWORD_HASH = 'register and fill me'
EBAY_KEY = 'register and fill me'
EBAY_VERSION = 'register and fill me'
EBAY_COUNTRY = 'register and fill me'
EBAY_LOGIN = 'register and fill me'

HINT_INPUT_ALLEGRO_CURRENT_QUANTITY = 100
HINT_INPUT_ALLEGRO_ENDED_QUANTITY = 100
PREDICTION_INPUT_ALLEGRO_CURRENT_QUANTITY = 100
PREDICTION_INPUT_ALLEGRO_ENDED_QUANTITY = 100

HINT_INPUT_EBAY_CURRENT_QUANTITY = 100
HINT_INPUT_EBAY_ENDED_QUANTITY = 100
PREDICTION_INPUT_EBAY_CURRENT_QUANTITY = 100
PREDICTION_INPUT_EBAY_ENDED_QUANTITY = 100

HINT_CORRELATIONS = True
HINT_NORMALIZE = True
HINT_CORRELATIONS_FILTERING = True
HINT_CORRELATIONS_FILTERING_MODE = 'number'
HINT_CORRELATIONS_FILTERING_NUMBER = 8
HINT_CORRELATIONS_FILTERING_THRESHOLD = 0.3
HINT_CORRELATIONS_RESULT_NUMBER = 5

PREDICTION_CORRELATIONS = True
PREDICTION_NORMALIZE = True
PREDICTION_CORRELATIONS_FILTERING = True
PREDICTION_CORRELATIONS_RESULT_NUMBER = 5
PREDICTION_CORRELATIONS_FILTERING_MODE = 'number'
PREDICTION_CORRELATIONS_FILTERING_NUMBER = 8
PREDICTION_CORRELATIONS_FILTERING_THRESHOLD = 0.3
PREDICTION_NEIGHBORS = True
PREDICTION_NEIGHBORS_WIN_ONLY = True
PREDICTION_NEIGHBORS_THRESHOLD = 0.01

BASE_EXCLUSION_SET = ['id', 'name', 'paymentTransfer', 'endingDate']
HINT_EXCLUSION_SET = BASE_EXCLUSION_SET + ['priceBuyNow', 'priceHighestBid', 'minPriceNotReached']
PREDICTION_EXCLUSION_SET = BASE_EXCLUSION_SET + ['success']

# http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC
PREDICTION_SVM_C = 1.0
PREDICTION_SVM_KERNEL = 'rbf'
PREDICTION_SVM_DEGREE = 3
PREDICTION_SVM_GAMMA = 0.0
PREDICTION_SVM_COEF0 = 0.0
PREDICTION_SVM_SHRINKING = True
PREDICTION_SVM_PROBABILITY = True
PREDICTION_SVM_TOL = 0.001
PREDICTION_SVM_CACHE_SIZE = 200
PREDICTION_SVM_CLASS_WEIGHT = None
PREDICTION_SVM_VERBOSE = False
PREDICTION_SVM_MAX_ITER = -1
PREDICTION_SVM_RANDOM_STATE = None

TRENDS_INTERVAL = 2592000 # 30 days

AUTH_PASSWORD_MIN_LENGTH = 5
AUTH_USERNAME_MAX_LENGTH = 25
