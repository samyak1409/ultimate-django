from .common import *
import os
import dj_database_url


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")  # TODO


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = []  # TODO


DATABASES = {"default": dj_database_url.config()}  # TODO


# Email:

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("?")  # TODO
EMAIL_PORT = os.environ.get("?")  # TODO
EMAIL_HOST_USER = os.environ.get("?")  # TODO
EMAIL_HOST_PASSWORD = os.environ.get("?")  # TODO
DEFAULT_FROM_EMAIL = "from@samyakstore.com"

ADMINS = [
    ("Samyak", "samyak65400@gmail.com"),
]


REDIS_URL = os.environ.get("REDIS_URL")  # TODO


# Celery:
CELERY_BROKER_URL = REDIS_URL


# Caching:
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,  # using same DB as Celery's redis
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,  # treat Redis being down as a cache miss instead of a 500
        },
        # "TIMEOUT": 600,  # override the default cache deletion time which is 300s
    }
}

DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
# `IGNORE_EXCEPTIONS` keeps the site up when Redis is down, but silently — log the
# ignored errors so a prod Redis outage is visible in logs instead of just slow pages
