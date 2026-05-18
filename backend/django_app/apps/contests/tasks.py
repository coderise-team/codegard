import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from redis import Redis

from .models import Contest

logger = logging.getLogger(__name__)


@shared_task
def update_contest_statuses() -> dict:
    """
    Periodic task: update contest statuses based on start/end times.

    Returns a small summary dict for logging/inspection.
    """

    now = timezone.now()

    # Finished: any contest whose end_time has passed should be finished.
    finished = Contest.objects.filter(end_time__lt=now).exclude(
        status=Contest.Status.FINISHED
    )
    finished_updated = finished.update(status=Contest.Status.FINISHED, updated_at=now)

    # Active: start_time <= now <= end_time
    active = Contest.objects.filter(start_time__lte=now, end_time__gte=now).exclude(
        status=Contest.Status.ACTIVE
    )
    active_updated = active.update(status=Contest.Status.ACTIVE, updated_at=now)

    # Pending: start_time in future
    pending = Contest.objects.filter(start_time__gt=now).exclude(
        status=Contest.Status.PENDING
    )
    pending_updated = pending.update(status=Contest.Status.PENDING, updated_at=now)

    total_current = {
        "finished": Contest.objects.filter(status=Contest.Status.FINISHED).count(),
        "active": Contest.objects.filter(status=Contest.Status.ACTIVE).count(),
        "pending": Contest.objects.filter(status=Contest.Status.PENDING).count(),
    }

    # Store previous totals in Redis so we can report net changes since the last run,
    # including contests created/edited outside this task.
    redis = Redis.from_url(settings.CELERY_BROKER_URL)
    key = "contests:status_totals"
    prev_raw = redis.hgetall(key)
    if prev_raw:
        prev = {k.decode(): int(v) for k, v in prev_raw.items()}
        delta = {k: total_current[k] - prev.get(k, 0) for k in total_current}
    else:
        delta = dict(total_current)
    redis.hset(
        key,
        mapping={k: str(v) for k, v in total_current.items()},
    )

    summary = {
        # What Celery changed in DB during this run.
        "db_updated": {
            "finished": finished_updated,
            "active": active_updated,
            "pending": pending_updated,
        },
        # Net change in totals since the previous run
        # (includes contests created/edited elsewhere).
        "delta_since_last_run": delta,
        "total_current": total_current,
    }

    logger.info(
        "update_contest_statuses db_updated=%s delta=%s total=%s",
        summary["db_updated"],
        summary["delta_since_last_run"],
        summary["total_current"],
    )

    return summary
