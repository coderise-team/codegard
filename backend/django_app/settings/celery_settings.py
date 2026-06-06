"""
Celery settings — all Celery configuration lives here.

Imported from settings/base.py via `from .celery_settings import *`. config/celery.py
only bootstraps `Celery()` and loads these via config_from_object(namespace="CELERY"),
so broker, reliability and the beat schedule are all kept in this single file.

Named celery_settings (not celery) to avoid confusion with config/celery.py,
which is the Celery *app* module, not its settings.
"""

import environ
from celery.schedules import crontab

env = environ.Env()

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)

# Reliability / observability
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Periodic tasks — applied to the app via namespace="CELERY" -> beat_schedule
CELERY_BEAT_SCHEDULE = {
    "contests-update-statuses-every-minute": {
        "task": "apps.contests.tasks.update_contest_statuses",
        "schedule": crontab(minute="*"),
    },
}
