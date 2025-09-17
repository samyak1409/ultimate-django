from .common import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-z^h%9*k325z6r@h0srqkm(0*h8dyl9$m4u-woq&vibgt&ha=wh"


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Apps only required while dev:
INSTALLED_APPS += [
    "debug_toolbar",  # display various debug information
    "silk",  # live profiling and inspection tool
]


# Middlewares only required while dev:
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#add-the-middleware
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# https://github.com/barseghyanartur/django-debug-toolbar-force/?tab=readme-ov-file#installation
MIDDLEWARE.insert(1, "debug_toolbar_force.middleware.ForceDebugToolbarMiddleware")
# https://github.com/jazzband/django-silk?tab=readme-ov-file#installation
MIDDLEWARE.append("silk.middleware.SilkyMiddleware")
# Intended order: DebugToolbar+ForceDebugTool, Security, Cors, WhiteNoise, 6, Silky
# See Notes > Part 3 > Preparing for Production > Order of Middlewares.


INTERNAL_IPS = [
    "127.0.0.1",  # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configure-internal-ips
]


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ultimate_django",
        "USER": "samyak",
        "PASSWORD": "temporary",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}


# Email:

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 2525
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "from@samyakstore.com"

ADMINS = [
    ("Samyak", "samyak65400@gmail.com"),
]


# Celery:
CELERY_BROKER_URL = "redis://127.0.0.1:6379/1"


# Caching:
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",  # using a DB different from Celery's redis
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        # "TIMEOUT": 600,  # override the default cache deletion time which is 300s
    }
}
