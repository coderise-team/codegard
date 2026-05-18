import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "settings.dev")
)

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "contests-update-statuses-every-minute": {
        "task": "apps.contests.tasks.update_contest_statuses",
        "schedule": crontab(minute="*"),
    },
}
