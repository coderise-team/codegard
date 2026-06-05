import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.prod")

# Bootstrap only. All Celery configuration (broker, reliability, beat schedule)
# lives in settings/celery_settings.py and is loaded via config_from_object.
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
