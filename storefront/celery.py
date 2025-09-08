import os
from celery import Celery


# Set env var:
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storefront.settings.dev")

# Create Celery instance:
app = Celery("storefront")

# Configure with Django settings:
app.config_from_object("django.conf:settings", namespace="CELERY")
# `namespace="CELERY"`: all celery settings should start with "CELERY"

# Set auto-discover `tasks.py` file(s) (which would actually contain our tasks):
app.autodiscover_tasks()
