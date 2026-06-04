"""
Celery configuration.

Imported from settings/base.py via `from config.settings.celery import *`.
The Celery app itself lives in config/celery.py — this module only holds settings.
"""

import os


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


_default_broker = _env("CELERY_BROKER_URL", "redis://redis:6379/0")

CELERY_BROKER_URL = _default_broker
CELERY_RESULT_BACKEND = _env("CELERY_RESULT_BACKEND", _default_broker)
CELERY_TASK_ALWAYS_EAGER = _env("CELERY_TASK_ALWAYS_EAGER", "").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# Reliability / observability
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
